require 'xcodeproj'
require 'find'

project_path = 'omlx.xcodeproj'
project = Xcodeproj::Project.open(project_path)
target = project.targets.find { |t| t.name == 'oMLX' }

build_phase = target.source_build_phase

Find.find('Sources/DiagnosticsView', 'Sources/AppView/Screens/DeveloperStudio', 'Sources/Views', 'Sources/ViewModels', 'Sources/Models', 'Sources/Services') do |path|
  if path =~ /.*\.swift$/
    # Skip if it's already added
    file_ref = project.main_group.find_file_by_path(path) || project.main_group.new_reference(path)
    unless build_phase.files.find { |f| f.file_ref == file_ref }
      build_phase.add_file_reference(file_ref)
      puts "Added #{path} to target"
    end
  end
end

project.save
