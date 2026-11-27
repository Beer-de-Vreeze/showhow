// Pure maths for the globe kind: no three.js, no DOM, so node can check it (scripts/test_scene3d.mjs).
// Places are { lat, lon } in degrees; vectors are [x, y, z] on the unit sphere in three.js axes:
// +y north, lon 0 at +x, lon -90 at +z. That is the layout of THREE.SphereGeometry's uv, so an
// equirectangular texture (u = (lon + 180) / 360, v = (lat + 90) / 180) lands where the maths says.

const rad = (d) => (d * Math.PI) / 180, deg = (r) => (r * 180) / Math.PI;

export function toVec({ lat, lon }) {
  const p = rad(lat), l = rad(lon);
  return [Math.cos(p) * Math.cos(l), Math.sin(p), -Math.cos(p) * Math.sin(l)];
}

export function fromVec([x, y, z]) {
  return { lat: deg(Math.asin(Math.max(-1, Math.min(1, y)))), lon: deg(Math.atan2(-z, x)) };
}

// Point a fraction u along the shortest great-circle arc from a to b (spherical lerp of the unit vectors).
// shortcut: antipodal places have no single shortest arc and give a degenerate result; avoid them in a route.
export function slerp(va, vb, u) {
  const dot = Math.max(-1, Math.min(1, va[0] * vb[0] + va[1] * vb[1] + va[2] * vb[2]));
  const w = Math.acos(dot), s = Math.sin(w);
  if (s < 1e-9) return va;
  const A = Math.sin((1 - u) * w) / s, B = Math.sin(u * w) / s;
  return [A * va[0] + B * vb[0], A * va[1] + B * vb[1], A * va[2] + B * vb[2]];
}

export const greatCircle = (a, b, u) => fromVec(slerp(toVec(a), toVec(b), u));

// Arc as points lifted off the surface by sin(pi * s) * lift (in sphere radii), `n` segments, for a radius-r globe.
export function arcPoints(a, b, { r = 1, lift = 0.25, n = 64 } = {}) {
  const va = toVec(a), vb = toVec(b);
  return Array.from({ length: n + 1 }, (_, i) => {
    const s = i / n, v = slerp(va, vb, s), k = r * (1 + lift * Math.sin(Math.PI * s));
    return [v[0] * k, v[1] * k, v[2] * k];
  });
}

// Euler angles (order XYZ, as three.js applies Ry then Rx) that turn the globe so `place` faces +z, north up.
export const faceRotation = ({ lat, lon }) => ({ x: rad(lat), y: -Math.PI / 2 - rad(lon) });

// Orthographic (azimuthal) projection of `place` seen from above `centre`: [x, y, facing], x right and y up on the unit disc;
// facing < 0 means the far side (the caller clips or pushes it to the limb).
// It is d3.geoOrthographic().rotate([-centre.lon, -centre.lat]); a 2D locator map drawn with it, at radius R px,
// is the globe's front view at the same R, which is what makes the match cut line up (references/3d-scenes.md).
export function orthoProject(place, centre) {
  const p = rad(place.lat), l = rad(place.lon - centre.lon), c = rad(centre.lat);
  const cosc = Math.sin(c) * Math.sin(p) + Math.cos(c) * Math.cos(p) * Math.cos(l);
  return [Math.cos(p) * Math.sin(l), Math.cos(c) * Math.sin(p) - Math.sin(c) * Math.cos(p) * Math.cos(l), cosc];
}

// Mean-direction centre of a route (or any places): the place its middle faces.
export function centreOf(places) {
  const sum = places.map(toVec).reduce((s, v) => [s[0] + v[0], s[1] + v[1], s[2] + v[2]]);
  return fromVec(sum.map((c) => c / Math.hypot(...sum)));
}
