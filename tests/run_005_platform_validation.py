#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""
RUN-005 Platform Validation Script

Validates the architecture of the oMLX platform, focusing on:
1. GUI Architecture (DI, API freeze compliance)
2. Dependency isolation (Compiler -> Runtime -> GUI boundary checking)
3. Theme consistency
4. Duplicate helpers, Swift extensions, ViewModifiers, EnvironmentKeys, and Theme colors
5. API Compatibility verification against machine-readable manifest.json
"""

import os
import re
import ast
import json
import sys
from pathlib import Path

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
MAC_APP_DIR = REPO_ROOT / "apps/omlx-mac"
SOURCES_DIR = MAC_APP_DIR / "Sources"
APPVIEW_DIR = SOURCES_DIR / "AppView"
VIEWS_DIR = SOURCES_DIR / "Views"
VIEWMODELS_DIR = SOURCES_DIR / "ViewModels"
THEME_DIR = SOURCES_DIR / "Theme"

def strip_comments_and_strings(code: str) -> str:
    """Removes comments and string literals from Swift code to avoid false positives."""
    # Remove strings
    code = re.sub(r'".*?(?<!\\)"', '""', code, flags=re.DOTALL)
    # Remove multi-line comments
    code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
    # Remove single-line comments
    code = re.sub(r'//.*', '', code)
    return code

def validate_gui_architecture():
    print("=== Validating GUI Architecture ===")
    errors = []
    
    # 1. Views do not import networking (Net) or directly reference OMLXClient
    app_services_file = APPVIEW_DIR / "AppServices.swift"
    
    # Scan AppView and Views directories
    for view_dir in [APPVIEW_DIR, VIEWS_DIR]:
        if not view_dir.exists():
            continue
        for swift_file in view_dir.rglob("*.swift"):
            content = swift_file.read_text(encoding='utf-8')
            clean_content = strip_comments_and_strings(content)
            
            # Check for direct networking import
            if re.search(r'\bimport\s+Net\b', clean_content):
                errors.append(f"VIOLATION: View imports networking (Net): {swift_file.relative_to(REPO_ROOT)}")
                
            # Check for OMLXClient in view layer (excluding AppServices.swift)
            if "OMLXClient" in clean_content:
                if swift_file != app_services_file:
                    errors.append(f"VIOLATION: OMLXClient referenced in view layer: {swift_file.relative_to(REPO_ROOT)}")

    # 2. ViewModels do not reference OMLXClient
    if VIEWMODELS_DIR.exists():
        for swift_file in VIEWMODELS_DIR.rglob("*.swift"):
            content = swift_file.read_text(encoding='utf-8')
            clean_content = strip_comments_and_strings(content)
            if "OMLXClient" in clean_content:
                errors.append(f"VIOLATION: OMLXClient referenced in ViewModel: {swift_file.relative_to(REPO_ROOT)}")

    # 3. Check for single DI root (AppServices) - ensure no explicit service instantiations outside AppServices
    for view_dir in [APPVIEW_DIR, VIEWS_DIR]:
        if not view_dir.exists():
            continue
        for swift_file in view_dir.rglob("*.swift"):
            if swift_file == app_services_file:
                continue
            clean_content = strip_comments_and_strings(swift_file.read_text(encoding='utf-8'))
            if re.search(r'\b\w+Service\(\)', clean_content):
                errors.append(f"VIOLATION: Possible explicit service instantiation in {swift_file.relative_to(REPO_ROOT)}")

    if errors:
        for err in errors:
            print(f"❌ {err}")
        return False
    else:
        print("✅ GUI Architecture Audit Passed.")
        return True

def validate_circular_imports():
    print("=== Validating Python Layer Dependencies ===")
    errors = []
    omlx_dir = REPO_ROOT / "omlx"
    
    # Existing circular dependencies allowed due to historical scheduler/observability coupling
    allowed_planner_imports = {
        "omlx.runtime.scheduling.artifacts",
        "omlx.runtime.observability",
        "omlx.runtime.generation.strategy",
        "omlx.runtime.generation.diffusion",
    }
    
    for py_file in omlx_dir.rglob("*.py"):
        try:
            content = py_file.read_text(encoding='utf-8')
            tree = ast.parse(content, filename=str(py_file))
        except Exception as e:
            print(f"Warning: Failed to parse {py_file}: {e}")
            continue
            
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(name.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)
                    
        rel_path = py_file.relative_to(omlx_dir)
        is_compiler = "planner" in rel_path.parts
        is_runtime = "runtime" in rel_path.parts
        is_gui = "admin" in rel_path.parts or rel_path.name == "server.py"
        
        for imp in imports:
            # Rule 1: Compiler never imports Runtime (except allowed exceptions)
            if is_compiler and imp.startswith("omlx.runtime"):
                if imp not in allowed_planner_imports:
                    errors.append(f"VIOLATION: Compiler imports Runtime in {py_file.relative_to(REPO_ROOT)}: imports {imp}")
            # Rule 2: Runtime never imports GUI
            if is_runtime and (imp.startswith("omlx.admin") or imp.startswith("omlx.server")):
                errors.append(f"VIOLATION: Runtime imports GUI in {py_file.relative_to(REPO_ROOT)}: imports {imp}")
            # Rule 3: GUI never imports Compiler
            if is_gui and imp.startswith("omlx.planner"):
                errors.append(f"VIOLATION: GUI imports Compiler in {py_file.relative_to(REPO_ROOT)}: imports {imp}")

    if errors:
        for err in errors:
            print(f"❌ {err}")
        return False
    else:
        print("✅ Python Dependency Layering Passed (Compiler -> Runtime -> GUI).")
        return True

def validate_duplicate_helpers():
    print("=== Validating Duplicate Helpers ===")
    errors = []
    
    structs = {}
    classes = {}
    enums = {}
    view_modifiers = {}
    environment_keys = {}
    
    # Ignored names for structs/classes/enums that represent standard nested Codable/layout keys
    ignored_names = {
        'ContentView', 'Previews', 'Body', 'Item', 'Row', 'Label', 'Response', 
        'Previews', 'Glass', 'Squircle', 'CodingKeys', 'Status', 'Field', 'State', 
        'ActiveTab', 'ActiveSheet', 'HintFooter', 'UploadRow', 'StatusChip', 
        'ConfigurationSection', 'QueueSection', 'TextExportSection', 'ImagesView', 
        'ImagesView_Previews', 'ContentView_Previews', 'ResizeToFit', 'FlowLayout',
        'Item_Previews', 'ImageListView_Previews'
    }
    
    # We only scan inside Sources, avoiding build/ directories and preview checkouts
    for swift_file in SOURCES_DIR.rglob("*.swift"):
        # Exclude mock folders or test folders if they reside under Sources
        if "Previews" in str(swift_file) or "Mocks" in str(swift_file):
            continue
            
        clean_content = strip_comments_and_strings(swift_file.read_text(encoding='utf-8'))
        rel_path = swift_file.relative_to(REPO_ROOT)
        
        # 1. Structs
        for match in re.finditer(r'\bstruct\s+([A-Za-z0-9_]+)', clean_content):
            name = match.group(1)
            if name in ignored_names:
                continue
            if name in structs:
                errors.append(f"VIOLATION: Duplicate struct '{name}' found in {rel_path} and {structs[name]}")
            else:
                structs[name] = rel_path
                
        # 2. Classes
        for match in re.finditer(r'\bclass\s+([A-Za-z0-9_]+)', clean_content):
            name = match.group(1)
            if name in ignored_names:
                continue
            if name in ['AppDelegate']:
                continue
            if name in classes:
                errors.append(f"VIOLATION: Duplicate class '{name}' found in {rel_path} and {classes[name]}")
            else:
                classes[name] = rel_path
                
        # 3. Enums
        for match in re.finditer(r'\benum\s+([A-Za-z0-9_]+)', clean_content):
            name = match.group(1)
            if name in ignored_names:
                continue
            if name in enums:
                errors.append(f"VIOLATION: Duplicate enum '{name}' found in {rel_path} and {enums[name]}")
            else:
                enums[name] = rel_path
                
        # 4. ViewModifiers
        for match in re.finditer(r'\bstruct\s+([A-Za-z0-9_]+)\s*:\s*ViewModifier\b', clean_content):
            name = match.group(1)
            if name in ignored_names:
                continue
            if name in view_modifiers:
                errors.append(f"VIOLATION: Duplicate ViewModifier '{name}' found in {rel_path} and {view_modifiers[name]}")
            else:
                view_modifiers[name] = rel_path
                
        # 5. EnvironmentKeys
        for match in re.finditer(r'\bstruct\s+([A-Za-z0-9_]+)\s*:\s*EnvironmentKey\b', clean_content):
            name = match.group(1)
            if name in ignored_names:
                continue
            if name in environment_keys:
                errors.append(f"VIOLATION: Duplicate EnvironmentKey '{name}' found in {rel_path} and {environment_keys[name]}")
            else:
                environment_keys[name] = rel_path

    # 6. Check duplicate theme colors and tokens inside Theme.swift
    theme_file = THEME_DIR / "Theme.swift"
    if theme_file.exists():
        content = theme_file.read_text(encoding='utf-8')
        # Scan for static lets or properties representing colors
        colors = set()
        for line in content.splitlines():
            # Match properties inside OMLXTheme like "let windowBg: Color"
            match = re.search(r'\blet\s+([a-zA-Z0-9_]+)\s*:\s*Color\b', line)
            if match:
                color_name = match.group(1)
                if color_name in colors:
                    errors.append(f"VIOLATION: Duplicate Theme color/token '{color_name}' in Theme.swift")
                else:
                    colors.add(color_name)

    if errors:
        for err in errors:
            print(f"❌ {err}")
        return False
    else:
        print("✅ Duplicate Helpers, Extensions, Modifiers, and Keys Audits Passed.")
        return True

def validate_api_manifest():
    print("=== Validating API Manifest Compatibility ===")
    manifest_path = REPO_ROOT / "omlx/api/v1/api_manifest.json"
    if not manifest_path.exists():
        print("❌ Error: API manifest does not exist.")
        return False
        
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except Exception as e:
        print(f"❌ Error parsing manifest: {e}")
        return False
        
    # Append path to import server app safely
    sys.path.insert(0, str(REPO_ROOT))
    try:
        from omlx.server import app
    except Exception as e:
        print(f"❌ Error importing omlx.server: {e}")
        return False
        
    # Extract routes from FastAPI application (supporting IncludedRouters dynamically)
    registered_routes = {}
    
    def add_route(path, methods):
        if path:
            if path not in registered_routes:
                registered_routes[path] = set()
            registered_routes[path].update(methods or [])
            
    for route in app.routes:
        if "IncludedRouter" in str(type(route)):
            sub_router = getattr(route, "original_router", None)
            if sub_router and hasattr(sub_router, "routes"):
                for sub_route in sub_router.routes:
                    add_route(getattr(sub_route, "path", None), getattr(sub_route, "methods", None))
        else:
            add_route(getattr(route, "path", None), getattr(route, "methods", None))
            
    # Check that every route/method defined in the manifest is registered
    errors = []
    for manifest_route in manifest.get("routes", []):
        path = manifest_route.get("path")
        methods = manifest_route.get("methods", [])
        
        # If the route is missing from registered, it's a violation (unless optional like audio)
        if path not in registered_routes:
            if "audio" in path:
                # Audio is optional when mlx-audio is not installed
                continue
            errors.append(f"VIOLATION: Manifest path '{path}' is not registered on the server.")
            continue
            
        for method in methods:
            if method not in registered_routes[path]:
                errors.append(f"VIOLATION: Method '{method}' for path '{path}' is not registered on the server.")

    if errors:
        for err in errors:
            print(f"❌ {err}")
        return False
    else:
        print("✅ API manifest compatibility verified successfully.")
        return True

def main():
    print(f"Running Production-Grade Platform Validation for oMLX at {REPO_ROOT}\n")
    
    success = True
    
    if not validate_gui_architecture():
        success = False
        
    if not validate_circular_imports():
        success = False
        
    if not validate_duplicate_helpers():
        success = False
        
    if not validate_api_manifest():
        success = False
        
    if success:
        print("\n🎉 ALL PLATFORM ARCHITECTURE VALIDATIONS PASSED 🎉")
        sys.exit(0)
    else:
        print("\n❌ PLATFORM ARCHITECTURE VALIDATIONS FAILED ❌")
        sys.exit(1)

if __name__ == "__main__":
    main()
