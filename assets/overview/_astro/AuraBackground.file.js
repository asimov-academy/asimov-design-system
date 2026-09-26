(() => {
  var __defProp = Object.defineProperty;
  var __getOwnPropNames = Object.getOwnPropertyNames;
  var __esm = (fn, res) => function __init() {
    return fn && (res = (0, fn[__getOwnPropNames(fn)[0]])(fn = 0)), res;
  };
  var __export = (target, all) => {
    for (var name in all)
      __defProp(target, name, { get: all[name], enumerable: true });
  };

  // extract-ds/lp.asimov.academy 2.0-design-system/assets/overview/_astro/perf-variant.-tKUhnCa.js
  var perf_variant_tKUhnCa_exports = {};
  __export(perf_variant_tKUhnCa_exports, {
    getPerfFlags: () => d2,
    initPerfDiag: () => m,
    markPerf: () => f,
    shouldSkipUnicornOnThisViewport: () => g
  });
  function w(e) {
    return e.split(/[+,]/).map((r2) => r2.trim().toLowerCase()).filter(Boolean);
  }
  function d2(e = typeof location < "u" ? location.search : "") {
    if (p) return p;
    const r2 = new URLSearchParams(e), a = (r2.get("perfVariant") || "").trim(), o = w(a || "current");
    let t = "current", c = false, s = false;
    const i = (r2.get("delayed-spark-network") || "").trim().toLowerCase();
    i === "proof" && (t = "proof"), i === "adaptive" && (t = "adaptive");
    for (const n of o) if (n !== "current") {
      if (n === "static-control") {
        s = true, t = "static";
        continue;
      }
      if (n === "no-unicorn-download") {
        c = true;
        continue;
      }
      if (n === "adaptive-no-unicorn") {
        t = "adaptive", c = true;
        continue;
      }
      if (n === "delayed-spark-network-proof" || n === "delayed-spark-network=proof" || n === "proof") {
        t = "proof";
        continue;
      }
      if (n === "delayed-spark-network-adaptive" || n === "delayed-spark-network=adaptive" || n === "adaptive") {
        t = "adaptive";
        continue;
      }
      n === "delayed-spark-network" && (t = (r2.get("sparkDelay") || r2.get("mode") || "adaptive").toLowerCase() === "proof" ? "proof" : "adaptive");
    }
    s && (t = "static");
    const u = r2.get("perfDiag") === "1" || r2.has("perfDiag"), l2 = s || c || t !== "current" || a !== "" && a.toLowerCase() !== "current" || !!i;
    return p = { raw: a || (i ? `delayed-spark-network=${i}` : "current"), sparkMode: t, noUnicornDownload: c, staticControl: s, diag: u || l2 }, p;
  }
  function f(e) {
    const r2 = d2();
    if (!r2.diag || typeof performance > "u") return;
    const a = window, o = a.__AA_PERF__ || (a.__AA_PERF__ = { t0: performance.now(), events: [] }), t = performance.now();
    o.events.push({ name: e, t });
    try {
      performance.mark(`aa:${e}`);
    } catch {
    }
    e === "load" && (o.load = t), e === "spark-import-start" && (o.sparkImportStart = t), e === "spark-import-end" && (o.sparkImportEnd = t), e === "spark-first-frame" && (o.sparkFirstFrame = t), e === "unicorn-start" && (o.unicornStart = t), e === "first-input" && (o.firstInput = t), r2.diag && console.info(`[aa:perf] ${e}`, Math.round(t));
  }
  function m() {
    if (!d2().diag || typeof window > "u") return;
    const r2 = window;
    if (r2.__AA_PERF__?.events.some((o) => o.name === "diag-init")) return;
    r2.__AA_PERF__ || (r2.__AA_PERF__ = { t0: performance.now(), events: [] }), f("diag-init"), document.readyState === "complete" ? f("load") : window.addEventListener("load", () => f("load"), { once: true });
    const a = () => f("first-input");
    for (const o of ["pointerdown", "keydown", "touchstart", "click"]) window.addEventListener(o, a, { once: true, passive: true, capture: true });
    try {
      new PerformanceObserver((t) => {
        for (const c of t.getEntries()) {
          const s = c.startTime, i = r2.__AA_PERF__;
          i && (i.lcp = s), f(`lcp:${Math.round(s)}`);
        }
      }).observe({ type: "largest-contentful-paint", buffered: true });
    } catch {
    }
  }
  function g(e = d2()) {
    return e.staticControl ? true : e.noUnicornDownload ? window.matchMedia("(max-width: 768px)").matches : false;
  }
  var p;
  var init_perf_variant_tKUhnCa = __esm({
    "extract-ds/lp.asimov.academy 2.0-design-system/assets/overview/_astro/perf-variant.-tKUhnCa.js"() {
      p = null;
    }
  });

  // extract-ds/lp.asimov.academy 2.0-design-system/assets/overview/_astro/preload-helper.CVfkMyKi.js
  var h = (function() {
    const s = typeof document < "u" && document.createElement("link").relList;
    return s && s.supports && s.supports("modulepreload") ? "modulepreload" : "preload";
  })();
  var v = function(l2) {
    return "/" + l2;
  };
  var d = {};
  var y = function(s, i, E) {
    let a = Promise.resolve();
    if (i && i.length > 0) {
      let f2 = function(e) {
        return Promise.all(e.map((o) => Promise.resolve(o).then((c) => ({ status: "fulfilled", value: c }), (c) => ({ status: "rejected", reason: c }))));
      };
      document.getElementsByTagName("link");
      const r2 = document.querySelector("meta[property=csp-nonce]"), t = r2?.nonce || r2?.getAttribute("nonce");
      a = f2(i.map((e) => {
        if (e = v(e), e in d) return;
        d[e] = true;
        const o = e.endsWith(".css"), c = o ? '[rel="stylesheet"]' : "";
        if (document.querySelector(`link[href="${e}"]${c}`)) return;
        const n = document.createElement("link");
        if (n.rel = o ? "stylesheet" : h, o || (n.as = "script"), n.crossOrigin = "", n.href = e, t && n.setAttribute("nonce", t), document.head.appendChild(n), o) return new Promise((m2, p2) => {
          n.addEventListener("load", m2), n.addEventListener("error", () => p2(new Error(`Unable to preload CSS for ${e}`)));
        });
      }));
    }
    function u(r2) {
      const t = new Event("vite:preloadError", { cancelable: true });
      if (t.payload = r2, window.dispatchEvent(t), !t.defaultPrevented) throw r2;
    }
    return a.then((r2) => {
      for (const t of r2 || []) t.status === "rejected" && u(t.reason);
      return s().catch(u);
    });
  };

  // extract-ds/lp.asimov.academy 2.0-design-system/assets/overview/_astro/AuraBackground.astro_astro_type_script_index_0_lang.BMCrMHec.js
  var r = null;
  function b() {
    if (r !== null) return r;
    if (typeof document > "u") return r = false, false;
    try {
      const e = document.createElement("canvas"), o = { failIfMajorPerformanceCaveat: true }, t = e.getContext("webgl", o) || e.getContext("experimental-webgl", o);
      return t ? (t.getExtension("WEBGL_lose_context")?.loseContext(), r = true, true) : (r = false, false);
    } catch {
      return r = false, false;
    }
  }
  var d3 = "vendor/unicornstudio/unicornStudio.umd.js";
  var d4 = "vendor/unicornstudio/aura-scene.js";
  var g2 = () => {
    try {
      return /[?&](perfVariant=|perfDiag(?:[=&]|$)|delayed-spark-network=)/.test(location.search || "");
    } catch {
      return false;
    }
  };
  async function l() {
    const e = document.querySelector("[data-aura-root]");
    if (!e || e.dataset.auraBooted === "1") return;
    if (e.dataset.auraBooted = "1", g2()) {
      const { getPerfFlags: n, initPerfDiag: a, markPerf: i, shouldSkipUnicornOnThisViewport: u } = await y(async () => {
        const { getPerfFlags: p2, initPerfDiag: y2, markPerf: S, shouldSkipUnicornOnThisViewport: v2 } = await Promise.resolve().then(() => (init_perf_variant_tKUhnCa(), perf_variant_tKUhnCa_exports));
        return { getPerfFlags: p2, initPerfDiag: y2, markPerf: S, shouldSkipUnicornOnThisViewport: v2 };
      }, []);
      if (a(), u(n())) {
        e.classList.add("aura-background--no-unicorn"), e.dataset.deferBoot === "1" && (e.dataset.auraReady = "1"), i("unicorn-skipped");
        return;
      }
    }
    if (e.dataset.mobileLite === "1") {
      const n = navigator.connection?.saveData === true, a = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      if (n || a) {
        e.classList.add("aura-background--no-unicorn"), e.dataset.deferBoot === "1" && (e.dataset.auraReady = "1");
        return;
      }
    }
    const o = () => {
      e.classList.add("aura-background--no-unicorn"), e.dataset.deferBoot === "1" && (e.dataset.auraReady = "1");
    };
    if (!b()) {
      o();
      return;
    }
    const t = window, c = () => {
      if (document.querySelector(`script[src="${d3}"]`)) return;
      t.UnicornStudio || (t.UnicornStudio = { isInitialized: false });
      const n = document.createElement("script");
      n.src = d3, n.async = true, (document.head || document.body).appendChild(n);
    }, f2 = () => {
      if (e.dataset.auraReady === "1") return;
      const n = e.querySelector("[data-us-project]"), a = () => {
        requestAnimationFrame(() => {
          e.dataset.auraReady = "1";
        });
      };
      if (n?.querySelector("canvas")) {
        a();
        return;
      }
      let i = 0;
      const u = window.setInterval(() => {
        i++, (n?.querySelector("canvas") || i >= 60) && (window.clearInterval(u), a());
      }, 50);
    }, h2 = () => {
      // Cena local (sem projectId remoto) com orçamento de GPU explícito: dpi 1 e 30 fps.
      // O runtime compensa a velocidade da animação pelo fps, então o ritmo não muda.
      const n = e.querySelector("[data-us-project]"), a = () => {
        if (!window.AsimovAuraScene || !n) return o();
        let i = document.getElementById("asimov-aura-scene");
        if (!i) {
          i = document.createElement("script");
          i.type = "application/json", i.id = "asimov-aura-scene", i.textContent = JSON.stringify(window.AsimovAuraScene);
          document.head.appendChild(i);
        }
        // filePath com o id de um elemento: o runtime lê o JSON do DOM, sem fetch (funciona via file://).
        t.UnicornStudio.addScene({
          element: n, filePath: i.id, dpi: 1, fps: 30, scale: 1, production: true, lazyLoad: false,
          fixed: getComputedStyle(e).position === "fixed", interactivity: { mouse: { disabled: true } }
        }).catch(o);
      };
      if (window.AsimovAuraScene) return a();
      const i = document.createElement("script");
      i.src = d4, i.onload = a, i.onerror = o, (document.head || document.body).appendChild(i);
    }, s = () => {
      if (document.visibilityState !== "visible") {
        document.addEventListener("visibilitychange", () => {
          document.visibilityState === "visible" && s();
        }, { once: true });
        return;
      }
      if (t.UnicornStudio?.isInitialized) {
        f2();
        return;
      }
      t.UnicornStudio || (t.UnicornStudio = { isInitialized: false });
      const n = () => {
        t.UnicornStudio?.isInitialized || (t.UnicornStudio?.addScene && h2(), t.UnicornStudio && (t.UnicornStudio.isInitialized = true)), f2();
      }, a = document.querySelector(`script[src="${d3}"]`);
      if (a) {
        t.UnicornStudio && "init" in t.UnicornStudio && typeof t.UnicornStudio.init == "function" ? n() : (a.addEventListener("load", n, { once: true }), window.setTimeout(n, 800));
        return;
      }
      const i = document.createElement("script");
      i.src = d3, i.async = true, i.onload = n, (document.head || document.body).appendChild(i);
    }, m2 = () => {
      "requestIdleCallback" in window ? requestIdleCallback(() => s(), { timeout: 400 }) : requestAnimationFrame(() => s());
    };
    if (e.dataset.deferBoot === "1") {
      requestAnimationFrame(() => {
        "requestIdleCallback" in window ? requestIdleCallback(() => c(), { timeout: 2e3 }) : setTimeout(c, 400);
      }), requestAnimationFrame(() => requestAnimationFrame(m2));
      return;
    }
    s();
  }
  document.readyState === "loading" ? document.addEventListener("DOMContentLoaded", l, { once: true }) : l();
  document.addEventListener("astro:page-load", () => {
    const e = document.querySelector("[data-aura-root]");
    e && (delete e.dataset.auraBooted, delete e.dataset.auraReady), l();
  });
})();
