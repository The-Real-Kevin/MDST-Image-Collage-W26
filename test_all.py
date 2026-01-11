"""Test all components"""
import os
import sys

print("="*60)
print("TESTING ALL COMPONENTS")
print("="*60)

# Check directories exist
dirs_to_check = [
    'data/source_images',
    'data/target_images',
    'cache',
    'output/collages'
]

print("\n1. Checking directories...")
for dir_path in dirs_to_check:
    if os.path.exists(dir_path):
        print(f"✓ {dir_path} exists")
    else:
        print(f"✗ {dir_path} missing - creating...")
        os.makedirs(dir_path, exist_ok=True)

# Check for images
print("\n2. Checking for images...")
source_images = [f for f in os.listdir('data/source_images') 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]
target_images = [f for f in os.listdir('data/target_images') 
                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))]

print(f"Source images: {len(source_images)} found")
if len(source_images) == 0:
    print("⚠️  WARNING: No source images found!")
    print("   Add some images to data/source_images/")

print(f"Target images: {len(target_images)} found")
if len(target_images) == 0:
    print("⚠️  WARNING: No target images found!")
    print("   Add an image to data/target_images/")

# Test imports
print("\n3. Testing imports...")
try:
    from src.color_analysis import calculate_average_color, color_to_hex
    print("✓ color_analysis.py imports successfully")
except Exception as e:
    print(f"✗ color_analysis.py import failed: {e}")

try:
    from src.categorize_source_images import categorize_all_images, SourceImagePalette
    print("✓ categorize_source_images.py imports successfully")
except Exception as e:
    print(f"✗ categorize_source_images.py import failed: {e}")

try:
    from src.extract_target_colors import extract_target_colors, TargetGrid
    print("✓ extract_target_colors.py imports successfully")
except Exception as e:
    print(f"✗ extract_target_colors.py import failed: {e}")

try:
    from utils.image_loader import load_image
    print("✓ image_loader.py imports successfully")
except Exception as e:
    print(f"✗ image_loader.py import failed: {e}")

print("\n" + "="*60)
print("SETUP CHECK COMPLETE")
print("="*60)

if len(source_images) > 0 and len(target_images) > 0:
    print("\n✓ Ready to test!")
    print("\nNext steps:")
    print("1. Run: python -m src.categorize_source_images")
    print("2. Run: python -m src.extract_target_colors")
else:
    print("\n⚠️  Add images before testing")