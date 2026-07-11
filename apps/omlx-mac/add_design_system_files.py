import os
from pbxproj import XcodeProject
from pbxproj.pbxextensions.ProjectFiles import ProjectFiles

# Monkeypatch pbxproj to prevent attribute error on certain project configurations
orig_filter = ProjectFiles._filter_targets_without_path
def patched_filter(self, path, target_name):
    try:
        return orig_filter(self, path, target_name)
    except AttributeError:
        return target_name
ProjectFiles._filter_targets_without_path = patched_filter

project_path = 'oMLX.xcodeproj/project.pbxproj'
if not os.path.exists(project_path):
    print(f"Error: Xcode project file not found at {project_path}")
    exit(1)

project = XcodeProject.load(project_path)

files_to_add = [
    'Sources/Theme/OneDesign+Colors.swift',
    'Sources/Theme/OneDesign+Spacing.swift',
    'Sources/Theme/OneDesign+Typography.swift',
    'Sources/Theme/OneDesign+Motion.swift',
    'Sources/Theme/OneDesign+Layout.swift',
    'Sources/Theme/OneDesign+Surfaces.swift',
    'Sources/Theme/OneDesign+Shapes.swift',
    'Sources/Theme/OneDesign+Icons.swift',
    'Sources/Theme/OneDesign+SemanticRoles.swift',
    'Sources/Theme/OneDesign+Interaction.swift',
    'Sources/Theme/OneDesign+Themes.swift',
    'Sources/Theme/Components/ProgressIndicator.swift'
]

for file in files_to_add:
    project.add_file(file, force=False, target_name='oMLX')

project.save()
print("Successfully linked all design system foundation files to the Xcode project target 'oMLX'.")
