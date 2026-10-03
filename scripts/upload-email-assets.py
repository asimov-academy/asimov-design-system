#!/usr/bin/env python3
"""Sobe as imagens dos emails para o bunny.net, servidas em img.asimov.academy.

Cada sistema vai para email/<slug>/<versão>/ na Storage Zone, espelhando emails/<pasta>/img/
(slug e versão em SISTEMAS, no scripts/email_kit.py). Uma versão publicada nunca muda: se um
arquivo já existe lá com outro conteúdo, o script para e pede para subir a versão do sistema.
Assim emails já enviados continuam mostrando as mesmas imagens.

    python3 scripts/upload-email-assets.py              mostra o que falta subir (não envia nada)
    python3 scripts/upload-email-assets.py --enviar     sobe o que falta
    python3 scripts/upload-email-assets.py --verificar  confere na CDN cada imagem, byte a byte

Para --enviar, defina no seu terminal (os dados ficam em Storage → asimov-email → FTP & API Access):

    export BUNNY_STORAGE_ZONE=asimov-email
    export BUNNY_STORAGE_HOST=br.storage.bunnycdn.com    # o "Hostname" da zona
    export BUNNY_STORAGE_KEY=...                         # a "Password" da zona. Nunca versione.
"""
import argparse
import hashlib
import mimetypes
import os
import sys
import urllib.error
import urllib.request
from urllib.parse import urlparse

from email_kit import ASSETS_URL, ROOT, SISTEMAS

UA = "asimov-design-system/upload-email-assets"
PREFIX = urlparse(ASSETS_URL).path.strip("/")   # a pasta na Storage Zone é o caminho da URL: "email"


def local_files():
    """[(caminho relativo a ASSETS_URL, arquivo local)] de todas as imagens dos sistemas."""
    out = []
    for pasta, (slug, versao) in SISTEMAS.items():
        img = ROOT / "emails" / pasta / "img"
        for path in sorted(p for p in img.rglob("*") if p.is_file()):
            out.append((f"{slug}/{versao}/{path.relative_to(img).as_posix()}", path))
    return out


def fetch(url, headers=None):
    """Bytes do arquivo, ou None se não existe."""
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def cdn_url(remote):
    return f"{ASSETS_URL}/{remote}"


def storage():
    zone, host, key = (os.environ.get(k) for k in ("BUNNY_STORAGE_ZONE", "BUNNY_STORAGE_HOST", "BUNNY_STORAGE_KEY"))
    if not (zone and host and key):
        sys.exit("Defina BUNNY_STORAGE_ZONE, BUNNY_STORAGE_HOST e BUNNY_STORAGE_KEY (ver o topo deste script).")
    base = host if host.startswith("http") else f"https://{host}"
    return f"{base.rstrip('/')}/{zone}/{PREFIX}", {"AccessKey": key}


def plan(remote_get):
    """Compara cada imagem local com a publicada: novas, iguais e divergentes."""
    novas, iguais, divergentes = [], [], []
    for remote, path in local_files():
        data = path.read_bytes()
        publicado = remote_get(remote)
        if publicado is None:
            novas.append((remote, path, data))
        elif publicado == data:
            iguais.append(remote)
        else:
            divergentes.append(remote)
    return novas, iguais, divergentes


def main():
    try:
        run()
    except urllib.error.HTTPError as e:
        if e.code == 401:
            sys.exit("O bunny.net recusou a senha (HTTP 401). Confira BUNNY_STORAGE_KEY e BUNNY_STORAGE_ZONE.")
        sys.exit(f"O bunny.net respondeu HTTP {e.code} em {e.url}")
    except urllib.error.URLError as e:
        sys.exit(f"Não consegui acessar o bunny.net: {e.reason}")


def run():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--enviar", action="store_true", help="sobe as imagens que faltam")
    ap.add_argument("--verificar", action="store_true", help="confere na CDN cada imagem, byte a byte")
    args = ap.parse_args()

    if args.verificar:
        falhas = 0
        for remote, path in local_files():
            publicado = fetch(cdn_url(remote))
            if publicado != path.read_bytes():
                falhas += 1
                print(f"  {'falta' if publicado is None else 'diferente'}  {cdn_url(remote)}")
        total = len(local_files())
        print(f"{total - falhas} de {total} imagens corretas em {ASSETS_URL}/")
        sys.exit(1 if falhas else 0)

    if args.enviar:
        base, headers = storage()
        remote_get = lambda remote: fetch(f"{base}/{remote}", headers)
    else:
        remote_get = lambda remote: fetch(cdn_url(remote))

    novas, iguais, divergentes = plan(remote_get)
    if divergentes:
        print("Estas imagens já foram publicadas com outro conteúdo:")
        for remote in divergentes:
            print(f"  {cdn_url(remote)}")
        sys.exit("Uma versão publicada não muda. Suba a versão do sistema em SISTEMAS "
                 "(scripts/email_kit.py), rode os builds e envie de novo.")
    print(f"{len(iguais)} já publicadas, {len(novas)} para enviar.")
    if not args.enviar:
        for remote, _, _ in novas:
            print(f"  + {cdn_url(remote)}")
        if novas:
            print("Nada foi enviado. Rode com --enviar para subir.")
        return

    for remote, path, data in novas:
        req = urllib.request.Request(f"{base}/{remote}", data=data, method="PUT", headers={
            **headers, "User-Agent": UA,
            "Content-Type": mimetypes.guess_type(path.name)[0] or "application/octet-stream",
            "Checksum": hashlib.sha256(data).hexdigest().upper(),
        })
        with urllib.request.urlopen(req, timeout=60) as r:
            if r.status not in (200, 201):
                sys.exit(f"Falhou ao enviar {remote}: HTTP {r.status}")
        print(f"  enviado {cdn_url(remote)}")
    print(f"Pronto. Confira com: python3 scripts/upload-email-assets.py --verificar")


if __name__ == "__main__":
    main()
