# Functions needed:
#- load_source_images(directory)
#- calculate_average_color(image)
#- extract_metadata(image, filepath)
# - categorize_batch(image_list)
# - save_to_cache(data, filepath)
# - load_from_cache(filepath)


"""
Categorize source images by calculating their average colors.
This creates a palette that can be reused for multiple collages.
"""
import json
import os
from typing import List, Dict, Any
from PIL import Image
from tqdm import tqdm
import yaml

from utils.image_loader import get_image_files, load_image, get_image_dimensions
from src.color_analysis import calculate_average_color_optimized, color_to_hex


def categorize_single_image(filepath: str) -> Dict[str, Any]:
    """
    Categorize a single image by calculating its metadata.
    
    Args:
        filepath: Path to the image file
    
    Returns:
        Dictionary containing image metadata
    """
    try:
        # Load image
        image = load_image(filepath)
        
        # Get dimensions
        width, height = get_image_dimensions(image)
        
        # Calculate average color
        avg_color = calculate_average_color_optimized(image)
        
        # Create metadata dictionary
        metadata = {
            'filepath': filepath,
            'filename': os.path.basename(filepath),
            'width': width,
            'height': height,
            'avg_color_rgb': avg_color,
            'avg_color_hex': color_to_hex(avg_color)
        }
        
        return metadata
    
    except Exception as e:
        print(f"Error processing {filepath}: {str(e)}")
        return None


def categorize_images(image_directory: str, supported_formats: List[str]) -> List[Dict[str, Any]]:
    """
    Categorize all images in a directory.
    
    Args:
        image_directory: Path to directory containing source images
        supported_formats: List of supported file extensions
    
    Returns:
        List of image metadata dictionaries
    """
    print(f"Scanning directory: {image_directory}")
    
    # Get all image files
    image_files = get_image_files(image_directory, supported_formats)
    print(f"Found {len(image_files)} images")
    
    if len(image_files) == 0:
        print("Warning: No images found!")
        return []
    
    # Process each image with progress bar
    categorized_images = []
    print("Categorizing images...")
    
    for filepath in tqdm(image_files, desc="Processing images"):
        metadata = categorize_single_image(filepath)
        if metadata:
            categorized_images.append(metadata)
    
    print(f"Successfully categorized {len(categorized_images)} images")
    return categorized_images


def save_categorized_data(data: List[Dict[str, Any]], output_filepath: str) -> None:
    """
    Save categorized image data to JSON file.
    
    Args:
        data: List of image metadata dictionaries
        output_filepath: Path to save JSON file
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(output_filepath), exist_ok=True)
    
    # Save to JSON with pretty formatting
    with open(output_filepath, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved categorized data to: {output_filepath}")


def load_categorized_data(filepath: str) -> List[Dict[str, Any]]:
    """
    Load categorized image data from JSON file.
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        List of image metadata dictionaries
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Cache file not found: {filepath}")
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    print(f"Loaded {len(data)} categorized images from cache")
    return data


def main():
    """
    Main function to categorize source images.
    """
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    source_config = config['source_images']
    
    # Categorize images
    categorized_data = categorize_images(
        image_directory=source_config['directory'],
        supported_formats=source_config['supported_formats']
    )
    
    # Save to cache
    save_categorized_data(categorized_data, source_config['cache_file'])
    
    # Print some statistics
    if categorized_data:
        print("\n=== Statistics ===")
        print(f"Total images: {len(categorized_data)}")
        print(f"\nFirst 3 samples:")
        for i, img_data in enumerate(categorized_data[:3], 1):
            print(f"{i}. {img_data['filename']}")
            print(f"   Dimensions: {img_data['width']}x{img_data['height']}")
            print(f"   Average color: RGB{img_data['avg_color_rgb']} ({img_data['avg_color_hex']})")


if __name__ == "__main__":
    main()