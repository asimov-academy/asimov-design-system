#!/usr/bin/env python3
"""Design system de email "Cadence": a chuva de luz do Cadence Rain com cara de workspace.

Mesma família do design system de email principal (Inter, teal Asimov, fundo
#050505), com outra leitura:
  - cabeçalho com a chuva de luz como imagem de fundo e uma ficha técnica embaixo
  - trilho lateral numerado em mono que costura as seções do texto
  - janela de editor para a frase que merece destaque
  - CTA como tecla teal alinhada ao texto

Saída em emails/design-system-cadence/:

    index.html, email-escuro.html, email-claro.html, em-XXX-<tema>.html, img/

E o kit para download em emails/kits/asimov-email-cadence.zip (ver email_kit.py).

    python3 scripts/build-email-ds-cadence.py
"""
import re
from pathlib import Path

from email_copies import COPIES, render_blocks
from email_kit import Componente, Kit, Variante, write_kit

OUT = Path(__file__).resolve().parent.parent / "emails" / "design-system-cadence"

SANS = "Inter, 'Helvetica Neue', Helvetica, Arial, sans-serif"
MONO = "'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace"

THEMES = {
    "escuro": {
        "SCHEME": "dark",
        "PAGE": "#050505",
        "TEXT": "#ffffff",
        "BODY": "#b4b4b4",
        "MUTED": "#737373",
        "FAINT": "#3f3f46",
        "LINE": "#1f1f1f",
        "ACCENT_TEXT": "#2dd4bf",
        "SURFACE": "#0b0c0e",
        "SURFACE2": "#111214",
        "SURFACE_LINE": "#1f2023",
        "CTA_LINE": "#134e48",
        "HERO": "img/chuva-escuro.jpg",
        "LOGO": "img/logo-branco.png",
        "ARROW_ACCENT": "img/seta-teal.png",
    },
    "claro": {
        "SCHEME": "light",
        "PAGE": "#f6f6f7",
        "TEXT": "#09090b",
        "BODY": "#52525b",
        "MUTED": "#8a8a93",
        "FAINT": "#d4d4d8",
        "LINE": "#e4e4e7",
        "ACCENT_TEXT": "#0d9488",
        "SURFACE": "#ffffff",
        "SURFACE2": "#fafafa",
        "SURFACE_LINE": "#e4e4e7",
        "CTA_LINE": "#5eead4",
        "HERO": "img/chuva-claro.jpg",
        "LOGO": "img/logo-preto.png",
        "ARROW_ACCENT": "img/seta-teal-escuro.png",
    },
}

ACCENT = "#14b8a6"
ON_ACCENT = "#04201d"

# nome: (família, tamanho, entrelinha, peso, tracking, cor, mobile, uso)
TYPE = {
    "Manchete": ("SANS", 56, 56, 500, -2.4, "TEXT", "40/42", "Só no cabeçalho, alinhada à esquerda."),
    "Título de seção": ("SANS", 28, 34, 500, -0.8, "TEXT", "24/30", "Abre cada passo do trilho."),
    "Destaque": ("SANS", 20, 30, 400, -0.2, "TEXT", "18/28", "A frase dentro da janela."),
    "Corpo": ("SANS", 17, 29, 400, 0, "BODY", "16/27", "Todo o texto corrido."),
    "Índice": ("MONO", 12, 16, 500, 0.5, "ACCENT_TEXT", "12/16", "Números do trilho e da ficha."),
    "Rótulo": ("MONO", 11, 16, 400, 1.2, "MUTED", "11/16", "Caixa alta. Ficha técnica, janela, rodapé."),
}

LOREM = {
    "curto": "Lorem ipsum dolor sit amet.",
    "medio": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Integer posuere erat a ante, "
             "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
    "longo": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Curabitur pretium tincidunt lacus, "
             "nulla gravida orci a odio. Nullam varius, turpis et commodo pharetra, est eros bibendum elit, "
             "nec luctus magna felis sollicitudin mauris. Integer in mauris eu nibh euismod gravida. Duis ac "
             "tellus et risus vulputate vehicula. Donec lobortis risus a elit. Etiam tempor ut ullamcorper.",
}


def ts(name, t, color=None):
    fam, size, lh, weight, track, key, _, _ = TYPE[name]
    font = SANS if fam == "SANS" else MONO
    upper = " text-transform:uppercase;" if name == "Rótulo" else ""
    return (f"font-family:{font}; font-size:{size}px; line-height:{lh}px; font-weight:{weight}; "
            f"letter-spacing:{track}px; color:{color or t[key]};{upper}")


# ------------------------------------------------------------------ componentes

def spec_bar(t, items=(("De", "Lorem Ipsum"), ("Leitura", "4 min"), ("Edição", "01"))):
    """Ficha técnica: três células separadas por fio, como metadados de um arquivo."""
    cells = []
    for i, (label, value) in enumerate(items):
        border = f" border-left:1px solid {t['LINE']};" if i else ""
        pad = "14px 0 14px 18px" if i else "14px 18px 14px 0"
        cells.append(f'<td class="spec-cell" valign="top" style="padding:{pad};{border}">'
                     f'<div style="{ts("Rótulo", t)}">{label}</div>'
                     f'<div style="margin-top:4px; font-family:{SANS}; font-size:14px; line-height:20px; font-weight:500; color:{t["TEXT"]};">{value}</div></td>')
    return (f'<table role="presentation" width="100%" style="border-top:1px solid {t["LINE"]}; border-bottom:1px solid {t["LINE"]};">'
            f'<tr>{"".join(cells)}</tr></table>')


def hero(t):
    return f'''<table role="presentation" width="100%">
  <tr>
    <td class="hero" height="500" valign="top" background="{t["HERO"]}" bgcolor="{t["PAGE"]}"
        style="height:500px; background:{t["PAGE"]} url('{t["HERO"]}') right top / cover no-repeat;">
      <!--[if gte mso 9]>
      <v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false" style="width:600px;height:500px;">
        <v:fill type="frame" src="{t["HERO"]}" color="{t["PAGE"]}" />
        <v:textbox inset="0,0,0,0">
      <![endif]-->
      <table role="presentation" width="100%">
        <tr>
          <td class="px" style="padding:32px 40px 0;">
            <table role="presentation" width="100%"><tr>
              <td><img src="{t["LOGO"]}" width="72" height="22" alt="Asimov Academy" style="width:72px; height:22px;"></td>
              <td align="right" style="{ts("Rótulo", t)}"><span style="color:{ACCENT};">&#9632;</span>&nbsp; Edição 01</td>
            </tr></table>
          </td>
        </tr>
        <tr>
          <td class="px" style="padding:96px 40px 0;">
            <div style="{ts("Índice", t)}">01 &mdash; 03</div>
            <div class="h1" style="margin:14px 0 0; max-width:470px; {ts("Manchete", t)}">Lorem ipsum dolor sit amet.</div>
            <p class="lead" style="margin:20px 0 0; max-width:400px; font-family:{SANS}; font-size:17px; line-height:27px; color:{t["BODY"]};">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor.</p>
          </td>
        </tr>
      </table>
      <!--[if gte mso 9]></v:textbox></v:rect><![endif]-->
    </td>
  </tr>
  <tr><td class="px" style="padding:0 40px;">{spec_bar(t)}</td></tr>
</table>'''


def rail(num, inner, t, last=False):
    """Um passo do trilho: índice em mono à esquerda, fio vertical, conteúdo à direita."""
    pad_bottom = "0" if last else "48px"
    return (f'<table role="presentation" width="100%"><tr>'
            f'<td class="rail" width="52" valign="top" style="width:52px; padding-top:9px;">'
            f'<table role="presentation" width="100%"><tr>'
            f'<td style="{ts("Índice", t)}">{num}</td>'
            f'<td width="14" valign="middle"><div style="height:1px; line-height:1px; font-size:0; background:{ACCENT};">&nbsp;</div></td>'
            f'</tr></table></td>'
            f'<td class="rail-body" valign="top" style="border-left:1px solid {t["LINE"]}; padding:0 0 {pad_bottom} 28px;">{inner}</td>'
            f'</tr></table>')


def section_title(text, t):
    return f'<div class="h2" style="margin:0; {ts("Título de seção", t)}">{text}</div>'


def paragraphs(items, t, first_margin="18px"):
    out = []
    for i, text in enumerate(items):
        top = first_margin if i == 0 else "20px"
        out.append(f'<p style="margin:{top} 0 0; {ts("Corpo", t)}">{text}</p>')
    return "".join(out)


def window(t, filename="lorem-ipsum.md", text=None, caption="Lorem ipsum, 2026"):
    """Janela de editor: barra com três pontos e nome de arquivo; dentro, a frase em destaque."""
    text = text or "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore."
    dots = "".join(
        f'<td width="8" height="8" bgcolor="{c}" style="width:8px; height:8px; background:{c}; border-radius:999px; font-size:0; line-height:0;">&nbsp;</td>'
        f'<td width="6" style="font-size:0;">&nbsp;</td>'
        for c in (ACCENT, t["FAINT"], t["FAINT"]))
    return (f'<table role="presentation" width="100%" style="border-collapse:separate; border:1px solid {t["SURFACE_LINE"]}; border-radius:14px;">'
            f'<tr><td bgcolor="{t["SURFACE2"]}" style="background:{t["SURFACE2"]}; border-bottom:1px solid {t["SURFACE_LINE"]}; border-radius:14px 14px 0 0; padding:12px 16px;">'
            f'<table role="presentation" width="100%"><tr>'
            f'<td width="60"><table role="presentation" style="border-collapse:separate;"><tr>{dots}</tr></table></td>'
            f'<td style="{ts("Rótulo", t)} text-transform:none; letter-spacing:0.2px;">{filename}</td>'
            f'</tr></table></td></tr>'
            f'<tr><td bgcolor="{t["SURFACE"]}" style="background:{t["SURFACE"]}; border-radius:0 0 14px 14px; padding:24px 24px 22px;">'
            f'<div class="quote" style="{ts("Destaque", t)}">{text}</div>'
            f'<div style="margin-top:14px; {ts("Rótulo", t)}">&mdash; {caption}</div>'
            f'</td></tr></table>')


def signature(t):
    return (f'<div style="margin-top:28px; font-family:{SANS}; font-size:15px; line-height:22px; font-weight:500; color:{t["TEXT"]};">Lorem Ipsum</div>'
            f'<div style="margin-top:2px; {ts("Rótulo", t)}">Dolor sit amet &middot; Asimov</div>')


def button(t, label="Lorem ipsum dolor", href="{{link_cta}}"):
    """CTA: uma tecla teal com o texto da ação e a seta, alinhada à esquerda com o texto."""
    width = max(220, 9 * len(label) + 90)
    return (f'<table role="presentation" style="border-collapse:separate;"><tr>'
            f'<td bgcolor="{ACCENT}" style="background:{ACCENT}; background-image:linear-gradient(135deg, #2dd4bf, #0d9488); border-radius:12px; '
            f'box-shadow:0 10px 28px rgba(20,184,166,.22);">'
            f'<!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" href="{href}" style="height:50px;v-text-anchor:middle;width:{width}px;" '
            f'arcsize="24%" stroke="f" fillcolor="{ACCENT}"><w:anchorlock/><center style="color:{ON_ACCENT};font-family:Arial,sans-serif;font-size:15px;font-weight:bold;">{label}</center></v:roundrect><![endif]-->'
            f'<!--[if !mso]><!--><a class="btn-a" href="{href}" style="display:inline-block; padding:14px 18px 14px 22px; text-decoration:none; border-radius:12px;">'
            f'<table role="presentation" style="border-collapse:separate;"><tr>'
            f'<td class="btn-t" style="font-family:{SANS}; font-size:15px; line-height:22px; font-weight:600; color:{ON_ACCENT};">{label}</td>'
            f'<td width="14" style="font-size:0;">&nbsp;</td>'
            f'<td valign="middle"><img src="img/seta-escura.png" width="18" height="18" alt="" style="width:18px; height:18px;"></td>'
            f'</tr></table></a><!--<![endif]--></td></tr></table>')


def footer(t):
    links = "&nbsp;&nbsp;/&nbsp;&nbsp;".join(
        f'<a href="{{{{link_{k.lower()}}}}}" style="color:{t["MUTED"]}; text-decoration:none;">{k}</a>'
        for k in ("YouTube", "Instagram", "LinkedIn"))
    return (f'<table role="presentation" width="100%" style="border-top:1px solid {t["LINE"]};"><tr>'
            f'<td class="stack" valign="top" style="padding-top:22px; {ts("Rótulo", t)}">Asimov Academy<br><span style="text-transform:none; letter-spacing:0.2px;">{{{{endereco}}}}</span></td>'
            f'<td class="stack" align="right" valign="top" style="padding-top:22px; {ts("Rótulo", t)}">{links}<br>'
            f'<a href="{{{{link_descadastro}}}}" style="color:{t["MUTED"]};">Cancelar inscrição</a></td>'
            f'</tr></table>')


# ------------------------------------------------------------------ email

SHELL = """<!DOCTYPE html>
<html lang="pt-BR" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="x-apple-disable-message-reformatting">
  <meta name="format-detection" content="telephone=no, date=no, address=no">
  <meta name="color-scheme" content="%SCHEME%">
  <meta name="supported-color-schemes" content="%SCHEME%">
  <title>%TITLE%</title>
  <!--[if mso]><noscript><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch></o:OfficeDocumentSettings></xml></noscript><![endif]-->
  <!--
    Gerado por scripts/build-email-ds-cadence.py. Edite o script, não este arquivo.
    Antes do disparo, troque img/... por URLs absolutas hospedadas.
  -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&amp;family=JetBrains+Mono:wght@400;500&amp;display=swap" rel="stylesheet">
  <style>
    body { margin: 0; padding: 0; width: 100% !important; background: %PAGE%; -webkit-text-size-adjust: 100%; }
    table { border-collapse: collapse; mso-table-lspace: 0; mso-table-rspace: 0; }
    img { border: 0; display: block; outline: none; text-decoration: none; -ms-interpolation-mode: bicubic; }
    a { color: %ACCENT_TEXT%; }
    p { margin: 0; }
    @media (max-width: 620px) {
      .container { width: 100% !important; }
      .px { padding-left: 24px !important; padding-right: 24px !important; }
      .hero { height: auto !important; padding-bottom: 48px !important; }
      .h1 { font-size: 40px !important; line-height: 42px !important; letter-spacing: -1.6px !important; }
      .h2 { font-size: 24px !important; line-height: 30px !important; }
      .quote { font-size: 18px !important; line-height: 28px !important; }
      .rail { width: 40px !important; }
      .rail-body { padding-left: 18px !important; }
      .rail-body p { font-size: 16px !important; line-height: 27px !important; }
      .spec-cell { padding-left: 12px !important; padding-right: 8px !important; }
      .btn-t { white-space: normal !important; }
      .stack { display: block !important; width: 100% !important; text-align: left !important; box-sizing: border-box; }
    }
  </style>
</head>
<body style="margin:0; padding:0; background:%PAGE%;">
  <div style="display:none; max-height:0; overflow:hidden; mso-hide:all;">%PREHEADER%&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;</div>
  <table role="presentation" width="100%" bgcolor="%PAGE%" style="background:%PAGE%;">
    <tr>
      <td align="center" style="padding:0 0 48px;">
        <table role="presentation" class="container" width="600" style="width:600px; max-width:600px;">
%ROWS%
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def row(html, pad, cls="px"):
    return f'          <tr>\n            <td class="{cls}" style="padding:{pad};">{html}</td>\n          </tr>'


def email(theme):
    t = THEMES[theme]
    rows = [
        row(hero(t), "0", cls=""),
        row(rail("01", section_title("Lorem ipsum dolor sit amet, consectetur.", t)
                 + paragraphs([LOREM["longo"], LOREM["curto"]], t), t), "56px 40px 0"),
        row(rail("02", section_title("Sed ut perspiciatis unde omnis.", t)
                 + paragraphs([LOREM["medio"]], t)
                 + f'<div style="height:28px;"></div>{window(t)}'
                 + paragraphs([LOREM["longo"]], t, "28px"), t), "0 40px"),
        row(rail("03", paragraphs([LOREM["medio"]], t, "0") + signature(t), t, last=True), "0 40px"),
        row(f'<div style="margin-bottom:14px; {ts("Rótulo", t)}">Próximo passo</div>' + button(t), "56px 40px 0"),
        row(footer(t), "56px 40px 0"),
    ]
    tokens = dict(t, ROWS="\n\n".join(rows), TITLE="Lorem ipsum", PREHEADER="Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
    html = re.sub(r"%([A-Z_0-9]+)%", lambda m: tokens.get(m.group(1), m.group(0)), SHELL)
    leftover = set(re.findall(r"%[A-Z_0-9]+%", html))
    if leftover:
        raise SystemExit(f"email-{theme}: tokens sem valor {leftover}")
    return html


def blocos(t):
    """Os blocos de texto do email conversacional, na ordem de email_copies.render_blocks."""
    p = lambda text: f'<p style="margin:0 0 18px; {ts("Corpo", t)}">{text}</p>'
    cta_ = lambda label: f'<div style="padding:10px 0 30px;">{button(t, label)}</div>'
    ul = lambda items: ('<table role="presentation" style="margin:0 0 22px;">' + "".join(
        f'<tr><td width="28" valign="top" style="padding:0; {ts("Índice", t)} line-height:29px;">{n:02d}</td>'
        f'<td style="padding:0 0 4px; {ts("Corpo", t)}">{i}</td></tr>' for n, i in enumerate(items, 1)) + "</table>")
    sign = lambda name, role: (f'<div style="margin-top:4px; font-family:{SANS}; font-size:16px; line-height:22px; font-weight:500; color:{t["TEXT"]};">{name}</div>'
                               + (f'<div style="margin-top:2px; {ts("Rótulo", t)}">{role}</div>' if role else ""))
    ps = lambda text: (f'<p style="margin:28px 0 0; padding-top:20px; border-top:1px solid {t["LINE"]}; {ts("Corpo", t)}">'
                       f'<span style="{ts("Índice", t)}">PS &rsaquo;</span>&nbsp; {text}</p>')
    return p, cta_, ul, sign, ps


def capa(t):
    src = t["HERO"].replace("chuva", "capa")
    return f'<img src="{src}" width="600" height="150" alt="Asimov Academy" style="display:block; width:100%; max-width:600px; height:auto;">'


def fill(t, rows, title, preheader):
    tokens = dict(t, ROWS=rows, TITLE=title, PREHEADER=preheader)
    return re.sub(r"%([A-Z_0-9]+)%", lambda m: tokens.get(m.group(1), m.group(0)), SHELL)


def conversa(theme, copy):
    """Email conversacional (sem título): capa estreita da chuva, a conversa, botões no texto, assinatura."""
    t = THEMES[theme]
    rows = [
        row(capa(t), "0", cls=""),
        row(render_blocks(copy["blocks"], *blocos(t)), "44px 40px 0", "px body"),
        row(footer(t), "48px 40px 0"),
    ]
    return fill(t, "\n\n".join(rows), copy["assunto"], copy["preheader"])


# ------------------------------------------------------------------ kit para download

def kit():
    """O sistema inteiro para aplicações: casca, todas as peças e tokens (ver email_kit.py)."""
    variantes = []
    for theme, t in THEMES.items():
        p, cta_, ul, sign, ps = blocos(t)
        passo = section_title("Lorem ipsum dolor sit amet, consectetur.", t) + paragraphs([LOREM["medio"]], t)
        pecas = [
            ("capa", "Capa", "linha", "Topo dos emails conversacionais: a chuva de luz numa faixa de 600x150.", row(capa(t), "0", cls="")),
            ("hero", "Cabeçalho", "linha", "Topo dos emails com título: chuva de luz, manchete e ficha técnica.", row(hero(t), "0", cls="")),
            ("passo", "Passo do trilho", "linha", "Um trecho numerado do texto: índice em mono, fio e título. Troque o número (01, 02...).",
             row(rail("01", passo, t), "56px 40px 0")),
            ("passo-final", "Último passo", "linha", "Fecha o trilho: vem logo depois de um passo, sem espaço acima.",
             row(rail("03", paragraphs([LOREM["medio"]], t, "0") + signature(t), t, last=True), "0 40px")),
            ("corpo", "Corpo", "linha", "O texto do email. Recebe os blocos em {{blocos}}.", row("{{blocos}}", "44px 40px 0", "px body")),
            ("proximo-passo", "Próximo passo", "linha", "Fechamento com a ação: rótulo em mono e a tecla teal.",
             row(f'<div style="margin-bottom:14px; {ts("Rótulo", t)}">Próximo passo</div>' + button(t), "56px 40px 0")),
            ("rodape", "Rodapé", "linha", "Endereço, redes e descadastro. Obrigatório.", row(footer(t), "48px 40px 0")),
            ("paragrafo", "Parágrafo", "bloco", "Todo o texto corrido. Frases curtas, um parágrafo por ideia.", p(LOREM["medio"])),
            ("botao", "Botão", "bloco", "A ação do email: a tecla teal, alinhada ao texto.", cta_("Lorem ipsum dolor")),
            ("janela", "Janela de editor", "bloco", "A frase que merece destaque, como um arquivo aberto.",
             f'<div style="padding:10px 0 28px;">{window(t)}</div>'),
            ("lista", "Lista numerada", "bloco", "Itens curtos e paralelos, numerados em mono.", ul(["Lorem ipsum dolor sit amet", "Consectetur adipiscing elit", "Sed do eiusmod tempor"])),
            ("assinatura", "Assinatura", "bloco", "Quem assina o email. O cargo é opcional.", sign("Lorem Ipsum", "Dolor sit amet da Asimov Academy")),
            ("ps", "PS", "bloco", "Pós-escrito no fim do texto.", ps(LOREM["curto"])),
        ]
        variantes.append(Variante(
            id=theme, rotulo=f"Tema {theme}", tema=theme,
            casca=fill(t, "{{linhas}}", "{{assunto}}", "{{preheader}}"),
            componentes=[Componente(s, n, tp, u, h) for s, n, tp, u, h in pecas],
            cores=dict({k: v for k, v in t.items() if isinstance(v, str) and v.startswith("#")}, ACCENT=ACCENT, ON_ACCENT=ON_ACCENT)))
    return Kit(
        slug="cadence", nome="Cadence", pasta="design-system-cadence",
        descricao="A chuva de luz do Cadence Rain com cara de workspace: trilho numerado em mono, janela de editor e CTA como tecla teal.",
        fontes=["Inter (Google Fonts), com Helvetica e Arial de reserva", "JetBrains Mono nos rótulos, com Menlo e Consolas de reserva"],
        tipografia=[dict(nome=n, familia="mono" if fam == "MONO" else "sans", tamanho=s, entrelinha=lh, peso=w, tracking=tr, mobile=m, uso=u)
                    for n, (fam, s, lh, w, tr, _, m, u) in TYPE.items()],
        variantes=variantes,
        exemplos=sorted(p.name for p in OUT.glob("*.html") if p.name != "index.html"),
        montagem=[("Conversacional", ["capa", "corpo", "rodape"]),
                  ("Com título", ["hero", "passo", "passo", "passo-final", "proximo-passo", "rodape"])],
    )


def spec_conversas():
    return f'<div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:14px;">' + "".join(
        f'<article style="border:1px solid rgba(255,255,255,.1); border-radius:18px; padding:20px; background:#0b0b0c;">'
        f'<div style="display:flex; justify-content:space-between; font-size:12px; color:#737373;"><span style="font-family:ui-monospace,Menlo,monospace; color:#2dd4bf;">{c["code"]}</span><span>{c["fase"]}</span></div>'
        f'<b style="display:block; margin-top:12px; font-weight:500; font-size:18px; letter-spacing:-0.3px; color:#fff;">{c["assunto"]}</b>'
        f'<p style="margin:6px 0 0; color:#a1a1aa; font-size:14px; line-height:21px;">{c["preheader"]}</p>'
        f'<small style="display:block; margin-top:10px; color:#737373; font-size:12px;">{c["publico"]} &middot; {c["data"]}</small>'
        f'<div style="display:flex; gap:16px; margin-top:14px; font-size:13px;"><a href="{c['id']}-escuro.html" target="_blank" style="color:#2dd4bf; text-decoration:none;">Escuro &rarr;</a><a href="{c['id']}-claro.html" target="_blank" style="color:#2dd4bf; text-decoration:none;">Claro &rarr;</a></div></article>' for c in COPIES) + '</div>'


# ------------------------------------------------------------------ página do design system

def both(fn, cls=""):
    return '<div class="pair">' + "".join(
        f'<div class="stage {cls}" style="background:{THEMES[th]["PAGE"]};"><span class="tag {th}">{th}</span>{fn(THEMES[th])}</div>'
        for th in THEMES) + "</div>"


def spec_type(t):
    out = ""
    for name, (fam, size, lh, weight, track, key, mob, use) in TYPE.items():
        sample = {"Índice": "01 &mdash; 03", "Rótulo": "Lorem ipsum"}.get(name, "Lorem ipsum dolor sit amet")
        out += (f'<div class="type-row" style="border-color:{t["LINE"]};">'
                f'<div style="{ts("Rótulo", t)} text-transform:none;"><b style="color:{t["TEXT"]}; font-weight:500;">{name}</b><br>'
                f'{"Inter" if fam == "SANS" else "JetBrains Mono"} {size}/{lh}<br>mobile {mob}</div>'
                f'<div style="{ts(name, t)}">{sample}</div></div>')
    return out


def spec_colors(t):
    keys = [("PAGE", "Página"), ("SURFACE", "Superfície"), ("SURFACE2", "Barra da janela"), ("TEXT", "Texto"),
            ("BODY", "Corpo"), ("MUTED", "Rótulo"), ("LINE", "Fio do trilho"), ("ACCENT_TEXT", "Índice")]
    out = '<div class="swatches">'
    for k, label in keys:
        out += (f'<div><div class="chip" style="background:{t[k]}; border-color:{t["SURFACE_LINE"]};"></div>'
                f'<div style="font-family:{SANS}; font-size:13px; color:{t["TEXT"]};">{label}</div>'
                f'<div style="{ts("Rótulo", t)} text-transform:none;">{t[k]}</div></div>')
    return out + "</div>"


def spec_paragraphs(t):
    return rail("A", f'<div style="{ts("Rótulo", t)}">Curto</div>' + paragraphs([LOREM["curto"]], t, "8px"), t) + \
        rail("B", f'<div style="{ts("Rótulo", t)}">Médio</div>' + paragraphs([LOREM["medio"]], t, "8px"), t) + \
        rail("C", f'<div style="{ts("Rótulo", t)}">Longo + longo</div>' + paragraphs([LOREM["longo"], LOREM["longo"]], t, "8px"), t, last=True)


SPEC = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Email Cadence · Asimov Design System</title>
  <link rel="stylesheet" href="../../assets/fonts/fonts.css">
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; background: #050505; color: #fff; font-family: %SANS%; -webkit-font-smoothing: antialiased; }
    .mono { font-family: %MONO%; }
    .masthead { background: #050505 url('img/chuva-escuro.jpg') right top / cover no-repeat; border-bottom: 1px solid #1f1f1f; }
    .masthead .in { max-width: 1240px; margin: 0 auto; padding: 28px 24px 0; }
    .masthead .bar { display: flex; justify-content: space-between; align-items: center; }
    .masthead .bar img { height: 20px; }
    .masthead .bar a { color: #a1a1aa; font-size: 12px; text-decoration: none; letter-spacing: 1.2px; text-transform: uppercase; }
    .masthead h1 { margin: 140px 0 0; max-width: 760px; font-weight: 500; font-size: clamp(44px, 7vw, 88px); line-height: .98; letter-spacing: -3.4px; }
    .masthead p { max-width: 520px; margin: 24px 0 0; color: #b4b4b4; font-size: 18px; line-height: 29px; }
    .masthead .spec { display: grid; grid-template-columns: repeat(4, 1fr); margin-top: 72px; border-top: 1px solid #1f1f1f; }
    .masthead .spec div { padding: 16px 18px; border-left: 1px solid #1f1f1f; font-size: 14px; font-weight: 500; }
    .masthead .spec div:first-child { border-left: 0; padding-left: 0; }
    .masthead .spec span { display: block; color: #737373; font-size: 11px; letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 4px; font-weight: 400; }
    .layout { max-width: 1240px; margin: 0 auto; padding: 0 24px 120px; display: grid; grid-template-columns: 200px 1fr; gap: 48px; }
    nav { position: sticky; top: 0; align-self: start; padding-top: 72px; }
    nav a { display: flex; gap: 12px; padding: 8px 0; color: #737373; text-decoration: none; font-size: 13px; border-left: 1px solid #1f1f1f; padding-left: 16px; }
    nav a b { color: #2dd4bf; font-weight: 500; }
    nav a:hover { color: #fff; border-color: #14b8a6; }
    section { padding-top: 72px; scroll-margin-top: 0; }
    .sec-head { display: grid; grid-template-columns: 80px 1fr 1fr; gap: 24px; align-items: start; margin-bottom: 28px; }
    .sec-head .n { color: #2dd4bf; font-size: 12px; padding-top: 12px; }
    .sec-head h2 { margin: 0; font-weight: 500; font-size: 36px; line-height: 40px; letter-spacing: -1.2px; }
    .sec-head p { margin: 4px 0 0; color: #a1a1aa; font-size: 14px; line-height: 23px; }
    .pair { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .stage { position: relative; min-width: 0; border: 1px solid #1f1f1f; border-radius: 16px; padding: 52px 32px 32px; overflow: hidden; }
    .tag { position: absolute; top: 14px; left: 32px; font-family: %MONO%; font-size: 10px; letter-spacing: 1.2px; text-transform: uppercase; }
    .tag::before { content: "\\25A0  "; color: #14b8a6; }
    .tag.escuro { color: #737373; } .tag.claro { color: #8a8a93; }
    .type-row { display: grid; grid-template-columns: 150px 1fr; gap: 20px; align-items: baseline; padding: 16px 0; border-bottom: 1px solid; }
    .type-row:last-child { border-bottom: 0; }
    .swatches { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px 12px; }
    .chip { height: 48px; border-radius: 10px; border: 1px solid; margin-bottom: 8px; }
    .single { max-width: 640px; }
    .frames { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
    .frames figure { margin: 0; }
    .frames figcaption { display: flex; justify-content: space-between; color: #737373; font-family: %MONO%; font-size: 11px; letter-spacing: 1.2px; text-transform: uppercase; margin-bottom: 12px; }
    .frames a { color: #2dd4bf; text-decoration: none; }
    iframe { display: block; width: 100%; height: 2300px; border: 1px solid #1f1f1f; border-radius: 16px; background: #050505; }
    @media (max-width: 980px) {
      .layout { grid-template-columns: 1fr; } nav { display: none; }
      .pair, .frames { grid-template-columns: 1fr; }
      .sec-head { grid-template-columns: 1fr; gap: 8px; }
      .masthead .spec { grid-template-columns: repeat(2, 1fr); }
      .masthead .spec div:nth-child(3) { border-left: 0; padding-left: 0; }
      .stage { padding: 48px 18px 24px; } .tag { left: 18px; }
      .swatches { grid-template-columns: repeat(2, 1fr); }
      .type-row { grid-template-columns: 1fr; gap: 6px; }
    }
  </style>
</head>
<body>
  <div class="masthead"><div class="in">
    <div class="bar"><img src="img/logo-branco.png" alt="Asimov"><a class="mono" href="../../design-system.html">Asimov Design System &rarr;</a></div>
    <div class="mono" style="margin-top:120px; color:#2dd4bf; font-size:12px;">EMAIL / CADENCE</div>
    <h1 style="margin-top:16px;">Chuva de luz, trilho e linha de comando.</h1>
    <p>Uma leitura do Cadence Rain para email. O texto anda por um trilho numerado, a frase importante ganha uma janela e o CTA é uma tecla teal.</p>
    <div class="spec">
      <div><span class="mono">Fundo</span>Cadence Rain</div>
      <div><span class="mono">Tipos</span>Inter + JetBrains Mono</div>
      <div><span class="mono">Acento</span>Teal Asimov</div>
      <div><span class="mono">Temas</span>Escuro e claro</div>
    </div>
  </div></div>

  <div class="layout">
    <nav class="mono">
      <a href="#tipografia"><b>01</b>Tipografia</a>
      <a href="#cores"><b>02</b>Cores</a>
      <a href="#paragrafos"><b>03</b>Parágrafos</a>
      <a href="#cabecalho"><b>04</b>Cabeçalho</a>
      <a href="#trilho"><b>05</b>Trilho</a>
      <a href="#janela"><b>06</b>Janela</a>
      <a href="#comando"><b>07</b>Botão</a>
      <a href="#rodape"><b>08</b>Rodapé</a>
      <a href="#conversas"><b>09</b>Conversacionais</a>
      <a href="#aplicacao"><b>10</b>Aplicação</a>
    </nav>
    <main>
      <section id="tipografia">
        <div class="sec-head"><div class="n mono">01</div><h2>Tipografia</h2><p>Inter para ler, JetBrains Mono para orientar. O mono só aparece em números, rótulos e no nome da janela. Fora do Apple Mail, cai para Menlo ou Consolas.</p></div>
        %TYPE%
      </section>
      <section id="cores">
        <div class="sec-head"><div class="n mono">02</div><h2>Cores</h2><p>A mesma base do design system principal. O teal aparece em pequenas doses: índices, o traço de cada passo, o primeiro ponto da janela e a tecla do CTA.</p></div>
        %COLORS%
      </section>
      <section id="paragrafos">
        <div class="sec-head"><div class="n mono">03</div><h2>Parágrafos</h2><p>Corpo 17/29 com 20px entre parágrafos. O trilho estreita a coluna para cerca de 60 caracteres por linha. No mobile, 16/27.</p></div>
        %PARAGRAPHS%
      </section>
      <section id="cabecalho">
        <div class="sec-head"><div class="n mono">04</div><h2>Cabeçalho</h2><p>A chuva de luz como imagem de fundo, mais escura do lado do texto. Embaixo, uma ficha técnica em três células. No claro, a chuva fica teal sobre cinza-claro.</p></div>
        %HERO%
      </section>
      <section id="trilho">
        <div class="sec-head"><div class="n mono">05</div><h2>Trilho</h2><p>Cada bloco do texto é um passo numerado. O fio vertical é a borda da célula e o traço teal liga o número ao fio. Tudo é tabela, então funciona até no Outlook.</p></div>
        %RAIL%
      </section>
      <section id="janela">
        <div class="sec-head"><div class="n mono">06</div><h2>Janela</h2><p>Para a frase que precisa de pausa. A barra tem três pontos, o primeiro em teal, e um nome de arquivo. Use uma por email, no máximo.</p></div>
        %WINDOW%
      </section>
      <section id="comando">
        <div class="sec-head"><div class="n mono">07</div><h2>Botão</h2><p>Uma tecla teal com o texto da ação e a seta, alinhada à esquerda como o texto. Cantos de 12px, como a janela. Textos longos quebram de linha no mobile. No Outlook, VML.</p></div>
        %COMMAND%
      </section>
      <section id="rodape">
        <div class="sec-head"><div class="n mono">08</div><h2>Rodapé</h2><p>Mono em caixa alta, links separados por barra. Sem logo: o cabeçalho já assinou.</p></div>
        %FOOTER%
      </section>
      <section id="conversas">
        <div class="sec-head"><div class="n mono">09</div><h2>Emails conversacionais</h2><p>Copies reais, sem título: capa estreita da chuva, a conversa, o botão no meio do texto e a assinatura. Listas viram índice numerado.</p></div>
        %CONVERSAS%
        <div class="frames" style="margin-top:16px;">
          <figure><figcaption>EM-022 · escuro <a href="em-022-escuro.html" target="_blank">Abrir &rarr;</a></figcaption><iframe src="em-022-escuro.html" title="EM-022, escuro"></iframe></figure>
          <figure><figcaption>EM-001 · claro <a href="em-001-claro.html" target="_blank">Abrir &rarr;</a></figcaption><iframe src="em-001-claro.html" title="EM-001, claro"></iframe></figure>
        </div>
      </section>
      <section id="aplicacao">
        <div class="sec-head"><div class="n mono">09</div><h2>Aplicação</h2><p>Um email escrito com o CTA no final, montado com os componentes acima pelo mesmo script.</p></div>
        <div class="frames">
          <figure><figcaption>Escuro <a href="email-escuro.html" target="_blank">Abrir &rarr;</a></figcaption><iframe src="email-escuro.html" title="Email Cadence, escuro"></iframe></figure>
          <figure><figcaption>Claro <a href="email-claro.html" target="_blank">Abrir &rarr;</a></figcaption><iframe src="email-claro.html" title="Email Cadence, claro"></iframe></figure>
        </div>
      </section>
    </main>
  </div>
  <script>
    document.querySelectorAll("iframe").forEach(f => f.addEventListener("load", () => {
      try { f.style.height = "0px"; f.style.height = f.contentDocument.documentElement.scrollHeight + "px"; } catch (_) {}  /* zera antes de medir: scrollHeight nunca é menor que a altura atual */
    }));
  </script>
</body>
</html>
"""


def specimen():
    parts = {
        "SANS": SANS, "MONO": MONO,
        "TYPE": both(spec_type),
        "COLORS": both(spec_colors),
        "PARAGRAPHS": both(spec_paragraphs),
        "HERO": both(hero),
        "RAIL": both(lambda t: rail("01", section_title("Lorem ipsum dolor sit.", t) + paragraphs([LOREM["medio"]], t), t)
                     + rail("02", section_title("Sed ut perspiciatis.", t) + paragraphs([LOREM["curto"]], t), t, last=True)),
        "WINDOW": both(window),
        "COMMAND": both(lambda t: button(t, href="#") + '<div style="height:20px;"></div>' + button(t, "Quero receber o guia com 50 Skills do Claude", "#")),
        "FOOTER": both(footer),
        "CONVERSAS": spec_conversas(),
    }
    return re.sub(r"%([A-Z_]+)%", lambda m: parts.get(m.group(1), m.group(0)), SPEC)


def main():
    for theme in THEMES:
        (OUT / f"email-{theme}.html").write_text(email(theme))
        print(f"email-{theme}.html")
    for copy in COPIES:
        for theme in THEMES:
            (OUT / f'{copy["id"]}-{theme}.html').write_text(conversa(theme, copy))
            print(f'{copy["id"]}-{theme}.html')
    (OUT / "index.html").write_text(specimen())
    print("index.html")
    write_kit(kit())


if __name__ == "__main__":
    main()
