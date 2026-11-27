// scene3d kind "hero-number": one key figure (Params.value) as extruded 3D text, swinging into view.
// The text is String(Params.value), so what is on screen is what P-params checked is spoken.
import { THREE, part, ease, lerp } from "./scene3d.js";
import { FontLoader } from "three/addons/loaders/FontLoader.js";
import { TextGeometry } from "three/addons/geometries/TextGeometry.js";

// A typeface JSON shipped with three.js (MIT); swap the URL for another converted font.
export const FONT_URL = "https://cdn.jsdelivr.net/npm/three@0.184.0/examples/fonts/helvetiker_bold.typeface.json";

export async function buildHeroNumber(stage, P, { fontUrl = FONT_URL, color = "#e0533d", width = 14 } = {}) {
  if (P.value === undefined) throw new Error("hero-number: Params.value is required");
  const font = await new FontLoader().loadAsync(fontUrl);
  const geo = new TextGeometry(String(P.value), { font, size: 3, depth: 1.2, curveSegments: 8, bevelEnabled: true, bevelThickness: 0.12, bevelSize: 0.08, bevelSegments: 2 });
  geo.computeBoundingBox();
  const box = geo.boundingBox, centre = box.getCenter(new THREE.Vector3());
  geo.translate(-centre.x, -centre.y, -centre.z);
  const mesh = part(geo, stage, { color });
  mesh.scale.setScalar(Math.min(1.6, width / (box.max.x - box.min.x)));
  stage.scene.add(mesh);
  await stage.renderer.compileAsync(stage.scene, stage.camera);
  return (t) => {
    const k = ease(t / 1.6);
    mesh.rotation.set(-0.12, lerp(-1.1, 0.22, k) + 0.1 * Math.sin(t * 0.9), 0);
    mesh.position.y = lerp(-1.5, 0, k);
    stage.draw();
  };
}
