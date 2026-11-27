// Pure kinematics for the machine kind: closed forms of a time value, no three.js, no DOM.
import { hash, ease } from "./scene3d-math.js";

const TAU = Math.PI * 2;
const inv = (a) => Math.tan(a) - a;

// Involute spur gear outline, tooth 0 centred on angle 0, as [x, y] points counter-clockwise.
// Module m, N teeth, pressure angle pa: pitch r = mN/2, tip r + m, root r - 1.25m, base r cos(pa).
export function gearOutline({ teeth: N, module: m = 1, pressureAngle = (20 * Math.PI) / 180, steps = 6 }) {
  const r = (m * N) / 2, rb = r * Math.cos(pressureAngle), ra = r + m, rf = r - 1.25 * m;
  // Half the tooth's angular width at radius rho: half the circular pitch thick on the pitch circle.
  const half = (rho) => Math.PI / (2 * N) + inv(pressureAngle) - inv(Math.acos(Math.min(1, rb / rho)));
  const flank = [];
  const r0 = Math.max(rb, rf);
  for (let k = 0; k <= steps; k++) {
    const rho = r0 + ((ra - r0) * k) / steps;
    flank.push([rho, half(rho)]);
  }
  if (rf < rb) flank.unshift([rf, half(rb)]); // radial flank below the base circle
  const pts = [];
  const polar = (rho, a) => pts.push([rho * Math.cos(a), rho * Math.sin(a)]);
  for (let i = 0; i < N; i++) {
    const c = (i * TAU) / N;
    for (const [rho, h] of flank) polar(rho, c - h); // trailing flank, root to tip
    for (let k = flank.length - 1; k >= 0; k--) polar(flank[k][0], c + flank[k][1]); // leading flank, tip to root
    const a0 = c + flank[0][1], a1 = c + TAU / N - flank[0][1]; // root arc to the next tooth
    for (let k = 1; k < 3; k++) polar(rf, a0 + ((a1 - a0) * k) / 3);
  }
  return { points: pts, pitch: r, tip: ra, root: rf, base: rb };
}

// Angle of a gear meshing with a parent gear; dir is the direction from the parent's centre to this one's.
// When a parent tooth points along dir, this gear shows a gap there; the ratio is -parentTeeth / teeth.
// (The often-quoted offset pi/N alone only works for an even tooth count on the far side.)
export function meshAngle(parentAngle, parentTeeth, teeth, dir) {
  return dir + Math.PI + Math.PI / teeth - ((parentAngle - dir) * parentTeeth) / teeth;
}

// Crank-slider: crank radius r, rod l, crank angle a -> slider distance from the crank axis and rod angle.
export function crankSlider(a, r, l) {
  const s = r * Math.sin(a);
  return { x: r * Math.cos(a) + Math.sqrt(l * l - s * s), rod: Math.asin(s / l) };
}

// Exploded view: 0 (home) to 1 (fully out) for part i, each part starting `stagger` seconds after the last.
// The part sits at home + vector * explodeAmount(...); its spin stays a function of t, so it keeps turning.
export function explodeAmount(i, t, { at = 0, stagger = 0.15, dur = 1 }) {
  return ease((t - at - i * stagger) / dur);
}

// Airflow particle i at time t: a stream along x, y and z fixed by the hash plus a gentle swirl.
// Stateless: it depends on (i, t, seed) only, and repeats every 1 / speed seconds. Never Math.random().
export function flowPoint(i, t, seed, { speed = 0.25, length = 40, spread = 6 }) {
  const u = (((hash(i, seed) + speed * t) % 1) + 1) % 1;
  const y = (hash(i + 0x10000, seed) - 0.5) * spread, z0 = (hash(i + 0x20000, seed) - 0.5) * spread;
  const swirl = (spread / 6) * Math.sin(TAU * (u * 3 + hash(i + 0x30000, seed)));
  return [(u - 0.5) * length, y, Math.max(-spread, Math.min(spread, z0 + swirl))];
}
