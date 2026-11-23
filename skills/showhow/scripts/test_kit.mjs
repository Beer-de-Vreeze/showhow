// Self-check for the showhow kit's guards, with a minimal fake DOM. Run:
//   node <skill-dir>/scripts/test_kit.mjs
// The visual behaviour (rings, cursor press) is checked by rendering fixtures/kit-demo.
import { readFileSync } from "node:fs";

const nodes = {
  "#root": { matches: (s) => s === "#root", offsetLeft: 0, offsetTop: 0, offsetParent: null, offsetWidth: 1920, offsetHeight: 1080, style: {} },
};
const node = (id, parent, w = 100, h = 40) =>
  (nodes[id] = { matches: (s) => s === id, offsetLeft: 10, offsetTop: 20, offsetParent: parent, offsetWidth: w, offsetHeight: h, style: {} });
node("#btn", nodes["#root"]);
node("#hidden", nodes["#root"], 0, 0);
node("#orphan", null);
node("#ring", nodes["#root"]);
node("#sh-count-1", nodes["#root"]);
node("#sh-count-2", nodes["#root"]);

globalThis.document = { querySelector: (s) => nodes[s] || null };
globalThis.gsap = { set: () => {} };
globalThis.window = globalThis;
new Function(readFileSync(new URL("../assets/kit/showhow-kit.js", import.meta.url), "utf8"))();

const tweens = [];
const kit = window.showhowKit({ fromTo: (target) => tweens.push(target) }, { root: "#root" }); // no #sh-cursor: fine until used

function expectThrow(fn, text) {
  try {
    fn();
  } catch (e) {
    if (!e.message.includes(text)) throw e;
    return;
  }
  throw new Error(`expected an error containing ${text}`);
}

kit.ring(1, "#btn", "#ring", 1);
const [x, y, w, h] = kit.R("#btn", 6);
if (x !== 4 || y !== 14 || w !== 112 || h !== 52) throw new Error(`R measured ${[x, y, w, h]}`);
expectThrow(() => kit.ring(1, "#hidden", "#ring", 1), "has no size");
expectThrow(() => kit.ring(1, "#orphan", "#ring", 1), "not inside a positioned");
expectThrow(() => kit.counter(1, 1), "must be 2 or more");
expectThrow(() => kit.move(1, "#btn"), "no element #sh-cursor");
kit.counter(2, 2);
if (tweens.length !== 4) throw new Error(`expected 4 tweens, got ${tweens.length}`);
console.log("ok");
