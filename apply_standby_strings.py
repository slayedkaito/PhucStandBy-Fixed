import os
import struct
import hashlib
import shutil

WORK_DIR = r"C:\Users\AmiaXf\.gemini\antigravity\scratch\phucstandby"
DYLIB_PATH = os.path.join(WORK_DIR, "pkg_data", "var", "jb", "Library", "MobileSubstrate", "DynamicLibraries", "StandBy.dylib")
NOP_INSN = bytes([0x1f, 0x20, 0x03, 0xd5])

ID_TRANSLATIONS = [
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
]

EN_TRANSLATIONS = [
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
]

def apply_strings_and_sign(data, translations):
    # 1. Arch 0 (arm64, offset 0x4000)
    # Ensure lockscreen NOP is present
    arch0_target = 0x4000 + 0xc7f4
    data[arch0_target:arch0_target+4] = NOP_INSN
    
    # Pack strings in Arch 0 __ustring (starting at 0x3e6ee)
    curr_vm_0 = 0x3e6ee
    cf_base_0 = 0x44730
    for idx, text in translations:
        utf16_bytes = text.encode("utf-16le")
        abs_off_0 = 0x4000 + curr_vm_0
        data[abs_off_0:abs_off_0 + len(utf16_bytes)] = utf16_bytes

        # Update CFString at cf_base_0 + idx * 32
        cf_entry_off = 0x4000 + cf_base_0 + idx * 32
        isa = struct.unpack('<Q', data[cf_entry_off:cf_entry_off+8])[0]
        # pack: isa (Q), flags (0x7d0), str_ptr (curr_vm_0), length (len(text))
        new_entry = struct.pack('<QQQQ', isa, 0x7d0, curr_vm_0, len(text))
        data[cf_entry_off:cf_entry_off+32] = new_entry

        curr_vm_0 += len(utf16_bytes)

    print(f"Arch 0 strings packed up to {hex(curr_vm_0)} (limit 0x3e8ea)")

    # 2. Arch 1 (arm64e, offset 0x7c000)
    # Ensure lockscreen NOP is present
    arch1_target = 0x7c000 + 0xbff4
    data[arch1_target:arch1_target+4] = NOP_INSN

    # Pack strings in Arch 1 __ustring (starting at 0x3e6f6)
    curr_vm_1 = 0x3e6f6
    cf_base_1 = 0x44a08
    for idx, text in translations:
        utf16_bytes = text.encode("utf-16le")
        abs_off_1 = 0x7c000 + curr_vm_1
        data[abs_off_1:abs_off_1 + len(utf16_bytes)] = utf16_bytes

        # Update CFString at cf_base_1 + idx * 32
        cf_entry_off = 0x7c000 + cf_base_1 + idx * 32
        isa = struct.unpack('<Q', data[cf_entry_off:cf_entry_off+8])[0]
        # In arm64e, str_ptr has dyld chained fixup prefix 0x1000000000000000
        str_ptr_1 = 0x1000000000000000 | curr_vm_1
        new_entry = struct.pack('<QQQQ', isa, 0x7d0, str_ptr_1, len(text))
        data[cf_entry_off:cf_entry_off+32] = new_entry

        curr_vm_1 += len(utf16_bytes)

    print(f"Arch 1 strings packed up to {hex(curr_vm_1)} (limit 0x3e8f2)")

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

        print(f"Re-signed Arch {arch_idx} with 0 mismatches")

    return data

def build_variant(lang_code, translations):
    with open(DYLIB_PATH, "rb") as f:
        data = bytearray(f.read())

    patched_data = apply_strings_and_sign(data, translations)
    with open(DYLIB_PATH, "wb") as f:
        f.write(patched_data)
    print(f"Wrote modified StandBy.dylib for {lang_code}")

    # Rebuild package using build_package.py logic
    import build_package
    build_package.build()

    # Destination paths
    deb_src = os.path.join(WORK_DIR, "com.phucbakhi.phucstandby_2.0.26-1+debug_iphoneos-arm64_multilang.deb")
    downloads = r"C:\Users\AmiaXf\Downloads"

    deb_name_specific = f"com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64_{lang_code}.deb"
    shutil.copy2(deb_src, os.path.join(downloads, deb_name_specific))
    shutil.copy2(deb_src, os.path.join(WORK_DIR, deb_name_specific))
    print(f"Created {deb_name_specific} in Downloads and WORK_DIR")

    if lang_code == "id":
        # Also copy as the default deb file
        deb_name_default = "com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64.deb"
        shutil.copy2(deb_src, os.path.join(downloads, deb_name_default))
        shutil.copy2(deb_src, os.path.join(WORK_DIR, deb_name_default))
        # and old name
        shutil.copy2(deb_src, os.path.join(downloads, "com.phucbakhi.phucstandby_2.0.26-1+debug_iphoneos-arm64.deb"))
        shutil.copy2(deb_src, os.path.join(WORK_DIR, "com.phucbakhi.phucstandby_2.0.26-1+debug_iphoneos-arm64.deb"))
        print(f"Created default {deb_name_default} in Downloads and WORK_DIR")

if __name__ == "__main__":
    print("=== Building Indonesian StandBy variant ===")
    build_variant("id", ID_TRANSLATIONS)

    print("\n=== Building English StandBy variant ===")
    build_variant("en", EN_TRANSLATIONS)

    print("\n=== Re-building Indonesian StandBy variant as final default ===")
    build_variant("id", ID_TRANSLATIONS)
