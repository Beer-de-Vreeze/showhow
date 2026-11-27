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

node("#path", nodes["#root"]).getAttribute = () => "M0 0L10 10";
node("#words", nodes["#root"]);
node("#num", nodes["#root"]);
node("#a", nodes["#root"]);
node("#b", nodes["#root"]);

globalThis.document = { querySelector: (s) => nodes[s] || null };
globalThis.gsap = { set: () => {} };
globalThis.SplitText = { create: () => ({ words: ["w1", "w2"] }) };
globalThis.window = globalThis;
new Function(readFileSync(new URL("../assets/kit/showhow-kit.js", import.meta.url), "utf8"))();

const tweens = [];
const calls = [];
const froms = [];
const kit = window.showhowKit({ fromTo: (target, from, to) => { tweens.push(target); calls.push(to); froms.push(from); } }, { root: "#root" }); // no #sh-cursor: fine until used

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

// 2D motion helpers: each writes fromTo tweens with immediateRender:false and throws on a missing element.
const helpers = {
  draw: (sel) => kit.draw(1, sel, 1),
  words: (sel) => kit.words(1, sel),
  count: (sel) => kit.count(1, sel, 0, 40, 1),
  morph: (sel) => kit.morph(1, sel, "M5 5L20 20", 1),
  along: (sel) => kit.along(1, sel, "#path", 1),
  rise: (sel) => kit.rise(1, [sel, "#b"]),
};
for (const [name, run] of Object.entries(helpers)) {
  const sel = name === "morph" ? "#path" : name === "words" ? "#words" : name === "count" ? "#num" : "#a";
  const before = calls.length;
  run(sel);
  if (calls.length === before || !calls.slice(before).every((c) => c.immediateRender === false)) throw new Error(`${name} needs fromTo with immediateRender:false`);
  expectThrow(() => run("#missing"), "no element #missing");
}
// rise is one fromTo per element, not one tween for the list.
const n = tweens.length;
kit.rise(1, ["#a", "#b"]);
if (tweens.length - n !== 2) throw new Error("rise must tween each element on its own");
// A second morph on one path starts from the first one's end shape, not the HTML d (call morphs in time order).
kit.morph(3, "#path", "M1 1L2 2", 1);
if (froms.at(-1).attr.d !== "M5 5L20 20") throw new Error(`chained morph started from ${froms.at(-1).attr.d}`);
console.log("ok");
