# Asimov / Lumina — instruções para aplicar este design system

Esta pasta é autocontida. Use-a como fonte de verdade visual para landing pages e
aplicativos. Abra `index.html` (composição principal com Aura),
`cadence-rain.html` (layout de workspace com Cadence Rain) e
`components.html` (biblioteca).
Comece uma implementação copiando `starter.html`. Não é necessário Astro,
Tailwind, npm, CDN ou servidor para abrir os HTMLs. Sirva em HTTP quando integrar
a um aplicativo; os mesmos caminhos relativos funcionam em subdiretórios.

## Antes de implementar

1. Examine os layouts e o componente correspondente no navegador.
2. Leia `tokens.json`, `assets/css/tokens.css` e este arquivo.
3. Reutilize o HTML de `components.html` ou os helpers em
   `scripts/build-pages.mjs`. Não substitua os materiais por cards genéricos.
4. Implemente a lógica do produto, estados, teclado e responsividade. Os dados,
   preços, formulários e ações deste pacote são demonstrações locais.
5. Use textos sóbrios, diretos e descritivos. Nomeie o recurso e explique sua
   função; evite superlativos, metáforas grandiosas e promessas genéricas.

## Assinatura visual

- Inter é a fonte de títulos e interface. Pesos: 400, 500, 600 e 700.
  H1 expressivo, peso 500, tracking negativo; H2 30–40px na home.
  Copy 18px/1.65, `#b4b4b4`; texto de card 16px/1.65, zinc translúcido.
- `text-gradient-silver` é um gradiente **vertical** branco → prata → cinza.
  Não transforme os títulos em um gradiente horizontal multicolorido.
- Fundo `#050505`; superfícies próximas de `#0a0a0a`. Branco e cinzas conduzem
  o texto, accent sinaliza interação. Respeite contraste de texto e foco.
- Tema da home: accent `#14b8a6`, dark `#0d9488`, light `#2dd4bf`,
  glow `#5eead4`. Mude os quatro juntos e o RGB `20 184 166`.
- Use espaço para criar hierarquia: escala 4/8/12/16/24/32/48/64/96px,
  container até 1280px, dobras 64–100px. Mobile tem 20–24px de margem.
- Raios: 8px em controles, 16px em painéis, 24px em cards, pill em CTAs.
- Vidro = fill escuro translúcido + blur + borda fina + highlight superior.
  Preserve beam, halo, pontilhado e pseudo-elementos mascarados.
- Cards de trilha mantêm sua paleta própria (`--card-accent*`), independente
  do tema global (`--ui-accent*`). Todas as paletas estão em `tokens.json`.
  Em Components e nos layouts, os exemplos de cards herdam o tema global escolhido
  na navbar fixa, assim como botões, gráficos e todas as opções de background. O padrão de cada
  visita é Asimov; não há seletor de cor independente no preview de background.
  As amostras do catálogo de paletas e as cores semânticas de sucesso, alerta e
  erro preservam suas cores de referência. O seletor também aparece na navbar
  dos layouts com Aura, Cadence Rain e no starter, recolorindo cada página inteira.
  O seletor e as amostras usam nomes de cores: Teal (padrão Asimov), Ciano,
  Laranja, Azul, Vermelho, Verde, Terracota e Roxo. Tons próximos de campanhas
  foram agrupados: n8n/Python Web em Vermelho e Cyan/Python em Ciano. Os IDs
  originais continuam internos, sem aparecer como nomes de cores na interface.
- A identidade demonstrada usa apenas Inter. Instrument Serif é um asset
  legado do projeto de origem e não deve ser apresentada como parte dela.

## Arquitetura e origem

- `assets/css/source-components.css`: snapshot de `src/styles/components.css`.
  As quatro diretivas Tailwind `@apply` foram expandidas para CSS nativo;
  seletores `:global(...)` foram convertidos para seletores normais.
- `source-header.css`, `source-pricing.css`, `source-motion.css` e
  `cadence-rain.css`: copiados dos estilos originais, com seu comportamento.
- `source-button-glow.css`: estilo original de `ButtonGlow.astro` sem scoping
  Astro. O HTML portátil recompõe as classes de utilidade no adaptador.
- `design-system.css`: ponto de entrada, importa tudo em ordem. Contém reset,
  adaptadores de utilitários, layouts e extensões de aplicativos. Não depende
  do Tailwind; não rode um purge contra os arquivos originais sem auditoria.
- `rain-shaders.js`: GLSL **inalterado** de CadenceRainBackground.client.ts.
  `rain.js` é o adaptador independente, com montagem, pausa, atualização de
  tokens, resize, perda/restauração de contexto e limpeza.
- `aurora.js` + `aurora.css`: adaptador portátil da Aurora boreal e camadas
  da paisagem original. Montagem, pausa, tint por accent, resize e limpeza.
- `aura-scene.js`: cena original local do Unicorn Studio. O SDK local recebe
  um blob de JSON em vez de buscar um projectId na nuvem.
- `system.js`: interações da demonstração. `themes.js`: paletas locais.
- `scripts/build-pages.mjs`: fonte dos HTMLs e ícones. É opcional para quem
  consome o pacote; usa apenas Node built-ins. Para editar as páginas de forma
  reproduzível, altere este script e execute `node scripts/build-pages.mjs`
  dentro desta pasta. Nunca execute o script após editar só os HTMLs sem
  transportar a edição para a fonte, pois ele regenera os quatro arquivos.

O pacote foi extraído da home disponível no repositório em 18/09/2026.
A home selecionava Aurora + paisagem; Cadence Rain também existia no projeto.
O layout principal, starter e a página Components usam **Aurora + paisagem**
como background principal. O fundo de Components acompanha o seletor global de
cores, com Asimov como padrão; os controles das prévias não alteram o efeito
do fundo da página. Não omita a imagem: ela faz parte da identidade da home.
`cadence-rain.html` demonstra um layout alternativo com chuva WebGL,
hero de aplicativo e dashboard, acessível pela navegação de exemplos em Layouts.
Em Components, os quatro backgrounds ficam renderizados em prévias separadas,
uma abaixo da outra: Aura + paisagem, Cadence Rain, Aura sem imagem e paisagem
estática. Não use dropdown nem esconda essas prévias. O HTML de cada exemplo
permanece disponível no código-fonte, sem botões de cópia na interface.
As animadas têm pausa independente, e Cadence Rain tem controle
de intensidade. A montagem e pausa fora da viewport são gerenciadas pelos
adaptadores. Cada preview tem base opaca para não receber a animação do fundo
da página por transparência.

## Uso mínimo

Carregue `assets/css/design-system.css`. Use scripts **clássicos**, nesta ordem,
com `defer`: `themes.js`, `rain-shaders.js`, `rain.js`, `aurora.js`, `system.js`.
Todos ficam em `assets/js/`. Scripts clássicos e cenas embutidas permitem
`file://`; não converta tudo para imports ES Modules sem considerar esse modo.

Para o fundo principal completo, Aurora boreal + paisagem:

```html
<div class="aura-background aura-background--composite" data-aura aria-hidden="true"></div>
<div class="landscape-layer" aria-hidden="true">
  <img class="landscape-layer__image"
    src="assets/images/landscape-1280.webp"
    srcset="assets/images/landscape-768.webp 768w, assets/images/landscape-1280.webp 1280w"
    sizes="100vw" width="1280" height="720" alt="" decoding="async">
</div>
<main style="position:relative;z-index:1">…</main>
```

Preserve a ordem: Aurora → paisagem → grid opcional → conteúdo. A classe
`aura-background--composite` retira o escurecimento extra da Aurora; a camada
da paisagem cuida da fusão, como `SiteBackground.astro` no projeto original:
imagem com `object-fit:cover` e opacidade 30%, gradiente vertical `#050505`
a 90% no topo / 60% no meio / 100% na base, e glow radial do accent-dark a 16%.
Não aplique opacidade ao container inteiro nem use uma imagem opaca por cima.
As camadas são fixed, sem bordas; o preto final coincide com o fundo da página.
Copie também as duas imagens `assets/images/landscape-*.webp`.
O snippet “01 / Aura + paisagem” em Components inclui ambas as camadas.

Para usar **somente Aurora**, carregue `tokens.css`, `aurora.css` e `aurora.js`.
Copie também `assets/fonts/`, `assets/js/aura-scene.js` e
`assets/vendor/unicornStudio.umd.js`, mantendo a estrutura de pastas.
Use `<div class="aura-background" data-aura aria-hidden="true"></div>`
sem o modificador `--composite` e sem a camada de paisagem.
O adaptador carrega cena e SDK localmente quando o fundo entra na viewport.
Não há espera por outro efeito da hero nem solicitação de projeto remoto.

`AsimovAurora.mount(element)` retorna `{refresh(), pause(bool), destroy()}`.
Há montagem automática de `[data-aura]`. Em SPA, monte após inserir o DOM e
chame `destroy()` ao desmontar; isso limpa apenas a cena correspondente.
`refresh()` atualiza o tint a partir de `--ui-accent`, com o mesmo cálculo HSV
do projeto original. O preview e o tema global usam esse contrato.
O efeito pausa com aba oculta ou fora da viewport. Movimento reduzido preserva
o fundo CSS estático. A pausa manual preserva o último frame da cena.
Tokens opcionais: `--aura-opacity`, `--aura-darken` e `--aura-filter`.
O filtro é atualizado por `refresh()`; aplique overrides depois da montagem.
Para uma seção, use `position:absolute` nos dois roots e
`position:relative; isolation:isolate; overflow:hidden` no container.

Uma CSP estrita deve permitir o blob local em `connect-src`, ou você pode
adaptar `filePath` em `aurora.js` para servir `assets/source/aura-default.json`
via HTTP. Não reative carregamento por projectId remoto.

Para a alternativa Cadence Rain:

```html
<div class="cadence-rain-bg" data-rain aria-hidden="true"></div>
<main style="position:relative;z-index:1">…</main>
```

Se quiser **somente a chuva**, carregue `tokens.css`, `cadence-rain.css`,
`rain-shaders.js` e `rain.js`, copiando também `assets/fonts/`. O CSS do fundo
é fixed por padrão; para uma seção, use `position:absolute` no root e
`position:relative; isolation:isolate; overflow:hidden` no container.

`AsimovRain.mount(element)` retorna `{refresh(), pause(bool), destroy()}`.
Há montagem automática de `[data-rain]` no load. Em SPA, monte após inserir
o DOM e chame `destroy()` ao desmontar; evite múltiplos canvases fixos.
Depois de mudar CSS vars, chame `refresh()`; isso atualiza as cores do shader.
Controles: `--cadence-rain-shader-intensity`, `--cadence-rain-shader-alpha`,
`--cadence-rain-center-glow`, `--cadence-rain-star-opacity` e fades no CSS.

## Componentes e comportamentos

Na biblioteca, os grupos de exemplos não têm card externo nem botões de cópia
de HTML: os títulos ficam diretamente sobre o fundo. Preserve apenas as superfícies dos
componentes demonstrados, sem adicionar borda, fundo ou padding ao `.specimen`.

| Componente | Contrato visual / interação |
| --- | --- |
| ButtonGlow | 3 camadas; borda cônica 3s, inner inset 1px, glow e scale 1.05 |
| CTA sólido / ghost | Gradiente dark→accent, sombra accent e hover -1px |
| Course card | Beam + halo + pontos 24px; hover -8px, rotate 2°, scale 1.03 |
| GlassBenefitCard | Pedestal, halo, anel, borda mascarada; elevação -5px |
| Platform media | Imagem inteira, glow e beam; sem recortar o screenshot |
| Instructor card | Foto e máscara; verso gradiente no hover/foco; carrossel |
| Social proof | Avatares sobrepostos com borda; texto compacto de duas linhas |
| Pricing | Blur, borda com máscara, badge flutuante; plano normal/destaque |
| Garantia | Selo SVG circular em rotação 30s, núcleo e layout responsivo |
| FAQ | Botão aria-expanded; região inert fechada; transição grid 0fr→1fr |
| Navbar / footer | Vidro escuro, divisórias discretas e hierarquia original |
| Aurora + paisagem / Cadence Rain | Composição da home principal; cenas e imagem locais |
| Formulários / dados | Extensões: mesmos tokens, estados explícitos e foco |
| Modal / toast | Dialog nativo, Escape e foco; status anunciado sem mover foco |

O adaptador usa SVGs inline locais para eliminar a dependência de Iconify.
Arrow, play, check, plus e chevrons preservam os paths de `Icon.astro`;
os demais ícones são adaptações locais de traço, não cópias do pacote Solar.
O sprite `assets/images/icons.svg` também pode ser usado em sites HTTP.

## Acessibilidade e desempenho

- Mantenha `prefers-reduced-motion`; não esconda conteúdo se JS falhar.
- Há fallback sem WebGL, pausa com aba oculta e limite de DPR/fps na chuva.
  Use no máximo um fundo WebGL contínuo por página de produto. Evite animação
  intensa atrás de formulários e tabelas. A biblioteca roda previews para QA.
- Inclua labels, mensagens de erro associadas, aria-invalid, estados de tabs,
  botões nativos e `:focus-visible`. Não dependa somente de hover ou de cor.
- Preserve Tab/Shift+Tab, setas nas tabs e Escape no modal. Renomeie IDs e
  aria-controls ao duplicar snippets; não gere IDs repetidos.
- Gráficos precisam de descrição textual e valores compreensíveis. Use dados
  reais na integração, sem transportar métricas ilustrativas para produção.
- Teste pelo menos 390px e 1280px, movimento reduzido, teclado, formulário
  inválido/válido, troca de abas e funcionamento num subdiretório diferente.

## Assets e marcas

`assets/images/` inclui as seis imagens PNG originais da plataforma, seis
avatares, treze retratos, duas paisagens e o logo SVG. São referências da marca
Asimov: preserve apenas onde sua utilização fizer sentido e for autorizada.
As licenças das fontes (OFL) estão em `assets/fonts/`.
O SDK Unicorn é uma cópia do SDK já utilizado no
projeto original; este pacote não concede novos direitos sobre SDK ou marcas.
Não copie tracking, checkout, dados pessoais ou links de campanha da home.

## Checklist de identidade ao entregar

Confira fonte local carregada, títulos Inter/prata, tema completo, fundos e
camadas dos cards, estados normal/hover/focus/disabled, layout mobile, redução
de movimento e ausência de recursos remotos necessários. Preserve a intenção
visual ao adaptar componentes a React, Vue, Astro ou qualquer outra stack.
