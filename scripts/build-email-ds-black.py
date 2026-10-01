#!/usr/bin/env python3
"""Design system de email "Black Friday 2026": a estrutura do design system Asimov
vestida com a identidade visual da Black (Figma "BLACK FRIDAY 2026 _ ASIMOV ACADEMY").

Do design system Asimov vêm a estrutura e os componentes à prova de cliente de email:
o cartão de topo, o sobretítulo, a superfície com brilho, o cartão de CTA, a assinatura,
o rodapé, os temas claro e escuro e o gerador por script.

Diretriz: é um design system com as cores da campanha, não uma peça comercial. O visual
não escreve "Black Friday"; quando o email precisa falar da Black, fala no texto. As peças
de campanha (pílula ao vivo, contagem, ingresso, selos, faixa com texto) ficam documentadas
como opcionais.

Do Figma da Black vêm a identidade: fundo preto, laranja #ff6e14 como protagonista, teal
#01caca como luz de apoio, Rethink Sans nos títulos, o logo metálico, a faixa "BLACK FRIDAY
✷ HISTÓRICA 2026", a pílula "Ao vivo", a contagem regressiva, o ingresso com borda
laranja e o botão em degradê.

Saída em emails/design-system-black/:

    index.html                          página do design system
    email-escuro.html, email-claro.html aplicação com título (lorem ipsum)
    em-XXX-<tema>.html                  emails conversacionais (copies reais, sem título)
    img/

    python3 scripts/build-email-ds-black.py
"""
import re
from pathlib import Path

from email_copies import COPIES, initials, render_blocks

OUT = Path(__file__).resolve().parent.parent / "emails" / "design-system-black"

TITLE_FONT = "'Rethink Sans', 'Helvetica Neue', Helvetica, Arial, sans-serif"
BODY_FONT = "Inter, 'Helvetica Neue', Helvetica, Arial, sans-serif"

# Cores da identidade (Figma): fixas nos dois temas.
BF = {
    "ORANGE": "#ff6e14",
    "RED": "#ff3700",
    "PEACH": "#ffae6b",
    "TEAL": "#01caca",
    "CYAN": "#6fffff",
    "BTN_TOP": "#d48859",     # topo do degradê do botão (180°)
    "BTN_TEXT": "#ffffff",
}

THEMES = {
    "escuro": {
        "SCHEME": "dark",
        "PAGE": "#000000",            # o logo metálico vem sobre preto puro
        "SURFACE": "#0b0908",
        "SURFACE_LINE": "#1b1b1b",
        "TITLE": "#fff7f2",           # o branco quente dos títulos do Figma (#fff → #fff2ec)
        "TEXT": "#ffffff",
        "BODY": "#b3b3b3",
        "MUTED": "#777777",
        "LINE": "#1b1b1b",
        "HL": "#ff6e14",              # palavra em destaque no título
        "ACCENT_TEXT": "#ff6e14",
        "PILL_BG": "#1a0d05",
        "PILL_TEXT": "#fff2ec",
        "TILE_BG": "#111111",
        "TILE_GRAD": "linear-gradient(180deg, #000 31%, #222 56%, #000 150%)",
        "TILE_LINE": "#1b1b1b",
        "TILE_NUM": "#ffffff",
        "TICKET_BG": "#050302",
        "CTA_LINE": "#6b2e0b",
        "CHIP_BG": "#063b3b",
        "CHIP_TEXT": "#ffae6b",
        "BTN_LINE": "#1b1b1b",
        "TOPO": "img/topo-escuro.jpg",
        "CAPA": "img/capa-escuro.jpg",
        "LUZ": "img/luz-escuro.jpg",
        "LOGO_BF": "img/logo-bf-escuro-t.png",
        "LOGO": "img/logo-branco.png",
        "GLOW": "img/glow-escuro.jpg",
        "CTA_IMG": "img/cta-escuro.jpg",
    },
    "claro": {
        "SCHEME": "light",
        "PAGE": "#f7f5f3",
        "SURFACE": "#ffffff",
        "SURFACE_LINE": "#ece7e2",
        "TITLE": "#0a0a0a",
        "TEXT": "#0a0a0a",
        "BODY": "#52525b",
        "MUTED": "#8a8a8a",
        "LINE": "#e7e1db",
        "HL": "#e2560a",
        "ACCENT_TEXT": "#c2410c",     # laranja escurecido para texto pequeno (5:1 no branco)
        "PILL_BG": "#fff1e8",
        "PILL_TEXT": "#9a3412",
        "TILE_BG": "#ffffff",
        "TILE_GRAD": "linear-gradient(180deg, #fff 31%, #f6f2ee 56%, #fff 150%)",
        "TILE_LINE": "#ece7e2",
        "TILE_NUM": "#0a0a0a",
        "TICKET_BG": "#ffffff",
        "CTA_LINE": "#ffc8a3",
        "CHIP_BG": "#e3f8f8",
        "CHIP_TEXT": "#c2410c",
        "BTN_LINE": "#e2560a",
        "TOPO": "img/topo-claro.jpg",
        "CAPA": "img/capa-claro.jpg",
        "LUZ": "img/luz-claro.jpg",
        "LOGO_BF": "img/logo-bf-claro-t.png",
        "LOGO": "img/logo-preto.png",
        "GLOW": "img/glow-claro.jpg",
        "CTA_IMG": "img/cta-claro.jpg",
    },
}

# nome: (fonte, tamanho, entrelinha, peso, tracking, cor, mobile, uso)
TYPE = {
    "Título": ("TITLE", 34, 38, 600, -0.7, "TITLE", "28/32", "Rethink Sans. Uma expressão em laranja."),
    "Título de seção": ("TITLE", 26, 31, 600, -0.5, "TITLE", "23/28", "Abre o corpo do email."),
    "Número": ("TITLE", 38, 38, 600, -0.8, "TILE_NUM", "30/30", "Contagem e dados do ingresso."),
    "Corpo": ("BODY", 17, 29, 400, 0, "BODY", "16/27", "Inter, do design system Asimov."),
    "Apoio": ("BODY", 15, 24, 400, 0, "BODY", "15/24", "Texto de cartões e ingresso."),
    "Rótulo": ("TITLE", 12, 16, 600, 1.4, "ACCENT_TEXT", "12/16", "Caixa alta, em laranja."),
    "Legenda": ("TITLE", 12, 16, 600, -0.2, "MUTED", "12/16", "Rótulos da contagem e notas."),
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

# Dados da live, como no Figma. 04/11/2026 cai numa quarta-feira.
LIVE = {"data": "04.11", "dia": "Quarta-feira", "hora": "19h00", "pill": "Ao vivo &bull; 04.11 &bull; 19h"}


def ts(name, t, color=None):
    fam, size, lh, weight, track, key, _, _ = TYPE[name]
    font = TITLE_FONT if fam == "TITLE" else BODY_FONT
    upper = " text-transform:uppercase;" if name == "Rótulo" else ""
    return (f"font-family:{font}; font-size:{size}px; line-height:{lh}px; font-weight:{weight}; "
            f"letter-spacing:{track}px; color:{color or t.get(key, BF.get(key))};{upper}")


def hl(text, t):
    """Troca [[...]] pela expressão em laranja, como nos títulos do Figma."""
    return re.sub(r"\[\[(.+?)\]\]", lambda m: f'<span style="color:{t["HL"]};">{m.group(1)}</span>', text)


# ------------------------------------------------------------------ componentes

SPECTRUM = f"linear-gradient(90deg, {BF['TEAL']}, #2b1a10 22%, {BF['RED']} 50%, #2b1a10 78%, {BF['TEAL']})"


def fio(t, height=4):
    """Fio de cor no topo do email: as cores da campanha sem nenhum texto."""
    return (f'<table role="presentation" width="100%"><tr>'
            f'<td height="{height}" bgcolor="{BF["ORANGE"]}" style="height:{height}px; background:{BF["ORANGE"]}; background-image:{SPECTRUM}; font-size:0; line-height:0;">&nbsp;</td>'
            f'</tr></table>')


def faixa_asimov(t):
    """Faixa de fechamento: o degradê teal → vermelho → teal da campanha, só com ASIMOV."""
    return (f'<table role="presentation" width="100%"><tr>'
            f'<td align="center" bgcolor="{BF["ORANGE"]}" style="background:{BF["ORANGE"]}; background-image:{SPECTRUM}; padding:14px 12px;">'
            f'<img src="img/logo-branco.png" width="66" height="20" alt="Asimov Academy" style="display:block; width:66px; height:20px; margin:0 auto;"></td>'
            f'</tr></table>')


def faixa(t, variant="laranja"):
    """Peça opcional de campanha: a faixa com texto do Figma. 'laranja' sólida; 'espectro' em degradê."""
    grad = (f" background-image:linear-gradient(90deg, {BF['TEAL']}, #2b1a10 22%, {BF['RED']} 50%, #2b1a10 78%, {BF['TEAL']});"
            if variant == "espectro" else "")
    star = f'&nbsp;&nbsp;<span style="color:#fff2ec;">&#10039;</span>&nbsp;&nbsp;'
    half = star.join(["BLACK FRIDAY", "HIST&Oacute;RICA 2026"])
    text = f'{half}<span class="hide-m">{star}{half}</span>'
    return (f'<table role="presentation" width="100%"><tr>'
            f'<td class="faixa" align="center" bgcolor="{BF["ORANGE"]}" style="background:{BF["ORANGE"]};{grad} padding:11px 12px; '
            f'font-family:{TITLE_FONT}; font-size:13px; line-height:16px; font-weight:600; letter-spacing:0.4px; color:#ffffff; white-space:nowrap;">'
            f'{text}</td></tr></table>')


def pill(t, text=LIVE["pill"]):
    return (f'<table role="presentation" align="center" style="border-collapse:separate; margin:0 auto;"><tr>'
            f'<td bgcolor="{t["PILL_BG"]}" style="background:{t["PILL_BG"]}; border:1px solid {BF["ORANGE"]}; border-radius:999px; padding:6px 14px 6px 10px;">'
            f'<table role="presentation" style="border-collapse:separate;"><tr>'
            f'<td width="12" valign="middle"><div style="width:8px; height:8px; margin:0 2px; border-radius:999px; background:{BF["ORANGE"]}; '
            f'box-shadow:0 0 0 2px rgba(255,110,20,.25), 0 0 6px rgba(255,110,20,.6); font-size:0; line-height:0;">&nbsp;</div></td>'
            f'<td style="padding-left:8px; font-family:{TITLE_FONT}; font-size:12px; line-height:16px; font-weight:600; color:{t["PILL_TEXT"]}; white-space:nowrap;">{text}</td>'
            f'</tr></table></td></tr></table>')


def topo(t):
    """Cartão de topo: a capa estreita (luz da campanha + ASIMOV) e o título logo abaixo."""
    return (f'<table role="presentation" width="100%" style="border-collapse:separate;">'
            f'<tr><td style="font-size:0; line-height:0; border:1px solid {t["SURFACE_LINE"]}; border-bottom:0; border-radius:24px 24px 0 0;">'
            f'<img src="{t["CAPA"]}" width="598" height="150" alt="Asimov Academy" '
            f'style="display:block; width:100%; max-width:598px; height:auto; border-radius:23px 23px 0 0;"></td></tr>'
            f'<tr><td class="px" align="center" bgcolor="{t["SURFACE"]}" style="background:{t["SURFACE"]}; border:1px solid {t["SURFACE_LINE"]}; border-top:0; '
            f'border-radius:0 0 24px 24px; padding:32px 40px 40px;">'
            f'<div class="h1" style="margin:0 auto; max-width:470px; text-align:center; {ts("Título", t)}">{hl("Lorem ipsum: o [[dolor sit amet]] consectetur, adipiscing elit", t)}</div>'
            f'<p style="margin:14px auto 0; max-width:440px; text-align:center; font-family:{BODY_FONT}; font-size:16px; line-height:25px; color:{t["BODY"]};">'
            f'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt.</p>'
            f'</td></tr></table>')


def countdown(t, values=(("42", "DIAS"), ("02", "HORAS"), ("19", "MIN"), ("40", "SEG"))):
    """Contagem regressiva estática. Para ela andar, troque a tabela por um GIF de contador."""
    cells = []
    for i, (n, label) in enumerate(values):
        gap = '<td width="10" style="font-size:0;">&nbsp;</td>' if i else ""
        cells.append(
            f'{gap}<td class="tile" width="78" height="81" align="center" valign="middle" bgcolor="{t["TILE_BG"]}" '
            f'style="width:78px; height:81px; background:{t["TILE_BG"]}; background-image:{t["TILE_GRAD"]}; border:1px solid {t["TILE_LINE"]}; border-radius:10px;">'
            f'<div class="tile-num" style="{ts("Número", t)}">{n}</div>'
            f'<div style="margin-top:3px; {ts("Legenda", t)}">{label}</div></td>')
    return (f'<div style="text-align:center; font-family:{TITLE_FONT}; font-size:12px; line-height:16px; font-weight:600; color:{t["TEXT"]};">A live começa em</div>'
            f'<table role="presentation" align="center" style="border-collapse:separate; margin:12px auto 0;"><tr>{"".join(cells)}</tr></table>')


def meta(text, t, margin="0", align="left"):
    return f'<div style="margin:{margin}; text-align:{align}; {ts("Rótulo", t)}">{text}</div>'


def section_title(text, t, align="left"):
    return f'<div class="h2" style="margin:10px 0 0; text-align:{align}; {ts("Título de seção", t)}">{hl(text, t)}</div>'


def paragraphs(items, t, first="0"):
    return "".join(f'<p style="margin:{first if i == 0 else "20px"} 0 0; {ts("Corpo", t)}">{p}</p>' for i, p in enumerate(items))


def ticket(t):
    """O ingresso da live: borda laranja com brilho, dados à esquerda, canhoto 'online ao vivo' à direita."""
    label = lambda s: f'<div style="font-family:{TITLE_FONT}; font-size:13px; line-height:16px; font-weight:600; color:{t["MUTED"] if t["SCHEME"] == "dark" else "#8a8a8a"};">{s}</div>'
    value = lambda s: f'<div style="margin-top:4px; font-family:{TITLE_FONT}; font-size:26px; line-height:28px; font-weight:700; letter-spacing:-0.5px; color:{t["TEXT"]};">{s}</div>'
    return f'''<table role="presentation" width="100%" style="border-collapse:separate;">
  <tr>
    <td bgcolor="{t["TICKET_BG"]}" style="background:{t["TICKET_BG"]}; border:1.5px solid {BF["ORANGE"]}; border-radius:18px; box-shadow:0 0 22px rgba(255,110,20,.45);">
      <table role="presentation" width="100%">
        <tr>
          <td class="stack" valign="top" style="padding:22px 24px 22px 26px;">
            <div style="font-family:{TITLE_FONT}; font-size:12px; line-height:16px; font-weight:600; letter-spacing:0.3px; color:{BF["ORANGE"]};">&#9679;&nbsp; LIVE &bull; BLACK FRIDAY</div>
            <table role="presentation" style="margin-top:16px;"><tr>
              <td valign="top" style="padding-right:40px;">{label("Data")}{value(LIVE["data"])}{label(LIVE["dia"])}</td>
              <td valign="top">{label("Horário")}{value(LIVE["hora"])}{label("Brasília")}</td>
            </tr></table>
          </td>
          <td class="stack stub" width="150" align="center" valign="middle" style="width:150px; border-left:2px dashed {BF["ORANGE"]}; padding:18px 16px;">
            <div style="width:10px; height:10px; margin:0 auto; border-radius:999px; background:{BF["ORANGE"]}; box-shadow:0 0 0 3px rgba(255,110,20,.25), 0 0 8px rgba(255,110,20,.7); font-size:0; line-height:0;">&nbsp;</div>
            <div style="margin-top:10px; font-family:{TITLE_FONT}; font-size:13px; line-height:16px; font-weight:600; color:{t["TEXT"]};">ONLINE<br>AO VIVO</div>
          </td>
        </tr>
      </table>
    </td>
  </tr>
</table>'''


def chips(t, labels=("Aluno Formação", "Aluno Trilha", "Aluno Anual")):
    # selos em linha (não em células) para quebrarem de linha em telas estreitas
    spans = "".join(
        f'<span style="display:inline-block; margin:0 6px 8px 0; background:{t["CHIP_BG"]}; border-radius:6px; padding:5px 10px; '
        f'font-family:{TITLE_FONT}; font-size:13px; line-height:16px; font-weight:700; color:{t["CHIP_TEXT"]}; white-space:nowrap;">{l}</span>'
        for l in labels)
    return f'<div style="font-size:0; line-height:0;">{spans}</div>'


def destaque(t, with_chips=False):
    """A superfície com brilho do design system, agora com a luz laranja e teal da Black."""
    return (f'<table role="presentation" width="100%" style="border-collapse:separate;"><tr>'
            f'<td background="{t["GLOW"]}" bgcolor="{t["SURFACE"]}" style="background:{t["SURFACE"]} url(\'{t["GLOW"]}\') left top / cover no-repeat; '
            f'border:1px solid {t["SURFACE_LINE"]}; border-radius:20px; padding:28px 28px 22px;">'
            f'{meta("Lorem ipsum", t)}'
            f'<div style="margin-top:8px; font-family:{TITLE_FONT}; font-size:22px; line-height:28px; font-weight:600; letter-spacing:-0.4px; color:{t["TITLE"]};">{hl("Lorem ipsum [[dolor sit]]", t)}</div>'
            f'<div style="margin:8px 0 {"18px" if with_chips else "6px"}; {ts("Apoio", t)}">{LOREM["medio"]}</div>'
            f'{chips(t) if with_chips else ""}</td></tr></table>')


def button(t, label="Lorem ipsum dolor", href="{{link_cta}}", full=False, align="center"):
    """O botão da Black: pílula em degradê vertical, texto branco em caixa alta, seta."""
    width = ' width="100%"' if full else ""
    margin = "0 auto" if align == "center" else "0"
    # align="left" numa tabela faz ela flutuar e o texto seguinte sobe ao lado; só centraliza com o atributo
    align_attr = ' align="center"' if align == "center" else ""
    return (f'<table role="presentation"{width}{align_attr} style="border-collapse:separate; margin:{margin};"><tr>'
            f'<td align="center" bgcolor="{BF["ORANGE"]}" style="background:{BF["ORANGE"]}; background-image:linear-gradient(180deg, {BF["BTN_TOP"]} 2%, {BF["ORANGE"]} 97%); '
            f'border:1px solid {t["BTN_LINE"]}; border-radius:999px; box-shadow:0 10px 30px rgba(255,110,20,.35);">'
            f'<!--[if mso]><v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" href="{href}" style="height:52px;v-text-anchor:middle;width:{"518" if full else "330"}px;" '
            f'arcsize="50%" stroke="f" fillcolor="{BF["ORANGE"]}"><w:anchorlock/><center style="color:#ffffff;font-family:Arial,sans-serif;font-size:15px;font-weight:bold;">{label.upper()}</center></v:roundrect><![endif]-->'
            f'<!--[if !mso]><!--><a class="btn-a" href="{href}" style="display:{"block" if full else "inline-block"}; padding:15px 24px 15px 32px; text-decoration:none; border-radius:999px;">'
            f'<table role="presentation" align="center" style="border-collapse:separate; margin:0 auto;"><tr>'
            f'<td class="btn-t" style="font-family:{TITLE_FONT}; font-size:15px; line-height:20px; font-weight:600; letter-spacing:-0.2px; color:#ffffff; white-space:nowrap;">{label.upper()}</td>'
            f'<td width="12" style="font-size:0;">&nbsp;</td>'
            f'<td><img src="img/seta-branca.png" width="20" height="20" alt="" style="width:20px; height:20px;"></td>'
            f'</tr></table></a><!--<![endif]--></td></tr></table>')


def cta(t, href="{{link_cta}}"):
    """O cartão de CTA do design system (Pricing), com a luz da Black subindo por baixo."""
    return (f'<table role="presentation" width="100%" style="border-collapse:separate;"><tr>'
            f'<td class="cta-in" align="center" background="{t["CTA_IMG"]}" bgcolor="{t["SURFACE"]}" style="background:{t["SURFACE"]} url(\'{t["CTA_IMG"]}\') center bottom / cover no-repeat; '
            f'border:1px solid {t["CTA_LINE"]}; border-radius:24px; padding:36px 28px 34px;">'
            f'{meta("Lorem ipsum", t, align="center")}'
            f'<div class="h2" style="margin:10px auto 0; max-width:420px; text-align:center; {ts("Título de seção", t)}">{hl("Lorem ipsum dolor: [[sit amet]] consectetur", t)}</div>'
            f'<table role="presentation" align="center" style="margin:26px auto 0;"><tr><td>{button(t, href=href)}</td></tr></table>'
            f'<div style="margin-top:16px; font-family:{TITLE_FONT}; font-size:12px; line-height:16px; font-weight:600; color:{t["MUTED"]};">Lorem ipsum dolor sit amet, consectetur.</div>'
            f'</td></tr></table>')


def signature(t):
    return (f'<div style="font-family:{TITLE_FONT}; font-size:15px; line-height:22px; font-weight:600; color:{t["TEXT"]};">Lorem Ipsum</div>'
            f'<div style="font-family:{BODY_FONT}; font-size:13px; line-height:20px; color:{t["MUTED"]};">Dolor sit amet &middot; Asimov Academy</div>')


def footer(t):
    links = "&nbsp;&nbsp;&middot;&nbsp;&nbsp;".join(
        f'<a href="{{{{link_{k.lower()}}}}}" style="color:{t["MUTED"]}; text-decoration:none;">{k}</a>'
        for k in ("YouTube", "Instagram", "LinkedIn"))
    return (f'<table role="presentation" width="100%"><tr>'
            f'<td valign="middle"><img src="{t["LOGO"]}" width="60" height="18" alt="Asimov Academy" style="width:60px; height:18px; opacity:.7;"></td>'
            f'<td align="right" valign="middle" style="font-family:{BODY_FONT}; font-size:12px; line-height:18px;">{links}</td></tr></table>'
            f'<div style="margin-top:16px; font-family:{BODY_FONT}; font-size:12px; line-height:19px; color:{t["MUTED"]};">'
            f'Asimov Academy &middot; {{{{endereco}}}}<br><a href="{{{{link_descadastro}}}}" style="color:{t["MUTED"]};">Cancelar inscrição</a></div>')


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
    Gerado por scripts/build-email-ds-black.py. Edite o script, não este arquivo.
    Antes do disparo, troque img/... por URLs absolutas hospedadas.
    A contagem é estática: para ela andar, troque pela imagem de um gerador de contador (GIF).
  -->
  <link href="https://fonts.googleapis.com/css2?family=Rethink+Sans:wght@400;600;700&amp;family=Inter:wght@400;500&amp;display=swap" rel="stylesheet">
  <style>
    body { margin: 0; padding: 0; width: 100% !important; background: %PAGE%; -webkit-text-size-adjust: 100%; }
    table { border-collapse: collapse; mso-table-lspace: 0; mso-table-rspace: 0; }
    img { border: 0; display: block; outline: none; text-decoration: none; -ms-interpolation-mode: bicubic; }
    a { color: %ACCENT_TEXT%; }
    p { margin: 0; }
    @media (max-width: 620px) {
      .container { width: 100% !important; }
      .px { padding-left: 24px !important; padding-right: 24px !important; }
      .faixa { font-size: 12px !important; }
      .hide-m { display: none !important; }
      .cta-in { padding-left: 16px !important; padding-right: 16px !important; }
      .btn-a { padding: 14px 18px 14px 22px !important; }
      .btn-t { font-size: 13px !important; }
      .h1 { font-size: 27px !important; line-height: 31px !important; }
      .h2 { font-size: 23px !important; line-height: 28px !important; }
      .body td { white-space: normal !important; }
      .body p { font-size: 16px !important; line-height: 27px !important; }
      .tile { width: 66px !important; height: 70px !important; }
      .tile-num { font-size: 30px !important; line-height: 30px !important; }
      .stack { display: block !important; width: 100% !important; box-sizing: border-box; }
      .stub { border-left: 0 !important; border-top: 2px dashed #ff6e14 !important; }
    }
  </style>
</head>
<body style="margin:0; padding:0; background:%PAGE%;">
  <div style="display:none; max-height:0; overflow:hidden; mso-hide:all;">%PREHEADER%&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;</div>
  <table role="presentation" width="100%" bgcolor="%PAGE%" style="background:%PAGE%;">
    <tr><td style="padding:0;">%FAIXA%</td></tr>
    <tr>
      <td align="center" style="padding:24px 12px 0;">
        <table role="presentation" class="container" width="600" style="width:600px; max-width:600px;">
%ROWS%
        </table>
      </td>
    </tr>
    <tr><td style="padding:40px 0 0;">%FAIXA2%</td></tr>
    <tr>
      <td align="center" style="padding:28px 12px 48px;">
        <table role="presentation" class="container" width="600" style="width:600px; max-width:600px;">
          <tr><td class="px" style="padding:0 40px;">%FOOTER%</td></tr>
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
        row(topo(t), "0", cls=""),
        row(meta("Lorem ipsum", t) + section_title("Lorem ipsum dolor sit amet, [[consectetur]] adipiscing.", t), "48px 40px 0"),
        row(paragraphs([f'<strong style="font-weight:500; color:{t["TEXT"]};">Lorem ipsum,</strong> {LOREM["longo"]}', LOREM["curto"]], t, "18px"), "0 40px", "px body"),
        row(paragraphs([LOREM["medio"], LOREM["longo"]], t), "36px 40px 0", "px body"),
        row(destaque(t), "36px 40px 0"),
        row(paragraphs([LOREM["medio"]], t), "36px 40px 0", "px body"),
        row(signature(t), "24px 40px 0"),
        row(cta(t), "48px 40px 0"),
    ]
    tokens = dict(t, ROWS="\n\n".join(rows), FAIXA=fio(t), FAIXA2=faixa_asimov(t), FOOTER=footer(t), TITLE="Lorem ipsum", PREHEADER=PREHEADER_LOREM)
    html = re.sub(r"%([A-Z_0-9]+)%", lambda m: tokens.get(m.group(1), m.group(0)), SHELL)
    leftover = set(re.findall(r"%[A-Z_0-9]+%", html))
    if leftover:
        raise SystemExit(f"email-{theme}: tokens sem valor {leftover}")
    return html


PREHEADER_LOREM = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."


def conversa(theme, copy):
    """Email conversacional: sem título. Capa estreita, a conversa, botões no meio do texto, assinatura."""
    t = THEMES[theme]
    p = lambda text: f'<p style="margin:0 0 18px; {ts("Corpo", t)}">{text}</p>'
    cta_ = lambda label: f'<div style="padding:10px 0 28px;">{button(t, label, align="left")}</div>'
    ul = lambda items: ('<table role="presentation" style="margin:0 0 22px;">' + "".join(
        f'<tr><td width="22" valign="top" style="padding:11px 0 0;"><div style="width:7px; height:7px; border-radius:999px; background:{BF["ORANGE"]}; font-size:0; line-height:0;">&nbsp;</div></td>'
        f'<td style="padding:0 0 6px; {ts("Corpo", t)}">{i}</td></tr>' for i in items) + "</table>")
    sign = lambda name, role: (
        f'<table role="presentation" style="border-collapse:separate; margin:4px 0 0;"><tr>'
        f'<td width="44" height="44" align="center" valign="middle" style="width:44px; height:44px; border:1.5px solid {BF["ORANGE"]}; border-radius:999px; '
        f'font-family:{TITLE_FONT}; font-size:14px; font-weight:700; color:{t["ACCENT_TEXT"]};">{initials(name)}</td>'
        f'<td style="padding-left:14px;"><div style="font-family:{TITLE_FONT}; font-size:16px; line-height:22px; font-weight:600; color:{t["TEXT"]};">{name}</div>'
        + (f'<div style="font-family:{BODY_FONT}; font-size:13px; line-height:20px; color:{t["MUTED"]};">{role}</div>' if role else "")
        + '</td></tr></table>')
    ps = lambda text: (f'<p style="margin:28px 0 0; padding-top:20px; border-top:1px solid {t["LINE"]}; {ts("Corpo", t)}">'
                       f'<strong style="font-family:{TITLE_FONT}; font-weight:700; color:{t["ACCENT_TEXT"]};">PS:</strong> {text}</p>')
    body = render_blocks(copy["blocks"], p, cta_, ul, sign, ps)
    rows = [
        row(f'<img src="{t["CAPA"]}" width="600" height="150" alt="Asimov Academy" style="display:block; width:100%; max-width:600px; height:auto; border-radius:20px;">', "0", cls=""),
        row(body, "40px 40px 0", "px body"),
    ]
    tokens = dict(t, ROWS="\n\n".join(rows), FAIXA=fio(t), FAIXA2=faixa_asimov(t), FOOTER=footer(t),
                  TITLE=copy["assunto"], PREHEADER=copy["preheader"])
    return re.sub(r"%([A-Z_0-9]+)%", lambda m: tokens.get(m.group(1), m.group(0)), SHELL)


def spec_conversas():
    cards = ""
    for c in COPIES:
        cards += (f'<article class="conv"><div class="conv-head"><span class="code">{c["code"]}</span><span>{c["fase"]}</span></div>'
                  f'<b>{c["assunto"]}</b><p>{c["preheader"]}</p><small>{c["publico"]} &middot; {c["data"]}</small>'
                  f'<nav><a href="{c["id"]}-escuro.html" target="_blank">Escuro &rarr;</a><a href="{c["id"]}-claro.html" target="_blank">Claro &rarr;</a></nav></article>')
    return f'<div class="convs">{cards}</div>'


# ------------------------------------------------------------------ página do design system

def both(fn, cls=""):
    return '<div class="pair">' + "".join(
        f'<div class="stage {cls}" style="background:{THEMES[th]["PAGE"]};"><span class="tag {th}">{th}</span>{fn(THEMES[th])}</div>'
        for th in THEMES) + "</div>"


def spec_type(t):
    out = ""
    for name, (fam, size, lh, weight, track, key, mob, use) in TYPE.items():
        sample = {"Número": "42 02 19 40", "Rótulo": "Lorem ipsum", "Legenda": "DIAS &middot; HORAS &middot; MIN"}.get(
            name, hl("Lorem ipsum [[dolor sit]]", t) if fam == "TITLE" else "Lorem ipsum dolor sit amet, consectetur")
        out += (f'<div class="type-row" style="border-color:{t["LINE"]};">'
                f'<div class="type-meta" style="color:{t["MUTED"]};"><b style="color:{t["TEXT"]};">{name}</b><br>'
                f'{"Rethink Sans" if fam == "TITLE" else "Inter"} {size}/{lh} &middot; {weight}<br>mobile {mob}</div>'
                f'<div style="{ts(name, t)}">{sample}</div></div>')
    return out


def spec_colors(t):
    keys = [("PAGE", "Página"), ("SURFACE", "Superfície"), ("TITLE", "Título"), ("BODY", "Corpo"),
            ("MUTED", "Apoio"), ("HL", "Destaque"), ("ACCENT_TEXT", "Laranja em texto"), ("CHIP_BG", "Selo")]
    out = '<div class="swatches">'
    for k, label in keys:
        out += (f'<div><div class="chip" style="background:{t[k]}; border-color:{t["SURFACE_LINE"]};"></div>'
                f'<div style="color:{t["TEXT"]};">{label}</div><code style="color:{t["MUTED"]};">{t[k]}</code></div>')
    return out + "</div>"


SPEC = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Email Black Friday · Asimov Design System</title>
  <link rel="stylesheet" href="../../assets/fonts/fonts.css">
  <link href="https://fonts.googleapis.com/css2?family=Rethink+Sans:wght@400;600;700&display=swap" rel="stylesheet">
  <style>
    * { box-sizing: border-box; }
    body { margin: 0; background: #000; color: #fff; font-family: %BODY_FONT%; -webkit-font-smoothing: antialiased; }
    .t { font-family: %TITLE_FONT%; }
    .wrap { max-width: 1240px; margin: 0 auto; padding: 0 24px 120px; }
    .top { display: flex; justify-content: space-between; align-items: center; padding: 24px 0; }
    .top img { height: 20px; }
    .top a { color: #a1a1aa; font-size: 13px; text-decoration: none; }
    .hero { position: relative; border-radius: 28px; overflow: hidden; border: 1px solid #1b1b1b; max-height: 320px; width: 100%;
      background: #000 url('img/capa-escuro.jpg') center / cover no-repeat; aspect-ratio: 4 / 1; }
    .intro { text-align: center; padding: 48px 0 0; }
    .intro h1 { margin: 22px auto 0; max-width: 820px; font-family: %TITLE_FONT%; font-weight: 600; font-size: clamp(36px, 5.6vw, 64px); line-height: 1.04; letter-spacing: -1.8px; }
    .intro h1 span { color: #ff6e14; }
    .intro p { max-width: 600px; margin: 18px auto 0; color: #b3b3b3; font-size: 18px; line-height: 29px; }
    .mix { display: grid; grid-template-columns: 1fr 64px 1fr; gap: 0; margin-top: 56px; align-items: stretch; }
    .mix .col { border: 1px solid #1b1b1b; border-radius: 22px; padding: 28px; background: linear-gradient(135deg, #0a0a0a, #111); }
    .mix .col.bf { background: radial-gradient(ellipse 90% 70% at 0% 0%, rgba(255,110,20,.22), transparent 60%), radial-gradient(ellipse 60% 50% at 100% 100%, rgba(1,202,202,.14), transparent 60%), #070504; border-color: #3a1a08; }
    .mix .k { font-family: %TITLE_FONT%; font-size: 12px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; color: #2dd4bf; }
    .mix .bf .k { color: #ff6e14; }
    .mix h3 { margin: 8px 0 14px; font-family: %TITLE_FONT%; font-weight: 600; font-size: 24px; letter-spacing: -0.5px; }
    .mix ul { margin: 0; padding: 0; list-style: none; }
    .mix li { padding: 10px 0; border-top: 1px solid rgba(255,255,255,.07); color: #d4d4d8; font-size: 14px; line-height: 21px; }
    .mix .plus { display: grid; place-items: center; font-family: %TITLE_FONT%; font-size: 30px; color: #ff6e14; }
    .lettering { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 16px; }
    .lettering figure { margin: 0; border: 1px solid #1b1b1b; border-radius: 22px; display: grid; place-items: center; padding: 28px; min-height: 220px; }
    .lettering img { max-width: 100%; height: auto; display: block; }
    section { margin-top: 104px; }
    .sec-head { display: grid; grid-template-columns: 1fr 1fr; gap: 24px; align-items: end; padding-bottom: 26px; margin-bottom: 28px; border-bottom: 1px solid #1b1b1b; }
    .sec-head .k { font-family: %TITLE_FONT%; color: #ff6e14; font-size: 12px; font-weight: 600; letter-spacing: 1.4px; text-transform: uppercase; }
    .sec-head h2 { margin: 8px 0 0; font-family: %TITLE_FONT%; font-weight: 600; font-size: 40px; line-height: 44px; letter-spacing: -1px; }
    .sec-head p { margin: 0; color: #a1a1aa; font-size: 15px; line-height: 24px; }
    .pair { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .stage { position: relative; min-width: 0; border: 1px solid #1b1b1b; border-radius: 22px; padding: 52px 32px 32px; overflow: hidden; }
    .stage.flush { padding: 46px 14px 14px; }
    .tag { position: absolute; top: 16px; left: 50%; transform: translateX(-50%); font-family: %TITLE_FONT%; font-size: 10px; font-weight: 600; letter-spacing: 1.6px; text-transform: uppercase; }
    .tag.escuro { color: #777; } .tag.claro { color: #8a8a8a; }
    .type-row { display: grid; grid-template-columns: 140px 1fr; gap: 20px; align-items: baseline; padding: 16px 0; border-bottom: 1px solid; }
    .type-row:last-child { border-bottom: 0; }
    .type-meta { font-size: 12px; line-height: 18px; } .type-meta b { font-weight: 500; }
    .swatches { display: grid; grid-template-columns: repeat(4, 1fr); gap: 18px 12px; font-size: 13px; }
    .chip { height: 52px; border-radius: 12px; border: 1px solid; margin-bottom: 8px; }
    .brand { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; margin-top: 16px; }
    .brand div { border: 1px solid #1b1b1b; border-radius: 16px; overflow: hidden; font-size: 13px; }
    .brand i { display: block; height: 72px; }
    .brand span { display: block; padding: 10px 12px; color: #d4d4d8; } .brand code { display: block; color: #777; }
    code { font-family: ui-monospace, Menlo, Consolas, monospace; font-size: 11px; }
    .full { margin-top: 0; }
    .convs { display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; }
    .conv { border: 1px solid #1b1b1b; border-radius: 20px; padding: 22px; background: radial-gradient(ellipse 80% 60% at 0% 0%, rgba(255,110,20,.14), transparent 60%), #070504; }
    .conv-head { display: flex; justify-content: space-between; font-size: 12px; color: #777; }
    .conv .code { font-family: ui-monospace, Menlo, monospace; color: #ff6e14; }
    .conv b { display: block; margin-top: 14px; font-family: %TITLE_FONT%; font-weight: 600; font-size: 20px; letter-spacing: -0.3px; }
    .conv p { margin: 6px 0 0; color: #b3b3b3; font-size: 14px; line-height: 21px; }
    .conv small { display: block; margin-top: 12px; color: #777; font-size: 12px; }
    .conv nav { display: flex; gap: 16px; margin-top: 16px; font-size: 13px; }
    .conv nav a { color: #ff8a3d; text-decoration: none; }
    .frames { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
    .frames figure { margin: 0; }
    .frames figcaption { display: flex; justify-content: space-between; color: #a1a1aa; font-size: 13px; margin-bottom: 12px; }
    .frames a { color: #ff6e14; text-decoration: none; }
    iframe { display: block; width: 100%; height: 2700px; border: 1px solid #1b1b1b; border-radius: 22px; background: #000; }
    @media (max-width: 900px) {
      .pair, .frames, .sec-head, .lettering, .convs { grid-template-columns: 1fr; }
      .mix { grid-template-columns: 1fr; } .mix .plus { padding: 10px 0; }
      .stage { padding: 48px 16px 22px; }
      .swatches { grid-template-columns: repeat(2, 1fr); } .brand { grid-template-columns: repeat(3, 1fr); }
      .type-row { grid-template-columns: 1fr; gap: 6px; }
    }
  </style>
</head>
<body>
  %FAIXA%
  <div class="wrap">
    <div class="top"><img src="img/logo-branco.png" alt="Asimov"><a href="../index.html">&larr; Todos os design systems de email</a></div>
    <div class="hero" role="img" aria-label="Luz da campanha com o logo Asimov"></div>
    <div class="intro">
      <h1>O design system de email, <span>nas cores da campanha</span></h1>
      <p>A estrutura e os componentes do design system Asimov com a paleta da Black: preto, laranja, luz teal e Rethink Sans. O visual não escreve “Black Friday”; quando o email fala da Black, fala no texto.</p>
    </div>

    <div class="mix">
      <div class="col"><div class="k">Do design system Asimov</div><h3>Estrutura</h3><ul>
        <li>Cartão de topo com imagem e texto real embaixo</li>
        <li>Sobretítulo em caixa alta e título com tracking negativo</li>
        <li>Superfície com brilho para o destaque do texto</li>
        <li>Cartão de CTA, assinatura e rodapé</li>
        <li>Inter no texto corrido, 17/29</li>
        <li>Temas escuro e claro, gerados por script</li>
      </ul></div>
      <div class="plus">+</div>
      <div class="col bf"><div class="k">Da identidade Black Friday</div><h3>Pele</h3><ul>
        <li>Fundo preto e luz laranja com teal (capas do Figma)</li>
        <li>Laranja #ff6e14 nos destaques do título e no botão</li>
        <li>Rethink Sans em títulos, rótulos e botão</li>
        <li>Fio de cor no topo e faixa em degradê no fim, só com ASIMOV</li>
        <li>Botão em pílula com degradê laranja</li>
        <li>Peças de campanha opcionais: pílula, contagem, ingresso, selos</li>
      </ul></div>
    </div>
    <div class="lettering">
      <figure style="background:#000; padding:0; overflow:hidden;"><img src="img/capa-escuro.jpg" alt="Capa estreita, tema escuro" style="width:100%;"></figure>
      <figure style="background:#fff; padding:0; overflow:hidden;"><img src="img/capa-claro.jpg" alt="Capa estreita, tema claro" style="width:100%;"></figure>
    </div>

    <section>
      <div class="sec-head"><div><div class="k">Foundations</div><h2>Tipografia</h2></div>
        <p>Rethink Sans, a fonte das peças da Black, em títulos, números, rótulos e botão. Inter, do design system, no texto corrido. Onde as fontes não carregam, Helvetica e Arial.</p></div>
      %TYPE%
    </section>

    <section>
      <div class="sec-head"><div><div class="k">Foundations</div><h2>Cores</h2></div>
        <p>A paleta da campanha, tirada do Figma. No tema claro, o laranja de texto pequeno escurece para #c2410c para passar de 4.5:1 sobre o branco.</p></div>
      <div class="brand">
        <div><i style="background:#ff6e14"></i><span>Laranja<code>#ff6e14</code></span></div>
        <div><i style="background:#ff3700"></i><span>Vermelho<code>#ff3700</code></span></div>
        <div><i style="background:#ffae6b"></i><span>Pêssego<code>#ffae6b</code></span></div>
        <div><i style="background:#01caca"></i><span>Teal<code>#01caca</code></span></div>
        <div><i style="background:#6fffff"></i><span>Ciano<code>#6fffff</code></span></div>
        <div><i style="background:linear-gradient(180deg,#d48859,#ff6e14)"></i><span>Botão<code>#d48859 → #ff6e14</code></span></div>
      </div>
      <div style="height:16px;"></div>
      %COLORS%
    </section>

    <section>
      <div class="sec-head"><div><div class="k">Components</div><h2>Fio e faixa</h2></div>
        <p>O fio de 4px abre o email com as cores da campanha. A faixa fecha com o degradê teal, vermelho, teal e só o ASIMOV. Onde não há degradê (Gmail, Outlook), os dois ficam laranja.</p></div>
      <div class="stage flush" style="background:#000;"><span class="tag escuro">fio e faixa</span>%FAIXAS%</div>
    </section>

    <section>
      <div class="sec-head"><div><div class="k">Components</div><h2>Topo</h2></div>
        <p>Uma capa estreita (600×150): no escuro, a textura de luz do Figma da campanha; no claro, a mesma luz em versão clara. Só o ASIMOV no centro. O título embaixo é opcional: emails conversacionais não usam.</p></div>
      %TOPO%
    </section>

    <section>
      <div class="sec-head"><div><div class="k">Opcional</div><h2>Peças de campanha</h2></div>
        <p>Ficam fora do padrão e entram só quando o email pede: pílula ao vivo, contagem (estática; para andar, use um GIF de contador), ingresso, selos de aluno e a faixa com texto do Figma.</p></div>
      %OPCIONAIS%
      <div style="height:16px;"></div>
      %TICKET%
    </section>

    <section>
      <div class="sec-head"><div><div class="k">Components</div><h2>Destaque e CTA</h2></div>
        <p>As superfícies do design system com a luz da campanha subindo pelo canto. O CTA é o cartão do Pricing com o botão em degradê laranja.</p></div>
      %DESTAQUE%
      <div style="height:16px;"></div>
      %CTA%
    </section>

    <section>
      <div class="sec-head"><div><div class="k">Foundations</div><h2>Parágrafos</h2></div>
        <p>Inter 17/29, cinza #b3b3b3 no escuro, igual ao corpo das LPs da Black. 20px entre parágrafos.</p></div>
      %PARAGRAPHS%
    </section>

    <section>
      <div class="sec-head"><div><div class="k">Aplicação</div><h2>Emails conversacionais</h2></div>
        <p>Copies reais da campanha, sem título, como a maior parte dos emails da Asimov: a capa estreita, a conversa, o botão no meio do texto e a assinatura.</p></div>
      %CONVERSAS%
      <div class="frames" style="margin-top:16px;">
        <figure><figcaption>EM-022 · escuro <a href="em-022-escuro.html" target="_blank">Abrir &rarr;</a></figcaption><iframe src="em-022-escuro.html" title="EM-022, escuro"></iframe></figure>
        <figure><figcaption>EM-001 · claro <a href="em-001-claro.html" target="_blank">Abrir &rarr;</a></figcaption><iframe src="em-001-claro.html" title="EM-001, claro"></iframe></figure>
      </div>
    </section>

    <section>
      <div class="sec-head"><div><div class="k">Aplicação</div><h2>Email com título</h2></div>
        <p>Os componentes montados num email só, pelo mesmo script, nos dois temas.</p></div>
      <div class="frames">
        <figure><figcaption>Escuro <a href="email-escuro.html" target="_blank">Abrir &rarr;</a></figcaption><iframe src="email-escuro.html" title="Email Black Friday, escuro"></iframe></figure>
        <figure><figcaption>Claro <a href="email-claro.html" target="_blank">Abrir &rarr;</a></figcaption><iframe src="email-claro.html" title="Email Black Friday, claro"></iframe></figure>
      </div>
    </section>
  </div>
  %FAIXA_END%
  <script>
    document.querySelectorAll("iframe").forEach(f => f.addEventListener("load", () => {
      try { f.style.height = f.contentDocument.documentElement.scrollHeight + "px"; } catch (_) {}
    }));
  </script>
</body>
</html>
"""


def specimen():
    d = THEMES["escuro"]
    parts = {
        "TITLE_FONT": TITLE_FONT, "BODY_FONT": BODY_FONT,
        "FAIXA": fio(d), "FAIXA_END": faixa_asimov(d),
        "CONVERSAS": spec_conversas(),
        "OPCIONAIS": both(lambda t: pill(t) + '<div style="height:24px;"></div>' + countdown(t) + '<div style="height:28px;"></div>' + ticket(t) + '<div style="height:24px;"></div>' + chips(t)
                          + '<div style="height:16px;"></div>' + faixa(t)),
        "TYPE": both(spec_type),
        "COLORS": both(spec_colors),
        "FAIXAS": fio(d) + '<div style="height:24px;"></div>' + faixa_asimov(d),
        "TOPO": both(topo, "flush"),
        "TICKET": both(lambda t: countdown(t) + '<div style="height:28px;"></div>' + ticket(t)),
        "DESTAQUE": both(destaque),
        "CTA": both(lambda t: cta(t, "#")),
        "PARAGRAPHS": both(lambda t: paragraphs([LOREM["curto"], LOREM["medio"], LOREM["longo"]], t)),
    }
    return re.sub(r"%([A-Z_]+)%", lambda m: parts.get(m.group(1), m.group(0)), SPEC)


def main():
    for theme in THEMES:
        (OUT / f"email-{theme}.html").write_text(email(theme))
        print(f"email-{theme}.html")
    for copy in COPIES:
        for theme in THEMES:
            name = f'{copy["id"]}-{theme}.html'
            (OUT / name).write_text(conversa(theme, copy))
            print(name)
    (OUT / "index.html").write_text(specimen())
    print("index.html")


if __name__ == "__main__":
    main()
