#!/usr/bin/env python3
"""Draw highlight rings into copies of screenshot stills.

Hyperframes can drop DOM ring overlays from the rendered mp4 while snapshots
and plain Chrome show them, so /showhow bakes rings into the stills and swaps
images on the timeline instead (see references/step-3-compose.md).

Spec (JSON, paths relative to the spec file):
{
  "scale": 2,            # image pixels per box unit (2 for 2x captures of 1920-wide CSS boxes)
  "pad": 6,              # space between the target box and the ring, in box units
  "color": "#0078d4",    # optional, ring color
  "stills": [
    {"src": "screens/board.png", "out": "screens/board+backlog.png",
     "rings": [{"x": 16, "y": 216, "w": 368, "h": 844}]}
  ]
}
Each ring may override "pad", and may set "zoom": the on-screen scale the still is shown at
during that ring (camera zoom times any base scale), so the stroke looks the same at any zoom.

Timeline mode (preferred): give the rings with their times instead of "stills", and the script
cuts the spans itself, so no video re-implements the rounding and clamping rules:
{
  "scale": 2, "pad": 6,
  "screens": "screens/{name}.png",   # optional, clean still per screen name
  "out": "rings/{id}.png",           # optional, where ringed copies go
  "shows": [{"t": 11.8, "name": "menu", "fade": 0.12}],   # when each screen comes up
  "rings": [{"t": 16.7, "d": 2.4, "screen": "board", "x": 16, "y": 216, "w": 368, "h": 844, "zoom": 1.12}]
}
It writes one still per span of identical active rings and <spec>.overlays.json next to the spec:
[{"id", "src", "in", "in_dur", "out", "out_dur"}] in seconds. Fade each "#img-<id>" in at "in" and
out at "out". A ring still up when its screen is replaced ends with that cut. Times are compared in
whole centiseconds, ids are checked as CSS-safe, and a ring that lands in no span is an error. Run:
  uv run --project <skill-dir>/scripts <skill-dir>/scripts/bake_highlights.py work/rings.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageFilter

# Ring look in box units, matching the CSS ring in step-3-compose.md:
# border 3px, a 4px 18% spread, a 24px 35% glow, radius 9px.
BORDER = 3
SPREAD = 4
SPREAD_ALPHA = 0.18
GLOW = 24
GLOW_ALPHA = 0.35
RADIUS = 9

# Overlay fades in seconds: in, out, and the quick swap between two spans that touch.
RING_IN = 0.25
RING_OUT = 0.2
RING_SWAP = 0.12
CSS_ID = re.compile(r"^[A-Za-z0-9_-]+$")  # used as the suffix of "#img-<id>"


def cs(seconds: float) -> int:
    return round(float(seconds) * 100)


def plan(spec: dict) -> tuple[list[dict], list[dict]]:
    """Cut a ring timeline into baked stills. Returns (stills, overlays); times in centiseconds inside."""
    shows = sorted(({"t": cs(s["t"]), "name": s["name"], "fade": s.get("fade")} for s in spec["shows"]), key=lambda s: s["t"])
    screens = spec.get("screens", "screens/{name}.png")
    out = spec.get("out", "rings/{id}.png")
    rings = []
    for r in spec["rings"]:
        t = cs(r["t"])
        ring = {**r, "t": t, "end": t + cs(r["d"]), "out": None}
        on = [s for s in shows if s["t"] <= t]
        if not on or on[-1]["name"] != r["screen"]:
            raise SystemExit(f"ring at {r['t']}s is on {r['screen']} but {on[-1]['name'] if on else 'nothing'} shows then")
        nxt = next((s for s in shows if s["t"] > t), None)
        if nxt and nxt["t"] < ring["end"] + cs(RING_OUT):
            ring["end"], ring["out"] = nxt["t"], nxt["fade"]
        if ring["end"] <= t:
            raise SystemExit(f"ring at {r['t']}s on {r['screen']} has no time before its screen is replaced")
        rings.append(ring)

    stills, overlays = [], []
    for name in dict.fromkeys(r["screen"] for r in rings):
        mine = [r for r in rings if r["screen"] == name]
        cuts = sorted({c for r in mine for c in (r["t"], r["end"])})
        segs = []
        for a, b in zip(cuts, cuts[1:]):
            active = [r for r in mine if r["t"] <= a and r["end"] >= b]
            if active:
                segs.append((a, b, active))
        shown = {id(r) for _, _, active in segs for r in active}
        lost = [r["t"] / 100 for r in mine if id(r) not in shown]
        if lost:
            raise SystemExit(f"rings never shown on {name}: {lost}")
        for i, (a, b, active) in enumerate(segs):
            oid = f"{name}-r{len(overlays)}"
            if not CSS_ID.match(oid):
                raise SystemExit(f"overlay id {oid!r} is not CSS-safe; rename screen {name!r} (letters, digits, - and _ only)")
            src = out.format(id=oid)
            stills.append({
                "src": screens.format(name=name), "out": src,
                "rings": [{k: r[k] for k in ("x", "y", "w", "h", "pad", "zoom") if k in r} for r in active],
            })
            joined_before = i > 0 and segs[i - 1][1] == a
            joined_after = i + 1 < len(segs) and segs[i + 1][0] == b
            ender = next((r for r in active if r["end"] == b), None)
            overlays.append({
                "id": oid, "src": src,
                "in": a / 100, "in_dur": RING_SWAP if joined_before else RING_IN,
                "out": (b + cs(RING_SWAP)) / 100 if joined_after else b / 100,
                "out_dur": 0.01 if joined_after else (ender and ender["out"]) or RING_OUT,
            })
    return stills, overlays


def ring_layer(size: tuple[int, int], rect: list[float], s: float, rgb: tuple[int, int, int]) -> Image.Image:
    """s: image pixels per on-screen pixel of ring stroke."""
    x0, y0, x1, y1 = rect
    glow = Image.new("RGBA", size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle(
        rect, radius=RADIUS * s, outline=(*rgb, int(255 * GLOW_ALPHA)), width=round(BORDER * 2 * s)
    )
    layer = glow.filter(ImageFilter.GaussianBlur(GLOW * s / 3))
    draw = ImageDraw.Draw(layer)
    draw.rounded_rectangle(
        [x0 - SPREAD * s, y0 - SPREAD * s, x1 + SPREAD * s, y1 + SPREAD * s],
        radius=(RADIUS + SPREAD) * s,
        outline=(*rgb, int(255 * SPREAD_ALPHA)),
        width=round(SPREAD * s),
    )
    draw.rounded_rectangle(rect, radius=RADIUS * s, outline=(*rgb, 255), width=max(1, round(BORDER * s)))
    return layer


def bake(spec_path: Path) -> list[Path]:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    base = spec_path.parent
    scale = float(spec.get("scale", 1))
    default_pad = float(spec.get("pad", 6))
    rgb = ImageColor.getrgb(spec.get("color", "#0078d4"))[:3]
    stills = spec.get("stills")
    if "rings" in spec:
        stills, overlays = plan(spec)
        out_path = spec_path.with_suffix(".overlays.json")
        out_path.write_text(json.dumps(overlays, indent=1), encoding="utf-8")
        print(f"wrote {out_path} ({len(overlays)} overlays)")
    written = []
    for still in stills:
        src = (base / still["src"]).resolve()
        out = (base / still["out"]).resolve()
        if src == out:
            raise SystemExit(f"{still['out']}: out must differ from src, never overwrite the clean still")
        if not still.get("rings"):
            raise SystemExit(f"{still['out']}: no rings")
        img = Image.open(src).convert("RGBA")
        for ring in still["rings"]:
            pad = float(ring.get("pad", default_pad))
            rect = [
                (ring["x"] - pad) * scale,
                (ring["y"] - pad) * scale,
                (ring["x"] + ring["w"] + pad) * scale,
                (ring["y"] + ring["h"] + pad) * scale,
            ]
            if rect[0] < 0 or rect[1] < 0 or rect[2] > img.width or rect[3] > img.height:
                raise SystemExit(
                    f"{still['out']}: ring {ring} falls outside the {img.width}x{img.height} image "
                    f"at scale {scale}; check the scale and the box units"
                )
            zoom = float(ring.get("zoom", 1))
            if zoom <= 0:
                raise SystemExit(f"{still['out']}: zoom must be positive")
            img = Image.alpha_composite(img, ring_layer(img.size, rect, scale / zoom, rgb))
        out.parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(out)
        written.append(out)
    return written


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("spec", type=Path)
    args = parser.parse_args()
    for path in bake(args.spec):
        print(f"wrote {path}")


if __name__ == "__main__":
    sys.exit(main())
