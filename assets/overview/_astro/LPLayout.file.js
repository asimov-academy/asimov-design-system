(() => {
  // extract-ds/lp.asimov.academy 2.0-design-system/assets/overview/_astro/HotmartUtm.client.CF1FRD68.js
  var y = "pay.hotmart.com";
  var k = "/vsl/";
  var l = "-pricing";
  var b = ["formacoes/", "trilhas/"];
  function g(t2) {
    let e2 = t2.trim();
    if (!e2 || e2 === "/") return "home";
    const n2 = e2.includes(k);
    if (e2 = e2.replace(/^\/+/, "").replace(/\/+$/, ""), !e2) return "home";
    for (const o2 of b) if (e2.startsWith(o2)) {
      e2 = e2.slice(o2.length);
      break;
    }
    let r4 = e2.replace(/\//g, "_") || "home";
    return n2 && !r4.endsWith(l) && (r4 = `${r4}${l}`), r4;
  }
  function T(t2) {
    try {
      return new URL(t2.trim()).hostname === y;
    } catch {
      return false;
    }
  }
  function _(t2, e2) {
    if (!T(t2)) return t2;
    const n2 = new URL(t2.trim());
    return n2.searchParams.set("sck", g(e2)), n2.toString();
  }
  var U = 'a[href*="pay.hotmart.com"]';
  function C(t2 = window.location.pathname) {
    document.querySelectorAll(U).forEach((e2) => {
      const n2 = e2.getAttribute("href");
      n2 && (e2.href = _(n2, t2));
    });
  }
  var f = /^[0-9a-f]{32}$/;
  var H = ["source", "medium", "campaign", "content", "term", "id"];
  var d = /^utm_/i;
  var A = "aa-hotmart-utm-boot";
  function L(t2) {
    return t2.trim().replace(/\|/g, "-").replace(/\s+/g, "-");
  }
  function M(t2) {
    const e2 = t2.startsWith("?") ? t2.slice(1) : t2, n2 = new URLSearchParams(e2), r4 = /* @__PURE__ */ new Set(), o2 = [];
    for (const [s4, m] of n2.entries()) {
      if (!d.test(s4)) continue;
      const a4 = s4.replace(d, "").toLowerCase();
      if (!a4 || r4.has(a4)) continue;
      const c3 = L(m);
      c3 && (r4.add(a4), o2.push({ key: a4, value: c3 }));
    }
    return o2;
  }
  function O(t2) {
    const e2 = new Map(t2.map((o2) => [o2.key, o2])), n2 = [];
    for (const o2 of H) {
      const s4 = e2.get(o2);
      s4 && (n2.push(s4), e2.delete(o2));
    }
    const r4 = [...e2.values()].sort((o2, s4) => o2.key.localeCompare(s4.key));
    return n2.push(...r4), n2;
  }
  function P(t2, e2) {
    const n2 = (t2 || "home").trim() || "home", r4 = O(M(e2));
    return r4.length === 0 ? n2 : [n2, ...r4.map((o2) => `${o2.key}-${o2.value}`)].join("|");
  }
  function v(t2, e2, n2) {
    if (!T(t2)) return t2;
    const r4 = new URL(t2.trim()), o2 = (r4.searchParams.get("sck") || "").split("|").map((i3) => i3.trim()).filter(Boolean), s4 = o2.find((i3) => f.test(i3)), a4 = o2.find((i3) => !f.test(i3)) || g(e2), [c3, ...u2] = P(a4, n2).split("|"), S = s4 ? [c3, s4, ...u2] : [c3, ...u2];
    return r4.searchParams.set("sck", S.join("|")), r4.toString();
  }
  var E = 'a[href*="pay.hotmart.com"], a.smartplayer-anchor-button';
  var h = false;
  var p = false;
  function R(t2, e2, n2) {
    const r4 = t2.getAttribute("href");
    if (!r4) return;
    const o2 = v(r4, e2, n2);
    if (!(o2 === r4 || o2 === t2.href)) {
      try {
        const s4 = new URL(t2.href, window.location.origin).searchParams.get("sck"), m = new URL(o2, window.location.origin).searchParams.get("sck");
        if (s4 === m) return;
      } catch {
      }
      t2.href = o2;
    }
  }
  function w(t2, e2) {
    document.querySelectorAll(E).forEach((n2) => {
      R(n2, t2, e2);
    });
  }
  function I(t2 = window.location.pathname, e2 = window.location.search) {
    if (document.documentElement.dataset.aaHotmartUtm = A, w(t2, e2), !h && typeof MutationObserver < "u" && document.body) {
      h = true;
      let n2 = false;
      new MutationObserver(() => {
        n2 || (n2 = true, requestAnimationFrame(() => {
          n2 = false, w(window.location.pathname, window.location.search);
        }));
      }).observe(document.body, { childList: true, subtree: true });
    }
    p || (p = true, document.addEventListener("pointerdown", (n2) => {
      const r4 = n2.target;
      if (!(r4 instanceof Element)) return;
      const o2 = r4.closest(E);
      o2 instanceof HTMLAnchorElement && R(o2, window.location.pathname, window.location.search);
    }, true));
  }

  // extract-ds/lp.asimov.academy 2.0-design-system/assets/overview/_astro/ScrollReveal.client.aZGqK-Zn.js
  var i = { pathname: "", completed: /* @__PURE__ */ new Set() };
  function r() {
    const e2 = window;
    e2.__inViewIO?.disconnect(), e2.__inViewIO = void 0;
  }
  function a() {
    const e2 = location.pathname;
    e2 !== i.pathname && (i.pathname = e2, i.completed.clear(), r());
  }
  function s(e2, t2) {
    a(), !i.completed.has(e2) && (i.completed.add(e2), t2());
  }
  var d2 = () => window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function w2(e2) {
    const t2 = document.querySelectorAll(e2);
    if (d2()) {
      t2.forEach((n2) => n2.classList.add("in-view"));
      return;
    }
    const o2 = window;
    o2.__inViewIO || (o2.__inViewIO = new IntersectionObserver((n2) => {
      n2.forEach((c3) => {
        c3.isIntersecting && (c3.target.classList.add("in-view"), o2.__inViewIO?.unobserve(c3.target));
      });
    }, { threshold: 0.05, rootMargin: "0px 0px 12% 0px" })), t2.forEach((n2) => {
      o2.__inViewIO?.observe(n2);
    });
  }
  function l2(e2 = ".animate-on-scroll") {
    s("scrollReveal", () => w2(e2));
  }

  // extract-ds/lp.asimov.academy 2.0-design-system/assets/overview/_astro/OverflowLock.client.vCHvh3MW.js
  function e() {
    const l4 = document.documentElement, n2 = document.body;
    l4.style.overflowX = "clip", n2.style.overflowX = "clip", window.scrollX !== 0 && window.scrollTo(0, window.scrollY);
  }
  function r2() {
    s("overflowLock", e);
  }
  var o = 0;
  function c() {
    o && window.clearTimeout(o), o = window.setTimeout(() => {
      o = 0, e();
    }, 100);
  }

  // extract-ds/lp.asimov.academy 2.0-design-system/assets/overview/_astro/lead-tracker-events.v7xkezV7.js
  function a2() {
    const t2 = window.asq;
    return typeof t2 == "function" ? t2 : void 0;
  }
  function c2(t2) {
    try {
      a2()?.("track", "lead_form_submit", t2);
    } catch {
    }
  }

  // extract-ds/lp.asimov.academy 2.0-design-system/assets/overview/_astro/sanitize.DTMRfr3n.js
  var n = { fullName: 120, email: 120 };
  function t(e2, i3) {
    return e2.slice(0, i3);
  }
  function a3(e2, i3) {
    return t(e2.normalize("NFKC").replace(/[\u0000-\u001F\u007F\u200B-\u200D\uFEFF]/g, "").replace(/\s+/g, " "), i3);
  }
  function r3(e2) {
    return a3(e2, n.fullName).trim();
  }
  function s2(e2) {
    return t(e2.normalize("NFKC").replace(/\s+/g, "").trim().toLowerCase(), n.email);
  }
  function l3(e2) {
    return e2.replace(/\D/g, "");
  }
  function u(e2) {
    let i3 = l3(e2);
    return (i3.length === 12 || i3.length === 13) && i3.startsWith("55") && (i3 = i3.slice(2)), i3.slice(0, 11);
  }

  // extract-ds/lp.asimov.academy 2.0-design-system/assets/overview/_astro/LPLayout.astro_astro_type_script_index_0_lang.DiO7WEqH.js
  var w3 = "https://flowhooks.asimovautomations.com/webhook/form-pre-checkout";
  function A2(e2) {
    const t2 = new URLSearchParams();
    t2.set("form_fields[name]", e2.name.trim()), t2.set("form_fields[email]", e2.email.trim()), t2.set("form_fields[phone]", e2.phone.trim());
    const o2 = g(e2.pathname);
    return t2.set("form_fields[tag]", o2), t2.set("form_fields[origem]", o2), t2.set("form_fields[url]", window.location.href), e2.planId && t2.set("form_fields[plan_id]", e2.planId), e2.productName && t2.set("form_fields[product_name]", e2.productName), e2.hotmartCheckoutCode && t2.set("form_fields[hotmart_checkout_code]", e2.hotmartCheckoutCode), t2;
  }
  function $(e2) {
    try {
      const t2 = new URL(e2.trim());
      return t2.hostname !== "pay.hotmart.com" ? null : t2.pathname;
    } catch {
      return null;
    }
  }
  function F(e2) {
    try {
      const t2 = new URL(e2.trim());
      return t2.hostname !== "pay.hotmart.com" ? null : t2.searchParams.get("off")?.trim() || null;
    } catch {
      return null;
    }
  }
  function R2() {
    const e2 = document.getElementById("pre-checkout-catalog");
    if (!e2?.textContent) return null;
    try {
      return JSON.parse(e2.textContent);
    } catch {
      return null;
    }
  }
  function z(e2, t2) {
    const o2 = $(e2);
    return o2 ? t2.byCheckoutPath[o2] ?? null : null;
  }
  function N(e2) {
    const t2 = e2.replace(/\D/g, "");
    return t2.length < 10 ? null : { phoneac: t2.slice(0, 2), phonenumber: t2.slice(2) };
  }
  function D(e2, t2) {
    if (!e2 || !T(e2)) return e2;
    const o2 = new URL(e2.trim()), a4 = (t2.name || "").trim(), r4 = (t2.email || "").trim();
    a4 && o2.searchParams.set("name", a4), r4 && o2.searchParams.set("email", r4);
    const n2 = t2.phone ? N(t2.phone) : null;
    return n2 && (o2.searchParams.set("phoneac", n2.phoneac), o2.searchParams.set("phonenumber", n2.phonenumber)), o2.toString();
  }
  var x = 'a[href*="pay.hotmart.com"]';
  function M2() {
    return /^\/misc\/base-de-livros\/[^/]+\/?$/.test(window.location.pathname);
  }
  var k2 = "";
  var i2 = null;
  var g2 = "";
  var y2 = false;
  function K(e2) {
    const t2 = e2.replace(/\D/g, "").slice(0, 11);
    return t2.length <= 2 ? t2.replace(/^(\d{0,2})/, "($1") : t2.length <= 6 ? t2.replace(/^(\d{2})(\d{0,4})/, "($1) $2") : t2.length <= 10 ? t2.replace(/^(\d{2})(\d{4})(\d{0,4})/, "($1) $2-$3") : t2.replace(/^(\d{2})(\d{5})(\d{0,4})/, "($1) $2-$3");
  }
  function V() {
    const e2 = document.getElementById("pre-checkout-modal");
    if (!e2) return;
    e2.removeAttribute("hidden"), e2.setAttribute("aria-hidden", "false"), document.body.style.overflow = "hidden";
    const t2 = e2.querySelector('input:not([type="hidden"])');
    requestAnimationFrame(() => t2?.focus());
  }
  function s3() {
    const e2 = document.getElementById("pre-checkout-modal");
    e2 && (e2.setAttribute("hidden", ""), e2.setAttribute("aria-hidden", "true"), document.body.style.overflow = "");
  }
  function v2() {
    const e2 = document.getElementById("pre-checkout-modal"), t2 = document.getElementById("pre-checkout-form");
    if (e2 && !e2.dataset.pcoBound && (e2.dataset.pcoBound = "1", e2.addEventListener("click", (o2) => {
      o2.target === e2 && s3();
    })), t2 && !t2.dataset.pcoBound) {
      t2.dataset.pcoBound = "1";
      const o2 = t2.querySelector('input[name="phone"]');
      o2?.addEventListener("input", () => {
        o2 && (o2.value = K(o2.value));
      }), document.getElementById("pre-checkout-close")?.addEventListener("click", s3);
      const r4 = document.getElementById("pre-checkout-error");
      t2.addEventListener("submit", (n2) => {
        if (n2.preventDefault(), r4 && (r4.hidden = true), !t2.reportValidity()) return;
        const c3 = t2.querySelector('[type="submit"]');
        c3 && (c3.disabled = true, c3.classList.add("is-loading"));
        const l4 = new FormData(t2), d3 = r3(String(l4.get("name") || "")), u2 = s2(String(l4.get("email") || "")), m = u(String(l4.get("phone") || "")), f2 = A2({ name: d3, email: u2, phone: m, pathname: window.location.pathname, planId: i2?.planId, productName: i2?.productName, hotmartCheckoutCode: g2 || void 0 });
        c2({ form: "pre-checkout", email: u2, phone: m, name: d3, product_id: i2?.planId || void 0 });
        const p2 = D(k2, { name: d3, email: u2, phone: m });
        try {
          let h2 = false;
          typeof navigator.sendBeacon == "function" && (h2 = navigator.sendBeacon(w3, new Blob([f2], { type: "application/x-www-form-urlencoded;charset=UTF-8" }))), h2 || fetch(w3, { method: "POST", headers: { "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8" }, body: f2, keepalive: true }).catch(() => {
          });
        } catch {
        }
        s3(), p2 && (window.location.href = p2);
      });
    }
    y2 || (y2 = true, document.addEventListener("keydown", (o2) => {
      o2.key === "Escape" && s3();
    })), document.querySelectorAll(x).forEach((o2) => {
      o2.dataset.pcoIntercepted || M2() || (o2.dataset.pcoIntercepted = "1", o2.addEventListener("click", (a4) => {
        a4.preventDefault();
        const r4 = v(o2.href, window.location.pathname, window.location.search);
        o2.href = r4, k2 = r4, g2 = F(o2.href) ?? "";
        const n2 = R2();
        i2 = n2 ? z(o2.href, n2) : null, document.getElementById("pre-checkout-form")?.reset(), V();
      }));
    });
  }
  var J = () => {
    const e2 = () => {
      C(), I();
    };
    e2(), requestAnimationFrame(e2);
  };
  var W = () => {
    l2();
  };
  var j = () => {
    r2();
  };
  var G = () => {
    v2(), requestAnimationFrame(() => v2());
  };
  var C2 = () => {
    const e2 = () => {
      W(), j();
    };
    "requestIdleCallback" in window ? requestIdleCallback(e2, { timeout: 2e3 }) : setTimeout(e2, 200);
  };
  var E2 = () => {
    let e2 = false;
    const t2 = [], o2 = () => {
      if (!e2) {
        e2 = true;
        for (const n2 of t2) n2();
        t2.length = 0, J(), G();
      }
    }, a4 = () => o2();
    for (const n2 of ["pointerdown", "keydown", "touchstart"]) window.addEventListener(n2, a4, { passive: true, capture: true }), t2.push(() => window.removeEventListener(n2, a4, true));
    const r4 = () => {
      "requestIdleCallback" in window ? requestIdleCallback(o2, { timeout: 2500 }) : setTimeout(o2, 400);
    };
    document.readyState === "complete" ? r4() : window.addEventListener("load", r4, { once: true });
  };
  E2();
  C2();
  document.addEventListener("astro:page-load", () => {
    E2(), C2();
  });
  window.addEventListener("resize", c);
})();
