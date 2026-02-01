# Functions needed:
- create_canvas(dimensions)
- place_image(canvas, image, position, size)
- render_collage(collage_map, source_images)
- save_output(image, filepath)
- split_into_tiles(large_collage, tile_size)

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
