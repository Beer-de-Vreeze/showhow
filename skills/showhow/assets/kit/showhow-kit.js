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
(function () {
  window.showhowKit = function (tl, opts) {
    const o = Object.assign({ root: "#root", cursor: "#sh-cursor", cursorStart: [0, 0], countPrefix: "#sh-count-" }, opts);
    const el = (sel) => {
      const e = typeof sel === "string" ? document.querySelector(sel) : sel;
      if (!e) throw new Error(`showhowKit: no element ${sel}`);
      return e;
    };

    // Layout box [x, y, w, h] of a target in root pixels, padded by p, ignoring transforms.
    function R(sel, p = 6) {
      let e = el(sel);
      const w = e.offsetWidth, h = e.offsetHeight;
      let x = 0, y = 0;
      while (e && !e.matches(o.root)) { x += e.offsetLeft; y += e.offsetTop; e = e.offsetParent; }
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

    // tip: offset from the cursor element's top-left to its arrow tip.
    let cur = o.cursorStart.slice();
    gsap.set(el(o.cursor), { x: cur[0], y: cur[1] });
    function move(t, target, d = 0.6, { tip = [8, 5], dy = 0 } = {}) {
      const [x, y, w, h] = R(target, 0);
      const to = [x + w / 2 - tip[0], y + h / 2 - tip[1] + dy];
      tl.fromTo(o.cursor, { x: cur[0], y: cur[1] }, { x: to[0], y: to[1], duration: d, ease: "power2.inOut", immediateRender: false }, t);
      cur = to;
    }

    function ripple(t, target, rippleSel, { dy = 0, duration = 0.5 } = {}) {
      const [x, y, w, h] = R(target, 0);
      const r = el(rippleSel);
      place(r, x + w / 2, y + h / 2 + dy);
      tl.fromTo(r, { xPercent: -50, yPercent: -50, scale: 0.3, opacity: 0.9 },
        { xPercent: -50, yPercent: -50, scale: 1.6, opacity: 0, duration, ease: "power2.out", immediateRender: false }, t);
    }

    function counter(t, n, { fade = 0.3 } = {}) {
      tl.fromTo(o.countPrefix + (n - 1), { opacity: 1 }, { opacity: 0, duration: fade, immediateRender: false }, t);
      tl.fromTo(o.countPrefix + n, { opacity: 0 }, { opacity: 1, duration: fade, immediateRender: false }, t);
    }

    return { R, ring, move, ripple, counter };
  };
})();
