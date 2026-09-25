/* Original local Unicorn Studio scene, with a portable lifecycle adapter.
 * AsimovAurora.mount(element) -> { refresh(), pause(bool), destroy() }
 * No remote project ID, CDN, dependency on the main app or build step. */
(function () {
  'use strict';
  const base = new URL('.', document.currentScript.src);
  const instances = new Map();
  const scripts = new Map();
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  function loadScript(relative) {
    if (scripts.has(relative)) return scripts.get(relative);
    const promise = new Promise((resolve, reject) => {
      const script = document.createElement('script');
      script.src = new URL(relative, base).href;
      script.onload = resolve;
      script.onerror = () => { script.remove(); scripts.delete(relative); reject(new Error('Local Aurora asset unavailable')); };
      document.head.append(script);
    });
    scripts.set(relative, promise);
    return promise;
  }
  // Same HSV-based tint as src/lib/aura-accent-tint.ts in the original project.
  function accentFilter(hex) {
    const raw = hex.trim().replace('#', '');
    if (!/^[\da-f]{6}$/i.test(raw)) return;
    const [r, g, b] = [0, 2, 4].map(i => parseInt(raw.slice(i, i + 2), 16) / 255);
    const max = Math.max(r, g, b), min = Math.min(r, g, b), delta = max - min;
    const saturation = max === 0 ? 0 : delta / max;
    let hue = 0;
    if (delta) hue = max === r ? ((g - b) / delta + (g < b ? 6 : 0)) * 60 : max === g ? ((b - r) / delta + 2) * 60 : ((r - g) / delta + 4) * 60;
    const rotate = ((hue - 275 + 540) % 360) - 180;
    return `hue-rotate(${Math.round(rotate)}deg) saturate(${Math.round(Math.min(100, 40 + saturation * 60))}%) brightness(${(0.86 + max * 0.14).toFixed(2)})`;
  }
  function mount(root) {
    if (instances.has(root)) return instances.get(root);
    root.classList.add('aura-background');
    root.setAttribute('aria-hidden', 'true');
    const host = document.createElement('div');
    host.className = 'aura-background__scene';
    root.append(host);
    let scene, booting = false, failed = false, disposed = false, paused = false, visible = false;
    const canRun = () => !disposed && !paused && !reduced.matches && !document.hidden && visible && root.clientWidth > 0 && root.clientHeight > 0;
    function status(value) {
      if (root.dataset.auraStatus === value || disposed) return;
      root.dataset.auraStatus = value;
      root.dispatchEvent(new CustomEvent('asimov:aurora-status', { bubbles: true }));
    }
    async function boot() {
      if (scene || booting || failed || !canRun()) return;
      booting = true;
      status('loading');
      let blob;
      try {
        await loadScript('aura-scene.js');
        await loadScript('../vendor/unicornStudio.umd.js');
        if (!canRun()) return;
        blob = URL.createObjectURL(new Blob([JSON.stringify(window.AsimovAuraScene)], { type: 'application/json' }));
        const mounted = await window.UnicornStudio.addScene({
          element: host, filePath: blob, scale: 1, dpi: 1, fps: 30,
          fixed: getComputedStyle(root).position === 'fixed', lazyLoad: false, production: true,
          interactivity: { mouse: { disabled: true } }
        });
        if (disposed) { mounted.destroy(); return; }
        scene = mounted;
        root.dataset.auraReady = 'true';
      } catch {
        failed = true;
        root.dataset.auraReady = 'false';
        host.replaceChildren();
      } finally {
        if (blob) URL.revokeObjectURL(blob);
        booting = false;
        if (!disposed) sync();
      }
    }
    function sync() {
      if (disposed) return;
      const running = canRun();
      if (scene) scene.paused = !running;
      if (reduced.matches) status('static');
      else if (failed) status('fallback');
      else if (scene) status(running ? 'running' : 'paused');
      else if (booting) status('loading');
      else { status(running ? 'loading' : 'idle'); if (running) void boot(); }
    }
    function refresh() {
      const filter = accentFilter(getComputedStyle(root).getPropertyValue('--ui-accent'));
      if (filter) root.style.setProperty('--aura-filter', filter);
      if (scene && root.clientWidth && root.clientHeight) scene.resize();
    }
    const resize = new ResizeObserver(() => { refresh(); sync(); });
    const intersection = new IntersectionObserver(entries => { visible = entries[0].isIntersecting; sync(); });
    resize.observe(root);
    intersection.observe(root);
    reduced.addEventListener('change', sync);
    document.addEventListener('visibilitychange', sync);
    const api = {
      refresh,
      pause(value = true) { paused = Boolean(value); sync(); },
      destroy() {
        disposed = true;
        resize.disconnect();
        intersection.disconnect();
        reduced.removeEventListener('change', sync);
        document.removeEventListener('visibilitychange', sync);
        scene?.destroy();
        host.remove();
        instances.delete(root);
        delete root.dataset.auraReady;
        delete root.dataset.auraStatus;
      }
    };
    instances.set(root, api);
    refresh();
    sync();
    return api;
  }
  window.AsimovAurora = { mount, instances };
  document.querySelectorAll('[data-aura]').forEach(mount);
})();
