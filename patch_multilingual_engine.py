import os
import struct
import capstone

WORK_DIR = r"C:\Users\AmiaXf\.gemini\antigravity\scratch\phucstandby"
DYLIB_PATH = os.path.join(WORK_DIR, "pkg_data", "var", "jb", "Library", "MobileSubstrate", "DynamicLibraries", "StandBy.dylib")

ALL_STRINGS = [
    # 0: Now Playing (orig idx 81)
    ("Now Playing", "Sedang diputar", "Đang phát"),
    # 1: SUNDAY (orig idx 109)
    ("SUNDAY", "MINGGU", "CHỦ NHẬT"),
    # 2: DAY %ld (orig idx 110)
    ("DAY %ld", "HARI %ld", "THỨ %ld"),
    # 3: Sunday (orig idx 124)
    ("Sunday", "Minggu", "Chủ nhật"),
    # 4: Day %ld (orig idx 125)
    ("Day %ld", "Hari %ld", "Thứ %ld"),
    # 5: %@, %ld/%ld (orig idx 126)
    ("%@, %ld/%ld", "%@, %ld/%ld", "%@, %ld thg %ld"),
    # 6: %lu events today (orig idx 127)
    ("%lu events today", "%lu acara hari ini", "%lu sự kiện hôm nay"),
    # 7: Your day is clear (orig idx 128)
    ("Your day is clear", "Tidak ada acara", "Ngày của bạn trống"),
    # 8: Today (orig idx 129)
    ("Today", "Hari ini", "Hôm nay"),
    # 9: Cannot read calendar (orig idx 130)
    ("Cannot read calendar", "Gagal membaca kalender", "Chưa đọc được sự kiện lịch"),
    # 10: No music playing (orig idx 132)
    ("No music\nplaying", "Tidak ada musik\nyang diputar", "Chưa có nhạc\nđang phát"),
    # 11: Paused (orig idx 133)
    ("Paused", "Dijeda", "Tạm dừng"),
    # 12: No new notifications (orig idx 140)
    ("No new\nnotifications", "Tidak ada\npemberitahuan", "Chưa có\nthông báo mới"),
    # 13: Recent (orig idx 141)
    ("Recent", "Terbaru", "Mới đây"),
    # 14: Charging (orig idx 143)
    ("Charging", "Mengisi daya", "Đang sạc"),
    # 15: Battery (orig idx 144)
    ("Battery", "Baterai", "Pin"),
    # 16: Add photos to (orig idx 156)
    ("Add photos to ", "Tambahkan foto di ", "Bỏ ảnh vào ")
]

def make_adrp(target_page, pc, reg):
    imm = (target_page - (pc & ~0xfff)) >> 12
    immlo = imm & 0x3
    immhi = (imm >> 2) & 0x7ffff
    insn = 0x90000000 | (immlo << 29) | (immhi << 5) | reg
    return struct.pack('<I', insn)

def make_add_imm(dst_reg, src_reg, imm):
    assert 0 <= imm < 4096
    insn = 0x91000000 | (imm << 10) | (src_reg << 5) | dst_reg
    return struct.pack('<I', insn)

def make_b(target, pc):
    diff = (target - pc) >> 2
    insn = 0x14000000 | (diff & 0x3ffffff)
    return struct.pack('<I', insn)

def make_bl(target, pc):
    diff = (target - pc) >> 2
    insn = 0x94000000 | (diff & 0x3ffffff)
    return struct.pack('<I', insn)

def make_b_cond(cond, target, pc):
    diff = (target - pc) >> 2
    insn = 0x54000000 | ((diff & 0x7ffff) << 5) | (cond & 0x1f)
    return struct.pack('<I', insn)

def make_cbnz(reg, target, pc):
    diff = (target - pc) >> 2
    insn = 0x35000000 | ((diff & 0x7ffff) << 5) | reg
    return struct.pack('<I', insn)

def assemble_updater(fn_addr, read_stub, is_arm64e):
    insn_defs = [
        # Prologue
        (4, lambda pc, L: bytes([0xff, 0x83, 0x00, 0xd1])), # sub sp, sp, #0x20
        (4, lambda pc, L: bytes([0xfd, 0x7b, 0x01, 0xa9])), # stp x29, x30, [sp, #0x10]
        (4, lambda pc, L: bytes([0xfd, 0x43, 0x00, 0x91])), # add x29, sp, #0x10

        # Read key 'language'
        (4, lambda pc, L: make_adrp(0x4d000, pc, 0)),
        (4, lambda pc, L: make_add_imm(0, 0, 0xfc0)),        # CFSTR("language") at 0x4dfc0
        (4, lambda pc, L: bytes([0xe0, 0x03, 0x67, 0x9e])), # fmov d0, xzr
        (4, lambda pc, L: make_bl(read_stub, pc)),
        (4, lambda pc, L: bytes([0x08, 0x00, 0x78, 0x1e])), # fcvtzs w8, d0

        # If w8 != 0, skip to check_lang
        (4, lambda pc, L: make_cbnz(8, L['check_lang'], pc)),

        # If w8 == 0 (Auto), read 'effectiveLanguage'
        (4, lambda pc, L: make_adrp(0x4d000, pc, 0)),
        (4, lambda pc, L: make_add_imm(0, 0, 0xfe0)),        # CFSTR("effectiveLanguage") at 0x4dfe0
        (4, lambda pc, L: bytes([0xe0, 0x03, 0x67, 0x9e])), # fmov d0, xzr
        (4, lambda pc, L: make_bl(read_stub, pc)),
        (4, lambda pc, L: bytes([0x08, 0x00, 0x78, 0x1e])), # fcvtzs w8, d0

        'check_lang',
        # cmp w8, #2 (Indonesian)
        (4, lambda pc, L: bytes([0x1f, 0x09, 0x00, 0x71])), # cmp w8, #2
        (4, lambda pc, L: make_b_cond(1, L['not_id'], pc)),  # b.ne not_id
        (4, lambda pc, L: make_adrp(0x4e000, pc, 1)),
        (4, lambda pc, L: make_add_imm(1, 1, 0x440)),        # x1 = id_cfstrings at 0x4e440
        (4, lambda pc, L: make_b(L['do_copy'], pc)),

        'not_id',
        # cmp w8, #3 (Vietnamese)
        (4, lambda pc, L: bytes([0x1f, 0x0d, 0x00, 0x71])), # cmp w8, #3
        (4, lambda pc, L: make_b_cond(1, L['not_vi'], pc)),  # b.ne not_vi
        (4, lambda pc, L: make_adrp(0x4e000, pc, 1)),
        (4, lambda pc, L: make_add_imm(1, 1, 0x660)),        # x1 = vi_cfstrings at 0x4e660
        (4, lambda pc, L: make_b(L['do_copy'], pc)),

        'not_vi',
        # Default: English (1 or other)
        (4, lambda pc, L: make_adrp(0x4e000, pc, 1)),
        (4, lambda pc, L: make_add_imm(1, 1, 0x220)),        # x1 = en_cfstrings at 0x4e220

        'do_copy',
        (4, lambda pc, L: make_adrp(0x4e000, pc, 0)),        # x0 = active_cfstrings at 0x4e000
        (4, lambda pc, L: bytes([0x82, 0x08, 0x80, 0x52])), # mov w2, #68 (68 words = 544 bytes)

        'copy_loop',
        (4, lambda pc, L: bytes([0x23, 0x84, 0x40, 0xf8])), # ldr x3, [x1], #8
        (4, lambda pc, L: bytes([0x03, 0x84, 0x00, 0xf8])), # str x3, [x0], #8
        (4, lambda pc, L: bytes([0x42, 0x04, 0x00, 0x71])), # subs w2, w2, #1
        (4, lambda pc, L: make_b_cond(1, L['copy_loop'], pc)), # b.ne copy_loop

        # Epilogue
        (4, lambda pc, L: bytes([0xfd, 0x7b, 0x41, 0xa9])), # ldp x29, x30, [sp, #0x10]
        (4, lambda pc, L: bytes([0xff, 0x83, 0x00, 0x91])), # add sp, sp, #0x20
    ]

    if not is_arm64e:
        insn_defs.extend([
            (4, lambda pc, L: bytes([0xfd, 0x7b, 0x44, 0xa9])), # ldp x29, x30, [sp, #0x40]
            (4, lambda pc, L: bytes([0xff, 0x43, 0x01, 0x91])), # add sp, sp, #0x50
            (4, lambda pc, L: bytes([0xc0, 0x03, 0x5f, 0xd6]))  # ret
        ])
    else:
        insn_defs.extend([
            (4, lambda pc, L: bytes([0xfd, 0x7b, 0x43, 0xa9])), # ldp x29, x30, [sp, #0x30]
            (4, lambda pc, L: bytes([0xff, 0x03, 0x01, 0x91])), # add sp, sp, #0x40
            (4, lambda pc, L: bytes([0xff, 0x0f, 0x5f, 0xd6]))  # retab
        ])

    # Pass 1: compute labels
    labels = {}
    cur = fn_addr
    for item in insn_defs:
        if isinstance(item, str):
            labels[item] = cur
        else:
            cur += item[0]

    # Pass 2: generate bytes
    out = bytearray()
    cur = fn_addr
    for item in insn_defs:
        if isinstance(item, str):
            continue
        size, gen = item
        b = gen(cur, labels)
        assert len(b) == size
        out.extend(b)
        cur += size

    return out

def patch_multilingual():
    with open(DYLIB_PATH, "rb") as f:
        data = bytearray(f.read())

    slices = [
        (0, 0x4000, 487968, False), # Slice 0: ARM64
        (1, 0x7c000, 486416, True)  # Slice 1: ARM64E
    ]

    for s_idx, s_base, s_size, is_arm64e in slices:
        print(f"\n=======================================================")
        print(f"=== Setting up Multilingual tables in Slice {s_idx} ({'arm64e' if is_arm64e else 'arm64'}) ===")
        print(f"=======================================================")
        
        # 1. Write key strings and CFStrings
        str_lang_c = b"language\x00"
        str_eff_c = b"effectiveLanguage\x00"
        data[s_base + 0x4dfb4 : s_base + 0x4dfb4 + len(str_lang_c)] = str_lang_c
        data[s_base + 0x4dfa0 : s_base + 0x4dfa0 + len(str_eff_c)] = str_eff_c

        isa_cf = 0x4010000000000079 if is_arm64e else 0x0
        ptr_flag = 0x1000000000000000 if is_arm64e else 0x0

        # CFSTR("language") at 0x4dfc0
        cf_lang = struct.pack('<QQQQ', isa_cf, 0x7c8, ptr_flag | 0x4dfb4, len("language"))
        data[s_base + 0x4dfc0 : s_base + 0x4dfc0 + 32] = cf_lang

        # CFSTR("effectiveLanguage") at 0x4dfe0
        cf_eff = struct.pack('<QQQQ', isa_cf, 0x7c8, ptr_flag | 0x4dfa0, len("effectiveLanguage"))
        data[s_base + 0x4dfe0 : s_base + 0x4dfe0 + 32] = cf_eff

        # 2. Write String Characters & build CFStrings for EN, ID, VI
        char_cursor = 0x4e880
        tables = {"en": [], "id": [], "vi": []}

        for i, (en_s, id_s, vi_s) in enumerate(ALL_STRINGS):
            for lang_key, text in [("en", en_s), ("id", id_s), ("vi", vi_s)]:
                utf16 = text.encode("utf-16le")
                text_vm = char_cursor
                data[s_base + text_vm : s_base + text_vm + len(utf16)] = utf16
                char_cursor += len(utf16)
                if char_cursor % 8 != 0:
                    char_cursor += (8 - (char_cursor % 8))

                cf_struct = struct.pack('<QQQQ', isa_cf, 0x7d0, ptr_flag | text_vm, len(text))
                tables[lang_key].append(cf_struct)

        print(f"[+] Slice {s_idx} character data packed up to {hex(char_cursor)}")

        # Write en_cfstrings at 0x4e220
        for i, cf in enumerate(tables["en"]):
            data[s_base + 0x4e220 + i * 32 : s_base + 0x4e220 + (i + 1) * 32] = cf

        # Write id_cfstrings at 0x4e440
        for i, cf in enumerate(tables["id"]):
            data[s_base + 0x4e440 + i * 32 : s_base + 0x4e440 + (i + 1) * 32] = cf

        # Write vi_cfstrings at 0x4e660
        for i, cf in enumerate(tables["vi"]):
            data[s_base + 0x4e660 + i * 32 : s_base + 0x4e660 + (i + 1) * 32] = cf

        # Initialize active_cfstrings at 0x4e000 with English by default!
        for i, cf in enumerate(tables["en"]):
            data[s_base + 0x4e000 + i * 32 : s_base + 0x4e000 + (i + 1) * 32] = cf

        print(f"[+] Slice {s_idx} initialized active_cfstrings at 0x4e000 with default English")

        # 3. Patch all 18 call sites to point to 0x4e000 + string_idx * 32
        if not is_arm64e:
            callsites_0 = [
                (0x18d60, 0x18d64, 8, 8, 0),    # Now Playing
                (0x27a98, 0x27a9c, 9, 9, 0),    # Now Playing
                (0x230ec, 0x230f0, 0, 0, 1),    # SUNDAY
                (0x23118, 0x2311c, 2, 2, 2),    # DAY %ld
                (0x27080, 0x27084, 0, 0, 3),    # Sunday
                (0x270c4, 0x270c8, 2, 2, 4),    # Day %ld
                (0x2717c, 0x27180, 2, 2, 5),    # %@, %ld/%ld
                (0x272e4, 0x272e8, 2, 2, 6),    # %lu events today
                (0x27384, 0x27388, 10, 10, 7),  # Your day is clear
                (0x27448, 0x2744c, 2, 2, 8),    # Today
                (0x274ac, 0x274b0, 2, 2, 9),    # Cannot read calendar
                (0x27a4c, 0x27a50, 2, 2, 10),   # No music playing
                (0x27a90, 0x27a94, 10, 10, 11), # Paused
                (0x289b8, 0x289bc, 2, 2, 12),   # No new notifications
                (0x28a28, 0x28a2c, 2, 2, 13),   # Recent
                (0x29468, 0x2946c, 9, 9, 14),   # Charging
                (0x29460, 0x29464, 10, 10, 15), # Battery
                (0x2b0a0, 0x2b0a4, 0, 0, 16),   # Add photos to
            ]
            for adrp_pc, add_pc, dst, src, str_idx in callsites_0:
                target_addr = 0x4e000 + str_idx * 32
                target_page = target_addr & ~0xfff
                target_imm = target_addr & 0xfff
                data[s_base + adrp_pc : s_base + adrp_pc + 4] = make_adrp(target_page, adrp_pc, src)
                data[s_base + add_pc : s_base + add_pc + 4] = make_add_imm(dst, src, target_imm)
            print(f"[+] Slice 0: Redirected all 18 call sites to 0x4e000")

        else:
            callsites_1 = [
                (0x189dc, 0x189e0, 0, 8, 0),    # Now Playing
                (0x22d5c, 0x22d60, 0, 8, 1),    # SUNDAY
                (0x22d90, 0x22d94, 2, 2, 2),    # DAY %ld
                (0x26d08, 0x26d0c, 0, 8, 3),    # Sunday
                (0x26d58, 0x26d5c, 2, 2, 4),    # Day %ld
                (0x26e10, 0x26e14, 2, 2, 5),    # %@, %ld/%ld
                (0x26f78, 0x26f7c, 2, 2, 6),    # %lu events today
                (0x27014, 0x27018, 9, 9, 7),    # Your day is clear
                (0x270f0, 0x270f4, 2, 8, 8),    # Today
                (0x27160, 0x27164, 2, 8, 9),    # Cannot read calendar
                (0x276f0, 0x276f4, 2, 8, 10),   # No music playing
                (0x27734, 0x27738, 9, 9, 0),    # Now Playing
                (0x2773c, 0x27740, 10, 10, 11), # Paused
                (0x28688, 0x2868c, 2, 8, 12),   # No new notifications
                (0x28700, 0x28704, 2, 8, 13),   # Recent
                (0x29144, 0x29148, 8, 8, 14),   # Charging
                (0x2914c, 0x29150, 9, 9, 15),   # Battery
                (0x2ad8c, 0x2ad90, 0, 8, 16),   # Add photos to
            ]
            for adrp_pc, add_pc, dst, src, str_idx in callsites_1:
                target_addr = 0x4e000 + str_idx * 32
                target_page = target_addr & ~0xfff
                target_imm = target_addr & 0xfff
                data[s_base + adrp_pc : s_base + adrp_pc + 4] = make_adrp(target_page, adrp_pc, src)
                data[s_base + add_pc : s_base + add_pc + 4] = make_add_imm(dst, src, target_imm)
            print(f"[+] Slice 1: Redirected all 18 call sites to 0x4e000")

        # 4. Inject update_language_strings function at 0x3060
        read_stub = 0x39f54 if not is_arm64e else 0x3a270
        fn_addr = 0x3060
        fn_bytes = assemble_updater(fn_addr, read_stub, is_arm64e)
        data[s_base + fn_addr : s_base + fn_addr + len(fn_bytes)] = fn_bytes
        print(f"[+] Slice {s_idx}: Injected update_language_strings at 0x{fn_addr:x} ({len(fn_bytes)} bytes)")

        # Disassemble injected code with Capstone to thoroughly verify
        md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
        print("--- Disassembly of injected update_language_strings: ---")
        for insn in md.disasm(bytes(fn_bytes), fn_addr):
            print(f"  {hex(insn.address)}: {insn.mnemonic:8s} {insn.op_str}")

        # 5. Hook preference loading return
        if not is_arm64e:
            b_patch = make_b(fn_addr, 0x387c0)
            data[s_base + 0x387c0 : s_base + 0x387c4] = b_patch
            print(f"[+] Slice 0: Hooked 0x387c0 -> b 0x{fn_addr:x}")
        else:
            b_patch = make_b(fn_addr, 0x38a44)
            data[s_base + 0x38a44 : s_base + 0x38a48] = b_patch
            print(f"[+] Slice 1: Hooked 0x38a44 -> b 0x{fn_addr:x}")

    with open(DYLIB_PATH, "wb") as f:
        f.write(data)
    print("\n[+] Successfully saved patched StandBy.dylib with dynamic Multilingual engine!")

if __name__ == "__main__":
    patch_multilingual()
