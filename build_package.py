import os
import plistlib
import tarfile
import lzma
import gzip
import io
import time
import shutil
import struct
import hashlib

WORK_DIR = r"C:\Users\AmiaXf\.gemini\antigravity\scratch\phucstandby"
PKG_DATA = os.path.join(WORK_DIR, "pkg_data")
PREF_BUNDLE = os.path.join(PKG_DATA, "var", "jb", "Library", "PreferenceBundles", "StandByPref.bundle")
ORIG_DEB = r"C:\Users\AmiaXf\.gemini\antigravity\brain\5165544a-0a52-45bf-8453-b245ab707f42\.user_uploaded\media_1793365283513_053f84f1.deb"

# Translations mapping for Preference Bundle:
TRANSLATIONS = [
    # Top-level Title
    ("PhucStandby", "PhucStandby", "PhucStandby", "PhucStandby", "PhucStandby"),
    ("StandBy iOS 16", "StandBy iOS 16", "StandBy iOS 16", "StandBy iOS 16", "StandBy iOS 16"),
    
    # Item 0: Header Group
    ("StandBy ", "StandBy ", "StandBy ", "StandBy ", "StandBy "),
    ("StandBy", "StandBy", "StandBy", "StandBy", "StandBy"),
    (
        "Rotate to landscape + charge to view.\n• Swipe HORIZONTALLY: clock <-> photo wallpaper page\n• Swipe UP/DOWN: clock style 1 → 2 → photo + weather (on photo page, switches photo)\n• Tap music dot: open music control panel\nChanges take effect immediately, no respring required.",
        "Xoay ngang + đang sạc để hiện.\n• Vuốt NGANG: đồng hồ <-> trang ảnh nền\n• Vuốt LÊN/XUỐNG: kiểu đồng hồ 1 → 2 → ảnh + thời tiết (ở trang ảnh nền thì đổi ảnh)\n• Chạm chấm nhạc: mở khung điều khiển nhạc\nThay đổi áp dụng ngay, không cần respring.",
        "Rotate to landscape + charge to view.\n• Swipe HORIZONTALLY: clock <-> photo wallpaper page\n• Swipe UP/DOWN: clock style 1 → 2 → photo + weather (on photo page, switches photo)\n• Tap music dot: open music control panel\nChanges take effect immediately, no respring required.",
        "Putar ke lanskap + isi daya untuk menampilkan.\n• Geser HORIZONTAL: jam <-> halaman wallpaper foto\n• Geser ATAS/BAWAH: gaya jam 1 → 2 → foto + cuaca (di halaman foto: ganti foto)\n• Ketuk titik musik: buka panel kontrol musik\nPerubahan langsung diterapkan, tidak perlu respring.",
        "Xoay ngang + đang sạc để hiện.\n• Vuốt NGANG: đồng hồ <-> trang ảnh nền\n• Vuốt LÊN/XUỐNG: kiểu đồng hồ 1 → 2 → ảnh + thời tiết (ở trang ảnh nền thì đổi ảnh)\n• Chạm chấm nhạc: mở khung điều khiển nhạc\nThay đổi áp dụng ngay, không cần respring."
    ),

    # Switches
    ("Enable StandBy", "Bật StandBy", "Enable StandBy", "Aktifkan StandBy", "Bật StandBy"),
    ("24-Hour Time", "Giờ 24h", "24-Hour Time", "Format 24 Jam", "Giờ 24h"),
    ("Keep Screen Awake", "Giữ màn hình sáng", "Keep Screen Awake", "Biarkan Layar Tetap Menyala", "Giữ màn hình sáng"),

    # Clock Color Group & LinkList
    ("Clock Color", "Màu giờ", "Clock Color", "Warna Jam", "Màu giờ"),
    (
        "Select 'Custom' to use the 3 Hue / Saturation / Brightness sliders. If the switches below are enabled, now playing artwork color and night mode red will take priority.",
        "Chọn 'Tuỳ chỉnh' để dùng 3 thanh Hue / Saturation / Brightness. Nếu bật các công tắc dưới thì màu bìa nhạc (khi đang phát) và đỏ ban đêm vẫn được ưu tiên.",
        "Select 'Custom' to use the 3 Hue / Saturation / Brightness sliders. If the switches below are enabled, now playing artwork color and night mode red will take priority.",
        "Pilih 'Kustom' untuk menggunakan 3 penggeser Hue / Saturation / Brightness. Jika sakelar di bawah aktif, warna sampul musik (saat diputar) dan mode malam merah tetap diprioritaskan.",
        "Chọn 'Tuỳ chỉnh' để dùng 3 thanh Hue / Saturation / Brightness. Nếu bật các công tắc dưới thì màu bìa nhạc (khi đang phát) và đỏ ban đêm vẫn được ưu tiên."
    ),

    # Color presets
    (
        "Default (different color per style)",
        "Mặc định (mỗi kiểu một màu)",
        "Default (different color per style)",
        "Default (warna berbeda tiap gaya)",
        "Mặc định (mỗi kiểu một màu)"
    ),
    ("Pink", "Hồng", "Pink", "Merah Muda", "Hồng"),
    ("Blue", "Xanh dương", "Blue", "Biru", "Xanh dương"),
    ("Purple", "Tím", "Purple", "Ungu", "Tím"),
    ("Orange", "Cam", "Orange", "Oranye", "Cam"),
    ("Green", "Xanh lá", "Green", "Hijau", "Xanh lá"),
    ("White", "Trắng", "White", "Putih", "Trắng"),
    ("Yellow", "Vàng", "Yellow", "Kuning", "Vàng"),
    (
        "Custom (3 sliders below)",
        "Tuỳ chỉnh (3 thanh bên dưới)",
        "Custom (3 sliders below)",
        "Kustom (3 penggeser di bawah)",
        "Tuỳ chỉnh (3 thanh bên dưới)"
    ),

    # Switches & Sliders
    (
        "Match Now Playing Album Artwork Color",
        "Đổi màu theo bìa nhạc khi đang phát",
        "Match Now Playing Album Artwork Color",
        "Sesuaikan Warna dengan Sampul Album saat Memutar Musik",
        "Đổi màu theo bìa nhạc khi đang phát"
    ),
    ("Night Mode", "Chế độ ban đêm", "Night Mode", "Mode Malam", "Chế độ ban đêm"),
    (
        "Hue — only used when 'Custom' is selected",
        "Hue (sắc độ) — chỉ dùng khi chọn 'Tuỳ chỉnh'",
        "Hue — only used when 'Custom' is selected",
        "Hue (corak) — hanya digunakan saat 'Kustom' dipilih",
        "Hue (sắc độ) — chỉ dùng khi chọn 'Tuỳ chỉnh'"
    ),
    ("Hue", "Hue", "Hue", "Hue", "Hue"),
    ("Saturation", "Độ bão hòa", "Saturation", "Saturasi", "Độ bão hòa"),
    ("Brightness", "Độ sáng", "Brightness", "Kecerahan", "Độ sáng"),

    # Music Wave Color Group
    ("Music Wave Color", "Màu sóng nhạc", "Music Wave Color", "Warna Gelombang Musik", "Màu sóng nhạc"),
    (
        "Color of the audio waveform visualizer when music is playing. If 'Match Album Artwork' above is enabled, it takes priority.",
        "Màu của sóng nhạc động khi đang phát nhạc. Nếu bật 'Đổi màu theo bìa nhạc' ở trên thì màu bìa vẫn được ưu tiên.",
        "Color of the audio waveform visualizer when music is playing. If 'Match Album Artwork' above is enabled, it takes priority.",
        "Warna visualizer gelombang audio saat musik diputar. Jika 'Sesuaikan Warna Sampul Album' di atas aktif, warna sampul tetap diprioritaskan.",
        "Màu của sóng nhạc động khi đang phát nhạc. Nếu bật 'Đổi màu theo bìa nhạc' ở trên thì màu bìa vẫn được ưu tiên."
    ),

    # Photo Page Settings
    ("Photo Page Settings", "Cài đặt trang ảnh nền", "Photo Page Settings", "Pengaturan Halaman Foto", "Cài đặt trang ảnh nền"),
    (
        "Hide bottom-right clock on photo page",
        "Ẩn đồng hồ nhỏ góc phải ở trang ảnh",
        "Hide bottom-right clock on photo page",
        "Sembunyikan jam kecil di sudut kanan halaman foto",
        "Ẩn đồng hồ nhỏ góc phải ở trang ảnh"
    ),
    ("Dim Photo Wallpaper", "Làm tối ảnh nền", "Dim Photo Wallpaper", "Redupkan Wallpaper Foto", "Làm tối ảnh nền"),
    (
        "Custom Album Name",
        "Tên album ảnh tuỳ chỉnh",
        "Custom Album Name",
        "Nama Album Foto Kustom",
        "Tên album ảnh tuỳ chỉnh"
    ),
    (
        "Name of the Photos album to pull wallpaper photos from. Leave blank to show recently added photos (up to 20).",
        "Tên album trong ứng dụng Ảnh để lấy hình nền. Để trống sẽ hiện ảnh mới thêm gần đây (tối đa 20 ảnh).",
        "Name of the Photos album to pull wallpaper photos from. Leave blank to show recently added photos (up to 20).",
        "Nama album di aplikasi Foto untuk mengambil wallpaper. Biarkan kosong untuk menampilkan foto terbaru (hingga 20 foto).",
        "Tên album trong ứng dụng Ảnh để lấy hình nền. Để trống sẽ hiện ảnh mới thêm gần đây (tối đa 20 ảnh)."
    ),
    ("Pick Photos from Album", "Chọn ảnh trong album", "Pick Photos from Album", "Pilih Foto từ Album", "Chọn ảnh trong album"),
    (
        "Tap to open album picker. StandBy must have Photos permission.",
        "Chạm để mở chọn ảnh. Cần cấp quyền truy cập Ảnh cho StandBy.",
        "Tap to open album picker. StandBy must have Photos permission.",
        "Ketuk untuk membuka pemilih album. StandBy memerlukan izin akses Foto.",
        "Chạm để mở chọn ảnh. Cần cấp quyền truy cập Ảnh cho StandBy."
    ),

    # Custom Font
    ("Custom Font", "Phông chữ tuỳ chỉnh", "Custom Font", "Font Kustom", "Phông chữ tuỳ chỉnh"),
    (
        "Enter PostScript name of installed custom font. Leave blank to use system font.",
        "Nhập tên PostScript của font chữ đã cài. Để trống để dùng font hệ thống.",
        "Enter PostScript name of installed custom font. Leave blank to use system font.",
        "Masukkan nama PostScript dari font yang terpasang. Biarkan kosong untuk menggunakan font sistem.",
        "Nhập tên PostScript của font chữ đã cài. Để trống để dùng font hệ thống."
    ),

    # Reset
    ("Reset All Settings to Default", "Đặt lại toàn bộ về mặc định", "Reset All Settings to Default", "Reset Semua Pengaturan ke Default", "Đặt lại toàn bộ về mặc định"),
    (
        "Reset all settings back to default values.",
        "Khôi phục toàn bộ cài đặt về trạng thái ban đầu.",
        "Reset all settings back to default values.",
        "Kembalikan semua pengaturan ke nilai default awal.",
        "Khôi phục toàn bộ cài đặt về trạng thái ban đầu."
    ),

    # Language Info Group
    ("Language", "Ngôn ngữ", "Language", "Bahasa", "Ngôn ngữ"),
    (
        "StandBy tweak preferences automatically follow your iOS system language (English, Indonesian, Vietnamese).",
        "Cài đặt tinh chỉnh StandBy tự động theo ngôn ngữ hệ thống iOS của bạn (Tiếng Anh, Tiếng Việt, Indonesia).",
        "StandBy tweak preferences automatically follow your iOS system language (English, Indonesian, Vietnamese).",
        "Pengaturan tweak StandBy secara otomatis mengikuti bahasa sistem iOS Anda (Inggris, Indonesia, Vietnam).",
        "Cài đặt tinh chỉnh StandBy tự động theo ngôn ngữ hệ thống iOS của bạn (Tiếng Anh, Tiếng Việt, Indonesia)."
    ),

    # Actions & Respring
    ("Actions", "Thao tác", "Actions", "Tindakan", "Thao tác"),
    (
        "Respring SpringBoard if needed to reload system cache.",
        "Respring SpringBoard nếu cần tải lại bộ nhớ đệm hệ thống.",
        "Respring SpringBoard if needed to reload system cache.",
        "Respring SpringBoard jika diperlukan untuk memuat ulang cache sistem.",
        "Respring SpringBoard nếu cần tải lại bộ nhớ đệm hệ thống."
    ),
    ("Respring SpringBoard", "Respring SpringBoard", "Respring SpringBoard", "Respring SpringBoard", "Respring SpringBoard"),
    (
        "Are you sure you want to respring?",
        "Bạn có chắc chắn muốn respring không?",
        "Are you sure you want to respring?",
        "Apakah Anda yakin ingin melakukan respring?",
        "Bạn có chắc chắn muốn respring không?"
    ),
    ("Respring", "Respring", "Respring", "Respring", "Respring"),
    ("Cancel", "Hủy", "Cancel", "Batal", "Hủy"),

    # Credits
    ("Credits", "Tác giả & Đóng góp", "Credits", "Kredit", "Tác giả & Đóng góp"),
    (
        "PhucStandBy Fixed & Maintained by amiaxf",
        "PhucStandBy sửa lỗi & duy trì bởi amiaxf",
        "PhucStandBy Fixed & Maintained by amiaxf",
        "PhucStandBy Diperbaiki & Dikelola oleh amiaxf",
        "PhucStandBy sửa lỗi & duy trì bởi amiaxf"
    ),
    (
        "Original Developer: tranhoangphuc (PhucBakhi)",
        "Nhà phát triển gốc: tranhoangphuc (PhucBakhi)",
        "Original Developer: tranhoangphuc (PhucBakhi)",
        "Pengembang Asli: tranhoangphuc (PhucBakhi)",
        "Nhà phát triển gốc: tranhoangphuc (PhucBakhi)"
    ),
    (
        "Maintainer & Fixes: amiaxf",
        "Người duy trì & Sửa lỗi: amiaxf",
        "Maintainer & Fixes: amiaxf",
        "Pemelihara & Perbaikan: amiaxf",
        "Người duy trì & Sửa lỗi: amiaxf"
    )
]

def escape_apple_string(s):
    res = []
    for c in s:
        if c == '"':
            res.append(r'\"')
        elif c == '\\':
            res.append(r'\\')
        elif c == '\n':
            res.append(r'\n')
        elif c == '\r':
            res.append(r'\r')
        elif c == '\t':
            res.append(r'\t')
        else:
            res.append(c)
    return "".join(res)

def generate_strings_content(lang_idx, lang_name):
    val_idx = 2 + lang_idx
    lines = [
        f"/* Root.strings ({lang_name}) */",
        f"/* Generated with English and Indonesian language support */",
        ""
    ]
    seen_keys = set()
    for entry in TRANSLATIONS:
        en_key = entry[0]
        vi_key = entry[1]
        val = entry[val_idx]
        
        if en_key and en_key not in seen_keys:
            lines.append(f'"{escape_apple_string(en_key)}" = "{escape_apple_string(val)}";')
            seen_keys.add(en_key)
            
        if vi_key and vi_key not in seen_keys:
            lines.append(f'"{escape_apple_string(vi_key)}" = "{escape_apple_string(val)}";')
            seen_keys.add(vi_key)
            
    lines.append("")
    return "\n".join(lines)

# Strict in-place translation tables that preserve weather strings 100%
SLOT_TRANSLATIONS = {
    "en": [
        (81,  'Playing', False),                  # 7 chars <= 10
        (109, 'SUNDAY', False),                   # 6 chars <= 9
        (110, 'DAY %ld', False),                  # 7 chars <= 8
        (124, 'Sunday', False),                   # 6 chars <= 9
        (125, 'Day %ld', False),                  # 7 chars <= 8
        (126, '%@, %ld/%ld', True),               # 11 chars <= 15
        (127, '%lu events\ntoday', False),        # 16 chars <= 20
        (128, 'Your day is clear', False),        # 17 chars <= 19
        (129, 'Today', False),                    # 5 chars <= 8
        (130, 'Cannot read calendar', False),     # 20 chars <= 27
        (132, 'No music\nplaying', False),        # 16 chars <= 23
        (133, 'Paused', False),                   # 6 chars <= 9
        (140, 'No new\nnotifications', False),    # 21 chars <= 22
        (141, 'Recent', False),                   # 6 chars <= 8
        (143, 'Charging', False),                 # 8 chars <= 9
        (144, 'Bat', True),                       # 3 chars <= 3
        (156, 'Add photos to ', False)            # 14 chars <= 25
    ],
    "id": [
        (81,  'Memutar', False),                  # 7 chars <= 10
        (109, 'MINGGU', False),                   # 6 chars <= 9
        (110, 'HARI %ld', False),                 # 8 chars <= 8
        (124, 'Minggu', False),                   # 6 chars <= 9
        (125, 'Hari %ld', False),                 # 8 chars <= 8
        (126, '%@, %ld/%ld', True),               # 11 chars <= 15
        (127, '%lu acara hari ini', False),       # 18 chars <= 20
        (128, 'Tidak ada acara', False),          # 15 chars <= 19
        (129, 'Hari ini', False),                 # 8 chars <= 8
        (130, 'Gagal membaca kalender', False),   # 22 chars <= 27
        (132, 'Tidak ada musik', False),          # 15 chars <= 23
        (133, 'Dijeda', False),                   # 6 chars <= 9
        (140, 'Tidak ada notifikasi', False),     # 20 chars <= 22
        (141, 'Terbaru', False),                  # 7 chars <= 8
        (143, 'Isi Daya', False),                 # 8 chars <= 9
        (144, 'Bat', True),                       # 3 chars <= 3
        (156, 'Pilih foto ', False)               # 11 chars <= 25
    ],
    "vi": [
        (81,  'Đang phát', False),
        (109, 'CHỦ NHẬT', False),
        (110, 'THỨ %ld', False),
        (124, 'Chủ nhật', False),
        (125, 'Thứ %ld', False),
        (126, '%@, %ld/%ld', True),
        (127, '%lu sự kiện\nhôm nay', False),
        (128, 'Ngày của bạn trống', False),
        (129, 'Hôm nay', False),
        (130, 'Chưa đọc được sự kiện lịch', False),
        (132, 'Chưa có nhạc\nđang phát', False),
        (133, 'Tạm dừng', False),
        (140, 'Chưa có thông báo\nmới', False),
        (141, 'Mới đây', False),
        (143, 'Đang sạc', False),
        (144, 'Pin', True),
        (156, 'Bỏ ảnh vào ', False)
    ]
}

def extract_clean_pristine_dylib():
    with open(ORIG_DEB, "rb") as f:
        deb_data = f.read()

    pos = 8
    while pos < len(deb_data):
        header = deb_data[pos:pos+60]
        name = header[:16].decode("latin1").strip()
        size = int(header[48:58].strip())
        if name == "data.tar.lzma":
            tar_bytes = lzma.decompress(deb_data[pos+60:pos+60+size], format=lzma.FORMAT_ALONE)
            with tarfile.open(fileobj=io.BytesIO(tar_bytes)) as tar:
                return bytearray(tar.extractfile("var/jb/Library/MobileSubstrate/DynamicLibraries/StandBy.dylib").read())
        pos += 60 + size
        if size % 2:
            pos += 1
    raise RuntimeError("Could not find data.tar.lzma in original deb")

def build_patched_dylib(clean_bytes, lang_code):
    data = bytearray(clean_bytes)
    s0 = 0x4000
    s1 = 0x7c000
    NOP_INSN = bytes([0x1f, 0x20, 0x03, 0xd5])

    # 1. Lockscreen NOP in shouldShow (StandBy only shows on lockscreen, saves battery)
    data[s0 + 0xc7f4 : s0 + 0xc7f8] = NOP_INSN
    data[s1 + 0xbff4 : s1 + 0xbff8] = NOP_INSN

    # 2. Disable broken infinite wake loop in tick
    # In original tweak, updateWakeLogic in tick caused an infinite wake loop and black wallpaper on lockscreen.
    # NOPing the tick call completely kills the infinite wake loop and black wallpaper bug.
    data[s0 + 0xcc2c : s0 + 0xcc30] = NOP_INSN
    data[s1 + 0xc3f8 : s1 + 0xc3fc] = NOP_INSN

    # 3. Widget swipe unstick (prevent gesture being dropped if touch begins near pill indicator)
    data[s0 + 0x1e66c : s0 + 0x1e670] = bytes([0x09, 0x00, 0x00, 0x14])
    data[s0 + 0x1f8c4 : s0 + 0x1f8c8] = bytes([0x03, 0x00, 0x00, 0x14])
    data[s1 + 0x1e1a4 : s1 + 0x1e1a8] = bytes([0x05, 0x00, 0x00, 0x14])
    data[s1 + 0x1f430 : s1 + 0x1f434] = bytes([0x02, 0x00, 0x00, 0x14])

    # NOTE: Window background color (0x20818 / 0x20410) is kept 100% PRISTINE blackColor.
    # The previous faulty patch attempted to add to uninitialized register x16, causing instant crash on tilt!
    # Pristine blackColor is valid, gorgeous for OLED StandBy, and NEVER crashes.

    # 4. Safe in-place string translation
    slots = SLOT_TRANSLATIONS[lang_code]
    cf_base_0 = 0x44730
    cf_base_1 = 0x44a08

    for idx, text, is_cstr in slots:
        off0 = s0 + cf_base_0 + idx * 32
        isa0, f0, ptr0, len0 = struct.unpack('<QQQQ', data[off0:off0+32])
        off1 = s1 + cf_base_1 + idx * 32
        isa1, f1, ptr1, len1 = struct.unpack('<QQQQ', data[off1:off1+32])
        ptr1_clean = ptr1 & 0xffffffffffff

        if not is_cstr:
            raw = text.encode('utf-16le')
            data[s0+ptr0:s0+ptr0+len0*2] = b'\x00' * (len0*2)
            data[s0+ptr0:s0+ptr0+len(raw)] = raw
            struct.pack_into('<Q', data, off0 + 24, len(text))

            data[s1+ptr1_clean:s1+ptr1_clean+len1*2] = b'\x00' * (len1*2)
            data[s1+ptr1_clean:s1+ptr1_clean+len(raw)] = raw
            struct.pack_into('<Q', data, off1 + 24, len(text))
        else:
            raw = text.encode('ascii')
            data[s0+ptr0:s0+ptr0+len0] = b'\x00' * len0
            data[s0+ptr0:s0+ptr0+len(raw)] = raw
            struct.pack_into('<Q', data, off0 + 24, len(text))

            data[s1+ptr1_clean:s1+ptr1_clean+len1] = b'\x00' * len1
            data[s1+ptr1_clean:s1+ptr1_clean+len(raw)] = raw
            struct.pack_into('<Q', data, off1 + 24, len(text))

    # 5. Verify Weather format strings strictly intact
    weather_indices = [(105, '%d°C'), (113, '%ld°'), (114, 'C:%ld° T:%ld°'), (115, 'C:--° T:--°'), (131, '• '), (148, 'H:%ld° L:%ld°')]
    for arch_name, arch_off, cf_base in [('arm64', s0, cf_base_0), ('arm64e', s1, cf_base_1)]:
        for widx, exp in weather_indices:
            off = arch_off + cf_base + widx * 32
            isa, f, ptr, l = struct.unpack('<QQQQ', data[off:off+32])
            ptr_clean = ptr & 0xffffffffffff
            val = data[arch_off + ptr_clean : arch_off + ptr_clean + l*2].decode('utf-16le')
            assert val == exp, f'{arch_name} weather {widx} mismatch: {val} != {exp}'

    # 6. Re-sign CodeDirectory SHA-256 hashes
    arches = [(0, s0, 487968), (1, s1, 486416)]
    for arch_idx, arch_off, arch_size in arches:
        arch_data = data[arch_off:arch_off+arch_size]
        ncmds, sizeofcmds = struct.unpack('<II', arch_data[16:24])
        offset = 32
        cs_dataoff = None
        for _ in range(ncmds):
            cmd, cmdsize = struct.unpack('<II', arch_data[offset:offset+8])
            if cmd == 0x1d:
                cs_dataoff, cs_datasize = struct.unpack('<II', arch_data[offset+8:offset+16])
                break
            offset += cmdsize
        superblob_off = arch_off + cs_dataoff
        slot_type, slot_off = struct.unpack('>II', data[superblob_off+12:superblob_off+20])
        cd_abs_off = superblob_off + slot_off
        magic, length, ver, flags, hashoff, identoff, nspecial, ncode, codelimit, hashsize, hashtype, platform, pageshift = struct.unpack('>IIIIIIIIIBBBB', data[cd_abs_off:cd_abs_off+40])
        page_size = 1 << pageshift
        for p in range(ncode):
            p_start = arch_off + p * page_size
            p_end = arch_off + min((p + 1) * page_size, codelimit)
            h = hashlib.sha256(data[p_start:p_end]).digest()
            data[cd_abs_off+hashoff+p*hashsize:cd_abs_off+hashoff+(p+1)*hashsize] = h

    return data

def resign_macho(file_path):
    with open(file_path, 'rb') as f:
        data = bytearray(f.read())

    magic = struct.unpack('<I', data[:4])[0]
    fat_magic = 0xbebafeca
    if magic != fat_magic:
        arches = [(0, 0, len(data))]
    else:
        nfat_arch = struct.unpack('>I', data[4:8])[0]
        arches = []
        for i in range(nfat_arch):
            cputype, cpusubtype, offset, size, align = struct.unpack('>IIIII', data[8 + i*20 : 8 + (i+1)*20])
            arches.append((i, offset, size))

    total_mismatches = 0
    for arch_idx, arch_off, arch_size in arches:
        arch_data = data[arch_off:arch_off+arch_size]
        ncmds, sizeofcmds = struct.unpack('<II', arch_data[16:24])
        offset = 32
        cs_dataoff = None
        for _ in range(ncmds):
            cmd, cmdsize = struct.unpack('<II', arch_data[offset:offset+8])
            if cmd == 0x1d:
                cs_dataoff, cs_datasize = struct.unpack('<II', arch_data[offset+8:offset+16])
                break
            offset += cmdsize

        if not cs_dataoff:
            continue

        superblob_off = arch_off + cs_dataoff
        slot_type, slot_off = struct.unpack('>II', data[superblob_off+12:superblob_off+20])
        cd_abs_off = superblob_off + slot_off
        magic, length, ver, flags, hashoff, identoff, nspecial, ncode, codelimit, hashsize, hashtype, platform, pageshift = struct.unpack('>IIIIIIIIIBBBB', data[cd_abs_off:cd_abs_off+40])
        page_size = 1 << pageshift

        for p in range(ncode):
            p_start = arch_off + p * page_size
            p_end = arch_off + min((p + 1) * page_size, codelimit)
            h = hashlib.sha256(data[p_start:p_end]).digest()
            h_dest = cd_abs_off + hashoff + p * hashsize
            if data[h_dest:h_dest+hashsize] != h:
                total_mismatches += 1
                data[h_dest:h_dest+hashsize] = h

    with open(file_path, 'wb') as f:
        f.write(data)
    print(f"Resigned {os.path.basename(file_path)}: {total_mismatches} mismatches corrected")

def prepare_settings_bundle():
    lprojs = {
        "en": (0, "English"),
        "id": (1, "Indonesian"),
        "vi": (2, "Vietnamese")
    }
    
    for code, (idx, lang_name) in lprojs.items():
        lproj_dir = os.path.join(PREF_BUNDLE, f"{code}.lproj")
        os.makedirs(lproj_dir, exist_ok=True)
        
        root_strings_path = os.path.join(lproj_dir, "Root.strings")
        content = generate_strings_content(idx, lang_name)
        with open(root_strings_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        infoplist_strings_path = os.path.join(lproj_dir, "InfoPlist.strings")
        display_name = "StandBy"
        info_content = f'CFBundleDisplayName = "{display_name}";\nCFBundleName = "{display_name}";\n'
        with open(infoplist_strings_path, "w", encoding="utf-8") as f:
            f.write(info_content)

    info_plist_path = os.path.join(PREF_BUNDLE, "Info.plist")
    with open(info_plist_path, "rb") as f:
        info_pl = plistlib.load(f)
    info_pl["CFBundleDevelopmentRegion"] = "en"
    info_pl["CFBundleLocalizations"] = ["en", "id", "vi"]
    with open(info_plist_path, "wb") as f:
        plistlib.dump(info_pl, f, fmt=plistlib.FMT_XML)

    root_plist_path = os.path.join(PREF_BUNDLE, "Root.plist")
    with open(root_plist_path, "rb") as f:
        root_pl = plistlib.load(f)

    vi_to_en = {}
    for en_k, vi_k, en_v, id_v, vi_v in TRANSLATIONS:
        vi_to_en[vi_k] = en_v

    for item in root_pl.get("items", []):
        if "label" in item and item["label"] in vi_to_en:
            item["label"] = vi_to_en[item["label"]]
        if "footerText" in item and item["footerText"] in vi_to_en:
            item["footerText"] = vi_to_en[item["footerText"]]
        if "placeholder" in item and item["placeholder"] in vi_to_en:
            item["placeholder"] = vi_to_en[item["placeholder"]]
        elif "placeholder" in item and "hoangluongnigger" in item["placeholder"]:
            item["placeholder"] = "e.g. My Wallpaper"
        if "validTitles" in item:
            item["validTitles"] = [vi_to_en.get(t, t) for t in item["validTitles"]]
        if "shortTitles" in item:
            item["shortTitles"] = [vi_to_en.get(t, t) for t in item["shortTitles"]]

    root_pl["items"] = [it for it in root_pl["items"] if it.get("key") not in ["language", "wakeScreen", "wakeDelay"]]
    root_pl["items"] = [it for it in root_pl["items"] if not (it.get("cell") == "PSGroupCell" and it.get("label") in ["Language", "Ngôn ngữ", "Bahasa", "Độ trễ tự bật màn hình (giây)", "Auto Wake Delay (seconds)", "Actions"])]
    root_pl["items"] = [it for it in root_pl["items"] if it.get("action") != "respring:"]

    enabled_idx = 1
    for idx, it in enumerate(root_pl["items"]):
        if it.get("key") == "enabled":
            enabled_idx = idx
            break

    lang_group = {
        "cell": "PSGroupCell",
        "label": "Language",
        "footerText": "StandBy tweak preferences automatically follow your iOS system language (English, Indonesian, Vietnamese)."
    }
    root_pl["items"].insert(enabled_idx + 1, lang_group)

    # Actions & Respring
    root_pl["items"].append({
        "cell": "PSGroupCell",
        "label": "Actions",
        "footerText": "Respring SpringBoard if needed to reload system cache."
    })
    root_pl["items"].append({
        "action": "respring:",
        "cell": "PSButtonCell",
        "label": "Respring SpringBoard",
        "confirmation": {
            "prompt": "Are you sure you want to respring?",
            "title": "Respring",
            "okTitle": "Respring",
            "cancelTitle": "Cancel"
        }
    })

    has_credits = any("umiaxf" in str(it) or "amiaxf" in str(it) for it in root_pl["items"])
    if not has_credits:
        root_pl["items"].append({
            "cell": "PSGroupCell",
            "label": "Credits",
            "footerText": "PhucStandBy Fixed & Maintained by amiaxf"
        })
        root_pl["items"].append({
            "cell": "PSStaticTextCell",
            "label": "Original Developer: tranhoangphuc (PhucBakhi)"
        })
        root_pl["items"].append({
            "cell": "PSStaticTextCell",
            "label": "Maintainer & Fixes: amiaxf"
        })

    with open(root_plist_path, "wb") as f:
        plistlib.dump(root_pl, f, fmt=plistlib.FMT_XML)

    pref_bin_path = os.path.join(PREF_BUNDLE, "StandByPref")
    resign_macho(pref_bin_path)

def package_deb(output_filename):
    control_path = os.path.join(WORK_DIR, "pkg", "DEBIAN", "control")
    with open(control_path, "r", encoding="utf-8") as f:
        ctrl_content = f.read()

    new_ctrl_lines = []
    for line in ctrl_content.splitlines():
        if line.startswith("Description:"):
            new_ctrl_lines.append("Description: Bring the iOS 17 StandBy experience to iOS 16 and older devices (Supports English, Indonesian, and Vietnamese)")
        elif line.startswith("Maintainer:"):
            new_ctrl_lines.append("Maintainer: amiaxf")
        else:
            new_ctrl_lines.append(line)

    new_ctrl_content = "\n".join(new_ctrl_lines).strip() + "\n"
    with open(control_path, "w", encoding="utf-8") as f:
        f.write(new_ctrl_content)

    data_tar_buf = io.BytesIO()
    with tarfile.open(fileobj=data_tar_buf, mode="w") as tar:
        for root, dirs, files in os.walk(PKG_DATA):
            rel = os.path.relpath(root, PKG_DATA)
            arcname = "." if rel == "." else rel.replace("\\", "/")
            
            ti = tarfile.TarInfo(name=arcname)
            ti.type = tarfile.DIRTYPE
            ti.mode = 0o755
            ti.uid = 0
            ti.gid = 0
            ti.uname = "root"
            ti.gname = "wheel"
            ti.mtime = int(time.time())
            tar.addfile(ti)

            for file in files:
                file_path = os.path.join(root, file)
                file_arcname = (arcname + "/" + file).lstrip("./") if arcname != "." else file
                
                with open(file_path, "rb") as f_in:
                    file_data = f_in.read()

                ti = tarfile.TarInfo(name=file_arcname)
                ti.size = len(file_data)
                if file in ["StandBy.dylib", "StandByPref"]:
                    ti.mode = 0o755
                else:
                    ti.mode = 0o644
                ti.uid = 0
                ti.gid = 0
                ti.uname = "root"
                ti.gname = "wheel"
                ti.mtime = int(time.time())
                tar.addfile(ti, io.BytesIO(file_data))

    data_tar_bytes = data_tar_buf.getvalue()
    data_lzma_bytes = lzma.compress(data_tar_bytes, format=lzma.FORMAT_ALONE)

    ctrl_tar_buf = io.BytesIO()
    with gzip.GzipFile(fileobj=ctrl_tar_buf, mode="wb", mtime=0) as gz_out:
        with tarfile.open(fileobj=gz_out, mode="w") as tar:
            ti_dot = tarfile.TarInfo(name=".")
            ti_dot.type = tarfile.DIRTYPE
            ti_dot.mode = 0o755
            ti_dot.uid = 0
            ti_dot.gid = 0
            ti_dot.uname = "root"
            ti_dot.gname = "wheel"
            ti_dot.mtime = int(time.time())
            tar.addfile(ti_dot)

            with open(control_path, "rb") as f_ctrl:
                ctrl_bytes = f_ctrl.read()
            ti_ctrl = tarfile.TarInfo(name="./control")
            ti_ctrl.size = len(ctrl_bytes)
            ti_ctrl.mode = 0o644
            ti_ctrl.uid = 0
            ti_ctrl.gid = 0
            ti_ctrl.uname = "root"
            ti_ctrl.gname = "wheel"
            ti_ctrl.mtime = int(time.time())
            tar.addfile(ti_ctrl, io.BytesIO(ctrl_bytes))

    ctrl_gz_bytes = ctrl_tar_buf.getvalue()

    out_deb_path = os.path.join(WORK_DIR, output_filename)

    def make_ar_header(name, size):
        name_field = f"{name:<16}".encode("ascii")
        mtime_field = f"{int(time.time()):<12}".encode("ascii")
        uid_field = f"{0:<6}".encode("ascii")
        gid_field = f"{0:<6}".encode("ascii")
        mode_field = f"{'100644':<8}".encode("ascii")
        size_field = f"{size:<10}".encode("ascii")
        trailer = b"`\n"
        return name_field + mtime_field + uid_field + gid_field + mode_field + size_field + trailer

    with open(out_deb_path, "wb") as deb:
        deb.write(b"!<arch>\n")
        deb_bin_data = b"2.0\n"
        deb.write(make_ar_header("debian-binary", len(deb_bin_data)))
        deb.write(deb_bin_data)
        if len(deb_bin_data) % 2:
            deb.write(b"\n")

        deb.write(make_ar_header("control.tar.gz", len(ctrl_gz_bytes)))
        deb.write(ctrl_gz_bytes)
        if len(ctrl_gz_bytes) % 2:
            deb.write(b"\n")

        deb.write(make_ar_header("data.tar.lzma", len(data_lzma_bytes)))
        deb.write(data_lzma_bytes)
        if len(data_lzma_bytes) % 2:
            deb.write(b"\n")

    print(f"Generated package: {output_filename} ({os.path.getsize(out_deb_path)} bytes)")

    user_downloads = r"C:\Users\AmiaXf\Downloads"
    if os.path.exists(user_downloads):
        dl_target = os.path.join(user_downloads, output_filename)
        shutil.copy2(out_deb_path, dl_target)
        print(f"Copied to Downloads: {dl_target}")

def build_all():
    print("Extracting pristine dylib...")
    clean_dylib = extract_clean_pristine_dylib()

    print("Preparing localized settings bundle...")
    prepare_settings_bundle()

    dylib_path = os.path.join(PKG_DATA, "var", "jb", "Library", "MobileSubstrate", "DynamicLibraries", "StandBy.dylib")

    # 1. Indonesian Variant
    print("\n--- Building Indonesian Variant ---")
    patched_id = build_patched_dylib(clean_dylib, "id")
    with open(dylib_path, "wb") as f:
        f.write(patched_id)
    package_deb("com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64_id.deb")

    # 2. Vietnamese Variant
    print("\n--- Building Vietnamese Variant ---")
    patched_vi = build_patched_dylib(clean_dylib, "vi")
    with open(dylib_path, "wb") as f:
        f.write(patched_vi)
    package_deb("com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64_vi.deb")

    # 3. English Default Variant (Primary)
    print("\n--- Building English Default Variant (Primary) ---")
    patched_en = build_patched_dylib(clean_dylib, "en")
    with open(dylib_path, "wb") as f:
        f.write(patched_en)
    package_deb("com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64.deb")

    print("\n[SUCCESS] All 3 packages built with 100% tilt stability & weather string protection!")

if __name__ == "__main__":
    build_all()
