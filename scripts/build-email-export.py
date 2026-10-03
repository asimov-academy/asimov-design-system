#!/usr/bin/env python3
"""Gera os arquivos de download dos design systems de email, um por tema:

    emails/asimov-email-<tema>.html           os três sistemas (Aura, Cadence e Black Friday)
    emails/asimov-email-<sistema>-<tema>.html um sistema só

Cada um tem, num HTML só: como usar e, para cada sistema, fundações, casca, elementos e
exemplos de aplicação. As peças vêm do
kit() de cada gerador (ver email_kit.py), então nunca divergem dos emails.

O build trava se alguma imagem ficar fora da CDN (email_kit.audit).

Rode por último, depois dos build-email-ds*.py:

    python3 scripts/build-email-export.py
"""
import importlib.util
from pathlib import Path

from email_kit import reference_html

ROOT = Path(__file__).resolve().parent.parent
GERADORES = ("build-email-ds", "build-email-ds-cadence", "build-email-ds-black")


def _load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    kits = [_load(g).kit() for g in GERADORES]
    arquivos = [("", kits)] + [(f"{k.slug}-", [k]) for k in kits]
    for tema in ("escuro", "claro"):
        for prefixo, grupo in arquivos:
            path = ROOT / "emails" / f"asimov-email-{prefixo}{tema}.html"
            path.write_text(reference_html(grupo, tema), encoding="utf-8")
            print(f"emails/{path.name} ({path.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
