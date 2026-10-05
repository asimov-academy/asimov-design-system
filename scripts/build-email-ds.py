#!/usr/bin/env python3
"""Design system de email da Asimov, na linguagem do Overview.

Tokens e componentes moram aqui. A página do design system e o email de
aplicação são montados com as mesmas funções, então nunca divergem.

Saída em emails/design-system/:

    index.html          página do design system (fundações, componentes, aplicação)
    email-escuro.html   aplicação: email escrito com CTA no final, tema escuro
    email-claro.html    a mesma aplicação, tema claro
    em-XXX-<tema>.html  emails conversacionais (copies reais, sem título)
    img/                imagens de fundo e ícones (PNG/JPG; email não aceita SVG)

kit() descreve as peças do sistema para os arquivos de download (ver build-email-export.py).

    python3 scripts/build-email-ds.py
"""
import re
from pathlib import Path

from email_copies import COPIES, render_blocks
from email_kit import Componente, Kit, Variante, endereco

OUT = Path(__file__).resolve().parent.parent / "emails" / "design-system"

FONT = "Inter, 'Helvetica Neue', Helvetica, Arial, sans-serif"

# ------------------------------------------------------------------ tokens

THEMES = {
    "escuro": {
        "SCHEME": "dark",
        "PAGE": "#050505",
        "TEXT": "#ffffff",
        "BODY": "#b4b4b4",
        "MUTED": "#737373",
        "LINE": "#1a1a1a",
        "LINE_STRONG": "#2e2e2e",
        "ACCENT_TEXT": "#2dd4bf",
        "SURFACE": "#0b0c0e",
        "SURFACE_LINE": "#1c1d20",
        "ICON_BG": "#0b1514",
        "ICON_LINE": "#1f3a36",
        "CTA_LINE": "#134e48",
        "HERO_LINE": "#161616",
        "HERO_IMG": "img/aura-hero-escuro.jpg",
        "HERO_BG": "#050505",
        "H_TEXT": "#ffffff",
        "H_TEXT2": "#a1a1aa",
        "H_BODY": "#c4c4cc",
        "H_META": "#8a8a8a",
        "H_LOGO": "img/logo-branco.png",
        "PILL_BG": "#0a1413",
        "PILL_LINE": "#1f3a36",
        "PILL_TEXT": "#5eead4",
        "CHIP_LINE": "#2a3a38",
        "CHIP_TEXT": "#a1a1aa",
        "FAIXA": "img/aura-faixa-escuro.jpg",
        "GLOW": "img/glow-escuro.jpg",
        "ICON": "img/caneta-teal.png",
        "ARROW_TEXT": "img/seta-branca.png",
        "ARROW_ACCENT": "img/seta-teal.png",
        "LOGO": "img/logo-branco.png",
    },
    "claro": {
        "SCHEME": "light",
        "PAGE": "#f4f4f5",
        "TEXT": "#09090b",
        "BODY": "#52525b",
        "MUTED": "#8a8a93",
        "LINE": "#e4e4e7",
        "LINE_STRONG": "#d4d4d8",
        "ACCENT_TEXT": "#0d9488",
        "SURFACE": "#ffffff",
        "SURFACE_LINE": "#e4e4e7",
        "ICON_BG": "#f0fdfa",
        "ICON_LINE": "#ccfbf1",
        "CTA_LINE": "#99f6e4",
        "HERO_LINE": "#dbe5f7",
        "HERO_IMG": "img/aura-hero-claro.jpg",
        "HERO_BG": "#eef3fd",
        "H_TEXT": "#09090b",
        "H_TEXT2": "#3f4a63",
        "H_BODY": "#27304a",
        "H_META": "#4b5675",
        "H_LOGO": "img/logo-preto.png",
        "PILL_BG": "#ffffff",
        "PILL_LINE": "#b9cdf3",
        "PILL_TEXT": "#0f766e",
        "CHIP_LINE": "#c7d4ee",
        "CHIP_TEXT": "#4b5675",
        "FAIXA": "img/aura-faixa-claro.jpg",
        "GLOW": "img/glow-claro.jpg",
        "ICON": "img/caneta-teal-escuro.png",
        "ARROW_TEXT": "img/seta-preta.png",
        "ARROW_ACCENT": "img/seta-teal-escuro.png",
        "LOGO": "img/logo-preto.png",
    },
}

# Fixos nos dois temas: a aura é sempre escura e o botão é sempre teal.
BRAND = {
    "ACCENT": "#14b8a6",
    "ACCENT_LIGHT": "#2dd4bf",
    "ACCENT_DARK": "#0d9488",
    "ACCENT_GLOW": "#5eead4",
    "ON_ACCENT": "#04201d",
    "AURA_BG": "#050505",
}

# nome: (tamanho, entrelinha, peso, tracking, cor, mobile, uso)
TYPE = {
    "Display": (50, 52, 500, -2.0, "TEXT", "38/40", "Título da aura. Só existe um por email."),
    "Título de seção": (30, 36, 500, -0.9, "TEXT", "26/32", "Abre o corpo do email."),
    "Título de cartão": (22, 28, 500, -0.5, "TEXT", "22/28", "Dentro de superfícies."),
    "Corpo": (17, 29, 400, 0, "BODY", "16/27", "Todo o texto corrido."),
    "Corpo pequeno": (15, 24, 400, 0, "BODY", "15/24", "Texto dentro de cartões."),
    "Meta": (12, 16, 600, 1.4, "ACCENT_TEXT", "12/16", "Rótulo acima de títulos, sempre em caixa alta."),
    "Legenda": (13, 20, 400, 0, "MUTED", "13/20", "Notas abaixo do botão, assinatura, rodapé."),
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
    size, lh, weight, track, key, _, _ = TYPE[name]
    c = color or (t[key] if key in t else BRAND[key])
    return (f"font-family:{FONT}; font-size:{size}px; line-height:{lh}px; font-weight:{weight}; "
            f"letter-spacing:{track}px; color:{c};")


# ------------------------------------------------------------------ componentes

def meta(text, t, margin="0"):
    return f'<div style="margin:{margin}; {ts("Meta", t)}">{text.upper()}</div>'


def heading(text, t, kind="Título de seção", margin="10px 0 0", cls="h2"):
    return f'<div class="{cls}" style="margin:{margin}; {ts(kind, t)}">{text}</div>'


def paragraphs(items, t, kind="Corpo", gap=22):
    out = []
    for i, text in enumerate(items):
        m = f"0 0 {gap}px" if i < len(items) - 1 else "0"
        out.append(f'<p style="margin:{m}; {ts(kind, t)}">{text}</p>')
    return "".join(out)


def pill(t, label="Lorem ipsum", chip="V1.0"):
    """Pílula de sobretítulo do topo, com as cores do céu de cada tema."""
    chip_html = (f'<td width="10" style="font-size:0;">&nbsp;</td>'
                 f'<td style="border:1px solid {t["CHIP_LINE"]}; border-radius:999px; padding:1px 8px; font-family:{FONT}; '
                 f'font-size:10px; line-height:14px; font-weight:500; color:{t["CHIP_TEXT"]};">{chip}</td>') if chip else ""
    pad = "6px 6px 6px 14px" if chip else "6px 14px"
    return (f'<table role="presentation" style="border-collapse:separate;"><tr>'
            f'<td bgcolor="{t["PILL_BG"]}" style="background:{t["PILL_BG"]}; border:1px solid {t["PILL_LINE"]}; border-radius:999px; padding:{pad};">'
            f'<table role="presentation" style="border-collapse:separate;"><tr>'
            f'<td style="font-family:{FONT}; font-size:11px; line-height:16px; font-weight:600; letter-spacing:1.6px; '
            f'color:{t["PILL_TEXT"]}; white-space:nowrap;"><span style="color:{BRAND["ACCENT"]};">&#9679;</span>&nbsp;&nbsp;{label.upper()}</td>'
            f'{chip_html}</tr></table></td></tr></table>')


def button(label, href, variant, t):
    """primario: pílula com degradê teal (Pricing). secundario: contorno. link: texto teal."""
    if variant == "link":
        return (f'<a href="{href}" style="text-decoration:none;"><table role="presentation" style="border-collapse:separate;"><tr>'
                f'<td style="font-family:{FONT}; font-size:15px; line-height:20px; font-weight:500; color:{t["TEXT"]};">{label}</td>'
                f'<td width="8" style="font-size:0;">&nbsp;</td>'
                f'<td><img src="{t["ARROW_ACCENT"]}" width="16" height="16" alt="" style="width:16px; height:16px;"></td>'
                f'</tr></table></a>')
    if variant == "primario":
        bg, fg, arrow = BRAND["ACCENT"], BRAND["ON_ACCENT"], "img/seta-escura.png"
        cell = (f'bgcolor="{bg}" style="background:{bg}; background-image:linear-gradient(135deg, {BRAND["ACCENT_LIGHT"]}, {BRAND["ACCENT_DARK"]}); '
                f'border-radius:999px; box-shadow:0 10px 36px rgba(20,184,166,.35);"')
        vml = f'stroke="f" fillcolor="{bg}"'
    else:
        bg, fg, arrow = t["SURFACE"], t["TEXT"], t["ARROW_TEXT"]
        cell = f'bgcolor="{bg}" style="background:{bg}; border:1px solid {t["LINE_STRONG"]}; border-radius:999px;"'
        vml = f'strokecolor="{t["LINE_STRONG"]}" fillcolor="{bg}"'
    width = max(220, 10 * len(label) + 110)
    return (f'<table role="presentation" style="border-collapse:separate;"><tr><td align="center" {cell}>'
            f'<!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" href="{href}" '
            f'style="height:56px;v-text-anchor:middle;width:{width}px;" arcsize="50%" {vml}><w:anchorlock/>'
            f'<center style="color:{fg};font-family:Arial,sans-serif;font-size:16px;font-weight:bold;">{label}</center>'
            f'</v:roundrect><![endif]--><!--[if !mso]><!-->'
            f'<a href="{href}" style="display:inline-block; padding:17px 22px 17px 32px; text-decoration:none; border-radius:999px;">'
            f'<table role="presentation" style="border-collapse:separate;"><tr>'
            f'<td style="font-family:{FONT}; font-size:16px; line-height:22px; font-weight:600; color:{fg}; white-space:nowrap;">{label}</td>'
            f'<td width="14" style="font-size:0;">&nbsp;</td>'
            f'<td><img src="{arrow}" width="20" height="20" alt="" style="width:20px; height:20px;"></td>'
            f'</tr></table></a><!--<![endif]--></td></tr></table>')


def icon_box(t):
    return (f'<table role="presentation" style="border-collapse:separate;"><tr>'
            f'<td width="44" height="44" align="center" valign="middle" bgcolor="{t["ICON_BG"]}" '
            f'style="width:44px; height:44px; background:{t["ICON_BG"]}; border:1px solid {t["ICON_LINE"]}; border-radius:12px;">'
            f'<img src="{t["ICON"]}" width="22" height="22" alt="" style="width:22px; height:22px; margin:0 auto;"></td>'
            f'</tr></table>')


def surface(inner, t, cta=False):
    """Formation surface (cta=False) ou superfície do Pricing (cta=True, borda teal e centralizada)."""
    line = t["CTA_LINE"] if cta else t["SURFACE_LINE"]
    radius, pad, align, pos = (24, "40px 28px 34px", "center", "center top") if cta else (20, "30px 30px 32px", "left", "left top")
    return (f'<table role="presentation" width="100%" style="border-collapse:separate;"><tr>'
            f'<td align="{align}" background="{t["GLOW"]}" bgcolor="{t["SURFACE"]}" '
            f'style="background:{t["SURFACE"]} url(\'{t["GLOW"]}\') {pos} / cover no-repeat; border:1px solid {line}; '
            f'border-radius:{radius}px; padding:{pad};">{inner}</td></tr></table>')


def feature_card(t):
    return surface(
        icon_box(t) + meta("Lorem ipsum", t, "22px 0 0")
        + heading("Lorem ipsum dolor sit", t, "Título de cartão", "8px 0 0", "")
        + f'<div style="margin-top:8px; {ts("Corpo pequeno", t)}">{LOREM["medio"]}</div>', t)


def faixa(t, radius="20px 20px 0 0"):
    """Paisagem 3:1 (600x200). Sozinha ou no topo do cartão de CTA."""
    return (f'<img src="{t["FAIXA"]}" width="520" height="173" alt="" '
            f'style="display:block; width:100%; max-width:520px; height:auto; border-radius:{radius};">')


def cta_card(t, href="{{link_cta}}"):
    btn = button("Lorem ipsum dolor", href, "primario", t)
    inner = surface(
        meta("Lorem ipsum", t)
        + heading("Lorem ipsum dolor sit amet.", t, margin="10px 0 0")
        + f'<table role="presentation" style="border-collapse:separate; margin:26px auto 0;"><tr><td>{btn}</td></tr></table>'
        + f'<div style="margin-top:18px; {ts("Legenda", t)}">Lorem ipsum dolor sit amet, consectetur.</div>', t, cta=True)
    # a faixa encosta no cartão: o cartão perde o raio de cima
    inner = inner.replace("border-radius:24px;", "border-radius:0 0 24px 24px; border-top:0;", 1)
    return (f'<table role="presentation" width="100%" style="border-collapse:separate;">'
            f'<tr><td style="border:1px solid {t["CTA_LINE"]}; border-bottom:0; border-radius:24px 24px 0 0; font-size:0; line-height:0;">{faixa(t, "23px 23px 0 0")}</td></tr>'
            f'<tr><td>{inner}</td></tr></table>')


def divider(t):
    return (f'<table role="presentation" width="100%"><tr>'
            f'<td height="1" bgcolor="{t["LINE"]}" style="height:1px; background:{t["LINE"]}; '
            f'background-image:linear-gradient(90deg, {t["PAGE"]}, {BRAND["ACCENT"]} 50%, {t["PAGE"]}); font-size:0; line-height:0;">&nbsp;</td>'
            f'</tr></table>')


def signature(t):
    return (f'<div style="font-family:{FONT}; font-size:15px; line-height:22px; font-weight:500; color:{t["TEXT"]};">Lorem Ipsum</div>'
            f'<div style="{ts("Legenda", t)}">Dolor sit amet &middot; Asimov Academy</div>')


def hero(t):
    """Aura + paisagem como imagem de fundo, com texto real por cima. Noite no escuro, dia no claro."""
    return f'''<table role="presentation" width="100%" style="border-collapse:separate;">
  <tr>
    <td class="hero" height="600" valign="top" background="{t["HERO_IMG"]}" bgcolor="{t["HERO_BG"]}"
        style="height:600px; background:{t["HERO_BG"]} url('{t["HERO_IMG"]}') center bottom / cover no-repeat; border:1px solid {t["HERO_LINE"]}; border-radius:24px;">
      <!--[if gte mso 9]>
      <v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false" style="width:600px;height:600px;">
        <v:fill type="frame" src="{t["HERO_IMG"]}" color="{t["HERO_BG"]}" />
        <v:textbox inset="0,0,0,0">
      <![endif]-->
      <table role="presentation" width="100%">
        <tr>
          <td class="px" style="padding:36px 40px 0;">
            <table role="presentation" width="100%"><tr>
              <td><img src="{t["H_LOGO"]}" width="72" height="22" alt="Asimov Academy" style="width:72px; height:22px;"></td>
              <td align="right" style="font-family:{FONT}; font-size:12px; line-height:16px; color:{t["H_META"]};">Lorem ipsum &nbsp;&middot;&nbsp; 2026</td>
            </tr></table>
          </td>
        </tr>
        <tr>
          <td class="px" style="padding:64px 40px 0;">
            {pill(t)}
            <div class="h1" style="margin:22px 0 0; {ts("Display", t, t["H_TEXT"])}">Lorem ipsum dolor<br><span style="color:{t["H_TEXT2"]};">sit amet consectetur.</span></div>
            <p style="margin:18px 0 0; max-width:420px; font-family:{FONT}; font-size:17px; line-height:27px; color:{t["H_BODY"]};">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor.</p>
          </td>
        </tr>
        <tr><td class="hero-gap" height="210" style="height:210px; font-size:0; line-height:0;">&nbsp;</td></tr>
      </table>
      <!--[if gte mso 9]></v:textbox></v:rect><![endif]-->
    </td>
  </tr>
</table>'''


def footer(t):
    links = "&nbsp;&nbsp;&nbsp;".join(
        f'<a href="{{{{link_{k.lower()}}}}}" style="color:{t["MUTED"]}; text-decoration:none;">{k}</a>'
        for k in ("YouTube", "Instagram", "LinkedIn"))
    return (f'<table role="presentation" width="100%"><tr>'
            f'<td valign="top"><img src="{t["LOGO"]}" width="60" height="18" alt="Asimov Academy" style="width:60px; height:18px; opacity:.6;"></td>'
            f'<td align="right" valign="top" style="font-family:{FONT}; font-size:12px; line-height:18px;">{links}</td>'
            f'</tr></table>'
            f'<div style="margin-top:18px; font-family:{FONT}; font-size:12px; line-height:19px; color:{t["MUTED"]};">'
            f'Asimov Academy &middot; {endereco(t["MUTED"])}<br>'
            f'<a href="{{{{link_descadastro}}}}" style="color:{t["MUTED"]};">Cancelar inscrição</a></div>')


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
    Gerado por scripts/build-email-ds.py. Edite o script, não este arquivo.
    Antes do disparo, troque img/... por URLs absolutas hospedadas.
  -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&amp;display=swap" rel="stylesheet">
  <style>
    body { margin: 0; padding: 0; width: 100% !important; background: %PAGE%; -webkit-text-size-adjust: 100%; }
    table { border-collapse: collapse; mso-table-lspace: 0; mso-table-rspace: 0; }
    img { border: 0; display: block; outline: none; text-decoration: none; -ms-interpolation-mode: bicubic; }
    a { color: %ACCENT_TEXT%; }
    p { margin: 0; }
%MOBILE%
  </style>
</head>
<body style="margin:0; padding:0; background:%PAGE%;">
  <div style="display:none; max-height:0; overflow:hidden; mso-hide:all;">%PREHEADER%&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;</div>
  <table role="presentation" width="100%" bgcolor="%PAGE%" style="background:%PAGE%;">
    <tr>
      <td align="center" style="padding:24px 12px 48px;">
        <table role="presentation" class="container" width="600" style="width:600px; max-width:600px;">
%ROWS%
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

MOBILE = """    @media (max-width: 620px) {
      .container { width: 100% !important; }
      .px { padding-left: 24px !important; padding-right: 24px !important; }
      .hero { height: auto !important; }
      .hero-gap { height: 180px !important; }
      .h1 { font-size: 38px !important; line-height: 40px !important; letter-spacing: -1.4px !important; }
      .h2 { font-size: 26px !important; line-height: 32px !important; }
      .body td { white-space: normal !important; }
      .body p { font-size: 16px !important; line-height: 27px !important; }
    }"""


def row(html, pad, cls="px"):
    return f'          <tr>\n            <td class="{cls}" style="padding:{pad};">{html}</td>\n          </tr>'


def email(theme):
    t = THEMES[theme]
    rows = [
        row(hero(t), "0", cls=""),
        row(meta("Lorem ipsum", t) + heading("Lorem ipsum dolor sit amet, consectetur adipiscing.", t), "56px 40px 0"),
        row(paragraphs([f'<strong style="font-weight:500; color:{t["TEXT"]};">Lorem ipsum,</strong> {LOREM["longo"]}',
                        LOREM["curto"], LOREM["medio"]], t), "24px 40px 0", "px body"),
        row(feature_card(t), "40px 40px 0"),
        row(paragraphs([LOREM["medio"], LOREM["longo"]], t), "40px 40px 0", "px body"),
        row(signature(t), "32px 40px 0"),
        row(cta_card(t), "56px 40px 0"),
        row(divider(t), "48px 40px 0"),
        row(footer(t), "28px 40px 0"),
    ]
    tokens = dict(t, MOBILE=MOBILE, ROWS="\n\n".join(rows), TITLE="Lorem ipsum", PREHEADER="Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
    html = re.sub(r"%([A-Z_]+)%", lambda m: tokens.get(m.group(1), m.group(0)), SHELL)
    leftover = set(re.findall(r"%[A-Z_]+%", html))
    if leftover:
        raise SystemExit(f"email-{theme}: tokens sem valor {leftover}")
    return html


def blocos(t):
    """Os blocos de texto do email conversacional, na ordem de email_copies.render_blocks."""
    p = lambda text: f'<p style="margin:0 0 18px; {ts("Corpo", t)}">{text}</p>'
    cta_ = lambda label: f'<div style="padding:10px 0 28px;">{button(label, "{{link_cta}}", "primario", t)}</div>'
    ul = lambda items: ('<table role="presentation" style="margin:0 0 22px;">' + "".join(
        f'<tr><td width="22" valign="top" style="padding:12px 0 0;"><div style="width:6px; height:6px; border-radius:999px; background:{BRAND["ACCENT"]}; font-size:0; line-height:0;">&nbsp;</div></td>'
        f'<td style="padding:0 0 6px; {ts("Corpo", t)}">{i}</td></tr>' for i in items) + "</table>")
    sign = lambda name, role: (f'<div style="margin-top:4px; font-family:{FONT}; font-size:16px; line-height:22px; font-weight:500; color:{t["TEXT"]};">{name}</div>'
                               + (f'<div style="{ts("Legenda", t)}">{role}</div>' if role else ""))
    ps = lambda text: (f'<p style="margin:28px 0 0; padding-top:20px; border-top:1px solid {t["LINE"]}; {ts("Corpo", t)}">'
                       f'<strong style="font-weight:600; color:{t["TEXT"]};">PS:</strong> {text}</p>')
    return p, cta_, ul, sign, ps


def capa(t):
    src = t["HERO_IMG"].replace("aura-hero", "capa")
    return f'<img src="{src}" width="600" height="150" alt="Asimov Academy" style="display:block; width:100%; max-width:600px; height:auto; border-radius:20px;">'


def fill(t, rows, title, preheader):
    tokens = dict(t, MOBILE=MOBILE, ROWS=rows, TITLE=title, PREHEADER=preheader)
    return re.sub(r"%([A-Z_]+)%", lambda m: tokens.get(m.group(1), m.group(0)), SHELL)


def conversa(theme, copy):
    """Email conversacional (sem título): capa estreita da Aura, a conversa, botões no texto, assinatura."""
    t = THEMES[theme]
    rows = [
        row(capa(t), "0", cls=""),
        row(render_blocks(copy["blocks"], *blocos(t)), "40px 40px 0", "px body"),
        row(divider(t), "40px 40px 0"),
        row(footer(t), "28px 40px 0"),
    ]
    return fill(t, "\n\n".join(rows), copy["assunto"], copy["preheader"])


# ------------------------------------------------------------------ kit para download

def kit():
    """O sistema inteiro para aplicações: casca, todas as peças e tokens (ver email_kit.py)."""
    variantes = []
    for theme, t in THEMES.items():
        p, cta_, ul, sign, ps = blocos(t)
        pecas = [
            ("capa", "Capa", "linha", "Topo dos emails conversacionais: a paisagem Aura numa faixa de 600x150.", row(capa(t), "0", cls="")),
            ("hero", "Hero", "linha", "Topo dos emails com título: paisagem, pílula, título e subtítulo.", row(hero(t), "0", cls="")),
            ("titulo", "Título de seção", "linha", "Sobretítulo e título que abrem um trecho do email.",
             row(meta("Lorem ipsum", t) + heading("Lorem ipsum dolor sit amet, consectetur adipiscing.", t), "56px 40px 0")),
            ("corpo", "Corpo", "linha", "O texto do email. Recebe os blocos em {{blocos}}.", row("{{blocos}}", "40px 40px 0", "px body")),
            ("destaque", "Cartão de destaque", "linha", "Uma ideia em evidência no meio do texto: ícone, sobretítulo, título e texto.", row(feature_card(t), "40px 40px 0")),
            ("faixa", "Faixa de paisagem", "linha", "Respiro visual entre trechos longos.", row(faixa(t, "20px"), "40px 40px 0")),
            ("cta", "Cartão de CTA", "linha", "Fechamento com a ação principal: faixa, título, botão e nota.", row(cta_card(t), "56px 40px 0")),
            ("divisor", "Divisor", "linha", "Separa o conteúdo do rodapé.", row(divider(t), "48px 40px 0")),
            ("rodape", "Rodapé", "linha", "Logo, redes, endereço e descadastro. Obrigatório.", row(footer(t), "28px 40px 0")),
            ("paragrafo", "Parágrafo", "bloco", "Todo o texto corrido. Frases curtas, um parágrafo por ideia.", p(LOREM["medio"])),
            ("botao", "Botão principal", "bloco", "A ação do email, no meio ou no fim do texto.", cta_("Lorem ipsum dolor")),
            ("botao-secundario", "Botão secundário", "bloco", "Uma segunda ação, menos importante que a principal.",
             f'<div style="padding:10px 0 28px;">{button("Lorem ipsum dolor", "{{link_cta}}", "secundario", t)}</div>'),
            ("link", "Link com seta", "bloco", "Ação discreta, quando um botão seria demais.",
             f'<div style="padding:0 0 22px;">{button("Lorem ipsum dolor", "{{link_cta}}", "link", t)}</div>'),
            ("lista", "Lista", "bloco", "Itens curtos e paralelos.", ul(["Lorem ipsum dolor sit amet", "Consectetur adipiscing elit", "Sed do eiusmod tempor"])),
            ("assinatura", "Assinatura", "bloco", "Quem assina o email. O cargo é opcional.", sign("Lorem Ipsum", "Dolor sit amet da Asimov Academy")),
            ("ps", "PS", "bloco", "Pós-escrito no fim do texto.", ps(LOREM["curto"])),
        ]
        variantes.append(Variante(
            id=theme, rotulo=f"Tema {theme}", tema=theme,
            casca=fill(t, "{{linhas}}", "{{assunto}}", "{{preheader}}"),
            componentes=[Componente(s, n, tp, u, h) for s, n, tp, u, h in pecas],
            cores=dict({k: v for k, v in t.items() if isinstance(v, str) and v.startswith("#")}, **BRAND)))
    return Kit(
        slug="aura", quando="Padrão para newsletters, avisos e emails escritos.", nome="Aura", pasta="design-system",
        descricao="O design system de email principal da Asimov, na linguagem do Overview: a paisagem Aura, superfícies com brilho e o teal da marca.",
        fontes=["Inter (Google Fonts), com Helvetica e Arial de reserva"],
        tipografia=[dict(nome=n, tamanho=s, entrelinha=lh, peso=w, tracking=tr, mobile=m, uso=u)
                    for n, (s, lh, w, tr, _, m, u) in TYPE.items()],
        variantes=variantes,
        exemplos=sorted(p.name for p in OUT.glob("*.html") if p.name != "index.html"),
        montagem=[("Conversacional", ["capa", "corpo", "divisor", "rodape"]),
                  ("Com título", ["hero", "titulo", "corpo", "destaque", "corpo", "cta", "divisor", "rodape"])],
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
    """Renderiza o mesmo componente nos dois temas, lado a lado."""
    cells = "".join(
        f'<div class="stage {cls}" style="background:{THEMES[th]["PAGE"]};"><span class="theme-tag {th}">{th}</span>{fn(THEMES[th])}</div>'
        for th in THEMES)
    return f'<div class="pair">{cells}</div>'


def spec_type(t):
    rows = ""
    for name, (size, lh, weight, track, key, mob, use) in TYPE.items():
        sample = "Lorem ipsum dolor sit amet" if size >= 17 else "Lorem ipsum dolor sit amet, consectetur"
        if name == "Meta":
            sample = "LOREM IPSUM"
        rows += (f'<div class="type-row" style="border-color:{t["LINE"]};">'
                 f'<div class="type-meta" style="color:{t["MUTED"]};"><b style="color:{t["TEXT"]};">{name}</b><br>{size}/{lh} &middot; {weight}<br>mobile {mob}</div>'
                 f'<div style="{ts(name, t)}">{sample}</div></div>')
    return rows


def spec_colors(t):
    keys = [("PAGE", "Página"), ("SURFACE", "Superfície"), ("TEXT", "Texto"), ("BODY", "Corpo"),
            ("MUTED", "Apoio"), ("LINE", "Fio"), ("ACCENT_TEXT", "Acento em texto"), ("CTA_LINE", "Borda do CTA")]
    out = '<div class="swatches">'
    for k, label in keys:
        out += (f'<div><div class="chip" style="background:{t[k]}; border-color:{t["LINE_STRONG"]};"></div>'
                f'<div style="color:{t["TEXT"]};">{label}</div><code style="color:{t["MUTED"]};">{t[k]}</code></div>')
    return out + "</div>"


def spec_paragraphs(t):
    def lab(s):
        return meta(s, t, "0 0 10px")
    return (f'<div class="measure">'
            + lab("Curto") + paragraphs([LOREM["curto"]], t) + '<div style="height:32px;"></div>'
            + lab("Médio") + paragraphs([LOREM["medio"]], t) + '<div style="height:32px;"></div>'
            + lab("Longo, seguido de outro parágrafo") + paragraphs([LOREM["longo"], LOREM["medio"]], t)
            + '<div style="height:32px;"></div>'
            + lab("Corpo pequeno, dentro de cartões") + paragraphs([LOREM["medio"]], t, "Corpo pequeno")
            + "</div>")


def spec_buttons(t):
    def item(label, html):
        return f'<div class="btn-item" style="border-color:{t["LINE"]};"><div class="mini" style="color:{t["MUTED"]};">{label}</div>{html}</div>'
    return (item("Primário &middot; um por email", button("Lorem ipsum dolor", "#", "primario", t))
            + item("Secundário &middot; contorno", button("Lorem ipsum", "#", "secundario", t))
            + item("Link &middot; ação de apoio", button("Lorem ipsum dolor sit", "#", "link", t)))


SPEC = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Email · Asimov Design System</title>
  <link rel="stylesheet" href="../../assets/fonts/fonts.css">
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; background: #050505; color: #fff; font-family: %FONT%; -webkit-font-smoothing: antialiased; }
    body::before { content: ""; position: fixed; inset: 0; pointer-events: none;
      background: radial-gradient(ellipse 60% 40% at 50% -5%, rgba(20,184,166,.18), transparent 70%); }
    .wrap { position: relative; max-width: 1240px; margin: 0 auto; padding: 0 24px 120px; }
    .top { display: flex; justify-content: space-between; align-items: center; padding: 28px 0; border-bottom: 1px solid rgba(255,255,255,.08); }
    .top img { height: 20px; }
    .top a { color: #a1a1aa; font-size: 13px; text-decoration: none; }
    .top a:hover { color: #fff; }
    header { text-align: center; padding: 96px 0 40px; }
    header h1 { margin: 22px 0 0; font-weight: 500; font-size: clamp(40px, 6vw, 64px); line-height: 1.02; letter-spacing: -2.4px;
      background: linear-gradient(180deg, #fff 30%, #9ca3af); -webkit-background-clip: text; background-clip: text; color: transparent; }
    header p { max-width: 600px; margin: 20px auto 0; color: #b4b4b4; font-size: 18px; line-height: 29px; }
    header .pill-wrap { display: inline-block; }
    section { margin-top: 112px; }
    .sec-head { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: end; padding-bottom: 28px; margin-bottom: 28px; border-bottom: 1px solid rgba(255,255,255,.08); }
    .sec-head .kicker { color: #2dd4bf; font-size: 12px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; }
    .sec-head h2 { margin: 8px 0 0; font-weight: 500; font-size: 40px; line-height: 44px; letter-spacing: -1.2px; }
    .sec-head p { margin: 0; color: #a1a1aa; font-size: 15px; line-height: 24px; }
    .pair { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .stage { position: relative; min-width: 0; border: 1px solid rgba(255,255,255,.08); border-radius: 20px; padding: 48px 40px 40px; overflow: hidden; }
    .theme-tag { position: absolute; top: 14px; right: 16px; font-size: 10px; font-weight: 600; letter-spacing: 1.6px; text-transform: uppercase; border-radius: 999px; padding: 3px 9px; }
    .theme-tag.escuro { color: #a1a1aa; border: 1px solid #2e2e2e; }
    .theme-tag.claro { color: #52525b; border: 1px solid #d4d4d8; }
    .type-row { display: grid; grid-template-columns: 130px 1fr; gap: 20px; align-items: baseline; padding: 18px 0; border-bottom: 1px solid; }
    .type-row:last-child { border-bottom: 0; }
    .type-meta { font-size: 12px; line-height: 18px; }
    .type-meta b { font-weight: 500; }
    .measure { max-width: 520px; }
    .mini { font-size: 11px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; margin-bottom: 14px; }
    .btn-item { padding: 22px 0; border-bottom: 1px solid; }
    .btn-item:first-child { padding-top: 0; }
    .btn-item:last-child { border-bottom: 0; padding-bottom: 0; }
    .swatches { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px 12px; font-size: 13px; font-weight: 500; }
    .chip { height: 52px; border-radius: 12px; border: 1px solid; margin-bottom: 8px; }
    code { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 11px; }
    .stage.flush { padding: 44px 16px 16px; }
    .acervo { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
    .acervo figure { margin: 0; border: 1px solid rgba(255,255,255,.08); border-radius: 16px; overflow: hidden; background: #0a0a0a; }
    .acervo img { display: block; width: 100%; height: auto; }
    .acervo figcaption { display: flex; justify-content: space-between; gap: 12px; padding: 12px 16px; font-size: 13px; color: #a1a1aa; }
    .acervo figcaption b { color: #fff; font-weight: 500; }
    .acervo .wide { grid-column: span 2; }
    .notes { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 16px; }
    .note { border: 1px solid rgba(255,255,255,.08); border-radius: 20px; padding: 26px; background: linear-gradient(135deg, #0a0a0a, #121214); }
    .note b { display: block; font-weight: 500; font-size: 17px; margin-bottom: 8px; }
    .note p { margin: 0; color: #a1a1aa; font-size: 14px; line-height: 22px; }
    .frames { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .frames figure { margin: 0; }
    .frames figcaption { display: flex; justify-content: space-between; color: #a1a1aa; font-size: 13px; margin-bottom: 12px; }
    .frames a { color: #2dd4bf; text-decoration: none; }
    iframe { display: block; width: 100%; height: 2400px; border: 1px solid rgba(255,255,255,.08); border-radius: 20px; background: #050505; }
    @media (max-width: 900px) {
      .pair, .frames, .notes, .sec-head, .acervo { grid-template-columns: 1fr; }
      .acervo .wide { grid-column: auto; }
      .stage { padding: 44px 20px 28px; }
      .swatches { grid-template-columns: repeat(2, 1fr); }
      .type-row { grid-template-columns: 1fr; gap: 6px; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="top">
      <img src="img/logo-branco.png" alt="Asimov">
      <a href="../../design-system.html">Asimov Design System &rarr;</a>
    </div>

    <header>
      <div class="pill-wrap">%PILL%</div>
      <h1>Email<br>Asimov Academy</h1>
      <p>A linguagem do Overview traduzida para o que os clientes de email aceitam: tabelas, estilos inline, imagens com fallback de cor e Inter com substituto em Helvetica.</p>
    </header>

    <section>
      <div class="sec-head"><div><div class="kicker">Foundations</div><h2>Tipografia</h2></div>
        <p>Uma família só, como no site. Inter 500 com tracking negativo nos títulos, 400 no texto. Valores em px. No Gmail e no Outlook, cai para Helvetica ou Arial.</p></div>
      %TYPE%
    </section>

    <section>
      <div class="sec-head"><div><div class="kicker">Foundations</div><h2>Cores</h2></div>
        <p>Teal Asimov em dois papéis: #14b8a6 no botão, nos dois temas, e uma variação legível para texto em cada fundo.</p></div>
      %COLORS%
    </section>

    <section>
      <div class="sec-head"><div><div class="kicker">Foundations</div><h2>Parágrafos</h2></div>
        <p>Coluna de 520px, cerca de 65 caracteres por linha. Corpo 17/29 e 22px entre parágrafos. No mobile, 16/27.</p></div>
      %PARAGRAPHS%
    </section>

    <section>
      <div class="sec-head"><div><div class="kicker">Components</div><h2>Aura</h2></div>
        <p>A paisagem da Aura como imagem de fundo, com o céu estendido para cima para receber o texto. Noite no tema escuro, dia no claro. No Outlook, entra por VML.</p></div>
      %HERO%
    </section>

    <section>
      <div class="sec-head"><div><div class="kicker">Foundations</div><h2>Acervo Aura</h2></div>
        <p>As variações da paisagem, já em 1200px de largura (2x para retina). As de 3:1 viram faixa; as de 21:9 e 16:9 são a base do topo. As claras são para o tema claro.</p></div>
      %ACERVO%
    </section>

    <section>
      <div class="sec-head"><div><div class="kicker">Components</div><h2>Botões</h2></div>
        <p>Pílula com degradê teal e brilho, como no Pricing. Onde o degradê não carrega, fica teal sólido. No Outlook, VML. A seta é PNG, porque email não aceita SVG.</p></div>
      %BUTTONS%
    </section>

    <section>
      <div class="sec-head"><div><div class="kicker">Components</div><h2>Superfícies</h2></div>
        <p>O cartão de formação, com brilho no canto e ícone em caixa, destaca um ponto do texto. A superfície do Pricing, com borda teal e uma faixa da paisagem no topo, guarda o CTA.</p></div>
      %SURFACES%
      <div style="height:16px;"></div>
      %CTA%
    </section>

    <section>
      <div class="sec-head"><div><div class="kicker">Components</div><h2>Fechamento</h2></div>
        <p>Assinatura em duas linhas, nome e função. O fio teal em degradê separa o rodapé, que fica em cinza fio.</p></div>
      %CLOSING%
      <div class="notes">
        <div class="note"><b>Um botão por email</b><p>Ações secundárias viram link de texto com a seta teal.</p></div>
        <div class="note"><b>Texto sempre real</b><p>Nada escrito dentro de imagem. Se a imagem não carregar, a cor de fundo garante a leitura.</p></div>
        <div class="note"><b>600px de largura</b><p>Margem interna de 40px, 24px no mobile. Imagens em 2x para telas retina.</p></div>
      </div>
    </section>

    <section>
      <div class="sec-head"><div><div class="kicker">Aplicação</div><h2>Emails conversacionais</h2></div>
        <p>Copies reais, sem título, como a maior parte dos emails da Asimov: capa estreita, a conversa, o botão no meio do texto e a assinatura.</p></div>
      %CONVERSAS%
      <div class="frames" style="margin-top:16px;">
        <figure><figcaption>EM-001 · escuro <a href="em-001-escuro.html" target="_blank">Abrir sozinho &rarr;</a></figcaption><iframe src="em-001-escuro.html" title="EM-001, escuro"></iframe></figure>
        <figure><figcaption>EM-005 · claro <a href="em-005-claro.html" target="_blank">Abrir sozinho &rarr;</a></figcaption><iframe src="em-005-claro.html" title="EM-005, claro"></iframe></figure>
      </div>
    </section>

    <section>
      <div class="sec-head"><div><div class="kicker">Aplicação</div><h2>Email escrito com CTA</h2></div>
        <p>Os componentes acima montados em um email só, gerado no mesmo script, nos dois temas.</p></div>
      <div class="frames">
        <figure><figcaption>Escuro <a href="email-escuro.html" target="_blank">Abrir sozinho &rarr;</a></figcaption><iframe src="email-escuro.html" title="Email, tema escuro"></iframe></figure>
        <figure><figcaption>Claro <a href="email-claro.html" target="_blank">Abrir sozinho &rarr;</a></figcaption><iframe src="email-claro.html" title="Email, tema claro"></iframe></figure>
      </div>
    </section>
  </div>
  <script>
    /* A prévia tem a altura do email: mede no load, de novo quando as fontes chegam e sempre que o
       email muda de tamanho. Sem isso, sobram alguns pixels e aparece uma barra de rolagem. */
    document.querySelectorAll("iframe").forEach(f => f.addEventListener("load", () => {
      const medir = () => { try {
        f.style.height = "0px";  /* zera antes de medir: scrollHeight nunca é menor que a altura atual */
        f.style.height = f.contentDocument.documentElement.scrollHeight + (f.offsetHeight - f.clientHeight) + "px";  /* + a borda */
      } catch (_) {} };
      medir();
      try { f.contentDocument.fonts.ready.then(medir); new ResizeObserver(medir).observe(f.contentDocument.body); } catch (_) {}
    }));
  </script>
</body>
</html>
"""


ACERVO = [
    ("escuro-21x9", "Noite · 21:9", "base do topo escuro"),
    ("claro-21x9", "Dia · 21:9", "base do topo claro"),
    ("escuro-16x9", "Noite com planetas · 16:9", "topo alternativo"),
    ("claro-16x9", "Dia · 16:9", "topo alternativo"),
    ("escuro-3x1-a", "Noite · 3:1", "faixa"),
    ("claro-3x1-a", "Dia · 3:1", "faixa"),
    ("escuro-3x1-b", "Noite profunda · 3:1", "faixa do CTA escuro"),
    ("claro-3x1-b", "Névoa · 3:1", "faixa do CTA claro"),
    ("escuro-3x1-c", "Via Láctea · 3:1", "faixa"),
    ("escuro-3x1-d", "Lilás · 3:1", "faixa"),
]


def acervo():
    return '<div class="acervo">' + "".join(
        f'<figure><img loading="lazy" src="img/acervo/{f}.jpg" alt=""><figcaption><span><b>{name}</b> &middot; {use}</span>'
        f'<code>acervo/{f}.jpg</code></figcaption></figure>' for f, name, use in ACERVO) + "</div>"


def specimen():
    parts = {
        "FONT": FONT,
        "PILL": pill(THEMES["escuro"], "Design system de email", "V1.0"),
        "TYPE": both(spec_type),
        "COLORS": both(spec_colors),
        "PARAGRAPHS": both(spec_paragraphs),
        "HERO": both(hero, "flush"),
        "ACERVO": acervo(),
        "CONVERSAS": spec_conversas(),
        "BUTTONS": both(spec_buttons),
        "SURFACES": both(feature_card),
        "CTA": both(lambda t: cta_card(t, "#")),
        "CLOSING": both(lambda t: signature(t) + '<div style="height:32px;"></div>' + divider(t)
                        + '<div style="height:28px;"></div>' + footer(t)),
    }
    return re.sub(r"%([A-Z_]+)%", lambda m: parts.get(m.group(1), m.group(0)), SPEC)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for theme in THEMES:
        (OUT / f"email-{theme}.html").write_text(email(theme))
        print(f"email-{theme}.html")
    for copy in COPIES:
        for theme in THEMES:
            (OUT / f'{copy["id"]}-{theme}.html').write_text(conversa(theme, copy))
            print(f'{copy["id"]}-{theme}.html')
    (OUT / "index.html").write_text(specimen())
    print("index.html")


if __name__ == "__main__":
    main()
