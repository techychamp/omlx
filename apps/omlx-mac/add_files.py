import os
from pbxproj import XcodeProject
from pbxproj.pbxextensions.ProjectFiles import ProjectFiles

orig_filter = ProjectFiles._filter_targets_without_path

def patched_filter(self, path, target_name):
    try:
        return orig_filter(self, path, target_name)
    except AttributeError:
        return target_name

ProjectFiles._filter_targets_without_path = patched_filter

project_path = 'oMLX.xcodeproj/project.pbxproj'
project = XcodeProject.load(project_path)

files_to_add = [
    'Sources/Net/DTO/GenerationDTO.swift',
    'Sources/Net/DTO/PlatformDTO.swift',
    'Sources/Net/DTO/SessionDTO.swift',
    'Sources/Net/DTO/DiagnosticsDTO.swift',
    
    'Sources/Services/GenerationService.swift',
    'Sources/Services/SessionService.swift',
    'Sources/Services/ModelManagementService.swift',
    'Sources/Services/DiagnosticsService.swift',
    'Sources/Services/PlatformService.swift',
    
    'Sources/Services/Previews/PreviewMocks.swift'
]

# Add DTOs
for file in files_to_add[:4]:
    project.add_file(file, force=False, target_name='oMLX')

# Add services
for file in files_to_add[4:10]:
    project.add_file(file, force=False, target_name='oMLX')

# Now add test mocks
test_files = [
    'Tests/oMLXTests/Mocks/MockGenerationService.swift'
]

for file in test_files:
    project.add_file(file, force=False, target_name='oMLXTests')

project.save()
print("Successfully added files to Xcode project.")
