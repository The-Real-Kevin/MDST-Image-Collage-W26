
import os
import yaml
from PIL import Image
from typing import Dict, Any
import time

# Import our project modules
from src.categorize_images import (
    categorize_all_images, 
    load_palette, 
    save_palette,
    SourceImagePalette
)
from src.segment_target import segment_image, visualize_segments
from src.render_collage import render_collage


def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config.yaml file
        
    Returns:
        Dictionary containing configuration parameters
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def ensure_directories_exist(config: Dict[str, Any]) -> None:
    """
    Create necessary directories if they don't exist.
    
    Args:
        config: Configuration dictionary
    """
    directories = [
        config['source_images']['directory'],
        config['target_images']['directory'],
        config['collage']['output_directory'],
        os.path.dirname(config['source_images']['cache_file'])
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def load_or_build_palette(config: Dict[str, Any]) -> SourceImagePalette:
    """
    Load source image palette from cache or build it from scratch.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        SourceImagePalette containing all source images
    """
    cache_file = config['source_images']['cache_file']
    source_dir = config['source_images']['directory']
    supported_formats = config['source_images']['supported_formats']
    
    # Check if cache exists
    if os.path.exists(cache_file):
        print(f"✓ Found cached source images at: {cache_file}")
        try:
            palette = load_palette(cache_file)
            return palette
        except Exception as e:
            print(f"✗ Failed to load cache: {e}")
            print("  Building palette from scratch...")
    
    # Build palette from source images
    print(f"\nScanning source images directory: {source_dir}")
    palette = categorize_all_images(source_dir, supported_formats)
    
    if len(palette) == 0:
        raise ValueError(
            f"No source images found in {source_dir}!\n"
            f"Please add images to this directory."
        )
    
    # Save to cache for future use
    print(f"\nCaching palette for future use...")
    save_palette(palette, cache_file)
    
    return palette


def get_target_image_path(config: Dict[str, Any]) -> str:
    """
    Get the target image path from user or use first image in directory.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        Path to target image
    """
    target_dir = config['target_images']['directory']
    
    # List available target images
    target_files = [
        f for f in os.listdir(target_dir)
        if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
    ]
    
    if len(target_files) == 0:
        raise FileNotFoundError(
            f"No target images found in {target_dir}!\n"
            f"Please add an image to this directory."
        )
    
    # If only one image, use it automatically
    if len(target_files) == 1:
        target_path = os.path.join(target_dir, target_files[0])
        print(f"✓ Using target image: {target_files[0]}")
        return target_path
    
    # Multiple images - let user choose
    print(f"\nFound {len(target_files)} target images:")
    for i, filename in enumerate(target_files, 1):
        print(f"  {i}. {filename}")
    
    while True:
        try:
            choice = input(f"\nSelect image (1-{len(target_files)}) or press Enter for first: ").strip()
            if choice == "":
                idx = 0
            else:
                idx = int(choice) - 1
                if idx < 0 or idx >= len(target_files):
                    print(f"Please enter a number between 1 and {len(target_files)}")
                    continue
            
            target_path = os.path.join(target_dir, target_files[idx])
            print(f"✓ Selected: {target_files[idx]}")
            return target_path
        except ValueError:
            print("Invalid input. Please enter a number.")


def create_collage(target_image_path: str, palette: SourceImagePalette, 
                   config: Dict[str, Any]) -> Image.Image:
    """
    Create the final collage by matching target segments to source images.
    
    Args:
        target_image_path: Path to target image
        palette: SourceImagePalette with all source images
        config: Configuration dictionary
        
    Returns:
        PIL Image of the final collage
    """
    # Load target image
    print(f"\nLoading target image...")
    target_image = Image.open(target_image_path).convert("RGB")
    print(f"✓ Target image loaded: {target_image.size[0]}x{target_image.size[1]} pixels")
    
    # Get grid dimensions from config
    grid_x = config['collage']['grid_segments_x']
    grid_y = config['collage']['grid_segments_y']
    
    print(f"\nSegmenting image into {grid_x}x{grid_y} grid...")
    segments, metadata = segment_image(target_image, grid_x, grid_y)
    
    # Optional: Save segment visualization for debugging
    viz_path = os.path.join(config['collage']['output_directory'], 'segments_viz.png')
    print(f"\nSaving segment visualization to: {viz_path}")
    visualize_segments(segments, viz_path)
    
    # Calculate tile size (use base segment size from metadata)
    tile_size = min(
        metadata['base_segment_size']['width'],
        metadata['base_segment_size']['height']
    )
    
    # Render the collage
    print(f"\nRendering collage...")
    print(f"  Matching {metadata['total_segments']} segments to source images...")
    print(f"  This may take a moment...\n")
    
    collage = render_collage(
        target_image=target_image,
        palette=palette,
        tile_size=tile_size,
        method="euclidean"  # Can also use "delta_e" for perceptual matching
    )
    
    return collage


def save_collage(collage: Image.Image, target_image_path: str, 
                 config: Dict[str, Any]) -> str:
    """
    Save the final collage with a descriptive filename.
    
    Args:
        collage: PIL Image of the collage
        target_image_path: Original target image path
        config: Configuration dictionary
        
    Returns:
        Path to saved collage
    """
    # Create output filename
    target_name = os.path.splitext(os.path.basename(target_image_path))[0]
    grid_x = config['collage']['grid_segments_x']
    grid_y = config['collage']['grid_segments_y']
    
    output_filename = f"{target_name}_collage_{grid_x}x{grid_y}.png"
    output_path = os.path.join(config['collage']['output_directory'], output_filename)
    
    # Save the collage
    collage.save(output_path)
    print(f"✓ Collage saved to: {output_path}")
    
    return output_path


def print_banner():
    """Print a nice banner for the program."""
    print("\n" + "="*70)
    print(" "*20 + "IMAGE COLLAGE GENERATOR")
    print("="*70)


def print_summary(config: Dict[str, Any], palette_size: int, 
                  output_path: str, elapsed_time: float):
    """
    Print summary statistics after completion.
    
    Args:
        config: Configuration dictionary
        palette_size: Number of source images
        output_path: Path to saved collage
        elapsed_time: Time taken to create collage
    """
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Source images used: {palette_size}")
    print(f"Grid size: {config['collage']['grid_segments_x']}x{config['collage']['grid_segments_y']}")
    print(f"Total segments: {config['collage']['grid_segments_x'] * config['collage']['grid_segments_y']}")
    print(f"Output saved to: {output_path}")
    print(f"Time elapsed: {elapsed_time:.2f} seconds")
    print("="*70 + "\n")


def main():
    """
    Main driver function that orchestrates the entire collage creation process.
    """
    start_time = time.time()
    
    try:
        # Step 1: Print banner
        print_banner()
        
        # Step 2: Load configuration
        print("\n[Step 1/5] Loading configuration...")
        config = load_config()
        print("✓ Configuration loaded")
        
        # Step 3: Ensure directories exist
        print("\n[Step 2/5] Setting up directories...")
        ensure_directories_exist(config)
        print("✓ Directories ready")
        
        # Step 4: Load or build source image palette
        print("\n[Step 3/5] Processing source images...")
        palette = load_or_build_palette(config)
        print(f"✓ Source palette ready with {len(palette)} images")
        
        # Step 5: Get target image
        print("\n[Step 4/5] Selecting target image...")
        target_image_path = get_target_image_path(config)
        
        # Step 6: Create the collage
        print("\n[Step 5/5] Creating collage...")
        collage = create_collage(target_image_path, palette, config)
        
        # Step 7: Save the result
        print("\nSaving final collage...")
        output_path = save_collage(collage, target_image_path, config)
        
        # Calculate elapsed time
        elapsed_time = time.time() - start_time
        
        # Print summary
        print_summary(config, len(palette), output_path, elapsed_time)
        
        # Success!
        print("✓ SUCCESS! Your collage is ready.\n")
        
    except KeyboardInterrupt:
        print("\n\n✗ Process interrupted by user.")
        return 1
    
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())