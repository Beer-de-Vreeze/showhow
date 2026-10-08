#!/usr/bin/env python3
"""Pull frames from the rendered mp4 at given times and tile them into one labelled sheet.

The mp4 is the only proof: snapshots and plain Chrome can show highlights the
render dropped. Look at this sheet at every ring and result moment before delivery.

  uv run --project <skill-dir>/scripts <skill-dir>/scripts/frame_sheet.py video.mp4 \
      --at 16.5,21.5,24 -o work/check.jpg [--crop 0,200,960,540] [--cols 3]

--crop x,y,w,h (video pixels) zooms every frame on the same region, for judging small rings.
--overlays work/rings.overlays.json (written by bake_highlights.py) samples the middle of every
baked ring span instead of --at, so one sheet covers every ring in the video.
"""

from __future__ import annotations

import argparse
import io
import json
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

TILE_WIDTH = 640
LABEL_HEIGHT = 28


def grab(video: Path, t: float) -> Image.Image:
    result = subprocess.run(
        ["ffmpeg", "-v", "error", "-ss", f"{t}", "-i", str(video), "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "-"],
        capture_output=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout:
        raise SystemExit(f"ffmpeg could not read a frame at {t}s: {result.stderr.decode(errors='replace').strip()}")
    return Image.open(io.BytesIO(result.stdout)).convert("RGB")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video", type=Path)
    parser.add_argument("--at", help="comma-separated seconds")
    parser.add_argument("--overlays", type=Path, help="overlays JSON from bake_highlights.py")
    parser.add_argument("-o", "--out", type=Path, required=True)
    parser.add_argument("--crop", help="x,y,w,h in video pixels")
    parser.add_argument("--cols", type=int, default=3)
    args = parser.parse_args()

    labels = {}
    if args.overlays:
        for o in json.loads(args.overlays.read_text(encoding="utf-8")):
            labels[round((o["in"] + o["in_dur"] + o["out"]) / 2, 2)] = o["id"]
    times = sorted(labels) + [float(t) for t in (args.at or "").split(",") if t.strip()]
    if not times:
        raise SystemExit("give --at times or --overlays")
    crop = [int(v) for v in args.crop.split(",")] if args.crop else None
    if crop and len(crop) != 4:
        raise SystemExit("--crop needs x,y,w,h")
    font = ImageFont.load_default(size=20)

    tiles = []
    for t in times:
        frame = grab(args.video, t)
        if crop:
            x, y, w, h = crop
            frame = frame.crop((x, y, x + w, y + h))
        frame = frame.resize((TILE_WIDTH, round(frame.height * TILE_WIDTH / frame.width)))
        tile = Image.new("RGB", (frame.width, frame.height + LABEL_HEIGHT), "black")
        tile.paste(frame, (0, LABEL_HEIGHT))
        ImageDraw.Draw(tile).text((8, 3), f"{t:.2f}s {labels.get(t, '')}", fill="white", font=font)
        tiles.append(tile)

    cols = min(args.cols, len(tiles))
    rows = -(-len(tiles) // cols)
    tw, th = tiles[0].size
    sheet = Image.new("RGB", (cols * tw, rows * th), "black")
    for i, tile in enumerate(tiles):
        sheet.paste(tile, ((i % cols) * tw, (i // cols) * th))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(args.out, quality=90)
    print(f"wrote {args.out} ({len(tiles)} frames)")


if __name__ == "__main__":
    sys.exit(main())
