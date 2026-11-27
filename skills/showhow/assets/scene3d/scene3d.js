// showhow scene3d scaffold: the base every 3D kind (machine, globe, hero-number) builds on.
// Seek wiring, stage with camera presets, flat look, glTF model loading, projected labels (references/3d-scenes.md).
// Needs an import map for "three" and "three/addons/" (see scripts/fixtures/gear-train/index.html).
// Rule: render(t) sets every transform from t; nothing here reads a clock or keeps per-frame state.
import * as THREE from "three";
import { LineSegments2 } from "three/addons/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "three/addons/lines/LineSegmentsGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { layoutLabels, labelEdges, ease } from "./scene3d-math.js";

export * from "./scene3d-math.js";
export { THREE };

// ---- Theme: colours come from the composition's CSS variables, never from this code ----------

// --paper (ground), --ink (lines, text), --accent (the one part the narration names), --muted. The values below
// are the `showhow` frame preset, used only when a variable is missing. Everything else is a tint of these.
export const theme = { paper: "#F3ECDD", ink: "#23201B", accent: "#0F6E6A", muted: "#5B5547" };

// Reads the variables as the element sees them (so a brand kit or a scene override wins); createStage calls it.
export function readTheme(el) {
  const cs = getComputedStyle(el);
  for (const k of Object.keys(theme)) theme[k] = cs.getPropertyValue(`--${k}`).trim() || theme[k];
  return theme;
}

// Hex colour u of the way from a to b (any CSS colour in), for fills derived from the theme.
export const tint = (a, b, u) => `#${new THREE.Color(a).lerp(new THREE.Color(b), u).getHexString()}`;

// ---- Seek wiring --------------------------------------------------------------------------------

// Registers window.__hf.buildReady[key] at once, awaits build() (meshes, model, compile) and the fonts,
// then draws from every hf-seek. build() resolves to render(t). Outside HyperFrames, ?t=<s> previews a frame.
export function onSeek(key, build) {
  window.__hf = window.__hf || {};
  window.__hf.buildReady = window.__hf.buildReady || {};
  let render = null;
  let last = 0;
  addEventListener("hf-seek", (e) => { last = e.detail.time; if (render) render(last); });
  const ready = (async () => {
    render = await build();
    await document.fonts.ready;
    render(Number(new URLSearchParams(location.search).get("t")) || last);
  })();
  window.__hf.buildReady[key] = ready;
  return ready;
}

// ---- Stage: renderer, orthographic camera presets, flat light ---------------------------------

// Directions the orthographic camera looks from. iso: the (1, 1, 1) diagonal, parallel edges stay parallel;
// dimetric: lower and calmer; front and top: flat elevations. Animate camera.zoom for a dive, not distance.
export const VIEWS = { iso: [1, 1, 1], dimetric: [1, 0.6, 1], front: [0, 0, 1], top: [0, 1, 0.0001] };

export function orthoCamera(width, height, { viewHeight = 10, view = "iso", target = new THREE.Vector3() } = {}) {
  const h = viewHeight / 2, w = (h * width) / height;
  const camera = new THREE.OrthographicCamera(-w, w, h, -h, -1000, 1000);
  camera.position.copy(target).add(new THREE.Vector3(...VIEWS[view]).normalize().multiplyScalar(100));
  camera.lookAt(target);
  return camera;
}

export function createStage({ canvas, width = 1920, height = 1080, background, viewHeight = 10, view = "iso" }) {
  // Fixed pixel ratio and a kept drawing buffer, so capture never depends on the host's devicePixelRatio.
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true, stencil: true });
  renderer.setPixelRatio(1);
  renderer.setSize(width, height, false);
  readTheme(canvas);
  renderer.setClearColor(background ?? theme.paper);
  const scene = new THREE.Scene();
  const camera = orthoCamera(width, height, { viewHeight, view });
  scene.add(new THREE.AmbientLight(0xffffff, 1.4));
  const key = new THREE.DirectionalLight(0xffffff, 2.2);
  key.position.set(3, 10, 6);
  scene.add(key);
  const v = new THREE.Vector3();
  return {
    renderer, scene, camera, width, height,
    // World point -> pixel position in the frame.
    project(p) {
      v.copy(p).project(camera);
      return { x: ((v.x + 1) / 2) * width, y: ((1 - v.y) / 2) * height };
    },
    draw() { renderer.render(scene, camera); },
  };
}

// ---- Look: toon fill, fat edge lines, inverted-hull silhouette --------------------------------

let gradient;
function toonGradient() {
  // Three steps, NearestFilter, so the shading reads as flat bands.
  if (!gradient) {
    gradient = new THREE.DataTexture(new Uint8Array([90, 180, 255]), 3, 1, THREE.RedFormat);
    gradient.minFilter = gradient.magFilter = THREE.NearestFilter;
    gradient.needsUpdate = true;
  }
  return gradient;
}

export function toonMaterial(color) {
  // polygonOffset pushes the fill back so edge lines never z-fight it.
  return new THREE.MeshToonMaterial({ color, gradientMap: toonGradient(), polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 });
}

// Crease edges as screen-space fat lines; linewidth is in pixels at the stage size.
export function edgeLines(geometry, stage, { color = theme.ink, linewidth = 2.5, threshold = 25 } = {}) {
  return new LineSegments2(
    new LineSegmentsGeometry().fromEdgesGeometry(new THREE.EdgesGeometry(geometry, threshold)),
    new LineMaterial({ color, linewidth, resolution: new THREE.Vector2(stage.width, stage.height) }),
  );
}

// Silhouette for curved parts with few creases: back faces pushed out along their normals.
// The normal attribute, not objectNormal: MeshBasicMaterial's shader has no objectNormal, so the hull failed to compile.
export function hull(geometry, { color = theme.ink, thickness = 0.05 } = {}) {
  const mat = new THREE.MeshBasicMaterial({ color, side: THREE.BackSide });
  mat.onBeforeCompile = (shader) => {
    shader.vertexShader = shader.vertexShader.replace("#include <begin_vertex>", `#include <begin_vertex>\ntransformed += normalize(normal) * ${thickness.toFixed(4)};`);
  };
  return new THREE.Mesh(geometry, mat);
}

// One part: toon fill + fat edges (+ silhouette hull when asked), in a group the caller moves.
export function part(geometry, stage, { color = tint(theme.paper, theme.ink, 0.2), edges = {}, silhouette = false } = {}) {
  const group = new THREE.Group();
  group.add(new THREE.Mesh(geometry, toonMaterial(color)));
  group.add(edgeLines(geometry, stage, edges));
  if (silhouette) group.add(hull(geometry, typeof silhouette === "object" ? silhouette : {}));
  return group;
}

// ---- Params.model: a user glTF replaces the procedural build -----------------------------------

// Loads a .gltf/.glb, scales it to fit `size` world units, centres it, gives every mesh the flat look.
// Nodes named like the recipe's parts (getObjectByName) take over their motion and labels.
// A model that fails to load fails the build; it never falls back to a different object.
export async function loadModel(url, stage, { size = 10, restyle = true, color = tint(theme.paper, theme.ink, 0.2) } = {}) {
  const root = (await new GLTFLoader().loadAsync(url)).scene;
  const box = new THREE.Box3().setFromObject(root);
  const s = size / Math.max(...box.getSize(new THREE.Vector3()).toArray());
  root.scale.setScalar(s);
  root.position.copy(box.getCenter(new THREE.Vector3()).multiplyScalar(-s));
  if (restyle) {
    const meshes = [];
    root.traverse((o) => o.isMesh && meshes.push(o));
    for (const mesh of meshes) {
      mesh.material = toonMaterial(mesh.material?.color ?? color);
      mesh.add(edgeLines(mesh.geometry, stage));
    }
  }
  const wrap = new THREE.Group();
  wrap.add(root);
  return wrap;
}

// ---- Labels: projected HTML plates with SVG leaders in sorted slot columns --------------------

// items: [{ text, anchor: Object3D or Vector3, at: seconds it fades in, side?: "left" | "right" }].
// Build once, then call the returned layout(t) from render(t), after the scene is posed.
// avoid: the Object3D (the whole machine) the plates stay `gap` px clear of; the columns step outward when zoom
// or an exploded view grows it. Without it they sit at `margin`.
export function labels(container, stage, items, { margin = 150, top = 140, bottom = 900, pitch = 84, avoid = null, gap = 70, pad = 24 } = {}) {
  const ns = "http://www.w3.org/2000/svg";
  const svg = document.createElementNS(ns, "svg");
  svg.setAttribute("width", stage.width);
  svg.setAttribute("height", stage.height);
  svg.setAttribute("class", "s3d-leaders");
  container.appendChild(svg);
  const els = items.map((item) => {
    const plate = document.createElement("div");
    plate.className = "s3d-label";
    plate.textContent = item.text;
    container.appendChild(plate);
    const line = document.createElementNS(ns, "line");
    const dot = document.createElementNS(ns, "circle");
    dot.setAttribute("r", 6);
    svg.append(line, dot);
    return { plate, line, dot };
  });
  const world = new THREE.Vector3(), box = new THREE.Box3(), corner = new THREE.Vector3();
  // Screen x range of avoid's bounding box: its eight corners projected.
  const bounds = () => {
    box.setFromObject(avoid);
    let min = Infinity, max = -Infinity;
    for (let k = 0; k < 8; k++) {
      const x = stage.project(corner.set(k & 1 ? box.max.x : box.min.x, k & 2 ? box.max.y : box.min.y, k & 4 ? box.max.z : box.min.z)).x;
      min = Math.min(min, x); max = Math.max(max, x);
    }
    return { min, max };
  };
  return function layout(t) {
    const anchors = items.map((item, i) => {
      const p = item.anchor.isObject3D ? item.anchor.getWorldPosition(world) : item.anchor;
      return { i, side: item.side, ...stage.project(p) };
    });
    const placed = layoutLabels(anchors, { width: stage.width, top, bottom, pitch });
    const widest = (side) => Math.max(0, ...placed.filter((a) => a.side === side).map((a) => els[a.i].plate.offsetWidth));
    const edge = avoid ? labelEdges({ width: stage.width, margin, left: widest("left"), right: widest("right"), bounds: bounds(), gap, pad }) : { left: margin, right: stage.width - margin };
    for (const a of placed) {
      const { plate, line, dot } = els[a.i];
      const o = ease((t - (items[a.i].at ?? 0)) / 0.4);
      const left = a.side === "left";
      const x = left ? edge.left : edge.right;
      plate.style.opacity = line.style.opacity = dot.style.opacity = o;
      plate.style.transform = `translate(${left ? x : x - plate.offsetWidth}px, ${a.slotY - plate.offsetHeight / 2}px)`;
      const ex = left ? x + plate.offsetWidth + 12 : x - plate.offsetWidth - 12;
      line.setAttribute("x1", ex); line.setAttribute("y1", a.slotY);
      line.setAttribute("x2", a.x); line.setAttribute("y2", a.y);
      dot.setAttribute("cx", a.x); dot.setAttribute("cy", a.y);
    }
  };
}
