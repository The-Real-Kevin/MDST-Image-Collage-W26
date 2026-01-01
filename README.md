# Image Collage — 9‑Week Project Timeline

This repository contains a 9-week plan to build an image-collage generator (mosaic-style) using Python image libraries and efficient matching algorithms.

## Table of Contents

- [Week 1: Project Kickoff & Foundation](#week-1-project-kickoff--foundation)
- [Week 2: Data Collection & Environment Setup](#week-2-data-collection--environment-setup)
- [Week 3: Image Categorization (Step 2)](#week-3-image-categorization-step-2)
- [Week 4: Target Image Segmentation (Step 1)](#week-4-target-image-segmentation-step-1)
- [Week 5: Color Matching Algorithm (Step 3 - Part 1)](#week-5-color-matching-algorithm-step-3---part-1)
- [Week 6: Collage Generation & Rendering](#week-6-collage-generation--rendering)
- [Week 7: Enhancement & Optimization](#week-7-enhancement--optimization)
- [Week 8: Testing & Documentation](#week-8-testing--documentation)
- [Week 9: Final Presentation Prep](#week-9-final-presentation-prep)

---

## Week 1: Project Kickoff & Foundation

### Meeting Goals

- Team introductions and role assignments
- Discuss project vision and technical approach
- Dataset identification and collection strategy
- Set up development environment and GitHub workflow

### Deliverables

- GitHub repo structure established
- Dataset sources identified (aim for 1000+ images)
- Communication channels set up (Discord/Slack)
- Next meeting scheduled

## Week 2: Data Collection & Environment Setup

### Tasks

- Collect and organize source images dataset
- Set up Python environment (`PIL`/`Pillow`, `NumPy`, `OpenCV`)
- Create basic image loading utilities
- Begin image preprocessing research

### Code Components

- `utils/image_loader.py` — Load and validate images
- `utils/config.py` — Configuration management
- `data/` — Directory structure for datasets

## Week 3: Image Categorization (Step 2)

### Tasks

- Implement average color calculation for source images
- Create image metadata extraction (dimensions, filepath)
- Build caching system for processed images (JSON output)
- Parallel processing research (optional: `multiprocessing`)

### Code Components

- `src/categorize_images.py` — Main categorization logic
- `src/color_analysis.py` — Color averaging algorithms
- `cache/source_images.json` — Cached results

## Week 4: Target Image Segmentation (Step 1)

### Tasks

- Implement grid-based image division
- Calculate average color per section
- Create configurable section size / aspect ratio
- Visualization of segmented target image

### Code Components

- `src/segment_target.py` — Image segmentation logic
- `src/visualize.py` — Debug visualization tools
- `tests/` — Unit tests for segmentation

## Week 5: Color Matching Algorithm (Step 3 - Part 1)

### Tasks

- Implement color distance metrics (Euclidean, Delta E)
- Create matching algorithm (nearest neighbor)
- Handle duplicate image usage strategy
- Performance optimization research

### Code Components

- `src/color_matching.py` — Color distance calculations
- `src/match_sections.py` — Section-to-image matching
- `output/collage_map.json` — Matching results

## Week 6: Collage Generation & Rendering

### Tasks

- Implement image placement and scaling
- Create final collage renderer
- Memory management for large outputs
- Add option to split into tiles for huge collages

### Code Components

- `src/render_collage.py` — Final image generation
- `src/tile_manager.py` — Handle large output splitting
- `examples/` — Sample outputs

## Week 7: Enhancement & Optimization

### Tasks

- Implement advanced features (image rotation, filters)
- Add command-line interface (`argparse` / `Click`)
- Optimize for speed (vectorization, caching)
- Consider parallel processing (`multiprocessing` / `joblib`)

### Code Components

- `main.py` — CLI entry point
- `src/enhancements.py` — Optional filters/effects
- Performance benchmarking

## Week 8: Testing & Documentation

### Tasks

- Comprehensive testing with various datasets
- Create documentation (README, docstrings)
- Example notebooks or usage guides
- Bug fixes and edge case handling

### Deliverables

- Complete `README.md` with usage examples
- `requirements.txt` and setup instructions
- Sample outputs in `examples/`

## Week 9: Final Presentation Prep

### Tasks

- Prepare presentation slides
- Create demo with impressive examples
- Performance metrics and analysis
- Future improvements discussion (Spark integration)

### Deliverables

- Presentation materials
- Final polished codebase
- Project report / writeup

---

repo structure below: 

image-collage-generator/
├── README.md
├── requirements.txt
├── main.py                      # CLI entry point
├── config.yaml                  # Configuration file
├── src/
│   ├── __init__.py
│   ├── categorize_images.py    # Step 2: Source image processing
│   ├── segment_target.py       # Step 1: Target image division
│   ├── color_analysis.py       # Color calculations
│   ├── color_matching.py       # Color distance metrics
│   ├── match_sections.py       # Step 3: Matching algorithm
│   ├── render_collage.py       # Final rendering
│   ├── tile_manager.py         # Large output handling
│   └── enhancements.py         # Optional features
├── utils/
│   ├── __init__.py
│   ├── image_loader.py         # Image I/O utilities
│   ├── config.py               # Config management
│   └── visualize.py            # Debug visualizations
├── data/
│   ├── source_images/          # Source image dataset
│   └── target_images/          # Target images to transform
├── cache/
│   └── source_images.json      # Cached categorization
├── output/
│   ├── collages/               # Final collages
│   └── collage_maps/           # Intermediate JSON outputs
├── tests/
│   ├── test_categorize.py
│   ├── test_segment.py
│   └── test_matching.py
├── examples/
│   └── sample_outputs/         # Demo results
└── notebooks/
    └── demo.ipynb              # Interactive demo