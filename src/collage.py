import os
from PIL import Image
import numpy as np

# ----------------------------
# CONFIG
# ----------------------------

TARGET_IMAGE_PATH = "data/target_images/example.jpg"       # Your target image
SAMPLE_FOLDER = "data/source_images"             # Folder with 16 sample images
OUTPUT_IMAGE_PATH = "mosaic_result.png"

ROWS, COLS = 40, 40  # grid size of mosaic

# Optional RGB weights (perceptual)
WEIGHTS = np.array([0.3, 0.59, 0.11], dtype=np.float32)

# ----------------------------
# Load sample images and compute average colors
# ----------------------------

sample_files = [os.path.join(SAMPLE_FOLDER, f) 
                for f in os.listdir(SAMPLE_FOLDER) 
                if f.lower().endswith((".png", ".jpg", ".jpeg"))]

if len(sample_files) == 0:
    raise ValueError(f"No images found in folder: {SAMPLE_FOLDER}")

sample_data = []
for f in sample_files:
    img = Image.open(f).convert("RGB")
    avg_color = np.array(img).mean(axis=(0, 1))
    sample_data.append({
        "file": f,
        "avg_color_rgb": avg_color
    })

print(f"Loaded {len(sample_data)} sample images.")

# ----------------------------
# Load target image
# ----------------------------

target_img = Image.open(TARGET_IMAGE_PATH).convert("RGB")
target_width, target_height = target_img.size
segment_width = target_width // COLS
segment_height = target_height // ROWS

print(f"Target image size: {target_width}x{target_height}")
print(f"Each segment size: {segment_width}x{segment_height}")

# ----------------------------
# Function to find closest sample
# ----------------------------

def closest_sample(segment_avg):
    distances = []
    for sample in sample_data:
        diff = np.array(sample["avg_color_rgb"]) - segment_avg
        dist = np.sum(WEIGHTS * diff * diff)
        distances.append(dist)
    idx = np.argmin(distances)
    return sample_data[idx]["file"]

# ----------------------------
# Build mosaic
# ----------------------------

mosaic = Image.new("RGB", target_img.size)

for row in range(ROWS):
    for col in range(COLS):
        left = col * segment_width
        top = row * segment_height
        right = left + segment_width
        bottom = top + segment_height

        # Crop segment from target image
        segment = target_img.crop((left, top, right, bottom))
        avg_color = np.array(segment).mean(axis=(0, 1))

        # Find best matching sample image
        best_match_file = closest_sample(avg_color)

        # Open and resize sample image to fit segment
        sample_img = Image.open(best_match_file).convert("RGB")
        sample_resized = sample_img.resize((segment_width, segment_height), Image.BILINEAR)

        # Paste into mosaic
        mosaic.paste(sample_resized, (left, top))

# ----------------------------
# Save and show
# ----------------------------

mosaic.save(OUTPUT_IMAGE_PATH)
mosaic.show()
print(f"Mosaic saved → {OUTPUT_IMAGE_PATH}")

