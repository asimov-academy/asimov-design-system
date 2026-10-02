#!/usr/bin/env python3
"""Lista os templates de email prontos para uso fora do design system.

Varre emails/ e grava a mesma lista em dois formatos:

    emails/templates.json   para aplicações (descobrir templates por código)
    emails/templates.js     para a seção "Exportar HTML" do hub (funciona via file://)

Entram os templates dos quatro design systems (Aura, Cadence, Trilhas e Black Friday).

Rode depois de qualquer build-email-*.py que crie ou remova templates:

    python3 scripts/build-email-export.py
"""
import importlib.util
import json
import re
from pathlib import Path

from email_copies import COPIES

ROOT = Path(__file__).resolve().parent.parent
EMAILS = ROOT / "emails"


def _load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), ROOT / "scripts" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


TRILHAS = {slug: label for slug, (label, *_rest) in _load("build-email-ds-trilhas").ACCENTS.items()}
COPY_BY_ID = {c["id"]: c for c in COPIES}

SISTEMAS = {
    "design-system": "Aura",
    "design-system-cadence": "Cadence",
    "design-system-trilhas": "Trilhas",
    "design-system-black": "Black Friday",
}



def title(path):
    match = re.search(r"<title>(.*?)</title>", path.read_text(encoding="utf-8"), re.S)
    return match.group(1).strip() if match else ""


def ds_templates():
    for folder, sistema in SISTEMAS.items():
        for path in sorted((EMAILS / folder).glob("*.html")):
            if path.name == "index.html":
                continue
            stem = path.stem
            tema = "claro" if stem.endswith("-claro") else "escuro"
            stem = stem.rsplit("-", 1)[0]
            cor = None
            if folder == "design-system-trilhas":
                stem, cor = next((stem[: -len(slug) - 1], slug) for slug in TRILHAS if stem.endswith("-" + slug))
            if stem == "email":
                peca, nome, descricao = "Aplicação", "Vitrine de componentes", "Todos os componentes do sistema num email com texto de exemplo."
            else:
                copy = COPY_BY_ID[stem]
                peca, nome = copy["code"], copy["assunto"]
                descricao = f'Conversacional · {copy["fase"]} · {copy["publico"]}'
            yield {
                "id": path.relative_to(EMAILS).with_suffix("").as_posix().replace("/", "--"),
                "caminho": path.relative_to(EMAILS).as_posix(),
                "sistema": sistema,
                "peca": peca,
                "nome": nome,
                "descricao": descricao,
                "tema": tema,
                "cor": TRILHAS[cor] if cor else None,
                "assunto": title(path),
            }


def main():
    templates = list(ds_templates())
    data = json.dumps(templates, ensure_ascii=False, indent=2)
    (EMAILS / "templates.json").write_text(data + "\n", encoding="utf-8")
    (EMAILS / "templates.js").write_text(
        "/* Gerado por scripts/build-email-export.py. Não edite à mão. */\n"
        f"window.AsimovEmailTemplates = {data};\n",
        encoding="utf-8",
    )
    print(f"{len(templates)} templates em emails/templates.json e emails/templates.js")


if __name__ == "__main__":
    main()
