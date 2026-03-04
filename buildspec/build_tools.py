#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Build script for JMF tools.
Builds specified tools using PyInstaller.
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

# Define the tools to build
TOOLS = [
    'ReceiveSignals',
    'CreateMimePackage',
    'JMFSubmitter',
    'RemoveQueueEntries',
    'CreateTestPDF',
    'SetupConfig',
]

def clean_build_artifacts(tools_to_clean):
    """Remove build and dist directories for specified tools."""
    buildspec_dir = Path(__file__).resolve().parent
    
    for tool in tools_to_clean:
        # Clean dist/tool directory
        tool_dist_dir = buildspec_dir / 'dist' / tool
        if tool_dist_dir.exists():
            try:
                shutil.rmtree(tool_dist_dir)
                print(f"✅ Removed: {tool_dist_dir}")
            except Exception as e:
                print(f"⚠️  Failed to remove {tool_dist_dir}: {e}")
        
        # Clean build/tool directory
        tool_build_dir = buildspec_dir / 'build' / tool
        if tool_build_dir.exists():
            try:
                shutil.rmtree(tool_build_dir)
                print(f"✅ Removed: {tool_build_dir}")
            except Exception as e:
                print(f"⚠️  Failed to remove {tool_build_dir}: {e}")

def build_tools(tools_to_build):
    """Build specified tools using PyInstaller."""
    # Get the buildspec directory (where this script is located)
    buildspec_dir = Path(__file__).resolve().parent
    dist_dir = buildspec_dir / 'dist'
    
    print(f"Output directory: {dist_dir}")
    
    build_results = []
    
    # Build each tool
    for tool in tools_to_build:
        spec_file = buildspec_dir / f'{tool}.spec'
        
        if not spec_file.exists():
            print(f"❌ Spec file not found: {spec_file}")
            build_results.append((tool, False, f"Spec file not found"))
            continue
        
        print(f"\n{'='*60}")
        print(f"Building {tool}...")
        print(f"{'='*60}")
        
        # Run PyInstaller
        result = subprocess.run(
            ['pyinstaller', str(spec_file)],
            cwd=str(buildspec_dir),
            capture_output=False
        )
        
        if result.returncode != 0:
            print(f"❌ Build failed for {tool}")
            build_results.append((tool, False, "Build failed"))
            continue
        
        # Verify executable was created
        exe_file = dist_dir / f'{tool}.exe'
        
        if exe_file.exists():
            print(f"✅ Built {tool}.exe")
            build_results.append((tool, True, "Success"))
        else:
            print(f"⚠️  Executable not found: {exe_file}")
            build_results.append((tool, False, "Executable not found"))
    
    # Report summary
    print(f"\n{'='*60}")
    print("Build Summary:")
    print(f"{'='*60}")
    for tool, success, message in build_results:
        status = "✅" if success else "❌"
        print(f"{status} {tool}: {message}")
    
    successful = sum(1 for _, success, _ in build_results if success)
    total = len(build_results)
    print(f"\n{'='*60}")
    print(f"✅ Build complete! {successful}/{total} tools built successfully.")
    print(f"Executables are in: {dist_dir}")
    print(f"{'='*60}")

def main():
    """Parse arguments and execute build or clean operations."""
    parser = argparse.ArgumentParser(
        description="Build script for JMF tools. Builds specified tools using PyInstaller."
    )
    parser.add_argument(
        'tools',
        nargs='?',
        default='all',
        help='Tools to build/clean: "all", or specific tool name (e.g., CreateMimePackage). Default: all'
    )
    parser.add_argument(
        '--clean',
        action='store_true',
        help='Clean previous build artifacts for specified tool(s) before building'
    )
    
    args = parser.parse_args()
    
    # Determine which tools to build/clean
    if args.tools.lower() == 'all':
        tools_to_process = TOOLS
    else:
        tools_to_process = [args.tools]
    
    # Validate that spec files exist for requested tools
    buildspec_dir = Path(__file__).resolve().parent
    for tool in tools_to_process:
        spec_file = buildspec_dir / f'{tool}.spec'
        if not spec_file.exists():
            print(f"❌ Error: Spec file not found for {tool}: {spec_file}")
            sys.exit(1)
    
    # Clean if requested
    if args.clean:
        print(f"{'='*60}")
        print(f"Cleaning build artifacts for: {', '.join(tools_to_process)}")
        print(f"{'='*60}")
        clean_build_artifacts(tools_to_process)
        print("")
    
    # Build
    print(f"{'='*60}")
    print(f"Building: {', '.join(tools_to_process)}")
    print(f"{'='*60}")
    build_tools(tools_to_process)

if __name__ == '__main__':
    main()
