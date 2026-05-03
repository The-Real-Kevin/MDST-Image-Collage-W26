# Functions needed:
import numpy as np
from PIL import Image
from typing import Tuple, List
from src.color_matching import find_best_match
from PIL import Image
import numpy as np
from src.categorize_images import SourceImage, SourceImagePalette, categorize_all_images



def render_collage(target_image: Image.Image,
                   palette: SourceImagePalette,
                   tile_size: int = 40,
                   method: str = "euclidean",
                   max_uses_per_image: int = None,
                   diversity_strength: float = 0.0,
                   neighbor_radius: int = 3) -> Image.Image:
    """
    diversity_strength: penalty added per neighbor tile that already uses the same
    source image, scaled by 1/manhattan_distance. Set to 0 to disable.
    neighbor_radius: how many tiles away to look when computing the penalty.
    """
    if len(palette) == 0:
        raise ValueError("Palette is empty")

    width, height = target_image.size

    # Crop to clean tile grid
    num_cols = width // tile_size
    num_rows = height // tile_size
    width = num_cols * tile_size
    height = num_rows * tile_size
    target_image = target_image.crop((0, 0, width, height))

    mosaic = Image.new("RGB", (width, height))

    colors = palette.get_color_array().astype(np.float32)
    usage_counts = np.zeros(len(palette.images), dtype=np.int32)
    # Tracks which palette index was placed at each (row, col); -1 = not yet placed
    placed = np.full((num_rows, num_cols), -1, dtype=np.int32)

    for row in range(num_rows):
        for col in range(num_cols):
            x = col * tile_size
            y = row * tile_size

            tile = target_image.crop((x, y, x + tile_size, y + tile_size))
            target_color = np.array(tile).mean(axis=(0, 1)).astype(np.float32)

            distances = np.linalg.norm(colors - target_color, axis=1)

            # Spatial repulsion: penalise images already placed in nearby tiles
            if diversity_strength > 0:
                penalty = np.zeros(len(palette.images), dtype=np.float32)
                r_lo = max(0, row - neighbor_radius)
                r_hi = min(num_rows, row + neighbor_radius + 1)
                c_lo = max(0, col - neighbor_radius)
                c_hi = min(num_cols, col + neighbor_radius + 1)
                for nr in range(r_lo, r_hi):
                    for nc in range(c_lo, c_hi):
                        idx = placed[nr, nc]
                        if idx >= 0:
                            manhattan = abs(nr - row) + abs(nc - col)
                            penalty[idx] += diversity_strength / manhattan
                distances = distances + penalty

            if max_uses_per_image is not None:
                available = usage_counts < max_uses_per_image
                if available.any():
                    distances = np.where(available, distances, np.inf)

            best_idx = int(np.argmin(distances))
            placed[row, col] = best_idx
            best_match = palette.images[best_idx]
            usage_counts[best_idx] += 1

            source_img = Image.open(best_match.filepath).convert("RGB")
            source_img = source_img.resize(
                (tile_size, tile_size),
                Image.Resampling.LANCZOS
            )

            mosaic.paste(source_img, (x, y))

    used_count = int((usage_counts > 0).sum())
    print(f"  Source images used: {used_count}/{len(palette.images)}")
    print(f"  Max uses by any single image: {int(usage_counts.max())}")

    return mosaic

if __name__ == "__main__":
    palette = categorize_all_images(
        image_directory="data/source_images",
        supported_formats=[".jpg", ".jpeg", ".png"]
    )
    print("Loaded images:", len(palette))
    target_image = Image.open("data/target_images/example.jpg").convert("RGB")
    collage = render_collage(target_image, palette, tile_size=40)
    collage.save("collage.jpg")


