with open('oMLX.xcodeproj/project.pbxproj', 'r') as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    if '2D7759592FFFE88200955D55' in line or '2D77595A2FFFE88200955D55' in line:
        continue
    new_lines.append(line)

with open('oMLX.xcodeproj/project.pbxproj', 'w') as f:
    f.writelines(new_lines)

print("Cleaned duplicate ProgressIndicator reference from project file.")
