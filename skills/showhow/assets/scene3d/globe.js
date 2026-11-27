// scene3d kind "globe": Natural Earth globe, highlighted country, great-circle route arcs, zoom to the region,
// and a flat locator map (orthographic, same centre and scale) the 3D frame cuts to. References: references/3d-scenes.md.
// Every pose comes from t alone; geometry that changes with t (arc lift, draw-on) is rebuilt from t, never accumulated.
import { THREE, hull, labels, ease, lerp, theme, tint } from "./scene3d.js";
import { toVec, fromVec, arcPoints, faceRotation, orthoProject, centreOf } from "./globe-math.js";

export const R = 4; // globe radius in world units; R_px = R * (pixels per unit) * zoom, so any viewHeight works
let OCEAN, LAND, BORDER, ACCENT; // set from the theme in buildGlobe: paper and ink tints, the accent for the highlight and route
const ZOOM_END = 1.5;

export async function loadCountries(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`globe: cannot load ${url} (${res.status})`);
  return (await res.json()).features;
}

// Polygon rings of a feature as arrays of [lon, lat].
const rings = (f) => (f.geometry.type === "Polygon" ? [f.geometry.coordinates] : f.geometry.coordinates).flat();

export function findCountry(features, code) {
  const c = String(code).toUpperCase();
  const f = features.find((x) => x.properties.a3 === c || x.properties.a2 === c);
  if (!f) throw new Error(`globe: no country with ISO code ${code}`);
  return f;
}

// Seconds: highlight fades in over the first second, each leg draws over 2 s, then the zoom, then the cut to the flat map.
export function globeTiming(P) {
  const legs = Math.max(0, (P.route || []).length - 1);
  const legAt = (i) => [1.2 + 2.2 * i, 3.2 + 2.2 * i];
  const zoomStart = 1.7 + 2.2 * legs, zoomEnd = zoomStart + 2.5;
  return { legAt, zoomStart, zoomEnd, cut: zoomEnd + 0.3, cutFade: 0.4 };
}

function equirect(features, { fill, stroke, width = 6144, line = 2.5 }) {
  const c = document.createElement("canvas");
  c.width = width; c.height = width / 2;
  const g = c.getContext("2d");
  if (fill) { g.fillStyle = fill; g.fillRect(0, 0, c.width, c.height); }
  g.strokeStyle = BORDER; g.lineWidth = line; g.lineJoin = "round";
  for (const f of features) {
    g.beginPath();
    for (const ring of rings(f)) ring.forEach(([lon, lat], i) => g[i ? "lineTo" : "moveTo"](((lon + 180) / 360) * c.width, ((90 - lat) / 180) * c.height));
    g.fillStyle = f.fill; g.fill("evenodd"); g.stroke();
  }
  return c;
}

const texture = (canvas) => {
  const t = new THREE.CanvasTexture(canvas);
  t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; t.needsUpdate = true;
  return t;
};

// Builds the globe into `stage`; returns { pose(t), centre, timing, flatMap(canvas) }.
export async function buildGlobe(stage, root, P, url) {
  OCEAN = tint(theme.paper, theme.ink, 0.1); LAND = tint(theme.paper, theme.ink, 0.28); BORDER = theme.ink; ACCENT = theme.accent;
  const features = await loadCountries(url);
  const route = P.route || [];
  // A place without coordinates would draw at NaN and vanish; P-params catches it, this names it if a plan skipped the gate.
  for (const p of route) if (!Number.isFinite(p?.lat) || !Number.isFinite(p?.lon)) throw new Error(`globe: route place ${JSON.stringify(p)} needs numeric lat and lon`);
  const country = P.country ? findCountry(features, P.country) : null;
  const centre = P.focus || (route.length > 1 ? centreOf(route) : centreOf(rings(country)[0].map(([lon, lat]) => ({ lat, lon }))));
  const timing = globeTiming(P);

  const globe = new THREE.Group();
  stage.scene.add(globe);
  const sphere = new THREE.SphereGeometry(R, 96, 64);
  const base = equirect(features.map((f) => ({ ...f, fill: LAND })), { fill: OCEAN });
  globe.add(new THREE.Mesh(sphere, new THREE.MeshBasicMaterial({ map: texture(base) })));
  globe.add(hull(sphere, { thickness: 0.05 }));
  let glow = null;
  if (country) {
    const mask = equirect([{ ...country, fill: ACCENT }], {});
    glow = new THREE.Mesh(new THREE.SphereGeometry(R * 1.002, 96, 64), new THREE.MeshBasicMaterial({ map: texture(mask), transparent: true }));
    globe.add(glow);
  }

  const markers = route.map((place) => {
    const m = new THREE.Mesh(new THREE.SphereGeometry(1, 16, 12), new THREE.MeshBasicMaterial({ color: ACCENT }));
    m.position.set(...toVec(place).map((c) => c * R * 1.004)); // above the highlight shell
    globe.add(m);
    return m;
  });
  const arcMat = new THREE.MeshBasicMaterial({ color: ACCENT });
  const arcs = route.slice(1).map((to, i) => {
    const mesh = new THREE.Mesh(new THREE.BufferGeometry(), arcMat);
    globe.add(mesh);
    return { mesh, from: route[i], to };
  });

  // Plates for each place, in their own layer so the whole layer can fade out as the zoom starts.
  const layer = document.createElement("div");
  layer.style.cssText = "position:absolute;inset:0;pointer-events:none";
  root.appendChild(layer);
  const layout = route.length
    ? labels(layer, stage, route.map((p, i) => ({ text: p.name, anchor: markers[i], at: i ? timing.legAt(i - 1)[1] : 0.4, side: p.side })), { top: 240, bottom: 900 })
    : () => {};

  await stage.renderer.compileAsync(stage.scene, stage.camera);

  const lon0 = centre.lon - 50; // starts turned away, settles on the region by the end of the zoom
  // Pixels per world unit from the camera, not an assumed viewHeight of 10: a portrait or square stage widens
  // viewHeight (10 * height / width) so the globe fits the narrow side.
  const unit = stage.height / (stage.camera.top - stage.camera.bottom);
  const Rpx = unit * R * ZOOM_END;
  // A place's pixel position on the flat map (the globe's final frame), for the map and for labels placed over it.
  const flatAt = (p) => { const [x, y, f] = orthoProject(p, centre); const k = f < 0 ? 1 / Math.hypot(x, y) : 1; return [stage.width / 2 + x * k * Rpx, stage.height / 2 - y * k * Rpx]; };
  const SEG = 64, RADIAL = 6;
  return {
    centre, timing, flatAt,
    pose(t) {
      const z = ease((t - timing.zoomStart) / (timing.zoomEnd - timing.zoomStart));
      const spin = ease(t / timing.zoomEnd);
      const rot = faceRotation({ lat: centre.lat, lon: lerp(lon0, centre.lon, spin) });
      globe.rotation.set(rot.x, rot.y, 0);
      stage.camera.zoom = lerp(1, ZOOM_END, z);
      stage.camera.updateProjectionMatrix();
      const px = 1 / (unit * stage.camera.zoom); // world units per pixel at this zoom
      if (glow) glow.material.opacity = ease(t);
      markers.forEach((m, i) => m.scale.setScalar(Math.max(0.0001, ease((t - (i ? timing.legAt(i - 1)[1] - 0.2 : 0.2)) / 0.4)) * 9 * px));
      const lift = 0.25 * (1 - z); // arcs settle onto the surface so the flat map matches
      arcs.forEach((a, i) => {
        const [s, e] = timing.legAt(i);
        const f = ease((t - s) / (e - s));
        a.mesh.visible = f > 0;
        if (!a.mesh.visible) return;
        a.mesh.geometry.dispose();
        const curve = new THREE.CatmullRomCurve3(arcPoints(a.from, a.to, { r: R * 1.003, lift, n: SEG }).map((p) => new THREE.Vector3(...p)));
        const geo = new THREE.TubeGeometry(curve, SEG, 3 * px, RADIAL, false);
        geo.setDrawRange(0, Math.round(f * SEG) * RADIAL * 6);
        a.mesh.geometry = geo;
      });
      layer.style.opacity = 1 - ease((t - timing.zoomStart) / 0.5);
      stage.draw();
      layout(t);
    },
    // Flat locator map: the globe's front view at its final zoom, drawn with the same projection and radius.
    flatMap(canvas) {
      const g = canvas.getContext("2d");
      const cx = stage.width / 2, cy = stage.height / 2, at = flatAt; // the canvas matches the stage size
      g.fillStyle = OCEAN; g.beginPath(); g.arc(cx, cy, Rpx, 0, 2 * Math.PI); g.fill();
      g.save(); g.clip();
      g.strokeStyle = BORDER; g.lineWidth = (2.5 * 2 * Math.PI * Rpx) / 6144; g.lineJoin = "round"; // line width: the texture line (2.5 texels) as it lands on screen
      for (const f of features) {
        g.beginPath();
        for (const ring of rings(f)) ring.forEach(([lon, lat], i) => g[i ? "lineTo" : "moveTo"](...at({ lat, lon })));
        g.fillStyle = f === country ? ACCENT : LAND; g.fill("evenodd");
        // Outline only where both ends face the viewer, so far-side points pushed to the limb leave no ring.
        g.beginPath();
        for (const ring of rings(f)) ring.forEach(([lon, lat], i) => {
          const here = orthoProject({ lat, lon }, centre)[2] >= 0, prev = i && orthoProject({ lat: ring[i - 1][1], lon: ring[i - 1][0] }, centre)[2] >= 0;
          if (here && prev) g.lineTo(...at({ lat, lon })); else g.moveTo(...at({ lat, lon }));
        });
        g.stroke();
      }
      g.strokeStyle = ACCENT; g.lineWidth = 6; g.lineCap = "round";
      for (const a of arcs) {
        g.beginPath();
        arcPoints(a.from, a.to, { r: 1, lift: 0, n: SEG }).forEach((p, i) => g[i ? "lineTo" : "moveTo"](...at(fromVec(p))));
        g.stroke();
      }
      g.fillStyle = ACCENT;
      for (const p of route) { g.beginPath(); g.arc(...at(p), 9, 0, 2 * Math.PI); g.fill(); }
      g.restore();
      g.fillStyle = BORDER; g.font = "600 40px 'Segoe UI', system-ui, sans-serif";
      g.strokeStyle = OCEAN; g.lineWidth = 8; for (const p of route) { const [x, y] = at(p); g.strokeText(p.name, x + 16, y - 20); g.fillText(p.name, x + 16, y - 20); }
    },
  };
}

