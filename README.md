# PhucStandBy (Multilingual & Bugfixed Edition)

An optimized, multilingual edition of the iOS 17 StandBy mode tweak for iOS 16 (Rootless).

* **Original Author**: [tranhoangphuc (PhucBakhi)](https://github.com/phucbakhi)
* **Maintainer (Fixes & Localization)**: amiaxf
* **Package Identifier**: `com.phucbakhi.phucstandby`
* **Target Architecture**: `iphoneos-arm64` (ARM64 & ARM64E / Rootless iOS 16+)

---

## ✨ Improvements in this Edition (v2.0.26-2)

1. **Multilingual & System Language Auto-Detection**:
   * **Settings Bundle (`StandByPref.bundle`)**: Uses native iOS `.lproj` bundles (`id.lproj`, `en.lproj`, `vi.lproj`) to automatically detect and adapt to system language (Indonesian, English, and Vietnamese).
   * **StandBy Overlay UI (`StandBy.dylib`)**: Translated all 17 on-screen widget strings from Vietnamese to clear, modern Indonesian/English.
   * Cleaned offensive placeholder strings in settings to standard examples (`cth. Wallpaper Saya`).

2. **Lockscreen-Only Activation (`shouldShow` Patch)**:
   * Fixed a bug where StandBy activated on Homescreen or inside other apps when the phone was in landscape and charging.
   * With the ARM64 `NOP` patch, StandBy only runs when the device is locked (`isUILocked`). When unlocked, rendering stops completely to preserve battery and CPU.

3. **Safe Mode / Widget Swipe Crash Fix**:
   * Fixed a fatal crash (`EXC_BAD_ACCESS` / Safe Mode) occurring when swiping widgets horizontally or vertically.
   * Weather format strings (`%d°C`, `%ld°`, `C:%ld° T:%ld°`, `C:--° T:--°`, `• `, `H:%ld° L:%ld°`) are strictly preserved in their original memory slots.

4. **Infinite Wake Loop & Black Lockscreen Fix**:
   * Fixed a logic flaw in `updateWakeLogic:` where the screen continuously turned itself back on every 1.5 seconds after being manually put to sleep on the charger.
   * Fixed the resulting pitch-black lockscreen glitch caused by programmatic wake.

5. **100% Rootless & Sileo Native Compatibility**:
   * Packaged with standalone LZMA stream format (`0x5d`) resolving `lzma error: file format not recognized` in RootHide Patcher / Sileo.
   * Re-signed SHA-256 Mach-O `CodeDirectory` hashes for both ARM64 and ARM64E (PAC/Dopamine) slices with 0 mismatches.

---

## 📦 Installation

1. Download the latest `.deb` package from the [Releases](releases) tab.
2. Open with **Sileo**, **Zebra**, or **Filza**.
3. Tap **Install** / **Update**, then **Respring**.

---

## ⚖️ Disclaimer & Attribution

This project is an unofficial community enhancement and bugfix release of the original tweak by **tranhoangphuc**. All credit for the original design, architecture, and core tweak implementation belongs to the original developer.
