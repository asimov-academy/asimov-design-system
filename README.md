# Asimov Design System

![Prévia animada do Asimov Design System](assets/readme/index-preview.gif)

Biblioteca visual autocontida para criar landing pages e aplicativos com a identidade da Asimov Academy. A V2 reúne uma cópia funcional da landing page como **Overview** e um catálogo de **Components** extraído diretamente dela, preservando tipografia, temas, componentes, imagens e animações principais.

Não exige framework, npm, CDN ou servidor local.

## Como explorar

Abra `design-system.html` diretamente no navegador. O projeto funciona via `file://`.

Se preferir servir a pasta localmente:

```bash
python3 -m http.server 4173
```

Depois acesse `http://localhost:4173/design-system.html`.

- **Overview:** adaptação funcional da landing page original, com copy demonstrativa.
- **Components:** foundations e componentes reais reutilizados do Overview.
- **Cores:** 17 variantes de tema disponíveis no seletor da navbar.
- **Backgrounds:** Aura + paisagem, Cadence Rain, Aura isolada e paisagem estática.

## Estrutura

- `design-system.html`: entrada principal e navegação entre as duas visualizações.
- `assets/overview/index.html`: Overview completo e autocontido.
- `assets/components/index.html`: catálogo de foundations e componentes.
- `assets/themes.js`: variantes cromáticas compartilhadas.
- `assets/components/backgrounds/`: cenas, shaders, imagens e runtime dos fundos animados.

Todos os caminhos são relativos. Fontes, imagens e o runtime do Unicorn Studio estão armazenados localmente para preservar o funcionamento via `file://`.

## Como usar com IA

Peça para a IA tratar este diretório como fonte de verdade visual. Ela deve observar primeiro o Overview e reutilizar o HTML, as classes, os assets e os componentes existentes antes de criar novas interfaces.

Exemplo de prompt:

```text
Use o design system deste repositório para implementar [descreva a tela].
Abra design-system.html, observe o Overview e reutilize os componentes da
página Components. Preserve identidade visual, responsividade, acessibilidade,
temas e animações. Não redesenhe componentes existentes nem introduza
dependências remotas sem necessidade.
```

Os textos e dados exibidos são demonstrativos e devem ser substituídos pelo conteúdo real de cada implementação.
