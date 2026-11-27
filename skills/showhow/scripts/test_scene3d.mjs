// Self-check for the scene3d pure maths. Run: node <skill-dir>/scripts/test_scene3d.mjs
import assert from "node:assert/strict";
import { hash, timeMap, layoutLabels } from "../assets/scene3d/scene3d-math.js";
import { greatCircle } from "../assets/scene3d/globe-math.js";
import { gearOutline, meshAngle, crankSlider } from "../assets/scene3d/machine-math.js";

// hash: same input, same value, inside [0, 1), and spread out.
assert.equal(hash(7, 42), hash(7, 42));
const hs = Array.from({ length: 1000 }, (_, i) => hash(i, 1));
assert.ok(hs.every((h) => h >= 0 && h < 1));
assert.ok(Math.abs(hs.reduce((a, b) => a + b) / hs.length - 0.5) < 0.05);

// timeMap: slope 1 outside the keys, linear between them.
const slow = [[0, 0], [5, 5], [9, 6]];
assert.equal(timeMap(3, slow), 3);
assert.equal(timeMap(7, slow), 5.5);
assert.equal(timeMap(10, slow), 7);

// Labels: sorted by anchor y within a column, at least `pitch` apart, inside the band.
const placed = layoutLabels([{ x: 100, y: 500 }, { x: 120, y: 480 }, { x: 900, y: 100 }, { x: 1800, y: 990 }], { width: 1920, top: 140, bottom: 900, pitch: 84 });
const leftCol = placed.filter((a) => a.side === "left").sort((a, b) => a.y - b.y);
assert.deepEqual(leftCol.map((a) => a.slotY), [140, 480, 564]);
assert.equal(placed.find((a) => a.side === "right").slotY, 900);

// Gears placed by meshAngle never interpenetrate; half a pitch off, they do (odd and even teeth).
function posed(teeth, angle, cx = 0) {
  const c = Math.cos(angle), s = Math.sin(angle);
  return gearOutline({ teeth, steps: 10 }).points.map(([x, y]) => [cx + x * c - y * s, x * s + y * c]);
}
function inside([px, py], poly) {
  let ins = false;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [xi, yi] = poly[i], [xj, yj] = poly[j];
    if (yi > py !== yj > py && px < ((xj - xi) * (py - yi)) / (yj - yi) + xi) ins = !ins;
  }
  return ins;
}
function edgeDist([px, py], poly) {
  let best = Infinity;
  for (let i = 0, j = poly.length - 1; i < poly.length; j = i++) {
    const [ax, ay] = poly[j], dx = poly[i][0] - ax, dy = poly[i][1] - ay;
    const u = Math.max(0, Math.min(1, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)));
    best = Math.min(best, Math.hypot(px - ax - u * dx, py - ay - u * dy));
  }
  return best;
}
// How deep any outline point of b sits inside a (0 = no overlap), in modules.
function overlap(a, b) {
  let worst = 0;
  for (const p of b) if (inside(p, a)) worst = Math.max(worst, edgeDist(p, a));
  return worst;
}
for (const [n1, n2] of [[12, 24], [12, 15], [17, 13]]) {
  const a = (n1 + n2) / 2;
  for (let k = 0; k < 12; k++) {
    const t = (k / 12) * ((2 * Math.PI) / n1);
    const g1 = posed(n1, t), g2 = posed(n2, meshAngle(t, n1, n2, 0), a);
    assert.ok(overlap(g1, g2) < 0.05 && overlap(g2, g1) < 0.05, `${n1}->${n2} collide at ${t}`);
  }
  const bad = posed(n2, meshAngle(0, n1, n2, 0) + Math.PI / n2, a);
  assert.ok(overlap(posed(n1, 0), bad) > 0.3, `${n1}->${n2} half-pitch error not caught`);
}

// Crank-slider: the rod keeps its length at every crank angle; dead centres at r + l and l - r.
for (let k = 0; k < 16; k++) {
  const a = (k / 16) * 2 * Math.PI, { x, rod } = crankSlider(a, 1, 3.5);
  assert.ok(Math.abs(Math.hypot(x - Math.cos(a), Math.sin(a)) - 3.5) < 1e-9);
  assert.ok(Math.abs(Math.sin(rod) * 3.5 - Math.sin(a)) < 1e-9);
}
assert.ok(Math.abs(crankSlider(0, 1, 3.5).x - 4.5) < 1e-9 && Math.abs(crankSlider(Math.PI, 1, 3.5).x - 2.5) < 1e-9);

// Great circle: the midpoint of Seville -> Rio de Janeiro equals the standard midpoint formula (computed here, from spherical trig).
{
  const rad = (d) => (d * Math.PI) / 180, deg = (r) => (r * 180) / Math.PI;
  const [la1, lo1, la2, lo2] = [37.39, -5.98, -22.91, -43.17];
  const bx = Math.cos(rad(la2)) * Math.cos(rad(lo2 - lo1)), by = Math.cos(rad(la2)) * Math.sin(rad(lo2 - lo1));
  const latM = deg(Math.atan2(Math.sin(rad(la1)) + Math.sin(rad(la2)), Math.hypot(Math.cos(rad(la1)) + bx, by)));
  const lonM = lo1 + deg(Math.atan2(by, Math.cos(rad(la1)) + bx));
  const mid = greatCircle({ lat: la1, lon: lo1 }, { lat: la2, lon: lo2 }, 0.5);
  assert.ok(Math.abs(mid.lat - latM) < 0.01 && Math.abs(mid.lon - lonM) < 0.01, JSON.stringify([mid, latM, lonM]));
}

console.log("ok");
