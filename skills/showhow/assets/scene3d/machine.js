// scene3d kind "machine": a cached part library built from Params, on top of scene3d.js.
// Motion comes from machine-math.js (gear trains, escapement beat, crank-slider) as closed forms of t.
import { THREE, toonMaterial, theme, tint } from "./scene3d.js";
import { gearOutline, flowPoint } from "./machine-math.js";

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
export function bladeRow({ count = 24, hub = 1, span = 1, chord = 0.4, twist = 0.5, thickness = 0.05, color = tint(theme.paper, theme.ink, 0.2) }) {
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

// ---- Cutaway: clipping plane + stencil cap + world-space hatch ----------------------------------

// Clips every part under `root` with one horizontal plane (keeps y <= level) and caps the cut with a hatched
// face, following three.js's webgl_clipping_stencil: back faces +1, front faces -1 in the stencil, then a
// plane drawn where the count is not zero. Parts must be closed solids; sets renderer.localClippingEnabled.
// The cap is a flat tint with sparse 45-degree ink lines (spacing px apart at stage size, line px wide) drawn only on
// the cut faces; uncut surfaces keep their flat fill. The lines are measured on screen, so they read the same from any
// view and zoom, and are a function of the cap position, so they never swim while the parts turn.
// Defaults come from the theme: the cap is paper tinted with the accent, the lines are ink.
// Returns set(level): a pure function of the level, so call it from render(t); a level at or above `off` is "closed".
export function sectionCut(stage, root, { color = tint(theme.paper, theme.accent, 0.2), ink = theme.ink, spacing = 10, line = 2, off = 50 } = {}) {
  stage.renderer.localClippingEnabled = true;
  const plane = new THREE.Plane(new THREE.Vector3(0, -1, 0), off);
  const solids = [], extras = [];
  root.traverse((o) => {
    if (o.isMesh) {
      o.material.clippingPlanes = [plane];
      o.renderOrder = 6;
      if (!o.isLineSegments2) solids.push(o);
    }
  });
  const pass = (side, op) => new THREE.MeshBasicMaterial({
    side, colorWrite: false, depthWrite: false, depthTest: false, clippingPlanes: [plane],
    stencilWrite: true, stencilFunc: THREE.AlwaysStencilFunc, stencilFail: op, stencilZFail: op, stencilZPass: op,
  });
  for (const o of solids) {
    for (const [side, op] of [[THREE.BackSide, THREE.IncrementWrapStencilOp], [THREE.FrontSide, THREE.DecrementWrapStencilOp]]) {
      // An instanced part (a blade row) needs instanced passes sharing its matrices, or only one blade gets a cap.
      const m = o.isInstancedMesh
        ? Object.assign(new THREE.InstancedMesh(o.geometry, pass(side, op), o.count), { instanceMatrix: o.instanceMatrix })
        : new THREE.Mesh(o.geometry, pass(side, op));
      m.renderOrder = 1;
      o.add(m);
      extras.push(m);
    }
  }
  const cap = new THREE.Mesh(new THREE.PlaneGeometry(400, 400).rotateX(-Math.PI / 2), new THREE.ShaderMaterial({
    uniforms: { base: { value: new THREE.Color(color) }, ink: { value: new THREE.Color(ink) }, spacing: { value: spacing }, line: { value: line }, halfH: { value: stage.height / 2 } },
    // The hatch is sampled where the cap point sits at height 0, so sweeping the plane slides the cap, not the lines.
    vertexShader: `uniform float halfH; varying vec2 xy; varying float ppu;
      void main(){ vec4 w = modelMatrix * vec4(position, 1.0);
        xy = (viewMatrix * vec4(w.x, 0.0, w.z, 1.0)).xy; ppu = projectionMatrix[1][1] * halfH;
        gl_Position = projectionMatrix * viewMatrix * w; }`,
    // p: pixels along the normal of a 45-degree line; d: pixels to the nearest line (spacing is the pitch between lines).
    fragmentShader: `uniform vec3 base; uniform vec3 ink; uniform float spacing; uniform float line; varying vec2 xy; varying float ppu;
      void main(){ float p = (xy.x - xy.y) * 0.70710678 * ppu; float f = fract(p / spacing);
        float d = min(f, 1.0 - f) * spacing;
        gl_FragColor = vec4(mix(base, ink, 1.0 - smoothstep(line * 0.5 - 0.5, line * 0.5 + 0.5, d)), 1.0);
        #include <colorspace_fragment>
      }`,
    side: THREE.DoubleSide, stencilWrite: true, stencilRef: 0, stencilFunc: THREE.NotEqualStencilFunc,
    stencilFail: THREE.ReplaceStencilOp, stencilZFail: THREE.ReplaceStencilOp, stencilZPass: THREE.ReplaceStencilOp,
  }));
  cap.renderOrder = 1.1;
  cap.frustumCulled = false;
  cap.onAfterRender = (r) => r.clearStencil();
  stage.scene.add(cap);
  return function set(level) {
    const on = level < off;
    plane.constant = level;
    cap.position.y = level;
    cap.visible = on;
    for (const m of extras) m.visible = on;
  };
}

// ---- Airflow: stateless particles ----------------------------------------------------------------

// count round points whose positions are flowPoint(i, t, seed, ...) rewritten every frame (hundreds are cheap).
// Ink dots with a paper ring (size px across at stage size), so they read on the paper and on any part colour.
// update(t, amount) places them for time t; amount 0 hides them, 1 is full size.
export function flowParticles(stage, { count = 320, seed = 1, size = 18, color = theme.ink, ring = theme.paper, ...flow } = {}) {
  const geo = new THREE.BufferGeometry();
  geo.setAttribute("position", new THREE.BufferAttribute(new Float32Array(count * 3), 3));
  const points = new THREE.Points(geo, new THREE.ShaderMaterial({
    uniforms: { size: { value: size }, color: { value: new THREE.Color(color) }, ring: { value: new THREE.Color(ring) } },
    vertexShader: "uniform float size; void main(){ gl_PointSize = size; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }",
    fragmentShader: `uniform vec3 color; uniform vec3 ring; void main(){ float r = length(gl_PointCoord - 0.5) * 2.0; if (r > 1.0) discard;
      gl_FragColor = vec4(r > 0.74 ? ring : color, 1.0);
      #include <colorspace_fragment>
    }`,
  }));
  points.frustumCulled = false;
  const pos = geo.attributes.position;
  points.update = (t, amount = 1) => {
    points.visible = amount > 0;
    points.material.uniforms.size.value = size * amount;
    for (let i = 0; i < count; i++) pos.setXYZ(i, ...flowPoint(i, t, seed, flow));
    pos.needsUpdate = true;
  };
  return points;
}
