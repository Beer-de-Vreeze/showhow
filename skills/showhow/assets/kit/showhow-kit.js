// showhow kit: rings, cursor, click ripples and the step counter for a HyperFrames scene.
// Write every element in the scene's HTML with a stable id; the kit only measures and tweens.
// Every tween is a fromTo with immediateRender:false, so out-of-order seeks by render workers
// give the same frame. Call the functions after document.fonts.ready, before registering tl.
//
//   const kit = showhowKit(tl, { root: "#root", cursor: "#sh-cursor", cursorStart: [960, 900] });
//   kit.ring(2.0, "#btn-save", "#ring-01", 1.5);   // ring element on the target for 1.5s
//   kit.move(1.2, "#btn-save");                      // cursor tip to the target centre; call in time order
//   kit.ripple(1.9, "#btn-save", "#ripple-01");      // click ripple at the target centre
//   kit.counter(4.0, 2);                             // "#sh-count-1" out, "#sh-count-2" in
// 2D motion styles (references/motion-2d.md); the GSAP plugins come from the page's local gsap, never a CDN:
//   kit.draw(1.0, "#line-1", 0.8);                   // DrawSVG: the path draws itself (hide it in CSS first)
//   kit.words(1.0, "#quote");                        // SplitText: whole words rise out of a mask, 5 frames apart
//   kit.count(1.0, "#num", 0, 1700, 1.2);            // the number ticks from 0 to 1700
//   kit.bar(1.0, "#bar", "#bar-num", 8, 24, 1);      // the bar grows and its number ticks with it, always in step
//   kit.morph(1.0, "#shape", "M0 0L9 9", 0.8);       // MorphSVG: the path becomes the given path
//   kit.along(1.0, "#dot", "#route", 2);             // MotionPath: the element travels along the path
//   kit.rise(1.0, ["#a", "#b", "#c"]);               // flat scenes: each element settles up 24px, 0.15s apart
(function () {
  window.showhowKit = function (tl, opts) {
    // tip: offset from the cursor element's top-left to its arrow tip, shared by move and the press.
    const o = Object.assign({ root: "#root", cursor: "#sh-cursor", cursorStart: [0, 0], countPrefix: "#sh-count-", tip: [8, 5] }, opts);
    const el = (sel) => {
      const e = typeof sel === "string" ? document.querySelector(sel) : sel;
      if (!e) throw new Error(`showhowKit: no element ${sel}`);
      return e;
    };

    // Layout box [x, y, w, h] of a target in root pixels, padded by p, ignoring transforms.
    function R(sel, p = 6) {
      let e = el(sel);
      const w = e.offsetWidth, h = e.offsetHeight;
      // display:none (or not yet laid out) gives a 0x0 box at 0,0: a ring there points at nothing.
      if (!w || !h) throw new Error(`showhowKit: ${sel} has no size; is it hidden or not rendered yet?`);
      let x = 0, y = 0;
      while (e && !e.matches(o.root)) { x += e.offsetLeft; y += e.offsetTop; e = e.offsetParent; }
      // Walking past the root gives page coordinates; the root needs position: absolute or relative.
      if (!e) throw new Error(`showhowKit: ${sel} is not inside a positioned ${o.root}`);
      return [x - p, y - p, w + 2 * p, h + 2 * p];
    }

    // Static placement in root pixels, measured once at build time; tweens only touch opacity and transforms.
    function place(e, x, y, w, h) {
      Object.assign(e.style, { left: `${x}px`, top: `${y}px` });
      if (w !== undefined) Object.assign(e.style, { width: `${w}px`, height: `${h}px` });
    }

    // dy: known growth of content above the target by time t (it isn't laid out yet when you measure).
    function ring(t, target, ringSel, d, { pad = 6, dy = 0, fadeIn = 0.25, fadeOut = 0.15 } = {}) {
      const [x, y, w, h] = R(target, pad);
      const r = el(ringSel);
      place(r, x, y + dy, w, h);
      tl.fromTo(r, { opacity: 0 }, { opacity: 1, duration: fadeIn, immediateRender: false }, t);
      tl.fromTo(r, { opacity: 1 }, { opacity: 0, duration: fadeOut, immediateRender: false }, t + d);
    }

    // The cursor is only required once a scene moves or presses it; ring-only scenes need none.
    let cur = null;
    function cursor() {
      if (!cur) { cur = o.cursorStart.slice(); gsap.set(el(o.cursor), { x: cur[0], y: cur[1] }); }
    }
    function move(t, target, d = 0.6, { tip = o.tip, dy = 0 } = {}) {
      cursor();
      const [x, y, w, h] = R(target, 0);
      const to = [x + w / 2 - tip[0], y + h / 2 - tip[1] + dy];
      tl.fromTo(o.cursor, { x: cur[0], y: cur[1] }, { x: to[0], y: to[1], duration: d, ease: "power2.inOut", immediateRender: false }, t);
      cur = to;
    }

    // press: the cursor squashes over 2 frames and springs back over 3 (30fps) around its tip, so the click reads as physical
    // (timing from motionmaxxing, Apache-2.0). Pass press: false when no cursor is on screen.
    function ripple(t, target, rippleSel, { dy = 0, duration = 0.5, press = true, tip = o.tip } = {}) {
      const [x, y, w, h] = R(target, 0);
      const r = el(rippleSel);
      place(r, x + w / 2, y + h / 2 + dy);
      tl.fromTo(r, { xPercent: -50, yPercent: -50, scale: 0.3, opacity: 0.9 },
        { xPercent: -50, yPercent: -50, scale: 1.6, opacity: 0, duration, ease: "power2.out", immediateRender: false }, t);
      if (!press) return;
      cursor();
      const origin = `${tip[0]}px ${tip[1]}px`;
      tl.fromTo(o.cursor, { scale: 1, transformOrigin: origin }, { scale: 0.86, duration: 0.07, ease: "power2.out", immediateRender: false }, t - 0.07);
      tl.fromTo(o.cursor, { scale: 0.86, transformOrigin: origin }, { scale: 1, duration: 0.1, ease: "power2.out", immediateRender: false }, t);
    }

    function counter(t, n, { fade = 0.3 } = {}) {
      // The first counter span is shown by CSS; counter() switches from n-1 to n, so n starts at 2.
      if (!(n >= 2)) throw new Error(`showhowKit: counter(t, ${n}) switches from step n-1, so n must be 2 or more`);
      el(o.countPrefix + (n - 1)); el(o.countPrefix + n);
      tl.fromTo(o.countPrefix + (n - 1), { opacity: 1 }, { opacity: 0, duration: fade, immediateRender: false }, t);
      tl.fromTo(o.countPrefix + n, { opacity: 0 }, { opacity: 1, duration: fade, immediateRender: false }, t);
    }

    // 2D motion styles. Starting states (hidden paths, offset words) belong in CSS; these tweens only run the entrance.
    // A missing plugin would leave a still frame with no error; name it instead.
    const need = (plugin, fn) => {
      if (typeof window[plugin] === "undefined") throw new Error(`showhowKit: ${fn} needs the ${plugin} loaded and registered`);
    };
    function draw(t, sel, d, { ease = "none" } = {}) {
      need("DrawSVGPlugin", "draw");
      const e = el(sel);
      tl.fromTo(e, { drawSVG: "0%", opacity: 1 }, { drawSVG: "100%", opacity: 1, duration: d, ease, immediateRender: false }, t);
    }

    // Call after document.fonts.ready: SplitText measures the lines. gap 0.15s = 5 frames at 30fps.
    function words(t, sel, { gap = 0.15, duration = 0.33 } = {}) {
      const e = el(sel);
      need("SplitText", "words");
      const s = SplitText.create(e, { type: "words", mask: "words" });
      // The words exist only after the split, so CSS can't hide them: hide them here or the full text shows until t.
      gsap.set(s.words, { yPercent: 110 });
      tl.fromTo(s.words, { yPercent: 110 }, { yPercent: 0, duration, ease: "power3.out", stagger: gap, immediateRender: false }, t);
    }

    // The element's own text is the from value; write it in the HTML so frame 0 shows it.
    function count(t, sel, from, to, d, { decimals = 0 } = {}) {
      const e = el(sel);
      const fmt = (v) => Number(v).toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
      tl.fromTo(e, { textContent: from }, { textContent: to, duration: d, ease: "power1.out", modifiers: { textContent: fmt }, immediateRender: false }, t);
    }

    // A bar and its number as one value: height value / max and the label tick through the same ease and timing,
    // so the drawn bar never disagrees with its label (chart honesty, motion-2d.md). Write the from value in the
    // label's HTML and size the bar's CSS at from / max. SVG <rect> bars pass svgOrigin: "0 <baseline y>".
    function bar(t, sel, label, from, to, d, { max = Math.max(from, to), ease = "power1.out", decimals = 0, svgOrigin } = {}) {
      const e = el(sel), l = el(label);
      if (!(max > 0) || Math.max(from, to) > max) throw new Error(`showhowKit: bar ${sel} needs a max of at least ${Math.max(from, to)}`);
      const origin = svgOrigin ? { svgOrigin } : { transformOrigin: "50% 100%" };
      const fmt = (v) => Number(v).toLocaleString("en-US", { minimumFractionDigits: decimals, maximumFractionDigits: decimals });
      tl.fromTo(e, { scaleY: from / max, ...origin }, { scaleY: to / max, ...origin, duration: d, ease, immediateRender: false }, t);
      tl.fromTo(l, { textContent: from }, { textContent: to, duration: d, ease, modifiers: { textContent: fmt }, immediateRender: false }, t);
    }

    // The from shape is the path's HTML d, or the end shape of its previous morph (call morphs in time order),
    // so a second morph continues instead of snapping back to the HTML shape. toShape is path data or a path's selector.
    const shapes = new Map();
    function morph(t, sel, toShape, d, { ease = "power2.inOut" } = {}) {
      need("MorphSVGPlugin", "morph");
      const e = el(sel);
      const end = /^\s*[Mm]/.test(toShape) ? toShape : el(toShape).getAttribute("d"); // stored as path data, never "#circle"
      tl.fromTo(e, { attr: { d: shapes.get(e) ?? e.getAttribute("d") } }, { morphSVG: toShape, duration: d, ease, immediateRender: false }, t);
      shapes.set(e, end);
    }

    function along(t, sel, path, d, { ease = "power1.inOut", autoRotate = false } = {}) {
      need("MotionPathPlugin", "along");
      const e = el(sel);
      el(path);
      const mp = { path, align: path, alignOrigin: [0.5, 0.5], autoRotate };
      tl.fromTo(e, { motionPath: { ...mp, start: 0, end: 0 } }, { motionPath: { ...mp, start: 0, end: 1 }, duration: d, ease, immediateRender: false }, t);
    }

    // One fromTo per element, not a stagger, so each element keeps its own tween.
    function rise(t, sels, { gap = 0.15, dy = 24, duration = 0.33 } = {}) {
      sels.forEach((sel, i) => {
        tl.fromTo(el(sel), { y: dy, opacity: 0 }, { y: 0, opacity: 1, duration, ease: "power3.out", immediateRender: false }, t + i * gap);
      });
    }

    return { R, ring, move, ripple, counter, draw, words, count, bar, morph, along, rise };
  };
})();
