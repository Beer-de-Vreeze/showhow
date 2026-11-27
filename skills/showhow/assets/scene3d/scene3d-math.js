// Pure maths shared by every scene3d kind: no three.js, no DOM, so node can check it (scripts/test_scene3d.mjs).
// Every function depends on its arguments only; nothing here keeps state between calls.

export const clamp01 = (x) => Math.min(1, Math.max(0, x));
export const ease = (x) => { x = clamp01(x); return x * x * (3 - 2 * x); };
export const lerp = (a, b, u) => a + (b - a) * u;

// Integer hash of (i, seed) to [0, 1): mulberry32's mixer, never Math.random() or fract(sin()).
export function hash(i, seed = 0) {
  let a = (Math.imul(i | 0, 0x9e3779b1) ^ (seed | 0)) >>> 0;
  a = (a + 0x6d2b79f5) >>> 0;
  let t = Math.imul(a ^ (a >>> 15), 1 | a);
  t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
  return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
}

// Seed from text (the script, a scene name): FNV-1a.
export function seedOf(text) {
  let h = 0x811c9dc5;
  for (let k = 0; k < text.length; k++) h = Math.imul(h ^ text.charCodeAt(k), 0x01000193);
  return h >>> 0;
}

// Piecewise-linear time map for slow motion: keys [[t, tau], ...] sorted by t; slope 1 outside them.
export function timeMap(t, keys = []) {
  if (!keys.length) return t;
  if (t <= keys[0][0]) return keys[0][1] + (t - keys[0][0]);
  for (let i = 1; i < keys.length; i++) {
    const [t0, v0] = keys[i - 1], [t1, v1] = keys[i];
    if (t <= t1) return v0 + ((v1 - v0) * (t - t0)) / (t1 - t0);
  }
  const [tl, vl] = keys[keys.length - 1];
  return vl + (t - tl);
}

// Label slots: anchors [{x, y, side?}] in px -> copies with side and slotY, so leaders never cross.
// Anchors without a side go left or right by which half they sit in; each column is sorted by
// anchor y, pushed apart to at least `pitch`, then pulled back inside [top, bottom].
export function layoutLabels(anchors, { width, top, bottom, pitch }) {
  const out = anchors.map((a) => ({ ...a, side: a.side || (a.x < width / 2 ? "left" : "right") }));
  for (const side of ["left", "right"]) {
    const col = out.filter((a) => a.side === side).sort((p, q) => p.y - q.y || p.x - q.x);
    let y = -Infinity;
    for (const a of col) a.slotY = y = Math.max(Math.min(Math.max(a.y, top), bottom), y + pitch);
    let limit = bottom;
    for (let i = col.length - 1; i >= 0; i--) { col[i].slotY = Math.min(col[i].slotY, limit); limit = col[i].slotY - pitch; }
  }
  return out;
}
