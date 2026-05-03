"""
Streamlit web app for the Image Collage Generator.
Allows users to upload a target image and source images, tune parameters,
and generate a photomosaic collage in the browser.
"""

import io
import hashlib
import os
import tempfile
import time
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image

from src.categorize_images import SourceImagePalette, categorize_single_image

# ---------------------------------------------------------------------------
# Page config — must be first Streamlit call
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Image Collage Generator",
    page_icon="🎨",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Session state initialisation
# ---------------------------------------------------------------------------
for key, default in [
    ("palette", None),
    ("palette_key", None),      # hash of source files to detect changes
    ("palette_tmpdir", None),   # temp dir holding source files for rendering
    ("collage", None),
    ("target_image", None),
    ("processing_time", None),
    ("usage_stats", None),
]:
    if key not in st.session_state:
        st.session_state[key] = default


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _files_hash(uploaded_files) -> str:
    """Compute a deterministic hash over a list of UploadedFile objects."""
    h = hashlib.md5()
    for f in sorted(uploaded_files, key=lambda x: x.name):
        h.update(f.name.encode())
        h.update(str(f.size).encode())
    return h.hexdigest()


def build_palette(uploaded_files, status_placeholder):
    """
    Save uploaded files to a temp directory and build a SourceImagePalette.

    The temp directory is kept alive so render_collage can open the files
    later via SourceImage.filepath.  The caller is responsible for cleaning
    up the previous tmpdir before calling this function.

    Returns (SourceImagePalette, tmpdir_path).
    """
    import shutil

    palette = SourceImagePalette()
    tmpdir = tempfile.mkdtemp(prefix="collage_sources_")
    failed = []

    for i, f in enumerate(uploaded_files):
        status_placeholder.info(
            f"⚙️ Processing source image {i + 1}/{len(uploaded_files)}: **{f.name}**"
        )
        tmp_path = os.path.join(tmpdir, f.name)
        with open(tmp_path, "wb") as fh:
            fh.write(f.getbuffer())
        try:
            src_img = categorize_single_image(tmp_path)
            palette.add_image(src_img)
        except Exception as e:
            failed.append((f.name, str(e)))
            # Remove the file we just wrote if it couldn't be processed
            try:
                os.remove(tmp_path)
            except OSError:
                pass

    if failed:
        st.warning(
            f"⚠️ {len(failed)} source image(s) could not be processed: "
            + ", ".join(name for name, _ in failed)
        )

    return palette, tmpdir


def render_collage(
    target: Image.Image,
    palette: SourceImagePalette,
    num_cols: int,
    num_rows: int,
    progress_bar,
    max_uses_per_image: int = None,
    diversity_strength: float = 0.0,
    neighbor_radius: int = 3,
) -> tuple:
    """
    Render the photomosaic.

    Returns (mosaic, usage_stats) where usage_stats is a dict with
    'unique_used' and 'max_uses' keys.

    diversity_strength: penalty added per neighbour tile that already uses the
    same source image, scaled by 1/manhattan_distance. 0 = disabled.
    """
    width, height = target.size

    tile_w = width // num_cols
    tile_h = height // num_rows

    if tile_w == 0 or tile_h == 0:
        raise ValueError(
            f"Grid {num_cols}×{num_rows} is too fine for a "
            f"{width}×{height} image. Reduce grid size."
        )

    # Crop to a clean multiple of tile dimensions
    cropped_w = tile_w * num_cols
    cropped_h = tile_h * num_rows
    target = target.crop((0, 0, cropped_w, cropped_h))

    mosaic = Image.new("RGB", (cropped_w, cropped_h))
    total_tiles = num_cols * num_rows
    done = 0

    colors = palette.get_color_array().astype(np.float32)
    usage_counts = np.zeros(len(palette.images), dtype=np.int32)
    placed = np.full((num_rows, num_cols), -1, dtype=np.int32)

    for row in range(num_rows):
        for col in range(num_cols):
            x = col * tile_w
            y = row * tile_h

            tile = target.crop((x, y, x + tile_w, y + tile_h))
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
            usage_counts[best_idx] += 1
            best = palette.images[best_idx]

            src = Image.open(best.filepath).convert("RGB")
            src = src.resize((tile_w, tile_h), Image.Resampling.LANCZOS)
            mosaic.paste(src, (x, y))

            done += 1
            progress_bar.progress(done / total_tiles)

    usage_stats = {
        "unique_used": int((usage_counts > 0).sum()),
        "max_uses": int(usage_counts.max()),
    }
    return mosaic, usage_stats


def pil_to_bytes(image: Image.Image, fmt: str = "PNG") -> bytes:
    """Encode a PIL Image to bytes for download."""
    buf = io.BytesIO()
    image.save(buf, format=fmt)
    return buf.getvalue()


def show_image_previews(uploaded_files, max_cols: int = 8):
    """Display thumbnail previews for a list of UploadedFile objects."""
    cols = st.columns(min(len(uploaded_files), max_cols))
    for i, f in enumerate(uploaded_files):
        with cols[i % max_cols]:
            img = Image.open(f)
            img.thumbnail((120, 120))
            st.image(img, caption=f.name, use_container_width=False)


# ---------------------------------------------------------------------------
# App layout
# ---------------------------------------------------------------------------

st.title("🎨 Image Collage Generator")
st.markdown(
    """
    Turn any photo into a **photomosaic** — a collage built entirely from your
    own source images, each chosen by colour similarity.

    **How to use:**
    1. Upload a **target image** (the photo you want to recreate).
    2. Upload **source images** (the "tiles" — more variety = better results).
    3. Adjust the grid and matching settings in the sidebar.
    4. Click **Generate Collage** and download your result.
    """
)

st.divider()

# ---------------------------------------------------------------------------
# Sidebar — parameters
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    grid_cols = st.slider("Grid columns", min_value=10, max_value=100, value=40, step=1,
                          help="Number of tile columns across the output image.")
    grid_rows = st.slider("Grid rows",    min_value=10, max_value=100, value=30, step=1,
                          help="Number of tile rows down the output image.")

    with st.expander("Advanced settings"):
        match_method = st.selectbox(
            "Colour matching method",
            options=["Euclidean (faster)", "Delta E (perceptual)"],
            index=0,
            help=(
                "**Euclidean** computes distance in RGB space — fast and usually good.\n\n"
                "**Delta E** uses perceptual CIE LAB space — slower but more accurate."
            ),
        )

        max_uses_input = st.number_input(
            "Max reuses per image",
            min_value=0,
            max_value=500,
            value=3,
            step=1,
            help=(
                "Maximum number of times a single source image can appear in the collage. "
                "Set to **0** for no limit. "
                "Lower values force more variety but may degrade colour accuracy."
            ),
        )
        max_uses_per_image = int(max_uses_input) if max_uses_input > 0 else None

        diversity_strength = st.slider(
            "Diversity / spatial spread",
            min_value=0,
            max_value=150,
            value=50,
            step=5,
            help=(
                "Adds a penalty when the same source image appears in nearby tiles, "
                "pushing the collage to spread images more evenly across the canvas. "
                "**0** = pure colour accuracy. **50** = balanced. **150** = maximum spread "
                "(colour match quality will degrade)."
            ),
        )

        neighbor_radius = st.slider(
            "Neighbour radius",
            min_value=1,
            max_value=8,
            value=3,
            step=1,
            help=(
                "How many tiles away to look when computing the spatial penalty. "
                "Larger radius prevents the same image appearing in a wider area."
            ),
        )

    st.divider()
    st.markdown("**Minimum recommended sources:** 20+  \nMore unique colours → better collage.")

# ---------------------------------------------------------------------------
# Main columns — uploaders
# ---------------------------------------------------------------------------
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🖼️ Target image")
    target_file = st.file_uploader(
        "Upload the photo to recreate",
        type=["jpg", "jpeg", "png", "webp"],
        key="target_uploader",
    )

    if target_file:
        target_pil = Image.open(target_file).convert("RGB")
        st.session_state.target_image = target_pil
        st.image(target_pil, caption=f"{target_file.name}  ({target_pil.size[0]}×{target_pil.size[1]}px)", use_container_width=True)

with col_right:
    st.subheader("🗂️ Source images (tiles)")
    source_files = st.file_uploader(
        "Upload the images that will become tiles",
        type=["jpg", "jpeg", "png", "webp"],
        accept_multiple_files=True,
        key="source_uploader",
    )

    if source_files:
        st.caption(f"{len(source_files)} image(s) uploaded")
        show_image_previews(source_files, max_cols=8)

st.divider()

# ---------------------------------------------------------------------------
# Validation & Generate button
# ---------------------------------------------------------------------------
ready = bool(target_file and source_files)

if not target_file:
    st.info("ℹ️ Upload a target image to get started.")
elif not source_files:
    st.info("ℹ️ Upload at least one source image.")
elif len(source_files) < 5:
    st.warning("⚠️ Fewer than 5 source images will produce a low-quality collage. Upload more for better results.")

generate_clicked = st.button(
    "✨ Generate Collage",
    type="primary",
    disabled=not ready,
    use_container_width=True,
)

# ---------------------------------------------------------------------------
# Generation pipeline
# ---------------------------------------------------------------------------
if generate_clicked and ready:
    status = st.empty()
    start_time = time.time()

    try:
        # --- Step 1: Build / reuse palette ---
        current_key = _files_hash(source_files)
        if st.session_state.palette_key != current_key:
            # Clean up the previous temp directory before creating a new one
            if st.session_state.palette_tmpdir:
                import shutil
                shutil.rmtree(st.session_state.palette_tmpdir, ignore_errors=True)
                st.session_state.palette_tmpdir = None

            status.info("🔍 Processing source images…")
            with st.spinner("Building colour palette from source images…"):
                palette, tmpdir = build_palette(source_files, status)

            if len(palette) == 0:
                import shutil
                shutil.rmtree(tmpdir, ignore_errors=True)
                st.error("❌ No source images could be processed. Check that your files are valid images.")
                st.stop()

            st.session_state.palette = palette
            st.session_state.palette_key = current_key
            st.session_state.palette_tmpdir = tmpdir  # keep files alive for rendering
        else:
            palette = st.session_state.palette
            st.info(f"♻️ Reusing palette from previous run ({len(palette)} images).")

        # --- Step 2: Render ---
        status.info("🎨 Matching colours and rendering mosaic…")
        progress_bar = st.progress(0)

        target_pil = st.session_state.target_image
        if target_pil is None:
            st.error("❌ Target image not found in session. Please re-upload the target image and try again.")
            st.stop()

        collage, usage_stats = render_collage(
            target_pil, palette, grid_cols, grid_rows, progress_bar,
            max_uses_per_image=max_uses_per_image,
            diversity_strength=float(diversity_strength),
            neighbor_radius=neighbor_radius,
        )

        elapsed = time.time() - start_time
        st.session_state.collage = collage
        st.session_state.processing_time = elapsed
        st.session_state.usage_stats = usage_stats

        progress_bar.empty()
        status.success(f"✅ Collage generated in {elapsed:.1f}s!")

    except ValueError as e:
        st.error(f"❌ Configuration error: {e}")
        import traceback
        st.code(traceback.format_exc())
        st.stop()
    except Exception as e:
        st.error(f"❌ Unexpected error during generation: {e}")
        import traceback
        st.code(traceback.format_exc())
        st.stop()

# ---------------------------------------------------------------------------
# Results display
# ---------------------------------------------------------------------------
if st.session_state.collage is not None:
    st.divider()
    st.subheader("🖼️ Result")

    # Stats row
    c1, c2, c3, c4, c5 = st.columns(5)
    palette = st.session_state.palette
    collage = st.session_state.collage
    target_pil = st.session_state.target_image
    usage_stats = st.session_state.usage_stats

    c1.metric("Source images", len(palette) if palette else "—")
    c2.metric("Grid size", f"{grid_cols} × {grid_rows}")
    c3.metric("Output size", f"{collage.size[0]}×{collage.size[1]}px")
    c4.metric(
        "Unique images used",
        f"{usage_stats['unique_used']}/{len(palette)}" if usage_stats else "—",
        help="How many distinct source images appeared in the collage.",
    )
    c5.metric("Processing time", f"{st.session_state.processing_time:.1f}s" if st.session_state.processing_time else "—")

    # Side-by-side comparison
    tab_collage, tab_compare, tab_original = st.tabs(["Collage", "Side-by-side comparison", "Original"])

    with tab_collage:
        st.image(collage, caption="Generated photomosaic", use_container_width=True)

    with tab_compare:
        l, r = st.columns(2)
        with l:
            st.image(target_pil, caption="Original target", use_container_width=True)
        with r:
            st.image(collage, caption="Photomosaic collage", use_container_width=True)

    with tab_original:
        st.image(target_pil, caption="Original target image", use_container_width=True)

    # Download button
    st.download_button(
        label="⬇️ Download collage (PNG)",
        data=pil_to_bytes(collage, "PNG"),
        file_name="photomosaic_collage.png",
        mime="image/png",
        use_container_width=True,
        type="primary",
    )
