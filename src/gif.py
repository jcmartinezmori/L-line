import fitz
from PIL import Image
from pathlib import Path

# Configuration
gtfs = "gtfs_2025-08-31_2026-01-03"
kappa = 0.7
fig_name = "welton"
duration = 200  # milliseconds per frame

folder = Path("output/figures") / gtfs / fig_name
prefix = f"trip_durations_kappa_{kappa}_delta_"

# Find and sort PDFs by delta
files = sorted(
    folder.glob(f"{prefix}*.pdf"),
    key=lambda p: float(p.stem.removeprefix(prefix))
)

if not files:
    raise FileNotFoundError(f"No matching PDFs found in {folder}")

# Convert PDFs to images
frames = []

for file in files:
    with fitz.open(file) as doc:
        pix = doc[0].get_pixmap(
            matrix=fitz.Matrix(2, 2),
            alpha=False
        )
        img = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
        frames.append(img)

# Ensure consistent frame dimensions
size = frames[0].size
frames = [img.resize(size, Image.Resampling.LANCZOS) for img in frames]

# Save animated GIF
gif_path = folder / f"trip_durations_kappa_{kappa}.gif"

frames[0].save(
    gif_path,
    save_all=True,
    append_images=frames[1:],
    duration=duration,
    loop=0,
    optimize=True
)

print(f"Saved GIF: {gif_path}")

import subprocess

mp4_path = gif_path.with_suffix(".mp4")

subprocess.run(
    [
        "ffmpeg",
        "-y",
        "-i", str(gif_path),
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(mp4_path)
    ],
    check=True
)

print(f"Saved MP4: {mp4_path}")