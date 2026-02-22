# Instructions

## Setup
```bash
pip install -r requirements.txt
```

## Directory Structure
```
data/source_images/    # Put your source images here (any .jpg, .png, .jpeg)
data/target_images/    # Put your target image here
```

## Commands

### 1. Categorize Source Images


### 2. Extract Target Colors
```bash
python -m src.extract_target_colors
```
- Segments target image into grid
- Extracts average color per section
- Saves to `cache/target_grid.json`
- Creates visualization in `output/collages/`

### 3. Test Color Analysis
```bash
python test_color_analysis.py
```
- Tests color calculation on source images

### 4. Test All Components
```bash
python test_all.py
```
- Checks directory structure
- Verifies all imports work

## Configuration
Edit `config.yaml`:
```yaml
collage:
  grid_segments_x: 40  # Number of columns
  grid_segments_y: 30  # Number of rows
```

## Output Files
- `cache/source_images.json` - Source image color data
- `cache/target_grid.json` - Target grid color data
- `output/collages/target_grid_visualization.png` - Grid visualization

## [to be added] ... for matching images and 

## [to be added] ... for rendering final collage 

## [to be added] ... future CLI UI stuff?? 