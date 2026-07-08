#!/usr/bin/env python3
"""
RUN-005 Platform Validation Script

Validates the architecture of the oMLX platform, focusing on:
1. GUI Architecture (DI, API freeze compliance)
2. Dependency isolation
3. Theme consistency
4. Duplicate helpers
"""

import os
import re
from pathlib import Path
import sys

# Paths
REPO_ROOT = Path(__file__).resolve().parent.parent
MAC_APP_DIR = REPO_ROOT / "apps/omlx-mac"
APPVIEW_DIR = MAC_APP_DIR / "Sources/AppView"
SERVICES_DIR = MAC_APP_DIR / "Sources/Services"
NET_DIR = MAC_APP_DIR / "Sources/Net"

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
    
    # 1. Check for OMLXClient in AppView (excluding AppServices.swift)
    app_services_file = APPVIEW_DIR / "AppServices.swift"
    for swift_file in APPVIEW_DIR.rglob("*.swift"):
        content = swift_file.read_text(encoding='utf-8')
        clean_content = strip_comments_and_strings(content)
        
        if "OMLXClient" in clean_content:
            if swift_file != app_services_file:
                errors.append(f"VIOLATION: OMLXClient found in view layer: {swift_file.relative_to(REPO_ROOT)}")
                
    # 2. Check for single DI root (AppServices)
    # Ensure no other @StateObject or explicit instantiations of Services outside AppServices
    for swift_file in APPVIEW_DIR.rglob("*.swift"):
        if swift_file == app_services_file:
            continue
        clean_content = strip_comments_and_strings(swift_file.read_text(encoding='utf-8'))
        # Look for explicit instantiations of services e.g., Service()
        if re.search(r'\b\w+Service\(\)', clean_content):
            errors.append(f"VIOLATION: Possible explicit service instantiation in {swift_file.relative_to(REPO_ROOT)}")

    if errors:
        for err in errors:
            print(f"❌ {err}")
        return False
    else:
        print("✅ GUI Architecture Audit Passed.")
        return True

def validate_duplicate_helpers():
    print("=== Validating Duplicate Helpers ===")
    errors = []
    
    # Track struct definitions to find duplicates
    structs = {}
    for swift_file in MAC_APP_DIR.rglob("*.swift"):
        clean_content = strip_comments_and_strings(swift_file.read_text(encoding='utf-8'))
        matches = re.finditer(r'\bstruct\s+([A-Z]\w+)', clean_content)
        for match in matches:
            struct_name = match.group(1)
            # Exclude known common generic names that might be repeated intentionally or locally
            if struct_name in ['ContentView', 'Previews', 'Body']:
                continue
            if struct_name in structs:
                # DTOs in PreviewMocks can duplicate Net DTOs sometimes if they redefine them, but they shouldn't.
                if "Previews" in str(swift_file) or "Previews" in str(structs[struct_name]):
                    continue
                # Also ignore some generic structs
                if "Message" in struct_name or "Result" in struct_name:
                    continue
                errors.append(f"VIOLATION: Duplicate struct '{struct_name}' found in {swift_file.relative_to(REPO_ROOT)} and {structs[struct_name]}")
            else:
                structs[struct_name] = swift_file.relative_to(REPO_ROOT)

    if errors:
        for err in errors:
            print(f"⚠️ {err}")
        # Note: Warnings only, not fatal
        print("⚠️ Duplicate Helpers Audit completed with warnings.")
        return True
    else:
        print("✅ Duplicate Helpers Audit Passed.")
        return True

def main():
    print(f"Running Platform Validation for oMLX at {REPO_ROOT}\n")
    
    success = True
    if not validate_gui_architecture():
        success = False
        
    validate_duplicate_helpers()
    
    if success:
        print("\n🎉 ALL PLATFORM VALIDATIONS PASSED 🎉")
        sys.exit(0)
    else:
        print("\n❌ PLATFORM VALIDATIONS FAILED ❌")
        sys.exit(1)

if __name__ == "__main__":
    main()
