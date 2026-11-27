// scene3d kind "machine": a cached part library built from Params, on top of scene3d.js.
// Motion comes from machine-math.js (gear trains, escapement beat, crank-slider) as closed forms of t.
import { THREE, toonMaterial } from "./scene3d.js";
import { gearOutline } from "./machine-math.js";

export * from "./machine-math.js";

const cache = new Map();
const cached = (key, make) => cache.get(key) || cache.set(key, make()).get(key);

// Involute spur gear lying flat (axis +y), centred on its axis, so rotation.y turns it.
// Tooth 0 points along +x at rotation 0; feed meshAngle() with the same convention.
export function gearGeometry({ teeth, module = 1, width = 1, bore = 0 }) {
  return cached(`gear:${teeth}:${module}:${width}:${bore}`, () => {
    const { points } = gearOutline({ teeth, module });
    const shape = new THREE.Shape(points.map(([x, y]) => new THREE.Vector2(x, y)));
    if (bore > 0) shape.holes.push(new THREE.Path().absarc(0, 0, bore, 0, Math.PI * 2, true));
    const geo = new THREE.ExtrudeGeometry(shape, { depth: width, bevelEnabled: false, curveSegments: 24 });
    geo.translate(0, 0, -width / 2);
    geo.rotateX(-Math.PI / 2); // shape (x, y) -> world (x, -z): a CCW shape turn is +rotation.y
    return geo;
  });
}

// Round parts (shafts, hubs, discs, casings) from an [r, y] profile turned around +y.
export function latheGeometry(profile, segments = 64) {
  return cached(`lathe:${JSON.stringify(profile)}:${segments}`, () => new THREE.LatheGeometry(profile.map(([r, y]) => new THREE.Vector2(r, y)), segments));
}

// Coil spring along +y: coils turns of radius r over length, wire radius wire.
// Compress it by scaling its group along y; rebuilding the tube per frame is too slow.
export function springGeometry({ coils = 6, radius = 1, length = 4, wire = 0.12 }) {
  return cached(`spring:${coils}:${radius}:${length}:${wire}`, () => {
    const curve = new THREE.Curve();
    curve.getPoint = (u, out = new THREE.Vector3()) => out.set(radius * Math.cos(u * coils * Math.PI * 2), u * length, radius * Math.sin(u * coils * Math.PI * 2));
    return new THREE.TubeGeometry(curve, coils * 32, wire, 8, false);
  });
}

// A row of count blades around +y (a compressor or turbine stage): one geometry, one InstancedMesh.
// shortcut: no edge lines on instanced blades; merge per-blade edges if a close-up needs them.
export function bladeRow({ count = 24, hub = 1, span = 1, chord = 0.4, twist = 0.5, thickness = 0.05, color = "#c9d3df" }) {
  const geo = cached(`blade:${hub}:${span}:${chord}:${twist}:${thickness}`, () => {
    const g = new THREE.BoxGeometry(chord, thickness, span, 1, 1, 6);
    const p = g.attributes.position, v = new THREE.Vector3();
    for (let i = 0; i < p.count; i++) {
      v.fromBufferAttribute(p, i);
      const u = v.z / span + 0.5, a = twist * (u - 0.5);
      p.setXYZ(i, v.x * Math.cos(a) - v.y * Math.sin(a), v.x * Math.sin(a) + v.y * Math.cos(a), hub + u * span);
    }
    g.computeVertexNormals();
    return g;
  });
  const row = new THREE.InstancedMesh(geo, toonMaterial(color), count);
  const m = new THREE.Matrix4();
  for (let i = 0; i < count; i++) row.setMatrixAt(i, m.makeRotationY((i / count) * Math.PI * 2));
  return row; // spin the row (rotation.y), never rewrite its matrices per frame
}
