#!/usr/bin/env python3
"""
Deploy script to sync files from root to webapp folder before AWS deployment
"""
import shutil
import os

print("🚀 Syncing files to webapp folder...")

# Files to copy
files_to_copy = [
    'complete_social_media_agent.py',
    'app_config.py',
    'cache_utils.py',
    'http_utils.py',
    'utils.py',
    'scawthorpe_teams.json'
]

# Copy individual files
for file in files_to_copy:
    src = file
    dst = os.path.join('webapp', file)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"   ✅ Copied {file}")
    else:
        print(f"   ⚠️  Warning: {file} not found")

# Copy directories
for dir_name in ['assets', 'config']:
    src_dir = dir_name
    dst_dir = os.path.join('webapp', dir_name)
    if os.path.exists(src_dir):
        if os.path.exists(dst_dir):
            shutil.rmtree(dst_dir)
        shutil.copytree(src_dir, dst_dir)
        print(f"   ✅ Copied {dir_name}/")
    else:
        print(f"   ⚠️  Warning: {dir_name}/ not found")

print("\n✅ Sync complete! Ready to deploy with: eb deploy")
print("   Run from webapp folder: cd webapp && eb deploy")
