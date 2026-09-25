(() => {
  // extract-ds/lp.asimov.academy 2.0-design-system/assets/overview/_astro/FaqAccordion.client.tNW3DEY9.js
  function i(o2 = "[data-faq-accordion]") {
    const r = document.querySelector(o2);
    if (!r || r.dataset.bound === "1") return;
    r.dataset.bound = "1";
    const c = Array.from(r.querySelectorAll("[data-faq-item]")), n = (e, a) => {
      const s = e.querySelector("[data-faq-trigger]"), t = e.querySelector("[data-faq-panel]");
      e.classList.toggle("is-open", a), s?.setAttribute("aria-expanded", a ? "true" : "false"), t && (a ? t.removeAttribute("inert") : t.setAttribute("inert", ""));
    };
    c.forEach((e) => {
      const a = e.querySelector("[data-faq-trigger]");
      a && (n(e, false), a.addEventListener("click", () => {
        const s = e.classList.contains("is-open"), t = r.querySelector("[data-faq-item].is-open");
        t && t !== e && n(t, false), n(e, !s);
      }));
    });
  }

  // extract-ds/lp.asimov.academy 2.0-design-system/assets/overview/_astro/FaqBlock.astro_astro_type_script_index_0_lang.BgAwRraU.js
  var o = () => i();
  o();
  document.addEventListener("astro:page-load", o);
})();
