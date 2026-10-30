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

# Translations mapping for Preference Bundle:
# Each entry is (English_Key, Vietnamese_Key, English_Val, Indonesian_Val, Vietnamese_Val)
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
    (
        "Auto Wake Screen on Charge + Landscape",
        "Tự bật màn hình khi sạc + xoay ngang",
        "Auto Wake Screen on Charge + Landscape",
        "Bangunkan Layar Otomatis saat Mengisi Daya + Lanskap",
        "Tự bật màn hình khi sạc + xoay ngang"
    ),
    ("Keep Screen Awake", "Giữ màn hình sáng", "Keep Screen Awake", "Biarkan Layar Tetap Menyala", "Giữ màn hình sáng"),

    # Wake Delay Group
    (
        "Auto Wake Delay (seconds)",
        "Độ trễ tự bật màn hình (giây)",
        "Auto Wake Delay (seconds)",
        "Jeda Bangunkan Layar Otomatis (detik)",
        "Độ trễ tự bật màn hình (giây)"
    ),
    (
        "Delay when turning off screen while waiting for StandBy to start",
        "độ trễ khi tắt màn hình chờ standby khởi động",
        "Delay when turning off screen while waiting for StandBy to start",
        "Jeda saat mematikan layar sambil menunggu StandBy dimulai",
        "độ trễ khi tắt màn hình chờ standby khởi động"
    ),

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
    ("Pick Photos from Album", "Chọn ảnh trong album", "Pick Photos from Album", "Pilih Foto dari Album", "Chọn ảnh trong album"),
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

    # Actions & Respring
    ("Actions", "Thao tác", "Actions", "Tindakan", "Thao tác"),
    (
        "Respring to apply all changes cleanly.",
        "Respring để áp dụng sạch mọi thay đổi.",
        "Respring to apply all changes cleanly.",
        "Respring untuk menerapkan semua perubahan dengan bersih.",
        "Respring để áp dụng sạch mọi thay đổi."
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

    # Language Info Group
    ("Language", "Ngôn ngữ", "Language", "Bahasa", "Ngôn ngữ"),
    (
        "StandBy tweak preferences automatically follow your iOS system language (English, Indonesian, Vietnamese).",
        "Cài đặt tinh chỉnh StandBy tự động theo ngôn ngữ hệ thống iOS của bạn (Tiếng Anh, Tiếng Việt, Indonesia).",
        "StandBy tweak preferences automatically follow your iOS system language (English, Indonesian, Vietnamese).",
        "Pengaturan tweak StandBy secara otomatis mengikuti bahasa sistem iOS Anda (Inggris, Indonesia, Vietnam).",
        "Cài đặt tinh chỉnh StandBy tự động theo ngôn ngữ hệ thống iOS của bạn (Tiếng Anh, Tiếng Việt, Indonesia)."
    ),

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
    # lang_idx: 0 for EN, 1 for ID, 2 for VI
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
        
        # Add mapping for en_key -> val
        if en_key and en_key not in seen_keys:
            lines.append(f'"{escape_apple_string(en_key)}" = "{escape_apple_string(val)}";')
            seen_keys.add(en_key)
            
        # Add mapping for vi_key -> val (if different)
        if vi_key and vi_key not in seen_keys:
            lines.append(f'"{escape_apple_string(vi_key)}" = "{escape_apple_string(val)}";')
            seen_keys.add(vi_key)
            
    lines.append("")
    return "\n".join(lines)

# Translations for StandBy overlay CFStrings
DYLIB_STRINGS = {
    "en": [
        (81, "Now Playing"),
        (109, "SUNDAY"),
        (110, "DAY %ld"),
        (124, "Sunday"),
        (125, "Day %ld"),
        (126, "%@, %ld/%ld"),
        (127, "%lu events today"),
        (128, "Your day is clear"),
        (129, "Today"),
        (130, "Cannot read calendar"),
        (132, "No music\nplaying"),
        (133, "Paused"),
        (140, "No new\nnotifications"),
        (141, "Recent"),
        (143, "Charging"),
        (144, "Battery"),
        (156, "Add photos to ")
    ],
    "id": [
        (81, "Sedang diputar"),
        (109, "MINGGU"),
        (110, "HARI %ld"),
        (124, "Minggu"),
        (125, "Hari %ld"),
        (126, "%@, %ld/%ld"),
        (127, "%lu acara hari ini"),
        (128, "Tidak ada acara"),
        (129, "Hari ini"),
        (130, "Gagal membaca kalender"),
        (132, "Tidak ada musik\nyang diputar"),
        (133, "Dijeda"),
        (140, "Tidak ada\npemberitahuan"),
        (141, "Terbaru"),
        (143, "Mengisi daya"),
        (144, "Baterai"),
        (156, "Tambahkan foto di ")
    ],
    "vi": [
        (81, "Đang phát"),
        (109, "CHỦ NHẬT"),
        (110, "NGÀY %ld"),
        (124, "Chủ nhật"),
        (125, "Ngày %ld"),
        (126, "%@, %ld/%ld"),
        (127, "%lu sự kiện hôm nay"),
        (128, "Ngày của bạn trống"),
        (129, "Hôm nay"),
        (130, "Không thể đọc lịch"),
        (132, "Không có nhạc\nđang phát"),
        (133, "Đã tạm dừng"),
        (140, "Không có\nthông báo mới"),
        (141, "Gần đây"),
        (143, "Đang sạc"),
        (144, "Pin"),
        (156, "Thêm ảnh vào ")
    ]
}

def apply_standby_strings(data, translations):
    NOP_INSN = bytes([0x1f, 0x20, 0x03, 0xd5])
    # 1. Arch 0 (arm64, offset 0x4000)
    arch0_target = 0x4000 + 0xc7f4
    data[arch0_target:arch0_target+4] = NOP_INSN
    
    curr_vm_0 = 0x3e6ee
    cf_base_0 = 0x44730
    for idx, text in translations:
        utf16_bytes = text.encode("utf-16le")
        abs_off_0 = 0x4000 + curr_vm_0
        data[abs_off_0:abs_off_0 + len(utf16_bytes)] = utf16_bytes

        cf_entry_off = 0x4000 + cf_base_0 + idx * 32
        isa = struct.unpack('<Q', data[cf_entry_off:cf_entry_off+8])[0]
        new_entry = struct.pack('<QQQQ', isa, 0x7d0, curr_vm_0, len(text))
        data[cf_entry_off:cf_entry_off+32] = new_entry
        curr_vm_0 += len(utf16_bytes)

    # 2. Arch 1 (arm64e, offset 0x7c000)
    arch1_target = 0x7c000 + 0xbff4
    data[arch1_target:arch1_target+4] = NOP_INSN

    curr_vm_1 = 0x3e6f6
    cf_base_1 = 0x44a08
    for idx, text in translations:
        utf16_bytes = text.encode("utf-16le")
        abs_off_1 = 0x7c000 + curr_vm_1
        data[abs_off_1:abs_off_1 + len(utf16_bytes)] = utf16_bytes

        cf_entry_off = 0x7c000 + cf_base_1 + idx * 32
        isa = struct.unpack('<Q', data[cf_entry_off:cf_entry_off+8])[0]
        str_ptr_1 = 0x1000000000000000 | curr_vm_1
        new_entry = struct.pack('<QQQQ', isa, 0x7d0, str_ptr_1, len(text))
        data[cf_entry_off:cf_entry_off+32] = new_entry
        curr_vm_1 += len(utf16_bytes)

    # 3. Re-sign CodeDirectory SHA-256 hashes
    arches = [
        (0, 0x4000, 487968),
        (1, 0x7c000, 486416)
    ]
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
            h_dest = cd_abs_off + hashoff + p * hashsize
            data[h_dest:h_dest+hashsize] = h

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
    # 1. Create lproj directories
    lprojs = {
        "en": (0, "English"),
        "id": (1, "Indonesian"),
        "vi": (2, "Vietnamese")
    }
    
    for code, (idx, lang_name) in lprojs.items():
        lproj_dir = os.path.join(PREF_BUNDLE, f"{code}.lproj")
        os.makedirs(lproj_dir, exist_ok=True)
        
        # Write Root.strings
        root_strings_path = os.path.join(lproj_dir, "Root.strings")
        content = generate_strings_content(idx, lang_name)
        with open(root_strings_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Wrote {root_strings_path}")
        
        # Write InfoPlist.strings
        infoplist_strings_path = os.path.join(lproj_dir, "InfoPlist.strings")
        display_name = "StandBy"
        info_content = f'CFBundleDisplayName = "{display_name}";\nCFBundleName = "{display_name}";\n'
        with open(infoplist_strings_path, "w", encoding="utf-8") as f:
            f.write(info_content)
        print(f"Wrote {infoplist_strings_path}")

    # 2. Update Info.plist
    info_plist_path = os.path.join(PREF_BUNDLE, "Info.plist")
    with open(info_plist_path, "rb") as f:
        info_pl = plistlib.load(f)
    info_pl["CFBundleDevelopmentRegion"] = "en"
    info_pl["CFBundleLocalizations"] = ["en", "id", "vi"]
    with open(info_plist_path, "wb") as f:
        plistlib.dump(info_pl, f, fmt=plistlib.FMT_XML)
    print("Updated Info.plist with CFBundleLocalizations [en, id, vi]")

    # 3. Update Root.plist with English base text, wakeScreen=False, Respring & Credits
    root_plist_path = os.path.join(PREF_BUNDLE, "Root.plist")
    with open(root_plist_path, "rb") as f:
        root_pl = plistlib.load(f)

    # Mapping Vietnamese text -> English text
    vi_to_en = {}
    for en_k, vi_k, en_v, id_v, vi_v in TRANSLATIONS:
        vi_to_en[vi_k] = en_v

    # Replace translatable fields in Root.plist
    for item in root_pl.get("items", []):
        if item.get("key") == "wakeScreen":
            item["default"] = False  # Set wakeScreen default to False (OFF)
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

    # Remove any old language link list or group
    root_pl["items"] = [it for it in root_pl["items"] if it.get("key") != "language"]
    root_pl["items"] = [it for it in root_pl["items"] if not (it.get("cell") == "PSGroupCell" and it.get("label") in ["Language", "Ngôn ngữ", "Bahasa"])]

    # Insert clean Language info group
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

    # Check if Respring and Credits cells already exist
    existing_actions = [it for it in root_pl["items"] if it.get("action") == "respring:"]
    if not existing_actions:
        root_pl["items"].append({
            "cell": "PSGroupCell",
            "label": "Actions",
            "footerText": "Respring to apply all changes cleanly."
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
    print("Updated Root.plist with wakeScreen default OFF, clean Language info, Respring, and Credits")

    # Resign StandByPref binary
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

    # Pack data.tar.lzma
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
    print(f"Compressed data.tar.lzma: {len(data_lzma_bytes)} bytes")

    # Pack control.tar.gz
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

        # debian-binary
        deb_bin_data = b"2.0\n"
        deb.write(make_ar_header("debian-binary", len(deb_bin_data)))
        deb.write(deb_bin_data)
        if len(deb_bin_data) % 2:
            deb.write(b"\n")

        # control.tar.gz
        deb.write(make_ar_header("control.tar.gz", len(ctrl_gz_bytes)))
        deb.write(ctrl_gz_bytes)
        if len(ctrl_gz_bytes) % 2:
            deb.write(b"\n")

        # data.tar.lzma
        deb.write(make_ar_header("data.tar.lzma", len(data_lzma_bytes)))
        deb.write(data_lzma_bytes)
        if len(data_lzma_bytes) % 2:
            deb.write(b"\n")

    print(f"Successfully generated package: {out_deb_path} ({os.path.getsize(out_deb_path)} bytes)")

    user_downloads = r"C:\Users\AmiaXf\Downloads"
    if os.path.exists(user_downloads):
        dl_target = os.path.join(user_downloads, output_filename)
        shutil.copy2(out_deb_path, dl_target)
        print(f"Copied package to user Downloads: {dl_target}")

def build_all():
    prepare_settings_bundle()

    dylib_path = os.path.join(PKG_DATA, "var", "jb", "Library", "MobileSubstrate", "DynamicLibraries", "StandBy.dylib")
    # Read the clean baseline dylib (already patched with bug fixes)
    with open(dylib_path, "rb") as f:
        clean_dylib_base = bytearray(f.read())

    # 1. Build Indonesian Variant
    print("\n--- Building Indonesian Variant ---")
    data_id = bytearray(clean_dylib_base)
    patched_id = apply_standby_strings(data_id, DYLIB_STRINGS["id"])
    with open(dylib_path, "wb") as f:
        f.write(patched_id)
    package_deb("com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64_id.deb")

    # 2. Build Vietnamese Variant
    print("\n--- Building Vietnamese Variant ---")
    data_vi = bytearray(clean_dylib_base)
    patched_vi = apply_standby_strings(data_vi, DYLIB_STRINGS["vi"])
    with open(dylib_path, "wb") as f:
        f.write(patched_vi)
    package_deb("com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64_vi.deb")

    # 3. Build English Default Variant (Primary package)
    print("\n--- Building English Default Variant (Primary) ---")
    data_en = bytearray(clean_dylib_base)
    patched_en = apply_standby_strings(data_en, DYLIB_STRINGS["en"])
    with open(dylib_path, "wb") as f:
        f.write(patched_en)
    package_deb("com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64.deb")

    print("\n[SUCCESS] All packages built and copied to Downloads successfully!")

if __name__ == "__main__":
    build_all()
