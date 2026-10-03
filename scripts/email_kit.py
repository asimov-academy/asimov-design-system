"""Kit para download de um design system de email: tudo o que uma aplicação precisa para
montar emails novos, num .zip.

Cada build-email-ds*.py descreve o seu sistema (casca, componentes, tokens) e chama
write_kit(). O kit sai em emails/kits/asimov-email-<slug>.zip com:

    LEIA-ME.md               como montar um email, regras e prompt para LLM
    design-system.json       variantes, componentes, tokens e variáveis, para código
    <variante>/casca.html    o documento do email, com {{linhas}} no lugar do conteúdo
    <variante>/componentes/  uma peça por arquivo: linhas (vão na casca) e blocos (vão no corpo)
    <variante>/catalogo.html todas as peças da variante empilhadas, para ver de uma vez
    exemplos/                os emails prontos do sistema
    img/                     as imagens usadas, para hospedar em outro lugar se precisar

As imagens nos HTML apontam para a hospedagem de imagens de email (ASSETS_URL), não para
o site do design system. O zip é determinístico: o mesmo conteúdo gera o mesmo arquivo,
então rodar o build sem mudanças não suja o git.
"""
import json
import re
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KITS = ROOT / "emails" / "kits"
SITE_URL = "https://asimov-design-system.vercel.app"

# Onde as imagens dos emails ficam para disparo: bunny.net, Storage Zone "asimov-email" com a
# Pull Zone em img.asimov.academy. Cada sistema tem uma versão, e uma versão publicada nunca
# muda: emails já enviados continuam mostrando as mesmas imagens. Mudou alguma imagem de um
# sistema? Suba a versão dele aqui, rode os builds e scripts/upload-email-assets.py.
ASSETS_URL = "https://img.asimov.academy/email"
SISTEMAS = {  # pasta em emails/ -> (slug, versão das imagens)
    "design-system": ("aura", "v1"),
    "design-system-cadence": ("cadence", "v1"),
    "design-system-trilhas": ("trilhas", "v1"),
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
    "{{blocos}}": "Na linha 'corpo': onde entram os blocos de texto, em sequência.",
    "{{link_cta}}": "Destino dos botões.",
    "{{link_descadastro}}": "Link de cancelar inscrição (obrigatório).",
    "{{link_youtube}}": "Rodapé.",
    "{{link_instagram}}": "Rodapé.",
    "{{link_linkedin}}": "Rodapé.",
    "{{endereco}}": "Endereço da empresa no rodapé (obrigatório).",
}

_FIXED_DATE = (2026, 1, 1, 0, 0, 0)


@dataclass
class Componente:
    slug: str
    nome: str
    tipo: str          # "linha" (vai na casca) ou "bloco" (vai dentro da linha corpo)
    uso: str
    html: str


@dataclass
class Variante:
    id: str            # pasta no zip: "escuro", "claro", "teal-escuro"...
    rotulo: str
    tema: str          # "escuro" ou "claro"
    casca: str         # documento completo com {{assunto}}, {{preheader}} e {{linhas}}
    componentes: list
    cores: dict
    cor: str | None = None


@dataclass
class Kit:
    slug: str          # aura, cadence, trilhas, black
    nome: str
    pasta: str         # pasta do sistema em emails/
    descricao: str
    fontes: list
    tipografia: list   # [{nome, tamanho, entrelinha, peso, tracking, mobile, uso}]
    variantes: list
    exemplos: list     # nomes de arquivo em emails/<pasta>/
    montagem: list = field(default_factory=list)   # receitas: (nome, [slugs])
    notas: list = field(default_factory=list)


def absolutize(html, pasta):
    """Troca img/... pela URL hospedada. Texto puro, para alcançar também o VML do Outlook."""
    base = assets_base(pasta)
    html = re.sub(r'(\s(?:src|background)=")img/([^"]+)"', lambda m: f'{m.group(1)}{base}{m.group(2)}"', html)
    html = re.sub(r"url\((['\"]?)img/([^'\")]+)\1\)", lambda m: f"url({m.group(1)}{base}{m.group(2)}{m.group(1)})", html)
    return html.replace("Antes do disparo, troque img/... por URLs absolutas hospedadas.",
                        f"Imagens hospedadas em {base}")


_REFS = re.compile(r"""\s(?:src|background)=["']([^"']+)["']|url\(\s*["']?([^"')]+?)["']?\s*\)""")


def audit(html, pasta, onde):
    """Toda imagem de um email que sai daqui (kit ou "Copiar HTML") precisa apontar para a CDN,
    na pasta com versão do sistema, e existir em emails/<pasta>/img/ (é isso que o upload sobe).
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


def _images(html):
    return set(re.findall(r'(?:src|background)="(img/[^"]+)"', html)) | set(re.findall(r"url\(['\"]?(img/[^'\")]+)", html))


def _file(slug, n, c):
    return f"{n:02d}-{c.tipo}-{c.slug}.html"


def _catalogo(v, kit):
    """Todas as peças de uma variante empilhadas: linhas direto, blocos dentro de um corpo."""
    label = lambda c, n: (f'          <tr><td class="px" style="padding:44px 40px 12px; font-family:ui-monospace,Menlo,Consolas,monospace; '
                          f'font-size:11px; line-height:16px; letter-spacing:1px; color:#8a8a93;">'
                          f'{c.tipo.upper()} &middot; {_file(kit.slug, n, c)} &middot; {c.nome}</td></tr>')
    corpo = next((c for c in v.componentes if c.slug == "corpo"), None)
    rows = []
    for n, c in enumerate(v.componentes, 1):
        rows.append(label(c, n))
        rows.append(corpo.html.replace("{{blocos}}", c.html) if c.tipo == "bloco" and corpo else c.html)
    return (v.casca.replace("{{assunto}}", f"Catálogo · {kit.nome} · {v.rotulo}")
            .replace("{{preheader}}", "Todas as peças do design system.")
            .replace("{{linhas}}", "\n".join(rows)))


def _readme(kit):
    v0 = kit.variantes[0]
    linhas = [c for c in v0.componentes if c.tipo == "linha"]
    blocos = [c for c in v0.componentes if c.tipo == "bloco"]
    tabela = lambda cs: "\n".join(f"| `{_file(kit.slug, v0.componentes.index(c) + 1, c)}` | {c.nome} | {c.uso} |" for c in cs)
    receitas = "\n".join(f"- **{nome}:** " + " → ".join(f"`{s}`" for s in slugs) for nome, slugs in kit.montagem)
    variantes = "\n".join(f"- `{v.id}/`: {v.rotulo}" for v in kit.variantes)
    variaveis = "\n".join(f"| `{k}` | {d} |" for k, d in VARIAVEIS.items())
    notas = "\n".join(f"- {n}" for n in kit.notas)
    return f"""# Asimov · design system de email {kit.nome}

{kit.descricao}

Guia visual: {SITE_URL}/emails/{kit.pasta}/index.html

## O que tem aqui

- `design-system.json`: variantes, componentes, cores, tipografia e variáveis, para código.
- `<variante>/casca.html`: o documento do email (head, estilos, container de 600px). O conteúdo entra em `{{{{linhas}}}}`.
- `<variante>/componentes/`: uma peça por arquivo. **Linhas** vão direto na casca; **blocos** vão dentro da linha `corpo`, no lugar de `{{{{blocos}}}}`.
- `<variante>/catalogo.html`: todas as peças da variante, empilhadas. Abra no navegador para ver tudo de uma vez.
- `exemplos/`: emails prontos feitos com este sistema.
- `img/`: as imagens usadas.

Variantes:

{variantes}

As peças são iguais em todas as variantes; só mudam cores e imagens.

## Como montar um email

1. Escolha a variante e abra `casca.html`.
2. Troque `{{{{assunto}}}}` e `{{{{preheader}}}}`.
3. Em `{{{{linhas}}}}`, cole as linhas na ordem do email.
4. Na linha `corpo`, troque `{{{{blocos}}}}` pelos blocos de texto: parágrafos, botões, lista, assinatura, PS.
5. Troque os textos de exemplo (lorem ipsum) pelos reais e preencha as variáveis de link.

Receitas comuns:

{receitas}

## Linhas

| Arquivo | Peça | Quando usar |
|---|---|---|
{tabela(linhas)}

## Blocos

| Arquivo | Peça | Quando usar |
|---|---|---|
{tabela(blocos)}

## Variáveis

| Variável | O que é |
|---|---|
{variaveis}

## Regras

- Troque só textos e links. Tabelas, estilos inline, larguras e os blocos `<!--[if mso]>` (Outlook) precisam ficar como estão.
- Um botão por ideia. Rótulos curtos, com verbo.
- Imagens: já apontam para `{assets_base(kit.pasta)}`, uma pasta que nunca muda. Para hospedar em outro lugar, suba a pasta `img/` e troque esse prefixo.
- Teste no Gmail, no Outlook e no celular antes de disparar.
{notas}

## Com uma LLM

Entregue à LLM a casca, os componentes da variante e a copy, e peça algo como:

> Monte um email com a casca e os componentes abaixo. Use só esses componentes, na ordem que fizer
> sentido para a copy. Troque apenas os textos de exemplo pela copy. Não altere tabelas, estilos,
> atributos, comentários `<!--[if mso]>` nem variáveis `{{{{...}}}}`. Responda só com o HTML final.

Se a sua aplicação montar o email por código, a LLM pode devolver só a lista de peças e textos, e o
código junta os arquivos. É mais previsível do que pedir o HTML inteiro.
"""


def _manifest(kit):
    return {
        "nome": kit.nome,
        "slug": kit.slug,
        "descricao": kit.descricao,
        "guia": f"{SITE_URL}/emails/{kit.pasta}/index.html",
        "imagens_base": assets_base(kit.pasta),
        "fontes": kit.fontes,
        "tipografia": kit.tipografia,
        "variaveis": VARIAVEIS,
        "montagem": [{"nome": n, "linhas": s} for n, s in kit.montagem],
        "variantes": [{
            "id": v.id,
            "rotulo": v.rotulo,
            "tema": v.tema,
            "cor": v.cor,
            "casca": f"{v.id}/casca.html",
            "catalogo": f"{v.id}/catalogo.html",
            "cores": v.cores,
            "componentes": [{"slug": c.slug, "nome": c.nome, "tipo": c.tipo, "uso": c.uso,
                             "arquivo": f"{v.id}/componentes/{_file(kit.slug, n, c)}"}
                            for n, c in enumerate(v.componentes, 1)],
        } for v in kit.variantes],
        "exemplos": [f"exemplos/{e}" for e in kit.exemplos],
    }


def kit_files(kit):
    """Conteúdo do kit como {caminho no zip: bytes}."""
    src = ROOT / "emails" / kit.pasta
    root = f"asimov-email-{kit.slug}"
    html = {}
    for v in kit.variantes:
        html[f"{v.id}/casca.html"] = v.casca
        html[f"{v.id}/catalogo.html"] = _catalogo(v, kit)
        for n, c in enumerate(v.componentes, 1):
            html[f"{v.id}/componentes/{_file(kit.slug, n, c)}"] = c.html.strip("\n") + "\n"
    for e in kit.exemplos:
        html[f"exemplos/{e}"] = (src / e).read_text(encoding="utf-8")
    images = sorted(set().union(*(_images(h) for h in html.values())))
    html = {p: absolutize(h, kit.pasta) for p, h in html.items()}
    fail_on([problema for p, h in html.items() for problema in audit(h, kit.pasta, f"kit {kit.slug}/{p}")])
    files = {f"{root}/{p}": h.encode("utf-8") for p, h in html.items()}
    for img in images:
        files[f"{root}/{img}"] = (src / img).read_bytes()
    files[f"{root}/LEIA-ME.md"] = _readme(kit).encode("utf-8")
    files[f"{root}/design-system.json"] = (json.dumps(_manifest(kit), ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    return files


def write_zip(path, files):
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for name in sorted(files):
            info = zipfile.ZipInfo(name, _FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            z.writestr(info, files[name], compresslevel=9)


def write_kit(kit):
    path = KITS / f"asimov-email-{kit.slug}.zip"
    files = kit_files(kit)
    write_zip(path, files)
    print(f"kits/{path.name} ({len(files)} arquivos)")
    return path
