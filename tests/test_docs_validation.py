# SPDX-License-Identifier: Apache-2.0
"""
Markdown syntax and link validation tests.
"""

import os
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

def test_milestone_reports_exist():
    # Root-level documents that must always exist at the repo root
    root_docs = ["README.md"]
    for m in root_docs:
        file_path = REPO_ROOT / m
        assert file_path.exists(), f"Root document '{m}' is missing!"

    # Milestone reports — canonical location is docs/milestones/ after DOCS-001 migration
    milestones = [
        "RUN_005_PLATFORM_CERTIFICATION.md",
        "RUN_005_RELEASE_READINESS.md",
        "TEST_001_Test_Isolation.md",
        "REL_001_Release_Validation.md",
        "PERF_001_Performance_Baseline.md",
    ]
    milestones_dir = REPO_ROOT / "docs" / "milestones"
    for m in milestones:
        file_path = milestones_dir / m
        assert file_path.exists(), f"Milestone report '{m}' is missing from docs/milestones/!"

def test_markdown_and_links():
    # Scan all markdown files in the repo root and docs/
    md_files = list(REPO_ROOT.glob("*.md"))
    docs_dir = REPO_ROOT / "docs"
    if docs_dir.exists():
        md_files.extend(docs_dir.rglob("*.md"))
        
    for md_file in md_files:
        if ".gemini" in str(md_file) or ".venv" in str(md_file) or "build" in str(md_file):
            continue
            
        content = md_file.read_text(encoding="utf-8")
        
        # 1. Simple malformed markdown check: check for unclosed code blocks
        unclosed_code_blocks = content.count("```") % 2
        assert unclosed_code_blocks == 0, f"Malformed markdown in {md_file.relative_to(REPO_ROOT)}: Unclosed triple-backtick code block."
        
        # 2. Extract and check all local file and relative links
        # Match [text](link)
        links = re.findall(r'\[.*?\]\((.*?)\)', content)
        for link in links:
            # Clean anchors from link, e.g., "manual.md#L123" -> "manual.md"
            clean_link = link.split('#')[0]
            if not clean_link:
                continue
                
            # Skip remote HTTP/HTTPS links and email links
            if clean_link.startswith(("http://", "https://", "mailto:", "git:")):
                continue
                
            # Resolve relative link
            if clean_link.startswith("file:///"):
                # Handle absolute workspace links e.g. file:///Users/yugeshk/dev/repo/omlx/README.md
                # Strip file:/// and check if it is part of repo or verify it directly if local path
                link_path = Path(clean_link[8:])
            else:
                # Relative link
                link_path = (md_file.parent / clean_link).resolve()
                
            # Verify file exists if it points inside the repo
            if REPO_ROOT in link_path.parents or link_path == REPO_ROOT:
                assert link_path.exists(), f"Broken link in {md_file.relative_to(REPO_ROOT)}: '{link}' resolves to non-existent path '{link_path}'"
