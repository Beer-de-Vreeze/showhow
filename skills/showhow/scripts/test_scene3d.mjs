// Self-check for the scene3d pure maths. Run: node <skill-dir>/scripts/test_scene3d.mjs
import assert from "node:assert/strict";
import { hash, timeMap, layoutLabels, labelEdges, glyphOffsets, missingGlyphs } from "../assets/scene3d/scene3d-math.js";
import { readFileSync } from "node:fs";
import { greatCircle, countryCentre } from "../assets/scene3d/globe-math.js";
import { gearOutline, meshAngle, crankSlider, explodeAmount, explodeOffsets, flowPoint } from "../assets/scene3d/machine-math.js";

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

// Country centre: the largest polygon, not the first; France's first ring in the bundled map is French Guiana,
// Norway's is Svalbard. Bounds are mainland France and mainland Norway.
{
  const { features } = JSON.parse(readFileSync(new URL("../assets/scene3d/data/ne_110m_admin_0_countries.min.geojson", import.meta.url), "utf8"));
  const by = (a3) => features.find((f) => f.properties.a3 === a3);
  const fra = countryCentre(by("FRA")), nor = countryCentre(by("NOR"));
  assert.ok(fra.lat > 42 && fra.lat < 51 && fra.lon > -5 && fra.lon < 8, `FRA centre ${JSON.stringify(fra)}`);
  assert.ok(nor.lat > 58 && nor.lat < 71 && nor.lon > 4 && nor.lon < 31, `NOR centre ${JSON.stringify(nor)}`);
}

// Exploded view: staggered ease per part index; worked values from at 8, stagger 0.2, dur 1.
const ex = { at: 8, stagger: 0.2, dur: 1 };
assert.equal(explodeAmount(0, 7, ex), 0);
assert.equal(explodeAmount(0, 8.5, ex), 0.5);
assert.ok(explodeAmount(2, 8.4, ex) < 1e-9);
assert.equal(explodeAmount(2, 9.4, ex), 1);
assert.equal(explodeAmount(1, 100, ex), 1);

// Exploded layout: parts stack in array order about the first one; every neighbouring pair ends up
// `gap` apart face to face, whatever their home heights (offset = final centre - home centre).
const homes = [-5, 0, 0, 0, 0], thick = [1, 2, 2, 2, 6];
const offs = explodeOffsets(homes.map((y, k) => ({ y, t: thick[k] })), 4);
assert.equal(offs[0], 0);
const centres = offs.map((o, k) => homes[k] + o);
for (let k = 1; k < centres.length; k++) {
  const face = centres[k] - centres[k - 1] - (thick[k] + thick[k - 1]) / 2;
  assert.ok(Math.abs(face - 4) < 1e-9, `parts ${k - 1} and ${k} are ${face} apart`);
}
assert.deepEqual(explodeOffsets([], 4), []);

// Label columns: plates stay `gap` px clear of the object's screen bounds, on screen, and line up in a column.
const edges = (bounds, plate = 330) => labelEdges({ width: 1920, margin: 150, left: plate, right: plate, bounds, gap: 60, pad: 24 });
assert.deepEqual(edges({ min: 800, max: 1300 }), { left: 150, right: 1770 }); // room: margins as usual
const tight = edges({ min: 475, max: 1390 });
assert.ok(tight.left + 330 + 60 <= 475 && tight.left >= 24, `left plates at ${tight.left}`);
assert.ok(tight.right - 330 >= 1390 + 60 && tight.right <= 1896, `right edge ${tight.right}`);
const wide = edges({ min: 475, max: 1500 });
assert.ok(wide.right - 330 >= 1500 + 60 || wide.right === 1920 - 24, `right edge ${wide.right}`);
assert.equal(edges({ min: 0, max: 1920 }).left, 24); // no room anywhere: clamp inside the frame

// Glyph spacing: extruded glyphs (x0..x1 wide, z0..z1 deep) turned by any angle, seen side on, never overlap:
// the projected right edge of each is at least `gap` left of the next one's left edge. Offsets are pure in the angle.
const glyphs = [{ x0: 0.2, x1: 2.2, z0: -0.7, z1: 0.7 }, { x0: 0.1, x1: 2.9, z0: -0.7, z1: 0.7 }, { x0: 0.2, x1: 3.1, z0: -0.7, z1: 0.7 }, { x0: 0.2, x1: 3.1, z0: -0.7, z1: 0.7 }];
for (const angle of [-1.1, -0.4, 0, 0.22, 0.26, 0.6, 1.1]) {
  const off = glyphOffsets(glyphs, angle, 0.3);
  assert.equal(off[0], 0);
  const c = Math.cos(angle), s = Math.sin(angle);
  const hi = (g, o) => (g.x1 + o) * c + Math.max(g.z0 * s, g.z1 * s), lo = (g, o) => (g.x0 + o) * c + Math.min(g.z0 * s, g.z1 * s);
  for (let k = 1; k < glyphs.length; k++) assert.ok(lo(glyphs[k], off[k]) - hi(glyphs[k - 1], off[k - 1]) > 0.3 - 1e-9, `glyph ${k} at ${angle}`);
}
assert.deepEqual(glyphOffsets([], 0.2, 0.3), []);

// hero-number: characters the typeface lacks (helvetiker has no € − °) would render as "?"; they are named instead.
assert.deepEqual(missingGlyphs({ "4": {}, "0": {}, "%": {} }, "40 %"), []);
assert.deepEqual(missingGlyphs({ "4": {}, "0": {} }, "−40°€€"), ["−", "°", "€"]);

// Flow particles: a pure function of (i, t, seed). Order of calls never matters, one lap takes 1 / speed
// seconds, the stream stays inside its box, and a different seed gives a different stream.
const fl = { speed: 0.25, length: 40, spread: 6 };
const lap = 1 / fl.speed;
const before = flowPoint(5, 2.3, 9, fl);
for (let i = 0; i < 50; i++) flowPoint(i, i * 7.1, 9, fl); // other frames in between
assert.deepEqual(flowPoint(5, 2.3, 9, fl), before);
const later = flowPoint(5, 2.3 + lap, 9, fl);
before.forEach((v, k) => assert.ok(Math.abs(v - later[k]) < 1e-9, `lap axis ${k}`));
for (let i = 0; i < 200; i++) {
  const [x, y, z] = flowPoint(i, -3.7 + i * 0.13, 9, fl);
  assert.ok(Math.abs(x) <= 20 && Math.abs(z) <= 6 && Math.abs(y) <= 6);
}
assert.notDeepEqual(flowPoint(5, 2.3, 10, fl), before);
// The stream moves: a particle is further along +x a moment later (until it wraps).
assert.ok(flowPoint(3, 0.1, 1, fl)[0] > flowPoint(3, 0, 1, fl)[0] || flowPoint(3, 0, 1, fl)[0] > 19);

console.log("ok");
