/* Modo claro/escuro do design system.
 * O escuro é o padrão. A página entra no claro com ?modo=claro na URL:
 * o design-system.html recarrega o iframe com esse parâmetro ao trocar o modo.
 * Precisa rodar no <head>, antes do primeiro paint, para não piscar o escuro. */
(() => {
  const modo = new URLSearchParams(location.search).get("modo") === "claro" ? "claro" : "escuro";
  document.documentElement.dataset.modo = modo;
  window.AsimovModo = modo;
  if (modo !== "claro") return;

  // A paisagem noturna vira a paisagem de dia (mesma composição, usada também nos emails claros).
  const assets = new URL(".", document.currentScript.src);
  const dia = (largura) => new URL(`components/backgrounds/images/landscape-dia-${largura}.webp`, assets).href;
  const trocarPaisagem = () => {
    document.querySelectorAll('img[src*="landscape-1280"]').forEach((img) => {
      img.srcset = `${dia(768)} 768w, ${dia(1200)} 1200w`;
      img.src = dia(1200);
    });
  };
  // Textos que descrevem o modo escuro trazem a versão clara em data-texto-claro.
  const trocarTextos = () => {
    document.querySelectorAll("[data-texto-claro]").forEach((node) => { node.textContent = node.dataset.textoClaro; });
  };
  document.addEventListener("DOMContentLoaded", () => { trocarPaisagem(); trocarTextos(); });
})();
