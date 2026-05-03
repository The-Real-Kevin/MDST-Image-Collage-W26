# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Setup & Commands

```bash
pip install -r requirements.txt   # Install dependencies
python main.py                    # Run the full pipeline
python test_all.py                # Verify imports and directory structure
python test_color_analysis.py     # Test color calculation functions
```

Individual pipeline steps can be run standalone:
```bash
python src/categorize_images.py   # Process source images and test color matching
python src/segment_target.py      # Segment target image and create visualization
```

## Architecture

This is a photomosaic generator that replaces grid tiles of a target image with source images that have a similar average color. The pipeline has three stages:

**Stage 1 — Segment** (`src/segment_target.py`): Divides the target image into a grid (`grid_segments_x` × `grid_segments_y` from `config.yaml`). Each cell becomes an `ImageSegment` with its bounding box and average color. Remainder pixels (when image dimensions don't divide evenly) are absorbed by the last row/column.

**Stage 2 — Categorize** (`src/categorize_images.py`): Scans `data/source_images/`, computes the average RGB color of each image, and stores them in a `SourceImagePalette`. Results are cached to `cache/source_images.json` to avoid reprocessing on subsequent runs. The palette holds a pre-computed numpy color array for fast vectorized distance calculations.

**Stage 3 — Match & Render** (`src/color_matching.py`, `src/render_collage.py`): For each tile in the target grid, finds the closest-matching source image using either Euclidean distance (RGB space, fast) or Delta E (CIE LAB space, perceptually accurate). The matched source image is resized to the tile dimensions and pasted into the output mosaic.

**Orchestration** (`main.py`): Loads `config.yaml`, manages caching (loads palette from JSON if it exists, otherwise builds it), handles interactive target image selection when multiple targets exist, and saves the final output to `output/collages/`.

**Color utilities** (`src/color_analysis.py`): Average color calculation with an optimized variant that downsamples large images before averaging. Also in `utils/image_loader.py`: recursive image discovery, loading, and validation.

## Configuration

All tunable parameters live in `config.yaml`:
- `source_images.directory` — palette image source folder
- `target_images.directory` — target image folder
- `collage.grid_segments_x` / `grid_segments_y` — mosaic grid dimensions
- `collage.output_directory` — where the final PNG is saved
- `source_images.cache_file` — path for the palette JSON cache

## Notes

- The palette cache (`cache/source_images.json`) must be deleted manually if source images change, otherwise stale data will be used.
- `src/collage.py` is a legacy prototype; `src/extract_target_colors.py` is an alternative (less-used) segmentation approach. Neither is part of the main pipeline.
- Multiprocessing is wired into `config.yaml` but not yet implemented.
