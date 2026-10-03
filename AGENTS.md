# Asimov Design System: guia para agentes

Site estático, sem build e sem dependências: abre via `file://` e é publicado na Vercel
(`https://asimov-design-system.vercel.app`, público, `noindex`). Leia o `README.md` para a visão geral.

## Onde está cada coisa

- `design-system.html`: entrada. Navbar com Overview, Components, Emails, seletor Escuro/Claro e cores.
- `assets/overview/` e `assets/components/`: o design system web. O modo claro é uma camada
  (`assets/modo.js` + `assets/modo-claro.css`) presa a `html[data-modo="claro"]`; não duplique páginas.
- `emails/`: o hub e os quatro design systems de email (Aura, Cadence, Trilhas, Black Friday).
- `scripts/`: os geradores dos emails. Ficam fora do deploy (`.vercelignore`).

## Regras gerais

- Tudo com caminho relativo e local: fontes, ícones, imagens e scripts. Nada de CDN.
- Textos em português do Brasil. Copy demonstrativa em lorem ipsum.
- Os HTML de email são **gerados**. Edite o script, nunca o HTML em `emails/design-system*/`.
- Depois de mudar qualquer gerador, rode todos e confira que os emails que você não quis mudar
  continuam iguais (`git status` sem diferença neles).

```bash
python3 scripts/build-email-ds.py && python3 scripts/build-email-ds-cadence.py && python3 scripts/build-email-ds-trilhas.py && python3 scripts/build-email-ds-black.py && python3 scripts/build-email-export.py
```

## Como os design systems de email são montados

Cada sistema tem um gerador `scripts/build-email-ds*.py` que é a fonte de verdade: tokens,
componentes e a montagem dos emails moram nele. Ele grava em `emails/design-system-<nome>/`:

- `index.html`: a página do design system (fundações, componentes, aplicação).
- `email-<tema>.html`: a aplicação com título, em lorem ipsum.
- `em-XXX-<tema>.html`: os emails conversacionais, com as copies reais de `scripts/email_copies.py`.
- `img/`: imagens (só PNG e JPG; email não aceita SVG), no dobro do tamanho de exibição.

E grava o kit para download em `emails/kits/asimov-email-<slug>.zip` via `scripts/email_kit.py`.
Nos kits e no "Copiar HTML" do hub, `img/...` vira `https://img.asimov.academy/email/<slug>/<versão>/...`
(bunny.net). A versão de cada sistema fica em `SISTEMAS`, no `email_kit.py`, e uma versão publicada nunca
muda: mudou uma imagem, suba a versão e rode `scripts/upload-email-assets.py --enviar` (ver README).
Por último, `scripts/build-email-export.py` gera `emails/templates.json`/`.js` (lista de templates
do hub) e junta os kits em `emails/kits/asimov-email-design-systems.zip`. Os zips são
determinísticos: sem mudança de conteúdo, o arquivo não muda.

O contrato que todo gerador cumpre:

| Peça | O que é |
|---|---|
| `THEMES` | Um dicionário de cores por tema, `escuro` e `claro`. Os dois são obrigatórios. |
| `TYPE` | A escala tipográfica: tamanho, entrelinha, peso, tracking, cor, tamanho no mobile e uso. |
| `SHELL` | O documento do email com tokens `%NOME%`. O conteúdo entra em `%ROWS%`. |
| `row(html, pad, cls)` | Envolve uma peça numa linha `<tr>` do container de 600px. |
| componentes | Uma função por peça: hero, capa, título, cartões, CTA, rodapé... |
| `blocos(t)` | Devolve `p, cta, ul, sign, ps`, os blocos do email conversacional, na ordem de `email_copies.render_blocks`. |
| `fill(t, rows, assunto, preheader)` | Preenche a `SHELL`. |
| `email(theme)` / `conversa(theme, copy)` | A aplicação e os conversacionais. No Trilhas, recebem também a cor (`slug`). |
| `specimen()` | A página `index.html` do sistema. |
| `kit()` | Devolve um `email_kit.Kit`: casca, peças por variante, tipografia e receitas de montagem. |
| `main()` | Grava tudo e chama `write_kit(kit())`. |

## Criar um design system de email novo

1. **Combine o conceito antes de codar.** Qual o papel do sistema (campanha, formação, tipo de email),
   o que ele faz diferente dos quatro que existem e quais peças próprias ele terá. Se for só outra cor,
   provavelmente é uma variante do Trilhas, não um sistema novo.

2. **Copie o gerador mais próximo** para `scripts/build-email-ds-<nome>.py` e ajuste o docstring e
   `OUT = .../emails/design-system-<nome>`. Mantenha o contrato da tabela acima.

3. **Tokens.** Defina `THEMES` (escuro e claro) e `TYPE`. Texto pequeno em cor de acento precisa de
   contraste AA (4,5:1) no fundo do tema; no claro, escureça o acento para texto. Fontes do Google
   Fonts sempre com Helvetica e Arial de reserva: Gmail e Outlook não carregam fonte web.

4. **Componentes à prova de cliente de email.**
   - Layout em `<table role="presentation">`, estilos inline, largura máxima de 600px.
   - Botões e imagens de fundo com a versão VML do Outlook (`<!--[if mso]>`), como nos geradores atuais.
   - Toda cor com fallback sólido (`bgcolor` + `background`) antes de degradês.
   - Links como variáveis: `{{link_cta}}`, `{{link_descadastro}}`, `{{link_youtube}}`,
     `{{link_instagram}}`, `{{link_linkedin}}`, `{{endereco}}`. Rodapé com descadastro e endereço é obrigatório.
   - Media query só para o mobile (`.px`, `.h1`, `.h2`, `.body`...); o email precisa funcionar sem ela.

5. **Imagens** em `emails/design-system-<nome>/img/`, PNG ou JPG, no dobro do tamanho de exibição
   (a capa é 1200x300 para 600x150). Precisam existir nos dois temas. Registre o sistema em `SISTEMAS`
   no `scripts/email_kit.py` (`"design-system-<nome>": ("<slug>", "v1")`): é o que define a pasta no bunny.net.

6. **Emails.** `email(theme)` com a aplicação em lorem ipsum e `conversa(theme, copy)` para cada copy
   de `COPIES`. A conversa usa `render_blocks(copy["blocks"], *blocos(t))`.

7. **Página do sistema.** `specimen()` grava o `index.html` com fundações, componentes e a aplicação
   nos dois temas, no mesmo formato das páginas atuais.

8. **Kit.** Escreva `kit()` listando cada peça como `linha` (vai na casca) ou `bloco` (vai dentro da
   linha `corpo`, que precisa existir e conter `{{blocos}}`), com nome e quando usar. Inclua as receitas
   de montagem (`montagem`) e notas próprias. Chame `write_kit(kit())` no `main()`.

9. **Registre o sistema** no restante do repositório:
   - `scripts/build-email-export.py`: adicione a pasta e o nome em `SISTEMAS`.
   - `emails/index.html`:
     - um cartão em `#design-systems`, copiando um `<article class="ds">` existente, com o link "Baixar kit (.zip)";
     - as miniaturas `emails/_hub/<nome>-escuro.jpg` e `-claro.jpg` (captura do email em 600px de largura, JPG);
     - a linha na tabela de `#conversacionais`;
     - o cartão do kit em `#exportar`, com o número de peças igual ao que o `kit()` gera;
     - os números do topo (design systems e emails prontos).
   - O comando de build deste arquivo e do `README.md`.

10. **Gere e confira.**
    - Rode todos os geradores e o `build-email-export.py`; os outros sistemas não podem mudar.
    - Abra o `index.html` do sistema e os emails nos dois temas, no desktop e em 390px.
    - Abra `<variante>/catalogo.html` de dentro do zip.
    - Suba as imagens com `python3 scripts/upload-email-assets.py --enviar` e confira com `--verificar`.
    - No hub, teste "Baixar kit" e "Copiar HTML".
    - Antes de usar de verdade, envie um teste para Gmail, Outlook e celular.

## Remover um design system de email

Apague o gerador, a pasta em `emails/`, as miniaturas em `emails/_hub/`, o zip em `emails/kits/` e as
referências no hub, nos dois `SISTEMAS` (`build-email-export.py` e `email_kit.py`) e nos comandos de build.
Não apague as imagens no bunny.net: emails já enviados ainda as usam. Depois rode o
`build-email-export.py` para refazer a lista e o pacote completo.
