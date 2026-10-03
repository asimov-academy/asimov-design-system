"""Os design systems de email num arquivo só, para download: um HTML para o tema escuro e
outro para o claro (emails/asimov-email-<tema>.html).

Cada build-email-ds*.py descreve o seu sistema em kit(): casca, peças (linhas e blocos),
cores, tipografia e receitas de montagem. O build-email-export.py monta com reference_html()
um arquivo com todos os sistemas e um arquivo por sistema, em cada tema. A página tem, nesta ordem: como usar; e, para cada sistema, fundações,
casca, elementos e exemplos de aplicação.

Cada trecho de HTML (casca, peça, exemplo) fica no arquivo uma vez só, intacto, dentro de
um <script type="text/x-email">: uma aplicação ou uma LLM lê o código limpo, e a página usa
o mesmo trecho para mostrar a prévia e o código.

As imagens apontam para a hospedagem de imagens de email (ASSETS_URL), não para o site do
design system, e o build trava se alguma ficar fora dela (audit).
"""
import html as _html
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from email_copies import COPIES

ROOT = Path(__file__).resolve().parent.parent
SITE_URL = "https://asimov-design-system.vercel.app"

# Onde as imagens dos emails ficam para disparo: bunny.net, Storage Zone "asimov-email" com a
# Pull Zone em img.asimov.academy. Cada sistema tem uma versão, e uma versão publicada nunca
# muda: emails já enviados continuam mostrando as mesmas imagens. Mudou alguma imagem de um
# sistema? Suba a versão dele aqui, rode os builds e scripts/upload-email-assets.py.
ASSETS_URL = "https://img.asimov.academy/email"
SISTEMAS = {  # pasta em emails/ -> (slug, versão das imagens)
    "design-system": ("aura", "v1"),
    "design-system-cadence": ("cadence", "v1"),
    "design-system-black": ("black", "v1"),
}


def assets_base(pasta):
    """URL da pasta de imagens de um sistema, com a versão. img/x.png vira <base>x.png."""
    slug, versao = SISTEMAS[pasta]
    return f"{ASSETS_URL}/{slug}/{versao}/"


VARIAVEIS = {
    "{{assunto}}": "Assunto do email (vai no <title>).",
    "{{preheader}}": "Texto de prévia que aparece ao lado do assunto na caixa de entrada.",
    "{{linhas}}": "Na casca: onde entram as linhas, em sequência.",
    "{{blocos}}": "Na linha corpo: onde entram os blocos de texto, em sequência.",
    "{{link_cta}}": "Destino dos botões.",
    "{{link_descadastro}}": "Link de cancelar inscrição. Obrigatório.",
    "{{link_youtube}}, {{link_instagram}}, {{link_linkedin}}": "Redes no rodapé.",
    "{{endereco}}": "Endereço da empresa no rodapé. Obrigatório.",
}


@dataclass
class Componente:
    slug: str
    nome: str
    tipo: str          # "linha" (vai na casca) ou "bloco" (vai dentro da linha corpo)
    uso: str
    html: str


@dataclass
class Variante:
    id: str            # "escuro" ou "claro"
    rotulo: str
    tema: str          # "escuro" ou "claro"
    casca: str         # documento completo com {{assunto}}, {{preheader}} e {{linhas}}
    componentes: list
    cores: dict


@dataclass
class Kit:
    slug: str          # aura, cadence, black
    nome: str
    pasta: str         # pasta do sistema em emails/
    descricao: str
    fontes: list
    tipografia: list   # [{nome, tamanho, entrelinha, peso, tracking, mobile, uso}]
    variantes: list
    exemplos: list     # nomes de arquivo em emails/<pasta>/
    quando: str = ""
    montagem: list = field(default_factory=list)   # receitas: (nome, [slugs])
    notas: list = field(default_factory=list)


# ------------------------------------------------------------------ imagens

def absolutize(html, pasta):
    """Troca img/... pela URL hospedada. Texto puro, para alcançar também o VML do Outlook."""
    base = assets_base(pasta)
    html = re.sub(r'(\s(?:src|background)=")img/([^"]+)"', lambda m: f'{m.group(1)}{base}{m.group(2)}"', html)
    html = re.sub(r"url\((['\"]?)img/([^'\")]+)\1\)", lambda m: f"url({m.group(1)}{base}{m.group(2)}{m.group(1)})", html)
    return html.replace("Antes do disparo, troque img/... por URLs absolutas hospedadas.",
                        f"Imagens hospedadas em {base}")


_REFS = re.compile(r"""\s(?:src|background)=["']([^"']+)["']|url\(\s*["']?([^"')]+?)["']?\s*\)""")


def audit(html, pasta, onde):
    """Toda imagem de um email que sai daqui precisa apontar para a CDN, na pasta com versão
    do sistema, e existir em emails/<pasta>/img/ (é isso que o upload sobe).
    Devolve a lista de problemas; vazia quando está tudo certo."""
    base = assets_base(pasta)
    img = ROOT / "emails" / pasta / "img"
    problemas = []
    for m in _REFS.finditer(html):
        ref = (m.group(1) or m.group(2)).strip()
        if ref.startswith("{{"):
            continue
        if not ref.startswith(base):
            problemas.append(f"{onde}: imagem fora da CDN: {ref}")
        elif not (img / ref[len(base):]).is_file():
            problemas.append(f"{onde}: imagem sem arquivo em emails/{pasta}/img/: {ref}")
    return problemas


def fail_on(problemas):
    if problemas:
        sys.exit("Imagens de email fora da CDN (ver AGENTS.md):\n  " + "\n  ".join(problemas))


# ------------------------------------------------------------------ página de download

ESTILO = {
    "escuro": dict(bg="#0a0a0b", surface="#111113", text="#f4f4f5", body="#c4c4cc", muted="#8a8a93",
                   line="rgba(255,255,255,.1)", accent="#2dd4bf", code="#0d0d0f", scheme="dark"),
    "claro": dict(bg="#f4f4f5", surface="#ffffff", text="#09090b", body="#3f3f46", muted="#71717a",
                  line="#e4e4e7", accent="#0f766e", code="#fafafa", scheme="light"),
}

_COPY = {c["id"]: c for c in COPIES}


def _esc(text):
    return _html.escape(text, quote=True)


def _raw(source, onde):
    """Conteúdo seguro para ficar cru dentro de <script>: não pode abrir nem fechar script."""
    if re.search(r"</?script", source, re.I):
        raise SystemExit(f"{onde}: o HTML contém <script>, não dá para embutir na página de download.")
    return source.strip("\n")


def _variante(kit, tema):
    return next(v for v in kit.variantes if v.tema == tema)


def _exemplos(kit, tema):
    nomes = [e for e in kit.exemplos if e.endswith(f"-{tema}.html")]
    conversas = sorted(n for n in nomes if n.startswith("em-"))
    return conversas + [n for n in nomes if n.startswith("email-")]


def _exemplo_rotulo(nome):
    if nome.startswith("email-"):
        return "Aplicação com título", "Todas as peças num email com texto de exemplo (lorem ipsum)."
    copy = _COPY["-".join(nome.split("-")[:2])]
    return f'{copy["code"]} · {copy["assunto"]}', f'Email conversacional real. {copy["fase"]}, para {copy["publico"].lower()}.'


def _peca(sistema, tipo, slug, nome, uso, source, pasta, onde, problemas):
    source = absolutize(source, pasta)
    problemas += audit(source, pasta, onde)
    badge = {"linha": "Linha", "bloco": "Bloco", "exemplo": "Exemplo"}[tipo]
    return f'''      <article class="peca" id="{sistema}-{tipo}-{slug}" data-sistema="{sistema}" data-tipo="{tipo}" data-slug="{slug}">
        <header><div><span class="badge">{badge}</span><h4>{_esc(nome)}</h4><code class="slug">{sistema}/{slug}</code></div><p>{_esc(uso)}</p></header>
        <div class="preview"><iframe title="Prévia: {_esc(nome)}" scrolling="no"></iframe></div>
        <details><summary>Código</summary><button type="button" class="copiar">Copiar</button><pre><code></code></pre></details>
        <script type="text/x-email">
{_raw(source, onde)}
        </script>
      </article>'''


def _sistema(kit, tema, problemas):
    v = _variante(kit, tema)
    s = kit.slug
    casca = absolutize(v.casca, kit.pasta)
    problemas += audit(casca, kit.pasta, f"{s}/casca")
    cores = "".join(f'<li><i style="background:{c}"></i><b>{_esc(k)}</b><code>{c}</code></li>' for k, c in v.cores.items())
    tipos = "".join(
        f'<tr><td>{_esc(t["nome"])}</td><td>{t["tamanho"]}/{t["entrelinha"]}px</td><td>{t["peso"]}</td>'
        f'<td>{t["tracking"]}px</td><td>{t["mobile"]}</td><td>{_esc(t.get("familia", ""))}</td><td>{_esc(t["uso"])}</td></tr>'
        for t in kit.tipografia)
    receitas = "".join(f'<li><b>{_esc(n)}:</b> ' + " → ".join(f"<code>{x}</code>" for x in slugs) + "</li>" for n, slugs in kit.montagem)
    notas = "".join(f"<li>{_esc(n)}</li>" for n in kit.notas)
    linhas = [c for c in v.componentes if c.tipo == "linha"]
    blocos = [c for c in v.componentes if c.tipo == "bloco"]
    pecas = lambda cs: "\n".join(_peca(s, c.tipo, c.slug, c.nome, c.uso, c.html, kit.pasta, f"{s}/{c.slug}", problemas) for c in cs)
    exemplos = "\n".join(
        _peca(s, "exemplo", nome[:-5], *_exemplo_rotulo(nome), (ROOT / "emails" / kit.pasta / nome).read_text(encoding="utf-8"),
              kit.pasta, f"{s}/exemplos/{nome}", problemas)
        for nome in _exemplos(kit, tema))
    return f'''
    <section class="ds" id="{s}">
      <header class="ds-head">
        <p class="kicker">Design system</p>
        <h2>{_esc(kit.nome)}</h2>
        <p>{_esc(kit.descricao)}</p>
        <p><b>Quando usar:</b> {_esc(kit.quando)}</p>
      </header>

      <h3>Fundações</h3>
      <p class="sub">Fontes: {_esc("; ".join(kit.fontes))}.</p>
      <ul class="cores">{cores}</ul>
      <div class="tabela"><table class="tipos"><thead><tr><th>Estilo</th><th>Tamanho</th><th>Peso</th><th>Tracking</th><th>Mobile</th><th>Fonte</th><th>Uso</th></tr></thead><tbody>{tipos}</tbody></table></div>

      <h3>Casca</h3>
      <p class="sub">O documento do email: head, estilos, container de 600px. As linhas entram em <code>{{{{linhas}}}}</code>.</p>
      <details class="casca"><summary>Código da casca</summary><button type="button" class="copiar">Copiar</button><pre><code></code></pre></details>
      <script type="text/x-email" data-casca="{s}">
{_raw(casca, f"{s}/casca")}
      </script>
      <p class="sub"><b>Montagem:</b></p>
      <ul class="receitas">{receitas}{notas}</ul>

      <h3>Elementos: linhas</h3>
      <p class="sub">Vão direto na casca, uma depois da outra.</p>
{pecas(linhas)}

      <h3>Elementos: blocos</h3>
      <p class="sub">Vão dentro da linha <code>corpo</code>, no lugar de <code>{{{{blocos}}}}</code>.</p>
{pecas(blocos)}

      <h3>Exemplos de aplicação</h3>
      <p class="sub">Emails completos feitos com o sistema. Use como referência de ritmo e de combinação das peças.</p>
{exemplos}
    </section>'''


def _como_usar(kits, tema):
    outro = "claro" if tema == "escuro" else "escuro"
    um = len(kits) == 1
    conteudo = (f"o design system de email {_esc(kits[0].nome)} da Asimov" if um
                else "os design systems de email da Asimov")
    resto = (f"Os outros sistemas e o tema {outro} estão" if um else f"O tema {outro} está")
    sistemas = "".join(f'<tr><td><a href="#{k.slug}">{_esc(k.nome)}</a></td><td>{_esc(k.quando)}</td></tr>' for k in kits)
    variaveis = "".join(f"<tr><td><code>{_esc(k)}</code></td><td>{_esc(d)}</td></tr>" for k, d in VARIAVEIS.items())
    esquema = _esc("""casca do sistema ({{assunto}} e {{preheader}} preenchidos)
  {{linhas}} =
    linha capa
    linha corpo, com {{blocos}} =
      bloco parágrafo
      bloco parágrafo
      bloco botão
      bloco assinatura
    linha rodapé""")
    return f'''
    <section id="como-usar">
      <h2>Como usar</h2>
      <p>Este arquivo tem {conteudo} no tema {tema}: fundações, todos os elementos e emails de exemplo.
      Cada peça tem prévia e código. {resto} no hub de emails ({SITE_URL}/emails/).</p>

      <h3>1. {"Quando usar" if um else "Escolha o sistema"}</h3>
      {f"<p>{_esc(kits[0].quando)}</p>" if um else f'<div class="tabela"><table><thead><tr><th>Sistema</th><th>Quando usar</th></tr></thead><tbody>{sistemas}</tbody></table></div>'}

      <h3>2. Monte o email com peças</h3>
      <ol>
        <li>Comece pela <b>casca</b> do sistema. Troque <code>{{{{assunto}}}}</code> e <code>{{{{preheader}}}}</code>.</li>
        <li>Em <code>{{{{linhas}}}}</code>, cole as <b>linhas</b> na ordem do email: topo (capa ou hero), corpo, cartões, CTA, rodapé.</li>
        <li>Na linha <code>corpo</code>, troque <code>{{{{blocos}}}}</code> pelos <b>blocos</b> de texto: parágrafos, botões, lista, assinatura, PS.</li>
        <li>Troque os textos de exemplo pelos reais e preencha as variáveis de link.</li>
      </ol>
      <p>A maior parte dos emails da Asimov é conversacional: sem título, abre direto na conversa.
      A receita de cada sistema está em "Montagem", e os exemplos mostram o resultado.</p>
      <pre class="esquema"><code>{esquema}</code></pre>

      <h3>3. Variáveis</h3>
      <div class="tabela"><table><thead><tr><th>Variável</th><th>O que é</th></tr></thead><tbody>{variaveis}</tbody></table></div>

      <h3>4. Regras</h3>
      <ul>
        <li>Troque só textos e links. Tabelas, estilos inline, larguras e os comentários <code>&lt;!--[if mso]&gt;</code> (Outlook) ficam como estão.</li>
        <li>Use só as peças do sistema escolhido, no mesmo tema. Não misture sistemas num email.</li>
        <li>Um botão por ideia, com rótulo curto e verbo. Rodapé com descadastro e endereço é obrigatório.</li>
        <li>As imagens já estão hospedadas em <code>{ASSETS_URL}/</code>. Não troque nem baixe as imagens.</li>
        <li>Antes de disparar, mande um teste para Gmail, Outlook e celular.</li>
      </ul>

      <h3>5. Com uma LLM ou por código</h3>
      <p>O código de cada peça está neste arquivo, dentro de <code>&lt;script type="text/x-email"&gt;</code>,
      exatamente como deve ir no email. Cada peça é um <code>&lt;article class="peca"&gt;</code> com
      <code>data-sistema</code>, <code>data-tipo</code> (linha, bloco ou exemplo) e <code>data-slug</code>;
      a casca é o <code>&lt;script data-casca="..."&gt;</code> do sistema.</p>
      <blockquote>Monte um email com o design system abaixo. Use a casca e só as peças do sistema
      escolhido, na ordem que fizer sentido para a copy. Troque apenas os textos de exemplo pela copy.
      Não altere tabelas, estilos, atributos, comentários <code>&lt;!--[if mso]&gt;</code> nem variáveis
      <code>{{{{...}}}}</code>. Responda só com o HTML final.</blockquote>
      <p>Por código é mais previsível: a LLM devolve só a lista de peças e os textos, e a aplicação
      junta os trechos.</p>
    </section>'''


def reference_html(kits, tema):
    """O arquivo de download de um tema: como usar + os sistemas de `kits` (todos ou um só)."""
    e = ESTILO[tema]
    problemas = []
    sistemas = "".join(_sistema(k, tema, problemas) for k in kits)
    fail_on(problemas)
    toc = "".join(f'<a href="#{k.slug}">{_esc(k.nome)}</a>' for k in kits)
    outro = "claro" if tema == "escuro" else "escuro"
    um = len(kits) == 1
    nome = f"Design system de email {kits[0].nome}" if um else "Design systems de email"
    lead = ("Num arquivo só: como usar, fundações, todos os elementos e exemplos de aplicação." if um
            else "Os " + ("dois" if len(kits) == 2 else "três" if len(kits) == 3 else str(len(kits)))
            + " sistemas num arquivo só: como usar, fundações, todos os elementos e exemplos de aplicação.")
    return f'''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="{e["scheme"]}">
  <title>Asimov · {nome} · tema {tema}</title>
  <!-- Gerado por scripts/build-email-export.py. Edite os geradores, não este arquivo. -->
  <style>
    :root {{ --bg:{e["bg"]}; --surface:{e["surface"]}; --text:{e["text"]}; --body:{e["body"]}; --muted:{e["muted"]};
            --line:{e["line"]}; --accent:{e["accent"]}; --code:{e["code"]};
            --mono: ui-monospace, "SFMono-Regular", Menlo, Consolas, monospace; }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{ margin: 0; background: var(--bg); color: var(--text); font: 16px/1.6 Inter, "Helvetica Neue", Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased; }}
    a {{ color: var(--accent); }}
    code {{ font-family: var(--mono); font-size: .88em; }}
    .wrap {{ max-width: 1040px; margin: 0 auto; padding: 0 20px 96px; }}
    .top {{ padding: 64px 0 32px; border-bottom: 1px solid var(--line); }}
    .kicker {{ margin: 0; color: var(--accent); font-size: 12px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; }}
    h1 {{ margin: 10px 0 0; font-size: clamp(36px, 6vw, 56px); line-height: 1.05; font-weight: 500; letter-spacing: -1.6px; }}
    .lead {{ max-width: 680px; margin: 16px 0 0; color: var(--body); font-size: 18px; }}
    .toc {{ position: sticky; top: 0; z-index: 2; display: flex; flex-wrap: wrap; gap: 6px 18px; padding: 14px 0; background: var(--bg); border-bottom: 1px solid var(--line); font-size: 14px; }}
    .toc a {{ color: var(--body); text-decoration: none; }}
    .toc a:hover {{ color: var(--text); }}
    section {{ padding-top: 56px; scroll-margin-top: 40px; }}
    h2 {{ margin: 6px 0 0; font-size: 36px; line-height: 1.15; font-weight: 500; letter-spacing: -1px; }}
    h3 {{ margin: 48px 0 6px; font-size: 22px; font-weight: 500; letter-spacing: -.3px; }}
    h4 {{ display: inline; margin: 0 8px 0 0; font-size: 16px; font-weight: 600; }}
    p, li {{ color: var(--body); }}
    li {{ margin: 4px 0; }}
    b, strong {{ color: var(--text); font-weight: 600; }}
    .sub {{ margin: 0 0 16px; color: var(--muted); font-size: 14px; }}
    .ds {{ margin-top: 40px; border-top: 1px solid var(--line); }}
    .ds-head p {{ max-width: 760px; }}
    .tabela {{ overflow-x: auto; border: 1px solid var(--line); border-radius: 12px; background: var(--surface); }}
    table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
    th, td {{ padding: 10px 14px; border-bottom: 1px solid var(--line); text-align: left; vertical-align: top; color: var(--body); }}
    th {{ color: var(--text); font-weight: 500; }}
    tr:last-child td {{ border-bottom: 0; }}
    .cores {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(170px, 1fr)); gap: 8px; margin: 0 0 16px; padding: 0; list-style: none; }}
    .cores li {{ display: grid; grid-template-columns: 28px 1fr; gap: 0 10px; align-items: center; margin: 0; padding: 8px; border: 1px solid var(--line); border-radius: 10px; background: var(--surface); }}
    .cores i {{ grid-row: span 2; width: 28px; height: 28px; border-radius: 7px; box-shadow: inset 0 0 0 1px var(--line); }}
    .cores b {{ font-size: 12px; font-weight: 500; overflow-wrap: anywhere; }}
    .cores code {{ color: var(--muted); font-size: 11px; }}
    .receitas {{ margin-top: 0; }}
    .peca {{ margin: 16px 0; border: 1px solid var(--line); border-radius: 16px; background: var(--surface); overflow: hidden; scroll-margin-top: 60px; }}
    .peca > header {{ padding: 14px 18px 12px; border-bottom: 1px solid var(--line); }}
    .peca > header p {{ margin: 4px 0 0; font-size: 14px; }}
    .badge {{ display: inline-block; margin-right: 8px; padding: 1px 8px; border: 1px solid var(--line); border-radius: 999px; color: var(--muted); font-size: 11px; vertical-align: 2px; }}
    .slug {{ color: var(--muted); font-size: 12px; }}
    .preview {{ display: flex; justify-content: center; background: var(--bg); }}
    .preview iframe {{ display: block; width: 100%; max-width: 640px; height: 160px; border: 0; }}
    details {{ border-top: 1px solid var(--line); position: relative; }}
    .casca {{ border: 1px solid var(--line); border-radius: 12px; background: var(--surface); overflow: hidden; }}
    summary {{ padding: 10px 18px; color: var(--body); font-size: 14px; cursor: pointer; }}
    pre {{ margin: 0; max-height: 420px; overflow: auto; padding: 14px 18px; background: var(--code); color: var(--body); font: 12px/1.55 var(--mono); white-space: pre-wrap; overflow-wrap: anywhere; }}
    .esquema {{ border: 1px solid var(--line); border-radius: 12px; }}
    .copiar {{ position: absolute; top: 6px; right: 10px; padding: 4px 12px; border: 1px solid var(--line); border-radius: 999px; background: var(--surface); color: var(--text); font: inherit; font-size: 12px; cursor: pointer; }}
    details:not([open]) .copiar {{ display: none; }}
    blockquote {{ margin: 12px 0; padding: 12px 18px; border-left: 3px solid var(--accent); background: var(--surface); color: var(--body); border-radius: 0 12px 12px 0; }}
    @media (max-width: 640px) {{ h2 {{ font-size: 28px; }} }}
  </style>
</head>
<body>
  <div class="wrap">
    <header class="top">
      <p class="kicker">Asimov Academy · Email · Tema {tema}</p>
      <h1>{nome}</h1>
      <p class="lead">{lead}
      As imagens já vêm hospedadas, então os trechos funcionam direto num email. O tema {outro} está no outro arquivo.</p>
    </header>
    <nav class="toc" aria-label="Sumário"><a href="#como-usar">Como usar</a>{toc}</nav>
{_como_usar(kits, tema)}
{sistemas}
  </div>
  <script>
    // Prévia e código de cada peça a partir do <script type="text/x-email"> dela.
    (() => {{
      const raw = (el) => el.textContent.replace(/^\\n+|\\s+$/g, "");
      const casca = {{}}, corpo = {{}};
      document.querySelectorAll("script[data-casca]").forEach((s) => (casca[s.dataset.casca] = raw(s)));
      document.querySelectorAll('.peca[data-slug="corpo"]').forEach((p) => (corpo[p.dataset.sistema] = raw(p.querySelector("script"))));
      // Só na prévia: sem barra de rolagem dentro do quadro. O código mostrado é o original.
      const semRolagem = "<style>html, body {{ overflow: hidden !important; }}</style></head>";
      const documento = (p) => {{
        const html = raw(p.querySelector("script"));
        const doc = p.dataset.tipo === "exemplo" ? html : casca[p.dataset.sistema]
          .replace("{{{{assunto}}}}", "Prévia").replace("{{{{preheader}}}}", "")
          .replace("{{{{linhas}}}}", p.dataset.tipo === "bloco" ? corpo[p.dataset.sistema].replace("{{{{blocos}}}}", html) : html);
        return doc.replace("</head>", semRolagem);
      }};
      // A altura acompanha o email assim que ele existe, sem esperar fontes e imagens.
      const mostrar = (p) => {{
        if (p.dataset.mostrado) return;
        p.dataset.mostrado = "1";
        const frame = p.querySelector("iframe");
        frame.srcdoc = documento(p);
        const ajustar = () => {{ frame.style.height = frame.contentDocument.documentElement.scrollHeight + "px"; }};
        const esperar = setInterval(() => {{
          const d = frame.contentDocument;
          if (!d || d.URL !== "about:srcdoc" || !d.body) return;
          clearInterval(esperar);
          ajustar();
          if ("ResizeObserver" in window) new ResizeObserver(ajustar).observe(d.body);
          frame.addEventListener("load", ajustar);
        }}, 50);
      }};
      // Todas as prévias carregam aos poucos, em fila; as que estão na tela passam na frente.
      const pecas = [...document.querySelectorAll(".peca")];
      pecas.forEach((p) => (p.querySelector("pre code").textContent = raw(p.querySelector("script"))));
      if ("IntersectionObserver" in window) {{
        const io = new IntersectionObserver((itens) => itens.forEach((i) => i.isIntersecting && mostrar(i.target)), {{ rootMargin: "600px 0px" }});
        pecas.forEach((p) => io.observe(p));
      }}
      let fila = 0;
      const proxima = () => {{
        while (fila < pecas.length && pecas[fila].dataset.mostrado) fila++;
        if (fila < pecas.length) {{ mostrar(pecas[fila]); setTimeout(proxima, 80); }}
      }};
      setTimeout(proxima, 300);
      document.querySelectorAll("details.casca").forEach((d) => (d.querySelector("pre code").textContent = raw(d.nextElementSibling)));
      document.addEventListener("click", async (ev) => {{
        const b = ev.target.closest(".copiar");
        if (!b) return;
        const text = b.parentElement.querySelector("pre code").textContent;
        try {{ await navigator.clipboard.writeText(text); }} catch (e) {{
          const a = Object.assign(document.createElement("textarea"), {{ value: text }});
          document.body.append(a); a.select(); document.execCommand("copy"); a.remove();
        }}
        b.textContent = "Copiado"; setTimeout(() => (b.textContent = "Copiar"), 1500);
      }});
    }})();
  </script>
</body>
</html>
'''
