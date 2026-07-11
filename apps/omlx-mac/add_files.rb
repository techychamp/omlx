require 'xcodeproj'

project_path = 'omlx.xcodeproj'
project = Xcodeproj::Project.open(project_path)
target = project.targets.find { |t| t.name == 'oMLX' }

files_to_add = [
  'Sources/Managers/AppearanceManager.swift',
  'Sources/Managers/WindowStateManager.swift',
  'Sources/Managers/KeyboardShortcutManager.swift',
  'Sources/Views/Preferences/PreferencesView.swift',
  'Sources/Views/GlobalSearch/GlobalSearchViewModel.swift',
  'Sources/Views/GlobalSearch/GlobalSearchView.swift',
  'Sources/Theme/Components/StateViews.swift',
  'Sources/Theme/Components/Cards.swift'
]

files_to_add.each do |file_path|
  file_ref = project.main_group.find_file_by_path(file_path) || project.main_group.new_reference(file_path)
  
  # Check if it's already in the target's source build phase
  build_phase = target.source_build_phase
  unless build_phase.files.find { |f| f.file_ref == file_ref }
    build_file = build_phase.add_file_reference(file_ref)
    puts "Added #{file_path} to target"
  end
end

project.save
