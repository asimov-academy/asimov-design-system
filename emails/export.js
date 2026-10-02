/* Seção "Exportar HTML" do hub de emails.
 *
 * Lista os templates de window.AsimovEmailTemplates (gerado por
 * scripts/build-email-export.py) e, para cada um, copia ou baixa o HTML completo
 * com as imagens em URL absoluta. Assim o arquivo funciona fora deste site: numa
 * ferramenta de email ou entregue a uma LLM junto com a copy.
 *
 * Buscar o HTML exige http(s): via file:// o navegador bloqueia o fetch, e a
 * seção avisa isso em vez de falhar calada.
 */
(() => {
  const root = document.querySelector("[data-export]");
  const templates = window.AsimovEmailTemplates || [];
  if (!root || !templates.length) return;

  const list = root.querySelector("[data-export-list]");
  const status = root.querySelector("[data-export-status]");
  const filters = {
    sistema: root.querySelector('[data-filter="sistema"]'),
    tema: root.querySelector('[data-filter="tema"]'),
    cor: root.querySelector('[data-filter="cor"]'),
  };
  const isFile = location.protocol === "file:";
  const isLocal = ["localhost", "127.0.0.1", "[::1]"].includes(location.hostname) || location.hostname.endsWith(".localhost");

  const escape = (text) => String(text).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
  const unique = (key) => [...new Set(templates.map((t) => t[key]).filter(Boolean))];
  const fill = (select, values) => values.forEach((value) => select.append(new Option(value, value)));
  fill(filters.sistema, unique("sistema"));
  fill(filters.cor, unique("cor"));

  // Caminhos relativos (src, background, url()) viram absolutos em relação ao próprio
  // template. É texto puro de propósito: o código do Outlook mora dentro de comentários
  // (<!--[if mso]>) e um parser de HTML não reescreveria o que está ali.
  const keep = /^(?:[a-z][a-z0-9+.-]*:|\/\/|#|\{\{)/i;
  const absolutize = (html, base) => html
    .replace(/(\s(?:src|background)=)(["'])([^"']+)\2/gi, (all, attr, quote, value) => keep.test(value) ? all : `${attr}${quote}${new URL(value, base).href}${quote}`)
    .replace(/url\((["']?)([^"')]+)\1\)/gi, (all, quote, value) => keep.test(value.trim()) ? all : `url(${quote}${new URL(value.trim(), base).href}${quote})`);

  const say = (message, tone = "") => {
    status.textContent = message;
    status.dataset.tone = tone;
  };

  const load = async (template) => {
    const url = new URL(template.caminho, location.href);
    const response = await fetch(url, { cache: "no-cache" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return absolutize(await response.text(), url);
  };

  const copy = async (text) => {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      const area = Object.assign(document.createElement("textarea"), { value: text });
      area.style.cssText = "position:fixed; opacity:0;";
      document.body.append(area);
      area.select();
      const ok = document.execCommand("copy");
      area.remove();
      if (!ok) throw new Error("clipboard");
    }
  };

  const download = (text, name) => {
    const link = Object.assign(document.createElement("a"), {
      href: URL.createObjectURL(new Blob([text], { type: "text/html;charset=utf-8" })),
      download: name,
    });
    document.body.append(link);
    link.click();
    link.remove();
    setTimeout(() => URL.revokeObjectURL(link.href), 1000);
  };

  const label = (t) => [t.sistema, t.peca, t.cor, t.tema].filter(Boolean).join(" · ");

  const render = () => {
    // Cor só existe no Trilhas: fora dele o filtro some e não pode ficar valendo.
    const corLabel = filters.cor.closest("label");
    corLabel.hidden = Boolean(filters.sistema.value) && filters.sistema.value !== "Trilhas";
    if (corLabel.hidden) filters.cor.value = "";
    const visible = templates.filter((t) =>
      (!filters.sistema.value || t.sistema === filters.sistema.value) &&
      (!filters.tema.value || t.tema === filters.tema.value) &&
      (!filters.cor.value || t.cor === filters.cor.value));
    list.innerHTML = visible.map((t) => `
      <li>
        <div class="xp-name">
          <b>${escape(t.peca)} <span>${escape(t.nome)}</span></b>
          <small>${escape([t.sistema, t.cor, t.tema].filter(Boolean).join(" · "))}</small>
        </div>
        <div class="xp-actions">
          <a href="${escape(t.caminho)}" target="_blank" rel="noopener">Abrir</a>
          <button type="button" data-action="copy" data-id="${escape(t.id)}">Copiar HTML</button>
          <button type="button" data-action="download" data-id="${escape(t.id)}">Baixar .html</button>
        </div>
      </li>`).join("");
    root.querySelector("[data-export-count]").textContent = `${visible.length} de ${templates.length}`;
  };

  list.addEventListener("click", async (event) => {
    const button = event.target.closest("button[data-action]");
    if (!button) return;
    const template = templates.find((t) => t.id === button.dataset.id);
    if (isFile) {
      say("Para exportar, abra o hub pelo site publicado ou por um servidor local: via file:// o navegador bloqueia a leitura dos arquivos.", "error");
      return;
    }
    button.disabled = true;
    try {
      const html = await load(template);
      if (button.dataset.action === "copy") {
        await copy(html);
        say(`HTML copiado: ${label(template)}.`, "ok");
      } else {
        download(html, `asimov-${template.id.replace("--", "-")}.html`);
        say(`Download iniciado: ${label(template)}.`, "ok");
      }
    } catch (error) {
      say(`Não consegui exportar ${label(template)} (${error.message}).`, "error");
    } finally {
      button.disabled = false;
    }
  });

  Object.values(filters).forEach((select) => select.addEventListener("change", render));
  if (isFile) say("Aberto via file://: a exportação só funciona pelo site publicado ou por um servidor local.", "warn");
  else if (isLocal) say(`As imagens vão apontar para ${location.origin}. Para usar em emails reais, exporte pelo site publicado.`, "warn");
  render();
})();
