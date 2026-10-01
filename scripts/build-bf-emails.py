#!/usr/bin/env python3
"""Gera os emails da Black Friday nas versões escura e clara.

Cada arquivo em emails/black-friday/_src/ traz só o miolo do email, com tokens
%COR% no lugar das cores. Este script envolve o miolo no esqueleto comum
(head, preheader, container de 600px, rodapé) e grava uma cópia por tema.

    python3 scripts/build-bf-emails.py
"""
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "emails" / "black-friday"
SRC = ROOT / "_src"

THEMES = {
    "escuro": {
        "SCHEME": "dark",
        "BG": "#050505",
        "SURFACE": "#0e0e0e",
        "SURFACE2": "#161616",
        "LINE": "#262626",
        "TEXT": "#fafafa",
        "MUTED": "#a3a3a3",
        "FAINT": "#666666",
        "ACCENT": "#14b8a6",
        "ACCENT_TEXT": "#2dd4bf",
        "ACCENT_HI": "#5eead4",
        "ON_ACCENT": "#04201d",
        "ACCENT_SOFT": "#0b2522",
        "PAPER": "#f2efe8",
        "INK": "#111111",
        "PAPER_LINE": "#bdb8ad",
        "LOGO": "img/logo-branco.png",
    },
    "claro": {
        "SCHEME": "light",
        "BG": "#efede7",
        "SURFACE": "#ffffff",
        "SURFACE2": "#f7f6f2",
        "LINE": "#dedad2",
        "TEXT": "#0a0a0a",
        "MUTED": "#4f4f4f",
        "FAINT": "#8c8a85",
        "ACCENT": "#14b8a6",
        "ACCENT_TEXT": "#0f766e",
        "ACCENT_HI": "#0d9488",
        "ON_ACCENT": "#04201d",
        "ACCENT_SOFT": "#ddf3ef",
        "PAPER": "#ffffff",
        "INK": "#111111",
        "PAPER_LINE": "#c9c5bc",
        "LOGO": "img/logo-preto.png",
    },
}

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
    Gerado por scripts/build-bf-emails.py a partir de _src/%FILE%. Edite o _src.
    Preços, datas e números são demonstrativos. Antes do disparo, troque os
    caminhos de imagem (img/...) por URLs absolutas hospedadas.
  -->
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;800&family=Instrument+Serif:ital@1&family=Voltaire&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
  <style>
    body { margin: 0; padding: 0; width: 100% !important; background: %BG%; -webkit-text-size-adjust: 100%; }
    table { border-collapse: collapse; mso-table-lspace: 0; mso-table-rspace: 0; }
    img { border: 0; display: block; outline: none; text-decoration: none; -ms-interpolation-mode: bicubic; }
    a { color: %ACCENT_TEXT%; }
    .serif { font-family: 'Instrument Serif', Georgia, 'Times New Roman', serif; font-style: italic; font-weight: 400; }
    .display { font-family: Voltaire, 'Arial Narrow', Arial, sans-serif; }
    .mono { font-family: 'JetBrains Mono', 'SFMono-Regular', Menlo, Consolas, monospace; }
    @media (max-width: 620px) {
      .container { width: 100% !important; }
      .px { padding-left: 24px !important; padding-right: 24px !important; }
      .stack { display: block !important; width: 100% !important; box-sizing: border-box; }
      .hide-m { display: none !important; }
      .center-m { text-align: center !important; }
%MOBILE%
    }
  </style>
</head>
<body style="margin:0; padding:0; background:%BG%;">
  <div style="display:none; max-height:0; overflow:hidden; mso-hide:all;">%PREHEADER%&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;&#8199;&#847;</div>
  <table role="presentation" width="100%" bgcolor="%BG%" style="background:%BG%;">
    <tr>
      <td align="center" style="padding:32px 12px 48px;">
        <table role="presentation" class="container" width="600" style="width:600px; max-width:600px;">
%BODY%
          <tr>
            <td class="px" align="center" style="padding:48px 40px 0; font-family:Inter,Arial,sans-serif; font-size:12px; line-height:19px; color:%FAINT%;">
              <a href="{{link_youtube}}" style="color:%MUTED%; text-decoration:none;">YouTube</a> &nbsp;&middot;&nbsp;
              <a href="{{link_instagram}}" style="color:%MUTED%; text-decoration:none;">Instagram</a> &nbsp;&middot;&nbsp;
              <a href="{{link_linkedin}}" style="color:%MUTED%; text-decoration:none;">LinkedIn</a><br><br>
              Asimov Academy &middot; {{endereco}}<br>
              Você recebe este email porque se cadastrou na Black Friday Asimov.<br>
              <a href="{{link_descadastro}}" style="color:%FAINT%;">Cancelar inscrição</a>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def barcode(color, gap, height=44, seed=7):
    """Código de barras feito de células de tabela: aparece em qualquer cliente."""
    rng = random.Random(seed)
    cells = []
    for i in range(46):
        w = rng.choice((1, 1, 2, 2, 3, 4))
        bg = color if i % 2 == 0 else gap
        cells.append(f'<td width="{w}" height="{height}" bgcolor="{bg}" style="width:{w}px; height:{height}px; background:{bg}; font-size:0; line-height:0;">&nbsp;</td>')
    return '<table role="presentation" style="border-collapse:collapse;"><tr>' + "".join(cells) + "</tr></table>"


def parse(src):
    meta, body = src.split("---\n", 1)
    fields = dict(line.split(": ", 1) for line in meta.strip().splitlines())
    mobile = ""
    if "<!--mobile" in body:
        mobile = re.search(r"<!--mobile\n(.*?)-->\n", body, re.S).group(1)
        body = re.sub(r"<!--mobile\n.*?-->\n", "", body, flags=re.S)
    return fields, mobile.rstrip(), body.rstrip()


def render(text, tokens):
    return re.sub(r"%([A-Z_0-9]+)%", lambda m: tokens.get(m.group(1), m.group(0)), text)


def main():
    for theme, palette in THEMES.items():
        out_dir = ROOT / theme
        out_dir.mkdir(exist_ok=True)
        for path in sorted(SRC.glob("*.html")):
            fields, mobile, body = parse(path.read_text())
            tokens = dict(palette)
            tokens["LOGO"] = "../" + palette["LOGO"]
            tokens["BARCODE_INK"] = barcode(palette["INK"], palette["PAPER"])
            tokens["BARCODE_ON_ACCENT"] = barcode(palette["ON_ACCENT"], palette["ACCENT"], height=40, seed=3)
            tokens.update(TITLE=fields["title"], PREHEADER=fields["preheader"], FILE=path.name)
            tokens.update(MOBILE=render(mobile, tokens), BODY=render(body, tokens))
            html = render(SHELL, tokens)
            leftover = set(re.findall(r"%[A-Z_0-9]+%", html))
            if leftover:
                raise SystemExit(f"{path.name}: tokens sem valor {leftover}")
            (out_dir / path.name).write_text(html)
            print(f"{theme}/{path.name}")


if __name__ == "__main__":
    main()
