/* The copied landing-page links are references, not live actions in this offline catalog. */
(() => {
  let notice;
  let hideTimer;

  function showNotice() {
    if (!notice) {
      notice = document.createElement('div');
      notice.setAttribute('role', 'status');
      notice.setAttribute('aria-live', 'polite');
      Object.assign(notice.style, {
        position: 'fixed',
        zIndex: '10000',
        inset: 'auto 24px 24px auto',
        maxWidth: 'min(360px, calc(100vw - 48px))',
        padding: '12px 16px',
        border: '1px solid #ffffff30',
        borderRadius: '12px',
        background: '#101414f2',
        color: '#f3f4f6',
        boxShadow: '0 12px 32px #0008',
        font: '14px/1.5 Inter, sans-serif',
      });
      document.body.appendChild(notice);
    }
    notice.textContent = 'Link externo indisponível nesta demonstração offline.';
    notice.hidden = false;
    clearTimeout(hideTimer);
    hideTimer = setTimeout(() => { notice.hidden = true; }, 4000);
  }

  document.addEventListener('click', (event) => {
    const target = event.target;
    const link = target instanceof Element ? target.closest('a[href]') : null;
    if (!link || !/^https?:\/\//i.test(link.getAttribute('href') || '')) return;
    event.preventDefault();
    event.stopImmediatePropagation();
    showNotice();
  }, true);

  document.addEventListener('submit', (event) => {
    if (event.target?.id !== 'pre-checkout-form') return;
    event.preventDefault();
    event.stopImmediatePropagation();
    showNotice();
  }, true);
})();
