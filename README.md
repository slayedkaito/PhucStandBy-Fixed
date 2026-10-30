# PhucStandBy (Multilingual & Bugfixed Edition)

An optimized, multilingual edition of the iOS 17 StandBy mode tweak for iOS 16 (Rootless).

* **Original Author**: [tranhoangphuc (PhucBakhi)](https://github.com/phucbakhi)
* **Maintainer (Fixes & Localization)**: amiaxf
* **Package Identifier**: `com.phucbakhi.phucstandby`
* **Target Architecture**: `iphoneos-arm64` (ARM64 & ARM64E / Rootless iOS 16+)

---

## ✨ Improvements in this Edition (v2.0.26-2)

1. **Dynamic Language Selector & Multilingual Engine**:
   * **In-Settings Language Selector**: Added a dedicated **Language** setting in the tweak preferences with options: **Auto (System Language)**, **English**, **Bahasa Indonesia**, and **Tiếng Việt**.
   * **Synchronized Mode & Settings**: Both the Settings pane and the StandBy mode overlay adapt dynamically to the chosen language.
   * When set to **Auto**, StandBy mode automatically matches your device system language (English on English iPhones, Indonesian on Indonesian iPhones), completely eliminating the mixed-language issue.
   * Built with a zero-overhead, 100% crash-proof memory switching engine that preserves all format specifiers and never triggers Safe Mode.
   * Cleaned offensive placeholder strings in settings to standard examples (`e.g. My Wallpaper` / `cth. Wallpaper Saya`).

2. **Lockscreen-Only Activation (`shouldShow` Patch)**:
   * Fixed a bug where StandBy activated on Homescreen or inside other apps when the phone was in landscape and charging.
   * With the ARM64 `NOP` patch, StandBy only runs when the device is locked (`isUILocked`). When unlocked, rendering stops completely to preserve battery and CPU.

3. **Safe Mode / Widget Swipe Crash Fix**:
   * Fixed a fatal crash (`EXC_BAD_ACCESS` / Safe Mode) occurring when swiping widgets horizontally or vertically.
   * Weather format strings (`%d°C`, `%ld°`, `C:%ld° T:%ld°`, `C:--° T:--°`, `• `, `H:%ld° L:%ld°`) are strictly preserved in their original memory slots.

4. **Auto Wake Screen on Charge Restored & Fixed**:
   * Restored the **"Auto Wake Screen on Charge + Landscape"** feature with its delay slider, set to **OFF by default** to give users full control.
   * Completely eliminated the **infinite wake loop bug**: when manually locking the device while charging in landscape, the screen stays off cleanly until undocked or replugged.
   * Fixed the **pitch-black lockscreen wallpaper bug** by routing backlight wake through button wake events (`SBBacklightSourceButton`) and using transparent window clearing (`clearColor`).

5. **Widget Swipe Stuck Bug Fix**:
   * Fixed an issue where swiping between widgets in StandBy mode would permanently freeze or get stuck when gestures were cancelled or started near the page indicator pill.

6. **In-Settings Respring & Credits**:
   * Added a native **"Respring SpringBoard"** button at the bottom of the Settings page (`StandByPref.bundle`) with a confirmation dialog, safely invoking `sys_exit(0)` via Darwin notifications without breaking ARM64E PAC.
   * Added official **Credits** section inside Settings acknowledging Original Developer **tranhoangphuc (PhucBakhi)** and Maintainer **amiaxf**.

7. **100% Rootless & Sileo Native Compatibility**:
   * Packaged with standalone LZMA stream format (`0x5d`) resolving `lzma error: file format not recognized` in RootHide Patcher / Sileo.
   * Re-signed SHA-256 Mach-O `CodeDirectory` hashes for both ARM64 and ARM64E (PAC/Dopamine) slices on both `StandBy.dylib` and `StandByPref` with 0 mismatches.

---

## 📦 Installation

1. Download the latest `.deb` package from the [Releases](releases) tab.
2. Open with **Sileo**, **Zebra**, or **Filza**.
3. Tap **Install** / **Update**, then **Respring**.

---

## ⚖️ Disclaimer & Attribution

This project is an unofficial community enhancement and bugfix release of the original tweak by **tranhoangphuc**. All credit for the original design, architecture, and core tweak implementation belongs to the original developer.
