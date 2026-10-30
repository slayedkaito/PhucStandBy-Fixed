import os

bp_path = r"C:\Users\AmiaXf\.gemini\antigravity\scratch\phucstandby\build_package.py"
with open(bp_path, "r", encoding="utf-8") as f:
    text = f.read()

target = 'if line.startswith("Description:"):'
repl = 'if line.startswith("Description:"):\n            new_ctrl_lines.append("Description: Bring the iOS 17 StandBy experience to iOS 16 and older devices (Supports English, Indonesian, and Vietnamese)")\n        elif line.startswith("Maintainer:"):\n            new_ctrl_lines.append("Maintainer: amiaxf")'

lines = text.splitlines()
new_lines = []
for line in lines:
    if 'new_ctrl_lines.append("Description:' in line:
        new_lines.append(line)
        new_lines.append('        elif line.startswith("Maintainer:"):')
        new_lines.append('            new_ctrl_lines.append("Maintainer: amiaxf")')
    else:
        new_lines.append(line)

with open(bp_path, "w", encoding="utf-8", newline="\r\n") as f:
    f.write("\r\n".join(new_lines) + "\r\n")

print("Updated build_package.py successfully")
