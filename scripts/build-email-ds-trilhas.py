#!/usr/bin/env python3
"""Design system de email "Trilhas": um halo de luz na cor de cada formação.

Mesma família do design system de email principal (Inter 500, fundo #050505,
superfícies discretas), com a cor como protagonista:
  - cada email assume a paleta da formação ou trilha (as mesmas do assets/themes.js)
  - o topo é um halo, o eclipse do arco da paisagem, com o título dentro do anel
  - o espectro (dark, accent, light, glow) vira assinatura: faixa, pontos, citação
  - o CTA fica dentro de um halo menor, como a pupila do anel

Saída em emails/design-system-trilhas/:

    index.html                      página do design system, com seletor de cor
    email-<trilha>-<tema>.html      aplicação, 5 cores x 2 temas
    img/                            halos gerados por cor e tema

    python3 scripts/build-email-ds-trilhas.py
"""
import re
from pathlib import Path

from email_copies import COPIES, initials, render_blocks

OUT = Path(__file__).resolve().parent.parent / "emails" / "design-system-trilhas"

FONT = "Inter, 'Helvetica Neue', Helvetica, Arial, sans-serif"

# Paletas copiadas de assets/themes.js (dark, accent, light, glow).
ACCENTS = {
    "teal": ("Teal Asimov", "Asimov Academy", ("#0d9488", "#14b8a6", "#2dd4bf", "#5eead4")),
    "engenheiro-ia": ("Engenheiro de IA", "Formação", ("#0891b2", "#06b6d4", "#22d3ee", "#67e8f9")),
    "analista-dados": ("Analista de Dados", "Formação", ("#ea580c", "#f97316", "#fb923c", "#fdba74")),
    "ai-designer": ("AI Designer", "Formação", ("#1d4ed8", "#2563eb", "#60a5fa", "#93c5fd")),
    "n8n": ("Automações n8n", "Trilha", ("#e11d48", "#f43f5e", "#fb7185", "#fda4af")),
}

BASE = {
    "escuro": {
        "SCHEME": "dark", "PAGE": "#050505", "TEXT": "#ffffff", "BODY": "#b4b4b4", "MUTED": "#737373",
        "LINE": "#1c1c1c", "SURFACE": "#0b0b0c", "LOGO": "img/logo-branco.png",
    },
    "claro": {
        "SCHEME": "light", "PAGE": "#fafafa", "TEXT": "#09090b", "BODY": "#52525b", "MUTED": "#8a8a93",
        "LINE": "#e4e4e7", "SURFACE": "#ffffff", "LOGO": "img/logo-preto.png",
    },
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


# ------------------------------------------------------------------ cor

def _rgb(h):
    return [int(h[i:i + 2], 16) for i in (1, 3, 5)]


def _lum(h):
    def ch(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(c) for c in _rgb(h))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a, b):
    la, lb = sorted((_lum(a), _lum(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def darken(h, amount):
    return "#" + "".join(f"{round(c * (1 - amount)):02x}" for c in _rgb(h))


def theme(slug, mode):
    """Junta a base do tema com a paleta da trilha e escolhe as cores de texto legíveis."""
    name, kind, (dark, acc, light, glow) = ACCENTS[slug]
    t = dict(BASE[mode])
    on_accent = "#ffffff" if contrast("#ffffff", acc) > contrast("#09090b", acc) else "#09090b"
    t.update(
        SLUG=slug, NAME=name, KIND=kind,
        DARK=dark, ACCENT=acc, LIGHT=light, GLOW=glow,
        # texto em acento: claro no escuro; no claro, o dark escurecido até passar de 4.5:1
        ACCENT_TEXT=light if mode == "escuro" else next(
            darken(dark, a / 100) for a in range(0, 60, 2) if contrast(darken(dark, a / 100), "#fafafa") >= 4.5),
        ON_ACCENT=on_accent,
        ARROW="img/seta-branca.png" if on_accent == "#ffffff" else "img/seta-escura.png",
        HERO=f"img/halo-hero-{slug}-{mode}.jpg",
        CTA_IMG=f"img/halo-cta-{slug}-{mode}.jpg",
        RGB=",".join(str(c) for c in _rgb(acc)),
    )
    return t


TYPE = {
    "Título no halo": (44, 46, 500, -1.8, "TEXT", "34/37", "Centralizado, dentro do anel. Duas linhas curtas."),
    "Título de seção": (30, 36, 500, -0.9, "TEXT", "26/32", "Abre o corpo, alinhado à esquerda."),
    "Número": (40, 40, 500, -1.6, "ACCENT_TEXT", "36/36", "Os marcos. Sempre na cor da trilha."),
    "Citação": (22, 32, 500, -0.4, "TEXT", "20/30", "Uma por email, ao lado da barra de espectro."),
    "Corpo": (17, 29, 400, 0, "BODY", "16/27", "Todo o texto corrido."),
    "Corpo pequeno": (14, 22, 400, 0, "BODY", "14/22", "Dentro dos marcos."),
    "Meta": (12, 16, 600, 1.4, "ACCENT_TEXT", "12/16", "Caixa alta, na cor da trilha."),
}


def ts(name, t, color=None):
    size, lh, weight, track, key, _, _ = TYPE[name]
    return (f"font-family:{FONT}; font-size:{size}px; line-height:{lh}px; font-weight:{weight}; "
            f"letter-spacing:{track}px; color:{color or t[key]};")


# ------------------------------------------------------------------ componentes

def meta(text, t, margin="0", align="left"):
    return f'<div style="margin:{margin}; text-align:{align}; {ts("Meta", t)}">{text.upper()}</div>'


def paragraphs(items, t, kind="Corpo", first="0"):
    return "".join(f'<p style="margin:{first if i == 0 else "20px"} 0 0; {ts(kind, t)}">{p}</p>' for i, p in enumerate(items))


def trail_pill(t):
    """Pílula com a cor da trilha: ponto acento + tipo + nome."""
    bg = "rgba(255,255,255,.04)" if t["SCHEME"] == "dark" else "rgba(255,255,255,.7)"
    solid = "#0d0d0e" if t["SCHEME"] == "dark" else "#ffffff"
    return (f'<table role="presentation" align="center" style="border-collapse:separate; margin:0 auto;"><tr>'
            f'<td bgcolor="{solid}" style="background:{solid}; background:{bg}; border:1px solid rgba({t["RGB"]},.45); border-radius:999px; padding:6px 14px; '
            f'font-family:{FONT}; font-size:11px; line-height:16px; font-weight:600; letter-spacing:1.4px; color:{t["ACCENT_TEXT"]}; white-space:nowrap;">'
            f'<span style="color:{t["ACCENT"]};">&#9679;</span>&nbsp;&nbsp;{t["KIND"].upper()} &middot; {t["NAME"].upper()}</td>'
            f'</tr></table>')


def hero(t):
    return f'''<table role="presentation" width="100%">
  <tr>
    <td align="center" style="padding:32px 40px 4px;">
      <img src="{t["LOGO"]}" width="66" height="20" alt="Asimov Academy" style="width:66px; height:20px; margin:0 auto;">
    </td>
  </tr>
  <tr>
    <td class="hero" height="500" valign="top" align="center" background="{t["HERO"]}" bgcolor="{t["PAGE"]}"
        style="height:500px; background:{t["PAGE"]} url('{t["HERO"]}') center top / cover no-repeat;">
      <!--[if gte mso 9]>
      <v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false" style="width:600px;height:500px;">
        <v:fill type="frame" src="{t["HERO"]}" color="{t["PAGE"]}" />
        <v:textbox inset="0,0,0,0">
      <![endif]-->
      <table role="presentation" width="100%">
        <tr>
          <td class="hero-in" align="center" style="padding:146px 40px 0;">
            {trail_pill(t)}
            <div class="h1" style="margin:20px auto 0; max-width:340px; text-align:center; {ts("Título no halo", t)}">Lorem ipsum dolor sit amet.</div>
            <p style="margin:14px auto 0; max-width:280px; text-align:center; font-family:{FONT}; font-size:15px; line-height:23px; color:{t["BODY"]};">Lorem ipsum dolor sit amet, consectetur adipiscing.</p>
          </td>
        </tr>
      </table>
      <!--[if gte mso 9]></v:textbox></v:rect><![endif]-->
    </td>
  </tr>
</table>'''


def spectrum(t, height=4):
    """A paleta da trilha como faixa: dark, accent, light, glow."""
    cells = "".join(f'<td height="{height}" bgcolor="{c}" style="height:{height}px; background:{c}; font-size:0; line-height:0;">&nbsp;</td>'
                    for c in (t["DARK"], t["ACCENT"], t["LIGHT"], t["GLOW"]))
    return f'<table role="presentation" width="100%" style="border-collapse:separate;"><tr>{cells}</tr></table>'


def dots(t, size=8):
    cells = "".join(f'<td width="{size}" height="{size}" bgcolor="{c}" style="width:{size}px; height:{size}px; background:{c}; border-radius:999px; font-size:0; line-height:0;">&nbsp;</td>'
                    f'<td width="5" style="font-size:0;">&nbsp;</td>' for c in (t["DARK"], t["ACCENT"], t["LIGHT"], t["GLOW"]))
    return f'<table role="presentation" style="border-collapse:separate;"><tr>{cells}</tr></table>'


def trail_card(t):
    """Ficha da trilha: nome à esquerda, pontos do espectro à direita, faixa embaixo."""
    return (f'<table role="presentation" width="100%"><tr>'
            f'<td valign="bottom" style="padding-bottom:14px;">{meta(t["KIND"], t)}'
            f'<div style="margin-top:4px; font-family:{FONT}; font-size:16px; line-height:22px; font-weight:500; color:{t["TEXT"]};">{t["NAME"]}</div></td>'
            f'<td align="right" valign="bottom" style="padding-bottom:18px;">{dots(t)}</td>'
            f'</tr></table>{spectrum(t)}')


def milestones(t):
    """Três marcos em colunas: número grande na cor da trilha, traço, título e texto."""
    cols = []
    for i, n in enumerate(("01", "02", "03")):
        pad = "0 14px 0 0" if i == 0 else ("0 0 0 14px" if i == 2 else "0 7px")
        cols.append(
            f'<td class="stack mile" width="33%" valign="top" style="padding:{pad};">'
            f'<div style="{ts("Número", t)}">{n}</div>'
            f'<div style="width:24px; height:2px; margin:14px 0 14px; background:{t["ACCENT"]}; font-size:0; line-height:0;">&nbsp;</div>'
            f'<div style="font-family:{FONT}; font-size:15px; line-height:22px; font-weight:500; color:{t["TEXT"]};">Lorem ipsum</div>'
            f'<div style="margin-top:4px; {ts("Corpo pequeno", t)}">Dolor sit amet, consectetur adipiscing elit.</div></td>')
    return f'<table role="presentation" width="100%"><tr>{"".join(cols)}</tr></table>'


def quote(t, text="Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt."):
    bar = (f'<td width="3" bgcolor="{t["ACCENT"]}" style="width:3px; background:{t["ACCENT"]}; '
           f'background-image:linear-gradient(180deg, {t["GLOW"]}, {t["ACCENT"]} 50%, {t["DARK"]}); font-size:0;">&nbsp;</td>')
    return (f'<table role="presentation" width="100%"><tr>{bar}'
            f'<td style="padding:2px 0 2px 24px;"><div class="quote" style="{ts("Citação", t)}">{text}</div>'
            f'<div style="margin-top:12px; font-family:{FONT}; font-size:13px; line-height:20px; color:{t["MUTED"]};">Lorem Ipsum, dolor sit amet</div></td>'
            f'</tr></table>')


def signature(t):
    return (f'<table role="presentation" style="border-collapse:separate;"><tr>'
            f'<td width="40" height="40" align="center" valign="middle" style="width:40px; height:40px; border:1px solid {t["ACCENT"]}; border-radius:999px; '
            f'font-family:{FONT}; font-size:13px; font-weight:600; letter-spacing:0.5px; color:{t["ACCENT_TEXT"]};">LI</td>'
            f'<td style="padding-left:14px;"><div style="font-family:{FONT}; font-size:15px; line-height:22px; font-weight:500; color:{t["TEXT"]};">Lorem Ipsum</div>'
            f'<div style="font-family:{FONT}; font-size:13px; line-height:20px; color:{t["MUTED"]};">Dolor sit amet &middot; {t["NAME"]}</div></td>'
            f'</tr></table>')


def button(t, label="Lorem ipsum dolor", href="{{link_cta}}"):
    return (f'<table role="presentation" align="center" style="border-collapse:separate; margin:0 auto;"><tr>'
            f'<td align="center" bgcolor="{t["ACCENT"]}" style="background:{t["ACCENT"]}; border-radius:999px; '
            f'box-shadow:0 0 0 6px rgba({t["RGB"]},.14), 0 12px 40px rgba({t["RGB"]},.45);">'
            f'<!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" href="{href}" style="height:54px;v-text-anchor:middle;width:240px;" '
            f'arcsize="50%" stroke="f" fillcolor="{t["ACCENT"]}"><w:anchorlock/><center style="color:{t["ON_ACCENT"]};font-family:Arial,sans-serif;font-size:16px;font-weight:bold;">{label}</center></v:roundrect><![endif]-->'
            f'<!--[if !mso]><!--><a href="{href}" style="display:inline-block; padding:16px 22px 16px 30px; text-decoration:none; border-radius:999px;">'
            f'<table role="presentation" style="border-collapse:separate;"><tr>'
            f'<td style="font-family:{FONT}; font-size:16px; line-height:22px; font-weight:600; color:{t["ON_ACCENT"]}; white-space:nowrap;">{label}</td>'
            f'<td width="12" style="font-size:0;">&nbsp;</td>'
            f'<td><img src="{t["ARROW"]}" width="20" height="20" alt="" style="width:20px; height:20px;"></td>'
            f'</tr></table></a><!--<![endif]--></td></tr></table>')


def cta(t, href="{{link_cta}}"):
    """Título acima, o botão dentro de um halo menor, legenda abaixo."""
    return (f'{meta("Lorem ipsum", t, align="center")}'
            f'<div class="h2" style="margin:10px 0 0; text-align:center; {ts("Título de seção", t)}">Lorem ipsum dolor sit.</div>'
            f'<table role="presentation" width="100%" style="margin-top:4px;"><tr>'
            f'<td class="cta-halo" height="320" align="center" valign="middle" background="{t["CTA_IMG"]}" bgcolor="{t["PAGE"]}" '
            f'style="height:320px; background:{t["PAGE"]} url(\'{t["CTA_IMG"]}\') center center / cover no-repeat;">'
            f'<!--[if gte mso 9]><v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false" style="width:520px;height:320px;">'
            f'<v:fill type="frame" src="{t["CTA_IMG"]}" color="{t["PAGE"]}" /><v:textbox inset="0,130px,0,0"><![endif]-->'
            f'{button(t, href=href)}'
            f'<!--[if gte mso 9]></v:textbox></v:rect><![endif]--></td></tr></table>'
            f'<div style="text-align:center; font-family:{FONT}; font-size:13px; line-height:20px; color:{t["MUTED"]};">Lorem ipsum dolor sit amet, consectetur.</div>')


def footer(t):
    links = "&nbsp;&nbsp;&middot;&nbsp;&nbsp;".join(
        f'<a href="{{{{link_{k.lower()}}}}}" style="color:{t["MUTED"]}; text-decoration:none;">{k}</a>'
        for k in ("YouTube", "Instagram", "LinkedIn"))
    return (f'<table role="presentation" align="center" style="margin:0 auto;"><tr><td>{dots(t, 6)}</td></tr></table>'
            f'<div style="margin-top:18px; text-align:center; font-family:{FONT}; font-size:12px; line-height:19px; color:{t["MUTED"]};">'
            f'{links}<br><br>Asimov Academy &middot; {{{{endereco}}}}<br>'
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
    Gerado por scripts/build-email-ds-trilhas.py. Edite o script, não este arquivo.
    Trilha: %NAME%. Antes do disparo, troque img/... por URLs absolutas hospedadas.
  -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&amp;display=swap" rel="stylesheet">
  <style>
    body { margin: 0; padding: 0; width: 100% !important; background: %PAGE%; -webkit-text-size-adjust: 100%; }
    table { border-collapse: collapse; mso-table-lspace: 0; mso-table-rspace: 0; }
    img { border: 0; display: block; outline: none; text-decoration: none; -ms-interpolation-mode: bicubic; }
    a { color: %ACCENT_TEXT%; }
    p { margin: 0; }
    @media (max-width: 620px) {
      .container { width: 100% !important; }
      .px { padding-left: 24px !important; padding-right: 24px !important; }
      .hero { height: 440px !important; background-size: auto 440px !important; }
      .hero-in { padding-top: 120px !important; }
      .h1 { font-size: 34px !important; line-height: 37px !important; letter-spacing: -1.2px !important; }
      .h2 { font-size: 26px !important; line-height: 32px !important; }
      .quote { font-size: 20px !important; line-height: 30px !important; }
      .body td { white-space: normal !important; }
      .body p { font-size: 16px !important; line-height: 27px !important; }
      .stack { display: block !important; width: 100% !important; box-sizing: border-box; }
      .mile { padding: 0 0 28px !important; }
      .cta-halo { background-size: auto 320px !important; }
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


def email(slug, mode):
    t = theme(slug, mode)
    rows = [
        row(hero(t), "0", cls=""),
        row(trail_card(t), "8px 40px 0"),
        row(meta("Lorem ipsum", t) + f'<div class="h2" style="margin:10px 0 0; {ts("Título de seção", t)}">Lorem ipsum dolor sit amet, consectetur adipiscing.</div>', "52px 40px 0"),
        row(paragraphs([LOREM["longo"], LOREM["curto"]], t), "22px 40px 0", "px body"),
        row(milestones(t), "44px 40px 0"),
        row(paragraphs([LOREM["medio"], LOREM["longo"]], t), "44px 40px 0", "px body"),
        row(quote(t), "40px 40px 0"),
        row(paragraphs([LOREM["medio"]], t), "40px 40px 0", "px body"),
        row(signature(t), "28px 40px 0"),
        row(cta(t), "64px 40px 0"),
        row(footer(t), "56px 40px 0"),
    ]
    tokens = dict(t, ROWS="\n\n".join(rows), TITLE="Lorem ipsum", PREHEADER="Lorem ipsum dolor sit amet, consectetur adipiscing elit.")
    html = re.sub(r"%([A-Z_]+)%", lambda m: tokens.get(m.group(1), m.group(0)), SHELL)
    leftover = set(re.findall(r"%[A-Z_]+%", html))
    if leftover:
        raise SystemExit(f"email-{slug}-{mode}: tokens sem valor {leftover}")
    return html


def conversa(slug, mode, copy):
    """Email conversacional (sem título e sem halo): logo, faixa de espectro, a conversa e a assinatura em anel."""
    t = theme(slug, mode)
    p = lambda text: f'<p style="margin:0 0 18px; {ts("Corpo", t)}">{text}</p>'
    cta_ = lambda label: f'<div style="padding:12px 0 30px;">{button(t, label)}</div>'
    ul = lambda items: ('<table role="presentation" style="margin:0 0 22px;">' + "".join(
        f'<tr><td width="22" valign="top" style="padding:11px 0 0;"><div style="width:8px; height:8px; border-radius:999px; background:{t["ACCENT"]}; font-size:0; line-height:0;">&nbsp;</div></td>'
        f'<td style="padding:0 0 6px; {ts("Corpo", t)}">{i}</td></tr>' for i in items) + "</table>")
    sign = lambda name, role: (
        f'<table role="presentation" style="border-collapse:separate; margin-top:4px;"><tr>'
        f'<td width="44" height="44" align="center" valign="middle" style="width:44px; height:44px; border:1.5px solid {t["ACCENT"]}; border-radius:999px; '
        f'font-family:{FONT}; font-size:14px; font-weight:600; color:{t["ACCENT_TEXT"]};">{initials(name)}</td>'
        f'<td style="padding-left:14px;"><div style="font-family:{FONT}; font-size:16px; line-height:22px; font-weight:500; color:{t["TEXT"]};">{name}</div>'
        + (f'<div style="font-family:{FONT}; font-size:13px; line-height:20px; color:{t["MUTED"]};">{role}</div>' if role else "")
        + '</td></tr></table>')
    ps = lambda text: (f'<p style="margin:28px 0 0; padding-top:20px; border-top:1px solid {t["LINE"]}; {ts("Corpo", t)}">'
                       f'<strong style="font-weight:600; color:{t["ACCENT_TEXT"]};">PS:</strong> {text}</p>')
    rows = [
        row(f'<img src="{t["LOGO"]}" width="66" height="20" alt="Asimov Academy" style="width:66px; height:20px; margin:0 auto;">', "36px 40px 22px"),
        row(spectrum(t, 3), "0 40px"),
        row(render_blocks(copy["blocks"], p, cta_, ul, sign, ps), "44px 40px 0", "px body"),
        row(footer(t), "48px 40px 0"),
    ]
    tokens = dict(t, ROWS="\n\n".join(rows), TITLE=copy["assunto"], PREHEADER=copy["preheader"])
    return re.sub(r"%([A-Z_]+)%", lambda m: tokens.get(m.group(1), m.group(0)), SHELL)


# ------------------------------------------------------------------ página do design system

def both(slug, fn):
    cells = ""
    for mode in BASE:
        t = theme(slug, mode)
        cells += f'<div class="stage" style="background:{t["PAGE"]};"><span class="tag {mode}">{mode}</span>{fn(t)}</div>'
    return f'<div class="pair">{cells}</div>'


def spec_type(t):
    out = ""
    for name, (size, lh, weight, track, key, mob, use) in TYPE.items():
        sample = {"Número": "01 02 03", "Meta": "LOREM IPSUM"}.get(name, "Lorem ipsum dolor sit amet")
        out += (f'<div class="type-row" style="border-color:{t["LINE"]};">'
                f'<div class="type-meta" style="color:{t["MUTED"]};"><b style="color:{t["TEXT"]};">{name}</b><br>{size}/{lh} &middot; {weight}<br>mobile {mob}</div>'
                f'<div style="{ts(name, t)}">{sample}</div></div>')
    return out


def spec_palette(t):
    roles = [("DARK", "Dark", "Base da faixa"), ("ACCENT", "Accent", "Botão, pontos, traços"),
             ("LIGHT", "Light", "Texto no escuro"), ("GLOW", "Glow", "Brilho, topo da barra")]
    out = '<div class="swatches">'
    for k, label, use in roles:
        out += (f'<div><div class="chip" style="background:{t[k]};"></div>'
                f'<div style="color:{t["TEXT"]}; font-weight:500;">{label}</div><code style="color:{t["MUTED"]};">{t[k]}</code>'
                f'<div style="color:{t["MUTED"]}; font-size:12px;">{use}</div></div>')
    out += "</div>"
    ratio = contrast(t["ON_ACCENT"], t["ACCENT"])
    out += (f'<div style="margin-top:24px; padding-top:18px; border-top:1px solid {t["LINE"]}; color:{t["MUTED"]}; font-size:13px; line-height:21px;">'
            f'Texto em acento neste tema: <b style="color:{t["ACCENT_TEXT"]};">{t["ACCENT_TEXT"]}</b>. '
            f'Texto no botão: <b style="color:{t["TEXT"]};">{"branco" if t["ON_ACCENT"] == "#ffffff" else "preto"}</b> ({ratio:.1f}:1), escolhido pelo script.</div>')
    return out


SPEC = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Email Trilhas · Asimov Design System</title>
  <link rel="stylesheet" href="../../assets/fonts/fonts.css">
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; background: #050505; color: #fff; font-family: %FONT%; -webkit-font-smoothing: antialiased; }
    .top { max-width: 1240px; margin: 0 auto; padding: 28px 24px; display: flex; justify-content: space-between; align-items: center; }
    .top img { height: 20px; }
    .top a { color: #a1a1aa; font-size: 13px; text-decoration: none; }
    .stagehead { position: relative; text-align: center; padding: 40px 24px 0; min-height: 620px;
      background: #050505 var(--halo) center top / 980px auto no-repeat; transition: background-image .4s; }
    .stagehead .kicker { display: inline-block; margin-top: 210px; padding: 6px 14px; border-radius: 999px; border: 1px solid color-mix(in srgb, var(--acc) 45%, transparent);
      color: var(--light); font-size: 11px; font-weight: 600; letter-spacing: 1.4px; }
    .stagehead h1 { margin: 20px auto 0; max-width: 520px; font-weight: 500; font-size: clamp(40px, 6vw, 64px); line-height: 1.02; letter-spacing: -2.4px; }
    .stagehead p { max-width: 460px; margin: 18px auto 0; color: #b4b4b4; font-size: 17px; line-height: 27px; }
    .picker { position: sticky; top: 0; z-index: 5; background: rgba(5,5,5,.86); backdrop-filter: blur(12px); border-top: 1px solid #1c1c1c; border-bottom: 1px solid #1c1c1c; }
    .picker .in { max-width: 1240px; margin: 0 auto; padding: 12px 24px; display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; }
    .picker button { display: flex; align-items: center; gap: 8px; font: 500 13px %FONT%; color: #a1a1aa; background: transparent; border: 1px solid #262626; border-radius: 999px; padding: 8px 14px 8px 10px; cursor: pointer; }
    .picker button i { width: 12px; height: 12px; border-radius: 999px; background: var(--c); box-shadow: 0 0 12px var(--c); }
    .picker button[aria-pressed="true"] { color: #fff; border-color: var(--c); }
    .wrap { max-width: 1240px; margin: 0 auto; padding: 0 24px 120px; }
    section { margin-top: 104px; }
    .sec-head { text-align: center; max-width: 640px; margin: 0 auto 32px; }
    .sec-head .k { color: var(--light); font-size: 12px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; }
    .sec-head h2 { margin: 10px 0 0; font-weight: 500; font-size: 40px; line-height: 44px; letter-spacing: -1.4px; }
    .sec-head p { margin: 12px 0 0; color: #a1a1aa; font-size: 15px; line-height: 24px; }
    .pair { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .stage { position: relative; min-width: 0; border: 1px solid #1c1c1c; border-radius: 24px; padding: 52px 36px 36px; overflow: hidden; }
    .tag { position: absolute; top: 16px; left: 50%; transform: translateX(-50%); font-size: 10px; font-weight: 600; letter-spacing: 1.6px; text-transform: uppercase; }
    .tag.escuro { color: #737373; } .tag.claro { color: #8a8a93; }
    .type-row { display: grid; grid-template-columns: 130px 1fr; gap: 20px; align-items: baseline; padding: 16px 0; border-bottom: 1px solid; }
    .type-row:last-child { border-bottom: 0; }
    .type-meta { font-size: 12px; line-height: 18px; } .type-meta b { font-weight: 500; }
    .swatches { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; font-size: 13px; }
    .chip { height: 72px; border-radius: 16px; margin-bottom: 10px; }
    code { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 11px; display: block; margin: 2px 0 4px; }
    .solo { max-width: 640px; margin: 0 auto; }
    .frames { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .frames figure { margin: 0; }
    .frames figcaption { display: flex; justify-content: space-between; color: #a1a1aa; font-size: 13px; margin-bottom: 12px; }
    .frames a { color: var(--light); text-decoration: none; }
    iframe { display: block; width: 100%; height: 2600px; border: 1px solid #1c1c1c; border-radius: 24px; background: #050505; }
    [data-accent][hidden] { display: none; }
    @media (max-width: 900px) {
      .pair, .frames { grid-template-columns: 1fr; }
      .stage { padding: 48px 18px 24px; }
      .swatches { grid-template-columns: repeat(2, 1fr); }
      .type-row { grid-template-columns: 1fr; gap: 6px; }
      .stagehead { background-size: 640px auto; min-height: 480px; } .stagehead .kicker { margin-top: 150px; }
    }
  </style>
</head>
<body>
  <div class="top"><img src="img/logo-branco.png" alt="Asimov"><a href="../../design-system.html">Asimov Design System &rarr;</a></div>
  <div class="stagehead">
    <span class="kicker">EMAIL &middot; TRILHAS</span>
    <h1>Uma cor para cada trilha.</h1>
    <p>Mesma estrutura e mesmos componentes. A paleta da formação muda o halo, os números, a faixa de espectro e o botão.</p>
  </div>
  <div class="picker"><div class="in">%PICKER%</div></div>
  <div class="wrap">
%SECTIONS%
  </div>
  <script>
    const accents = %ACCENT_JSON%;
    const root = document.documentElement, head = document.querySelector(".stagehead");
    function pick(slug) {
      if (!accents[slug]) slug = "teal";
      const a = accents[slug];
      root.style.setProperty("--acc", a.accent); root.style.setProperty("--light", a.light);
      head.style.setProperty("--halo", `url('img/halo-hero-${slug}-escuro.jpg')`);
      document.querySelectorAll("[data-accent]").forEach(s => s.hidden = s.dataset.accent !== slug);
      document.querySelectorAll(".picker button").forEach(b => b.setAttribute("aria-pressed", b.dataset.slug === slug));
      try { history.replaceState(null, "", "#" + slug); } catch (_) {}
      fit();
    }
    function fit() {
      document.querySelectorAll("[data-accent]:not([hidden]) iframe").forEach(f => {
        try { f.style.height = f.contentDocument.documentElement.scrollHeight + "px"; } catch (_) {}
      });
    }
    document.querySelectorAll(".picker button").forEach(b => b.onclick = () => pick(b.dataset.slug));
    document.querySelectorAll("iframe").forEach(f => f.addEventListener("load", fit));
    pick(location.hash.slice(1));
  </script>
</body>
</html>
"""


def sections(slug):
    name = ACCENTS[slug][0]
    head = lambda k, h, p: f'<div class="sec-head"><div class="k">{k}</div><h2>{h}</h2><p>{p}</p></div>'
    return f'''
    <div data-accent="{slug}" hidden>
      <section>{head("Foundations", "Espectro", f"A paleta de {name}, a mesma do themes.js. O script escolhe sozinho a cor do texto no botão e escurece o acento no tema claro até passar de 4.5:1.")}
        {both(slug, spec_palette)}</section>
      <section>{head("Foundations", "Tipografia", "Inter em toda parte. O título é centralizado só dentro do halo. O resto do email lê da esquerda para a direita.")}
        {both(slug, spec_type)}</section>
      <section>{head("Components", "Halo", "O eclipse do arco da paisagem, gerado como imagem para cada cor e tema. O título fica dentro do anel. No Outlook, entra por VML.")}
        {both(slug, hero)}</section>
      <section>{head("Components", "Ficha e espectro", "Logo abaixo do halo: o nome da trilha, quatro pontos e uma faixa com as quatro cores. É o que identifica a trilha mesmo com as imagens bloqueadas.")}
        {both(slug, trail_card)}</section>
      <section>{head("Components", "Marcos", "Três colunas com o número na cor da trilha. No mobile, viram uma lista.")}
        {both(slug, milestones)}</section>
      <section>{head("Components", "Citação e assinatura", "A barra da citação é um degradê do glow ao dark. Onde não há degradê, fica na cor accent. A assinatura usa as iniciais num anel.")}
        {both(slug, lambda t: quote(t) + '<div style="height:36px;"></div>' + signature(t))}</section>
      <section>{head("Components", "CTA no halo", "O botão fica dentro de um anel menor. O texto do botão fica branco ou preto conforme o contraste com a cor.")}
        {both(slug, lambda t: cta(t, "#"))}</section>
      <section>{head("Components", "Parágrafos", "Corpo 17/29 com 20px entre parágrafos. No mobile, 16/27.")}
        {both(slug, lambda t: paragraphs([LOREM["curto"], LOREM["medio"], LOREM["longo"]], t))}</section>
      <section>{head("Aplicação", f"Emails conversacionais · {name}", "Copies reais, sem título e sem halo: o logo, a faixa de espectro, a conversa, o botão na cor da trilha e a assinatura em anel.")}
        <div class="frames" style="grid-template-columns:repeat(3,1fr);">''' + "".join(f'<figure><figcaption>{c["code"]} &middot; {c["fase"]} <span><a href="{c["id"]}-{slug}-escuro.html" target="_blank">Escuro</a> &middot; <a href="{c["id"]}-{slug}-claro.html" target="_blank">Claro</a></span></figcaption><iframe loading="lazy" src="{c["id"]}-{slug}-{"escuro" if i % 2 == 0 else "claro"}.html" title="{c["code"]}"></iframe></figure>' for i, c in enumerate(COPIES)) + f'''
        </div></section>
      <section>{head("Aplicação", f"Email escrito · {name}", "Montado com os componentes acima. Troque a cor no seletor para ver a mesma estrutura em outra trilha.")}
        <div class="frames">
          <figure><figcaption>Escuro <a href="email-{slug}-escuro.html" target="_blank">Abrir &rarr;</a></figcaption><iframe loading="lazy" src="email-{slug}-escuro.html" title="Email {name}, escuro"></iframe></figure>
          <figure><figcaption>Claro <a href="email-{slug}-claro.html" target="_blank">Abrir &rarr;</a></figcaption><iframe loading="lazy" src="email-{slug}-claro.html" title="Email {name}, claro"></iframe></figure>
        </div></section>
    </div>'''


def specimen():
    import json
    picker = "".join(f'<button data-slug="{s}" style="--c:{a[2][1]};"><i></i>{a[0]}</button>' for s, a in ACCENTS.items())
    acc_json = json.dumps({s: {"accent": a[2][1], "light": a[2][2]} for s, a in ACCENTS.items()})
    parts = {"FONT": FONT, "PICKER": picker, "ACCENT_JSON": acc_json, "SECTIONS": "".join(sections(s) for s in ACCENTS)}
    return re.sub(r"%([A-Z_]+)%", lambda m: parts.get(m.group(1), m.group(0)), SPEC)


def main():
    for slug in ACCENTS:
        for mode in BASE:
            (OUT / f"email-{slug}-{mode}.html").write_text(email(slug, mode))
            print(f"email-{slug}-{mode}.html")
            for copy in COPIES:
                (OUT / f'{copy["id"]}-{slug}-{mode}.html').write_text(conversa(slug, mode, copy))
    (OUT / "index.html").write_text(specimen())
    print("index.html")


if __name__ == "__main__":
    main()
