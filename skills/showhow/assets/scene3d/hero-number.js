// scene3d kind "hero-number": one key figure (Params.value) as extruded 3D text, swinging into view.
// The text is String(Params.value), so what is on screen is what P-params checked is spoken.
import { THREE, part, ease, lerp, theme, glyphOffsets } from "./scene3d.js";
import { FontLoader } from "three/addons/loaders/FontLoader.js";
import { TextGeometry } from "three/addons/geometries/TextGeometry.js";

// A typeface JSON from three's own package (examples/fonts, MIT), staged beside scene3d by stage.py; pass fontUrl
// for another converted font.
export const FONT_URL = new URL("../three/examples/fonts/helvetiker_bold.typeface.json", import.meta.url).href;

// Fill defaults to the theme accent: the number is the one thing the narration points at.
export async function buildHeroNumber(stage, P, { fontUrl = FONT_URL, color = theme.accent, width = 14, gap = 0.3 } = {}) {
  if (!String(P.value ?? "").trim()) throw new Error("hero-number: Params.value is required and must not be empty");
  const font = await new FontLoader().loadAsync(fontUrl);
  const size = 3;
  // One mesh per glyph, so each can be spaced by its extruded, projected bounds (a whole string overlaps once turned).
  const geos = [...String(P.value)].map((ch) => {
    const g = new TextGeometry(ch, { font, size, depth: 1.2, curveSegments: 8, bevelEnabled: true, bevelThickness: 0.12, bevelSize: 0.08, bevelSegments: 2 });
    g.computeBoundingBox();
    return g.boundingBox.isEmpty() ? null : g; // a space has no geometry
  });
  const boxes = geos.map((g) => (g ? { x0: g.boundingBox.min.x, x1: g.boundingBox.max.x, z0: g.boundingBox.min.z, z1: g.boundingBox.max.z } : { x0: 0, x1: size * 0.35, z0: 0, z1: 0 }));
  const all = new THREE.Box3();
  geos.forEach((g) => g && all.union(g.boundingBox));
  const centre = all.getCenter(new THREE.Vector3());
  const group = new THREE.Group();
  const glyphs = geos.map((g) => {
    if (!g) return null;
    g.translate(0, -centre.y, -centre.z);
    const m = part(g, stage, { color });
    group.add(m);
    return m;
  });
  // Places the row for turn `a` and returns its extent in unturned x.
  const place = (a) => {
    const off = glyphOffsets(boxes, a, gap), last = boxes.length - 1;
    glyphs.forEach((m, i) => m && (m.position.x = off[i]));
    return { x0: boxes[0].x0, x1: boxes[last].x1 + off[last] };
  };
  const rest = place(0.22);
  group.scale.setScalar(Math.min(1.6, width / (rest.x1 - rest.x0)));
  stage.scene.add(group);
  await stage.renderer.compileAsync(stage.scene, stage.camera);
  return (t) => {
    const k = ease(t / 1.6), a = lerp(-1.1, 0.22, k) + 0.1 * Math.sin(t * 0.9);
    const span = place(a);
    glyphs.forEach((m) => m && (m.position.x -= (span.x0 + span.x1) / 2)); // centred for this turn
    group.rotation.set(-0.12, a, 0);
    group.position.y = lerp(-1.5, 0, k);
    stage.draw();
  };
}
