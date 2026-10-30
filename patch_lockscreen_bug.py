import os
import struct
import hashlib
import shutil

WORK_DIR = r"C:\Users\AmiaXf\.gemini\antigravity\scratch\phucstandby"
DYLIB_PATH = os.path.join(WORK_DIR, "pkg_data", "var", "jb", "Library", "MobileSubstrate", "DynamicLibraries", "StandBy.dylib")

NOP_INSN = bytes([0x1f, 0x20, 0x03, 0xd5]) # ARM64 NOP

def patch_dylib():
    with open(DYLIB_PATH, "rb") as f:
        data = bytearray(f.read())

    # 1. Patch Arch 0 (arm64, offset 0x4000)
    # Instruction at vmaddr 0xc7f4: tbz w8, #0, #0xc850
    # Original bytes: e8 02 00 36
    arch0_target = 0x4000 + 0xc7f4
    assert data[arch0_target:arch0_target+4] == bytes([0xe8, 0x02, 0x00, 0x36]), f"Arch 0 target mismatch: {data[arch0_target:arch0_target+4]}"
    data[arch0_target:arch0_target+4] = NOP_INSN
    print("Patched Arch 0 (arm64) at 0x107f4 with NOP")

    # 2. Patch Arch 1 (arm64e, offset 0x7c000)
    # Instruction at vmaddr 0xbff4: tbz w8, #0, #0xc034
    # Original bytes: 08 02 00 36
    arch1_target = 0x7c000 + 0xbff4
    assert data[arch1_target:arch1_target+4] == bytes([0x08, 0x02, 0x00, 0x36]), f"Arch 1 target mismatch: {data[arch1_target:arch1_target+4]}"
    data[arch1_target:arch1_target+4] = NOP_INSN
    print("Patched Arch 1 (arm64e) at 0x87ff4 with NOP")

    # 3. Recompute CodeDirectory SHA-256 hashes for both arches
    arches = [
        (0, 0x4000, 487968),
        (1, 0x7c000, 486416)
    ]

    for arch_idx, arch_off, arch_size in arches:
        arch_data = data[arch_off:arch_off+arch_size]

        # Find LC_CODE_SIGNATURE
        ncmds, sizeofcmds = struct.unpack('<II', arch_data[16:24])
        offset = 32
        cs_dataoff = None
        for _ in range(ncmds):
            cmd, cmdsize = struct.unpack('<II', arch_data[offset:offset+8])
            if cmd == 0x1d: # LC_CODE_SIGNATURE
                cs_dataoff, cs_datasize = struct.unpack('<II', arch_data[offset+8:offset+16])
                break
            offset += cmdsize

        assert cs_dataoff is not None, f"No LC_CODE_SIGNATURE in arch {arch_idx}"

        # SuperBlob
        superblob_off = arch_off + cs_dataoff
        slot_type, slot_off = struct.unpack('>II', data[superblob_off+12:superblob_off+20])
        cd_abs_off = superblob_off + slot_off

        # CodeDirectory header
        magic, length, ver, flags, hashoff, identoff, nspecial, ncode, codelimit, hashsize, hashtype, platform, pageshift = struct.unpack('>IIIIIIIIIBBBB', data[cd_abs_off:cd_abs_off+40])
        page_size = 1 << pageshift
        print(f"Re-signing Arch {arch_idx}: ncode={ncode}, codelimit={hex(codelimit)}, pagesize={page_size}")

        # Update each page hash in data
        for p in range(ncode):
            p_start = arch_off + p * page_size
            p_end = arch_off + min((p + 1) * page_size, codelimit)
            page_data = data[p_start:p_end]
            h = hashlib.sha256(page_data).digest()

            h_dest = cd_abs_off + hashoff + p * hashsize
            data[h_dest:h_dest+hashsize] = h

        print(f"Successfully re-signed Arch {arch_idx}")

    # 4. Save modified dylib
    with open(DYLIB_PATH, "wb") as f:
        f.write(data)
    print(f"Saved patched and re-signed dylib: {DYLIB_PATH}")

if __name__ == "__main__":
    patch_dylib()
