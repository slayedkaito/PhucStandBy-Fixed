import subprocess
import urllib.request
import json
import os
import sys

def main():
    p = subprocess.Popen(['git', 'credential', 'fill'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = p.communicate('protocol=https\nhost=github.com\n\n')
    token = None
    for line in stdout.splitlines():
        if line.startswith('password='):
            token = line.split('=', 1)[1]

    if not token:
        print("[ERROR] Could not get GitHub token from git credential helper")
        sys.exit(1)

    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'Python'
    }

    req = urllib.request.Request('https://api.github.com/repos/slayedkaito/PhucStandBy-Fixed/releases/tags/v2.0.26-2', headers=headers)
    with urllib.request.urlopen(req) as resp:
        release = json.loads(resp.read().decode('utf-8'))

    release_id = release['id']
    upload_url = release['upload_url'].split('{')[0]
    print(f"Release ID: {release_id}")

    # Delete existing assets
    for asset in release.get('assets', []):
        asset_id = asset['id']
        asset_name = asset['name']
        print(f"Deleting old asset: {asset_name} (ID: {asset_id})...")
        del_req = urllib.request.Request(f'https://api.github.com/repos/slayedkaito/PhucStandBy-Fixed/releases/assets/{asset_id}', headers=headers, method='DELETE')
        try:
            with urllib.request.urlopen(del_req) as del_resp:
                print(f"  Deleted: {del_resp.status}")
        except Exception as e:
            print(f"  Error deleting {asset_name}: {e}")

    # Upload all 3 deb files
    debs = [
        "com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64.deb",
        "com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64_id.deb",
        "com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64_vi.deb"
    ]

    upload_headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/vnd.debian.binary-package',
        'User-Agent': 'Python'
    }

    uploaded_links = []
    for deb_name in debs:
        deb_path = os.path.join(r"C:\Users\AmiaXf\.gemini\antigravity\scratch\phucstandby", deb_name)
        with open(deb_path, 'rb') as f:
            deb_data = f.read()

        up_url = f"{upload_url}?name={deb_name}"
        print(f"\nUploading {deb_name} ({len(deb_data)} bytes)...")
        up_req = urllib.request.Request(up_url, data=deb_data, headers=upload_headers, method='POST')
        with urllib.request.urlopen(up_req) as up_resp:
            res = json.loads(up_resp.read().decode('utf-8'))
            download_url = res.get('browser_download_url')
            print(f"  Uploaded successfully: {download_url}")
            uploaded_links.append((deb_name, download_url))

    # Update release body
    release_body = """## PhucStandBy v2.0.26-2 (Crash-Free Tilt & Multilingual Edition)

An optimized, multilingual edition of the iOS 17 StandBy mode tweak for iOS 16 (Rootless).

### 🚀 What's New & Fixed in this Release:

1. **Fix Crash & Reboot to Safe Mode on Landscape Tilt**:
   - Fixed a fatal crash (`EXC_BAD_ACCESS` / SpringBoard panic) that occurred immediately when the iPhone was tilted to landscape while charging.
   - Identified and fixed an uninitialized scratch register (`x16` instead of `x8`) in the ARM64E window setup logic.
   - Restored pristine OLED black background initialization logic, ensuring 100% stability on rotation.

2. **Multilingual Architecture & Clean English Default**:
   - **Clean English Overlay (Primary DEB)**: `com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64.deb` features a pure native English StandBy overlay (`Battery`, `Charging`, `Now Playing`, `Paused`, `SUNDAY`, `DAY %ld`, `Today`, `Your day is clear`), completely fixing the mixed language issue on English devices.
   - **System-Adaptive Settings**: Preferences in Settings (`StandByPref.bundle`) automatically follow your iOS system language (English, Indonesian, Vietnamese).
   - **Dedicated Language Overlays**: Separate `.deb` packages for Indonesian (`..._id.deb`) and Vietnamese (`..._vi.deb`) StandBy overlays are attached below for users wanting their native language on the StandBy screen.

3. **Weather Widget 100% Preserved (Zero Safe Mode)**:
   - Preserves all 6 Weather format strings (`%d°C`, `%ld°`, `C:%ld° T:%ld°`, `C:--° T:--°`, `• `, `H:%ld° L:%ld°`) strictly in place, eliminating widget crash loops.

4. **Lockscreen-Only Activation (`shouldShow` Patch)**:
   - StandBy only activates when the device is locked (`isUILocked`). Prevents battery drain and unwanted popups when unlocked in landscape.

5. **Infinite Wake Loop & Black Wallpaper Eliminated**:
   - NOPed broken update wake loop in timer tick, allowing device to stay asleep when locked on charger.

6. **Widget Swipe Stuck Bug Fix**:
   - Fixed swipe freezing between widgets when gesture touched the pill indicator or was cancelled.

7. **In-Settings Respring & Credits**:
   - Added native **"Respring SpringBoard"** action in Settings with confirmation dialog.
   - Added official **Credits** section acknowledging Original Developer **tranhoangphuc (PhucBakhi)** and Maintainer **amiaxf**.

8. **Rootless & Sileo Native Compatibility**:
   - Packaged with standalone LZMA stream (`0x5d`) resolving `lzma error` in RootHide Patcher / Sileo.
   - SHA-256 CodeDirectory signatures verified with 0 mismatches for ARM64 and ARM64E.

### 📥 Downloads:
- **English Default (Recommended)**: [`com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64.deb`](https://github.com/slayedkaito/PhucStandBy-Fixed/releases/download/v2.0.26-2/com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64.deb)
- **Indonesian StandBy Overlay**: [`com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64_id.deb`](https://github.com/slayedkaito/PhucStandBy-Fixed/releases/download/v2.0.26-2/com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64_id.deb)
- **Vietnamese StandBy Overlay**: [`com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64_vi.deb`](https://github.com/slayedkaito/PhucStandBy-Fixed/releases/download/v2.0.26-2/com.phucbakhi.phucstandby_2.0.26-2_iphoneos-arm64_vi.deb)

---
- **Original Developer**: tranhoangphuc (PhucBakhi)
- **Maintainer & Fixes**: amiaxf
"""

    patch_body_req = urllib.request.Request(f'https://api.github.com/repos/slayedkaito/PhucStandBy-Fixed/releases/{release_id}', data=json.dumps({
        'name': 'v2.0.26-2 (Crash-Free Tilt & Multilingual Edition)',
        'body': release_body
    }).encode('utf-8'), headers={**headers, 'Content-Type': 'application/json'}, method='PATCH')

    with urllib.request.urlopen(patch_body_req) as patch_resp:
        print("\nUpdated release description successfully!")

if __name__ == "__main__":
    main()
