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

# Translations mapping:
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
        "Hue (Corak) — hanya digunakan saat memilih 'Kustom'",
        "Hue (sắc độ) — chỉ dùng khi chọn 'Tuỳ chỉnh'"
    ),
    ("Saturation", "Saturation (độ đậm)", "Saturation", "Saturasi (Kepekatan)", "Saturation (độ đậm)"),
    ("Brightness", "Brightness (độ sáng)", "Brightness", "Kecerahan", "Brightness (độ sáng)"),

    # Photo Page Group
    (
        "Photo Wallpaper Page (Swipe Horizontally)",
        "Trang ảnh nền (vuốt ngang)",
        "Photo Wallpaper Page (Swipe Horizontally)",
        "Halaman Wallpaper Foto (Geser Horizontal)",
        "Trang ảnh nền (vuốt ngang)"
    ),
    (
        "Customize the clock photo wallpaper to your preference",
        "Tuỳ chỉnh ảnh nền cho khung giờ theo ý cúa bạn",
        "Customize the clock photo wallpaper to your preference",
        "Sesuaikan wallpaper foto untuk tampilan jam sesuai keinginan Anda",
        "Tuỳ chỉnh ảnh nền cho khung giờ theo ý cúa bạn"
    ),
    (
        "Add Wallpaper from Photo Library…",
        "Thêm ảnh nền từ Thư viện ảnh…",
        "Add Wallpaper from Photo Library…",
        "Tambah Wallpaper dari Galeri Foto…",
        "Thêm ảnh nền từ Thư viện ảnh…"
    ),
    (
        "Time Format with Dot e.g. 19.49 (Off = 19:49)",
        "Giờ dạng 19.49 (tắt = 19:49)",
        "Time Format with Dot e.g. 19.49 (Off = 19:49)",
        "Format Jam Titik cth. 19.49 (Mati = 19:49)",
        "Giờ dạng 19.49 (tắt = 19:49)"
    ),
    (
        "Caption for your photo wallpaper",
        "Chú thích cho ảnh nền bạn muốn đặt",
        "Caption for your photo wallpaper",
        "Keterangan untuk wallpaper foto Anda",
        "Chú thích cho ảnh nền bạn muốn đặt"
    ),
    ("e.g. My Wallpaper", "vd: hoangluongnigger", "e.g. My Wallpaper", "cth. Wallpaper Saya", "vd: Hoang Luong"),

    # Weather Group
    (
        "Weather (Style 3: Photo + Temperature)",
        "Thời tiết (kiểu 3: ảnh + nhiệt độ)",
        "Weather (Style 3: Photo + Temperature)",
        "Cuaca (Gaya 3: Foto + Suhu)",
        "Thời tiết (kiểu 3: ảnh + nhiệt độ)"
    ),
    (
        "Fetched from Open-Meteo by coordinates. Default is HCMC (10.82, 106.63). City name is for display only.",
        "Lấy từ Open-Meteo theo toạ độ. Mặc định TP.HCM (10.82, 106.63). Tên thành phố chỉ để hiển thị.",
        "Fetched from Open-Meteo by coordinates. Default is HCMC (10.82, 106.63). City name is for display only.",
        "Diambil dari Open-Meteo berdasarkan koordinat. Default: TP.HCM (10.82, 106.63). Nama kota hanya untuk tampilan.",
        "Lấy từ Open-Meteo theo toạ độ. Mặc định TP.HCM (10.82, 106.63). Tên thành phố chỉ để hiển thị."
    ),
    ("City Name", "Tên thành phố", "City Name", "Nama Kota", "Tên thành phố"),
    ("Ho Chi Minh City", "TP. Hồ Chí Minh", "Ho Chi Minh City", "Kota Ho Chi Minh", "TP. Hồ Chí Minh"),
    ("Latitude (lat)", "Vĩ độ (lat)", "Latitude (lat)", "Lintang (lat)", "Vĩ độ (lat)"),
    ("Longitude (lon)", "Kinh độ (lon)", "Longitude (lon)", "Bujur (lon)", "Kinh độ (lon)"),

    # Donate Group
    ("Support (Donate)", "Ủng hộ (Donate)", "Support (Donate)", "Dukungan (Donasi)", "Ủng hộ (Donate)"),
    (
        "Donate to keep me motivated, thank you everyone! ☕️❤️",
        "Donate để tui có động lực nhá thank kiuu mn☕️❤️",
        "Donate to keep me motivated, thank you everyone! ☕️❤️",
        "Donasi agar saya tetap termotivasi, terima kasih semuanya! ☕️❤️",
        "Donate để tui có động lực nhá thank kiuu mn☕️❤️"
    ),
    ("Bank: VietinBank", "Ngân hàng: VietinBank", "Bank: VietinBank", "Bank: VietinBank", "Ngân hàng: VietinBank"),
    (
        "Account Number: 100888241596",
        "Số tài khoản: 100888241596",
        "Account Number: 100888241596",
        "Nomor Rekening: 100888241596",
        "Số tài khoản: 100888241596"
    ),
    (
        "Recipient: Hoang Duc Luong",
        "Người nhận: Hoang Duc Luong",
        "Recipient: Hoang Duc Luong",
        "Penerima: Hoang Duc Luong",
        "Người nhận: Hoang Duc Luong"
    ),

    # Actions / Respring
    ("Actions", "Thao tác", "Actions", "Aksi", "Thao tác"),
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
        if c == '\\':
            res.append('\\\\')
        elif c == '"':
            res.append('\\"')
        elif c == '\n':
            res.append('\\n')
        elif c == '\r':
            res.append('\\r')
        elif c == '\t':
            res.append('\\t')
        else:
            res.append(c)
    return "".join(res)

def generate_strings_content(lang_index, header_title):
    lines = [
        f"/* Root.strings ({header_title}) */",
        "/* Generated with English and Indonesian language support */",
        ""
    ]
    seen = set()
    for en_key, vi_key, en_val, id_val, vi_val in TRANSLATIONS:
        val = [en_val, id_val, vi_val][lang_index]
        
        # Include mapping for English key
        if en_key and (en_key, val) not in seen:
            seen.add((en_key, val))
            lines.append(f'"{escape_apple_string(en_key)}" = "{escape_apple_string(val)}";')
        
        # Include mapping for Vietnamese key
        if vi_key and vi_key != en_key and (vi_key, val) not in seen:
            seen.add((vi_key, val))
            lines.append(f'"{escape_apple_string(vi_key)}" = "{escape_apple_string(val)}";')
            
    lines.append("")
    return "\n".join(lines)

def resign_macho(file_path):
    with open(file_path, 'rb') as f:
        data = bytearray(f.read())

    magic = struct.unpack('>I', data[:4])[0]
    slices = []
    if magic in [0xcafebabe, 0xbebafeca]:
        nfat = struct.unpack('>I', data[4:8])[0]
        for i in range(nfat):
            cputype, cpusub, offset, size, align = struct.unpack('>IIIII', data[8+i*20:28+i*20])
            slices.append((offset, size))
    else:
        slices.append((0, len(data)))

    total_mismatches = 0
    for idx, (arch_off, arch_size) in enumerate(slices):
        arch_data = data[arch_off:arch_off+arch_size]
        ncmds, sizeofcmds = struct.unpack('<II', arch_data[16:24])
        cmd_off = 32
        cs_dataoff = None
        for _ in range(ncmds):
            cmd, cmdsize = struct.unpack('<II', arch_data[cmd_off:cmd_off+8])
            if cmd == 0x1d:
                cs_dataoff, cs_datasize = struct.unpack('<II', arch_data[cmd_off+8:cmd_off+16])
                break
            cmd_off += cmdsize

        if cs_dataoff is None:
            continue

        superblob_off = arch_off + cs_dataoff
        slot_type, slot_off = struct.unpack('>II', data[superblob_off+12:superblob_off+20])
        cd_abs_off = superblob_off + slot_off

        magic_cd, length, ver, flags, hashoff, identoff, nspecial, ncode, codelimit, hashsize, hashtype, platform, pageshift = struct.unpack('>IIIIIIIIIBBBB', data[cd_abs_off:cd_abs_off+40])
        page_size = 1 << pageshift
        
        for p in range(ncode):
            p_start = arch_off + p * page_size
            p_end = arch_off + min((p + 1) * page_size, codelimit)
            page_data = data[p_start:p_end]
            h = hashlib.sha256(page_data).digest()

            h_dest = cd_abs_off + hashoff + p * hashsize
            old_h = data[h_dest:h_dest+hashsize]
            if h != old_h:
                total_mismatches += 1
                data[h_dest:h_dest+hashsize] = h

    with open(file_path, 'wb') as f:
        f.write(data)
    print(f"Resigned {os.path.basename(file_path)}: {total_mismatches} mismatches corrected")

def build():
    # 0. Resign Mach-O binaries first
    dylib_path = os.path.join(PKG_DATA, "var", "jb", "Library", "MobileSubstrate", "DynamicLibraries", "StandBy.dylib")
    pref_bin_path = os.path.join(PREF_BUNDLE, "StandByPref")
    resign_macho(dylib_path)
    resign_macho(pref_bin_path)

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

    # Let's create a lookup mapping Vietnamese text -> English text
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

    # Check if Respring and Credits cells already exist
    existing_actions = [it for it in root_pl["items"] if it.get("action") == "respring:"]
    if not existing_actions:
        # Add Actions & Respring
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
        # Add Credits
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
    print("Updated Root.plist with wakeScreen default OFF, Respring button, and Credits")

    # 4. Update control file
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
    print("Updated DEBIAN/control description and maintainer")

    # 5. Pack data.tar.lzma and control.tar.gz
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

    # Prepare control.tar.gz
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
    print(f"Compressed control.tar.gz: {len(ctrl_gz_bytes)} bytes")

    # 6. Create Debian ar archive (.deb)
    out_deb_path = os.path.join(WORK_DIR, "com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64.deb")

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

    print(f"Successfully generated new debian package: {out_deb_path} ({os.path.getsize(out_deb_path)} bytes)")

    # Also copy to Downloads for direct user access
    user_downloads = r"C:\Users\AmiaXf\Downloads"
    if os.path.exists(user_downloads):
        dl_target = os.path.join(user_downloads, "com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64.deb")
        shutil.copy2(out_deb_path, dl_target)
        print(f"Copied package to user Downloads: {dl_target}")

if __name__ == "__main__":
    build()
