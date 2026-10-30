import os
import struct
import capstone

WORK_DIR = r"C:\Users\AmiaXf\.gemini\antigravity\scratch\phucstandby"
DYLIB_PATH = os.path.join(WORK_DIR, "pkg_data", "var", "jb", "Library", "MobileSubstrate", "DynamicLibraries", "StandBy.dylib")
PREF_PATH = os.path.join(WORK_DIR, "pkg_data", "var", "jb", "Library", "PreferenceBundles", "StandByPref.bundle", "StandByPref")

NOP_INSN = bytes([0x1f, 0x20, 0x03, 0xd5])

def patch_dylib():
    with open(DYLIB_PATH, "rb") as f:
        data = bytearray(f.read())
    
    # Slice 0: ARM64 (offset 0x4000 = 16384)
    # Slice 1: ARM64E (offset 0x7c000 = 507904)
    s0 = 0x4000
    s1 = 0x7c000

    print("=== Patching StandBy.dylib ===")

    # -------------------------------------------------------------
    # 1. AUTO WAKE LOGIC FIX (No more infinite wake loop)
    # -------------------------------------------------------------
    # Slice 0:
    # 0x33a04: tbnz w8, #0, #0x33af8 (screenIsOn -> return without clearing lcSince)
    data[s0 + 0x33a04 : s0 + 0x33a08] = bytes([0xa8, 0x07, 0x00, 0x37])
    # 0x33a54: b.gt #0x33a74 (only check delay if lcSince > 0.0)
    data[s0 + 0x33a54 : s0 + 0x33a58] = bytes([0x0c, 0x01, 0x00, 0x54])
    # 0x33a58: b.mi #0x33af8 (if lcSince < 0.0, return immediately)
    data[s0 + 0x33a58 : s0 + 0x33a5c] = bytes([0x04, 0x05, 0x00, 0x54])
    # 0x33aac: fmov d0, #-1.00000000 (disarm sentinel after wake)
    data[s0 + 0x33aac : s0 + 0x33ab0] = bytes([0x00, 0x10, 0x7e, 0x1e])

    # Slice 1:
    # 0x33a90: tbnz w8, #0, #0x33b90
    data[s1 + 0x33a90 : s1 + 0x33a94] = bytes([0x08, 0x08, 0x00, 0x37])
    # 0x33ae0: b.gt #0x33b00
    data[s1 + 0x33ae0 : s1 + 0x33ae4] = bytes([0x0c, 0x01, 0x00, 0x54])
    # 0x33ae4: b.mi #0x33b90
    data[s1 + 0x33ae4 : s1 + 0x33ae8] = bytes([0x64, 0x05, 0x00, 0x54])
    # 0x33b3c: fmov d0, #-1.00000000
    data[s1 + 0x33b3c : s1 + 0x33b40] = bytes([0x00, 0x10, 0x7e, 0x1e])
    print("[+] Applied Auto Wake loop fixes to Slice 0 & Slice 1")

    # -------------------------------------------------------------
    # 2. WAKE SCREEN BACKLIGHT SOURCE FIX (Power Button source = 1)
    # -------------------------------------------------------------
    # Slice 0 at 0x33c54: mov x2, #1 (0x22, 0x00, 0x80, 0x52)
    data[s0 + 0x33c54 : s0 + 0x33c58] = bytes([0x22, 0x00, 0x80, 0x52])
    # Slice 1 at 0x33d04: mov x2, #1 (0x22, 0x00, 0x80, 0x52)
    data[s1 + 0x33d04 : s1 + 0x33d08] = bytes([0x22, 0x00, 0x80, 0x52])
    print("[+] Applied Backlight Source = 1 fix to Slice 0 & Slice 1")

    # -------------------------------------------------------------
    # 3. BLACK WALLPAPER FIX (Window background = clearColor)
    # -------------------------------------------------------------
    # Slice 0 at 0x20818: ldr x1, [x8, #0x528] (clearColor)
    data[s0 + 0x20818 : s0 + 0x2081c] = bytes([0x01, 0x49, 0x41, 0xf9])
    # Slice 1 at 0x20410: add x8, x8, #0x248 (clearColor)
    data[s1 + 0x20410 : s1 + 0x20414] = bytes([0x08, 0x22, 0x09, 0x91])
    print("[+] Applied clearColor wallpaper fix to Slice 0 & Slice 1")

    # -------------------------------------------------------------
    # 4. WIDGET SWIPE STUCK BUG FIX
    # -------------------------------------------------------------
    # Slice 0:
    # 0x1e66c: b #0x1e690 (bypass tOnPill blocking gesture)
    data[s0 + 0x1e66c : s0 + 0x1e670] = bytes([0x09, 0x00, 0x00, 0x14])
    # 0x1f8c4: b #0x1f8d0 (bypass panBlocked dropping updates)
    data[s0 + 0x1f8c4 : s0 + 0x1f8c8] = bytes([0x03, 0x00, 0x00, 0x14])

    # Slice 1:
    # 0x1e1a4: b #0x1e1b8 (bypass tOnPill blocking gesture)
    data[s1 + 0x1e1a4 : s1 + 0x1e1a8] = bytes([0x05, 0x00, 0x00, 0x14])
    # 0x1f430: b #0x1f438 (bypass panBlocked dropping updates)
    data[s1 + 0x1f430 : s1 + 0x1f434] = bytes([0x02, 0x00, 0x00, 0x14])
    print("[+] Applied Widget Swipe un-stick fixes to Slice 0 & Slice 1")

    # -------------------------------------------------------------
    # 5. RESPRING DARWIN NOTIFICATION OBSERVER IN SPRINGBOARD
    # -------------------------------------------------------------
    # Slice 0:
    # At 0x38088: pass name = NULL to observe all tweak notifications
    data[s0 + 0x38088 : s0 + 0x38090] = bytes([0xe3, 0x03, 0x1f, 0xaa, 0x1f, 0x20, 0x03, 0xd5]) # mov x3, xzr; nop
    # In callback 0x387e0: jump to 0x3000
    # 0x3000 - 0x387e0 -> b 0x3000 (0x14000000 | ((-54776) & 0x3ffffff))
    data[s0 + 0x387e0 : s0 + 0x387ec] = bytes([
        0x08, 0x2a, 0xff, 0x17, # b 0x3000
        0x1f, 0x20, 0x03, 0xd5, # nop
        0x1f, 0x20, 0x03, 0xd5  # nop
    ])
    # Trampoline at 0x3000:
    s0_tramp = bytes([
        0xe2, 0x0f, 0x00, 0xf9, # str x2, [sp, #0x18]
        0xe3, 0x0b, 0x00, 0xf9, # str x3, [sp, #0x10]
        0xe4, 0x07, 0x00, 0xf9, # str x4, [sp, #8]
        0x42, 0x01, 0x00, 0xb4, # cbz x2, 0x3034
        0xe0, 0x03, 0x02, 0xaa, # mov x0, x2
        0x48, 0x02, 0x00, 0x90, # adrp x8, #0x4b000
        0x01, 0xdd, 0x44, 0xf9, # ldr x1, [x8, #0x9b8] (@selector(length))
        0xfa, 0xdc, 0x00, 0x94, # bl #0x3a404 (objc_msgSend)
        0x1f, 0x68, 0x00, 0xf1, # cmp x0, #26 ("com.standby.ios16/respring")
        0x81, 0x00, 0x00, 0x54, # b.ne 0x3034
        0x00, 0x00, 0x80, 0xd2, # mov x0, #0
        0x30, 0x00, 0x80, 0xd2, # mov x16, #1 (SYS_exit)
        0x01, 0x10, 0x00, 0xd4, # svc #0x80
        0xee, 0xd5, 0x00, 0x14  # b 0x387ec
    ])
    data[s0 + 0x3000 : s0 + 0x3000 + len(s0_tramp)] = s0_tramp

    # Slice 1:
    # At 0x382a8: pass name = NULL to observe all tweak notifications
    data[s1 + 0x382a8 : s1 + 0x382b0] = bytes([0xe3, 0x03, 0x1f, 0xaa, 0x1f, 0x20, 0x03, 0xd5]) # mov x3, xzr; nop
    # In callback 0x38a68: jump to 0x3000
    # (0x3000 - 0x38a68)/4 = -56986 -> 0x17fe2166 -> 66 21 fe 17
    data[s1 + 0x38a68 : s1 + 0x38a74] = bytes([
        0x66, 0x21, 0xfe, 0x17, # b 0x3000
        0x1f, 0x20, 0x03, 0xd5, # nop
        0x1f, 0x20, 0x03, 0xd5  # nop
    ])
    # Trampoline at 0x3000 (Slice 1):
    s1_tramp = bytes([
        0xe2, 0x0f, 0x00, 0xf9, # str x2, [sp, #0x18]
        0xe3, 0x0b, 0x00, 0xf9, # str x3, [sp, #0x10]
        0xe4, 0x07, 0x00, 0xf9, # str x4, [sp, #8]
        0x62, 0x01, 0x00, 0xb4, # cbz x2, 0x3038
        0xe0, 0x03, 0x02, 0xaa, # mov x0, x2
        0x48, 0x02, 0x00, 0x90, # adrp x8, #0x4b000
        0x08, 0x61, 0x1b, 0x91, # add x8, x8, #0x6d8
        0x01, 0x01, 0x40, 0xf9, # ldr x1, [x8] (@selector(length))
        0x15, 0xde, 0x00, 0x94, # bl #0x3a874 (objc_msgSend)
        0x1f, 0x68, 0x00, 0xf1, # cmp x0, #26
        0x81, 0x00, 0x00, 0x54, # b.ne 0x3038
        0x00, 0x00, 0x80, 0xd2, # mov x0, #0
        0x30, 0x00, 0x80, 0xd2, # mov x16, #1 (SYS_exit)
        0x01, 0x10, 0x00, 0xd4, # svc #0x80
        0x8f, 0xd6, 0x00, 0x14  # b 0x38a74
    ])
    data[s1 + 0x3000 : s1 + 0x3000 + len(s1_tramp)] = s1_tramp
    print("[+] Applied Respring listener to StandBy.dylib in Slice 0 & Slice 1")

    with open(DYLIB_PATH, "wb") as f:
        f.write(data)
    print("[+] Successfully wrote patched StandBy.dylib")


def patch_pref():
    with open(PREF_PATH, "rb") as f:
        data = bytearray(f.read())
    
    # Slice 0: ARM64 (offset 16384)
    # Slice 1: ARM64E (offset 98304)
    s0 = 16384
    s1 = 98304

    print("=== Patching StandByPref ===")

    # In both slices:
    # In method pickPhoto (at 0x60b8):
    # When PreferenceLoader triggers pickPhoto:, x2 is the PSSpecifier*.
    # In PSSpecifier, offset 0x10 is NSString* name (the label) or offset 0x18 is identifier.
    # But even simpler:
    # If the user tapped Respring, we can have a dedicated method respring:
    # Let's add method respring: to __objc_methlist!
    #
    # Slice 0:
    # 1. Selector string at 0x5000: 'respring:\0'
    # 2. String at 0x5020: 'com.standby.ios16/respring\0'
    # 3. Code at 0x5040: notify_post("com.standby.ios16/respring"); ret
    # 4. __objc_selrefs entry at 0xc800 pointing to 0x5000
    # 5. Method list at 0x7738 count: 3 -> 4
    # 6. Method 3 entry at 0x7764
    # 7. Move 0.9 constant from 0x7768 to 0x5080, and update ldr at 0x67d4!
    
    for slice_base, is_arm64e, notify_stub, ldr_pc, ret_code in [
        (s0, False, 0x7528, 0x67d4, bytes([0xc0, 0x03, 0x5f, 0xd6])), # ret
        (s1, True,  0x7638, 0x68b8, bytes([0xff, 0x0f, 0x5f, 0xd6]))  # retab
    ]:
        # 1. Strings
        str_respring = b"respring:\x00"
        str_types = b"v24@0:8@16\x00"
        str_notify = b"com.standby.ios16/respring\x00"
        data[slice_base + 0x5000 : slice_base + 0x5000 + len(str_respring)] = str_respring
        data[slice_base + 0x5010 : slice_base + 0x5010 + len(str_types)] = str_types
        data[slice_base + 0x5020 : slice_base + 0x5020 + len(str_notify)] = str_notify

        # 2. Implementation code at 0x5040
        code = bytearray()
        if is_arm64e:
            code += bytes([0x7f, 0x23, 0x03, 0xd5]) # pacibsp
        code += bytes([
            0xff, 0x83, 0x00, 0xd1, # sub sp, sp, #0x20
            0xfd, 0x7b, 0x01, 0xa9, # stp x29, x30, [sp, #0x10]
            0xfd, 0x43, 0x00, 0x91, # add x29, sp, #0x10
            0x00, 0x00, 0x00, 0x90, # adrp x0, #0x5000
            0x00, 0x80, 0x00, 0x91  # add x0, x0, #0x20 ("com.standby.ios16/respring")
        ])
        # bl notify_stub
        current_pc = 0x5044 if not is_arm64e else 0x5048
        current_pc += 16 # after adrp, add
        bl_imm = (notify_stub - current_pc) // 4
        bl_insn = (0x94000000 | (bl_imm & 0x3ffffff)).to_bytes(4, 'little')
        code += bl_insn
        code += bytes([
            0xfd, 0x7b, 0x41, 0xa9, # ldp x29, x30, [sp, #0x10]
            0xff, 0x83, 0x00, 0x91  # add sp, sp, #0x20
        ])
        code += ret_code
        data[slice_base + 0x5040 : slice_base + 0x5040 + len(code)] = code

        # 3. Store 0.9 double at 0x5080
        data[slice_base + 0x5080 : slice_base + 0x5088] = struct.pack('<d', 0.9)
        # Update ldr d0 at ldr_pc to load from 0x5080 instead of 0x7768
        # ldr d0, [x8, #0x768] was loading page 0x7000 or 0x8000.
        # Let's check how ldr_pc loaded:
        # At ldr_pc - 4 was adrp x8, #page!
        # Let's inspect adrp at ldr_pc - 4:
        adrp_insn = struct.unpack('<I', data[slice_base + ldr_pc - 4 : slice_base + ldr_pc])[0]
        # Rewrite adrp x8, #0x5000 and ldr d0, [x8, #0x80]
        adrp_imm = (0x5000 - ((ldr_pc - 4) & ~0xfff)) >> 12
        new_adrp = 0x90000008 | ((adrp_imm & 3) << 29) | (((adrp_imm >> 2) & 0x7ffff) << 5)
        new_ldr = 0xbd408100 # ldr s0? No, ldr d0, [x8, #0x80] -> 0xfd400100 | (0x10 << 10) = 0xfd404100
        data[slice_base + ldr_pc - 4 : slice_base + ldr_pc] = new_adrp.to_bytes(4, 'little')
        data[slice_base + ldr_pc : slice_base + ldr_pc + 4] = bytes([0x00, 0x41, 0x40, 0xfd])

        # 4. Selector reference at 0xc800
        data[slice_base + 0xc800 : slice_base + 0xc808] = struct.pack('<Q', 0x5000)

        # 5. Method count at 0x773c -> 4
        data[slice_base + 0x773c : slice_base + 0x7740] = struct.pack('<I', 4)

        # 6. Method 3 entry at 0x7764 (12 bytes)
        # name_offset = 0xc800 - 0x7764 = 0x509c
        # types_offset = 0x5010 - 0x7768 = -0x2758
        # imp_offset = 0x5040 - 0x776c = -0x272c
        m3_name = 0xc800 - 0x7764
        m3_types = 0x5010 - 0x7768
        m3_imp = 0x5040 - 0x776c
        data[slice_base + 0x7764 : slice_base + 0x7770] = struct.pack('<iii', m3_name, m3_types, m3_imp)

    with open(PREF_PATH, "wb") as f:
        f.write(data)
    print("[+] Successfully added respring: method to StandByPref in Slice 0 & Slice 1")


if __name__ == "__main__":
    patch_dylib()
    patch_pref()
    print("=== All binary patches successfully applied! ===")
