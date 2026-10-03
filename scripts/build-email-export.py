#!/usr/bin/env python3
"""Lista os templates de email prontos para uso fora do design system.

Varre emails/ e grava a mesma lista em dois formatos:

    emails/templates.json   para aplicações (descobrir templates por código)
    emails/templates.js     para a seção "Exportar" do hub (funciona via file://)

E junta os kits de cada sistema (emails/kits/asimov-email-<slug>.zip, gravados pelos
build-email-ds*.py) num pacote único: emails/kits/asimov-email-design-systems.zip.

Entram os templates dos quatro design systems (Aura, Cadence, Trilhas e Black Friday).

Rode por último, depois dos build-email-ds*.py:

    python3 scripts/build-email-export.py
"""
import importlib.util
import json
import re
import zipfile
from pathlib import Path

from email_copies import COPIES
from email_kit import KITS, absolutize, assets_base, audit, fail_on, write_zip

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
                "imagens_base": assets_base(folder),
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
    # A mesma troca que o "Copiar HTML" faz no hub (emails/export.js): nada pode sair fora da CDN.
    fail_on([problema for t in templates
             for problema in audit(absolutize((EMAILS / t["caminho"]).read_text(encoding="utf-8"), t["caminho"].split("/")[0]),
                                   t["caminho"].split("/")[0], t["caminho"])])
    print(f"Auditoria: as imagens dos {len(templates)} templates e dos kits apontam só para a CDN.")
    data = json.dumps(templates, ensure_ascii=False, indent=2)
    (EMAILS / "templates.json").write_text(data + "\n", encoding="utf-8")
    (EMAILS / "templates.js").write_text(
        "/* Gerado por scripts/build-email-export.py. Não edite à mão. */\n"
        f"window.AsimovEmailTemplates = {data};\n",
        encoding="utf-8",
    )
    print(f"{len(templates)} templates em emails/templates.json e emails/templates.js")

    files = {}
    for kit in sorted(KITS.glob("asimov-email-*.zip")):
        if kit.name == "asimov-email-design-systems.zip":
            continue
        with zipfile.ZipFile(kit) as z:
            files.update({f"asimov-email-design-systems/{n}": z.read(n) for n in z.namelist()})
    write_zip(KITS / "asimov-email-design-systems.zip", files)
    print(f"kits/asimov-email-design-systems.zip ({len(files)} arquivos)")


if __name__ == "__main__":
    main()
