"""Quick test for color_analysis.py"""
import os
from src.color_analysis import calculate_average_color, color_to_hex
from utils.image_loader import load_image

print("Testing color_analysis.py")
print("="*50)

# Find any image in the source_images directory
source_dir = "data/source_images"

# Get all image files (PNG, JPG, JPEG)
image_files = [f for f in os.listdir(source_dir) 
               if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp'))]

if len(image_files) == 0:
    print(f"✗ No images found in {source_dir}")
    print(f"  Please add some .png, .jpg, or .jpeg files to {source_dir}/")
    exit(1)

# Use the first image found
test_image_name = image_files[0]
test_image_path = os.path.join(source_dir, test_image_name)

print(f"Found {len(image_files)} images in {source_dir}")
print(f"Testing with: {test_image_name}\n")

try:
    image = load_image(test_image_path)
    print(f"✓ Loaded image: {image.size[0]}x{image.size[1]} pixels")
    
    avg_color = calculate_average_color(image)
    hex_color = color_to_hex(avg_color)
    
    print(f"✓ Average color: RGB{avg_color}")
    print(f"✓ Hex color: {hex_color}")
    
    print("\n" + "="*50)
    print("✓ color_analysis.py is working!")
    print("="*50)
    
    # Test multiple images if available
    if len(image_files) > 1:
        print(f"\nTesting {min(3, len(image_files))} more images:")
        for img_file in image_files[1:4]:
            img_path = os.path.join(source_dir, img_file)
            img = load_image(img_path)
            color = calculate_average_color(img)
            print(f"  {img_file}: RGB{color} ({color_to_hex(color)})")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()