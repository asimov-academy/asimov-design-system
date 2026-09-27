// Refresh the SVGs used by the static Overview and Components pages.
// Run only when intentionally updating the bundled Iconify artwork.
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const pages = [
  'assets/overview/index.html',
  'assets/components/index.html',
];
const names = new Set();

for (const page of pages) {
  const html = await readFile(path.join(root, page), 'utf8');
  for (const match of html.matchAll(/<iconify-icon\b[^>]*\bicon="([^"]+)"/g)) {
    names.add(match[1]);
  }
}

const ids = [...names].sort();
const iconRoot = path.join(root, 'assets/icons');
const encoded = new Map();
const rules = [
  '/* Local masks preserve currentColor and avoid Iconify runtime/API requests. */',
  'iconify-icon {',
  '  display: inline-block;',
  '  vertical-align: -0.125em;',
  '  flex: none;',
  '  width: 1em;',
  '  height: 1em;',
  '  background-color: currentColor;',
  '  -webkit-mask-image: var(--icon);',
  '  mask-image: var(--icon);',
  '  -webkit-mask-repeat: no-repeat;',
  '  mask-repeat: no-repeat;',
  '  -webkit-mask-position: center;',
  '  mask-position: center;',
  '  -webkit-mask-size: contain;',
  '  mask-size: contain;',
  '}',
  ...[14, 18, 22, 24, 28, 30, 36].map((size) =>
    `iconify-icon[width="${size}"] { width: ${size}px; height: ${size}px; }`),
];

await Promise.all(ids.map(async (id) => {
  const [collection, icon] = id.split(':');
  if (!/^[a-z0-9-]+$/.test(collection) || !/^[a-z0-9-]+$/.test(icon)) {
    throw new Error(`Unexpected icon ID: ${id}`);
  }
  const response = await fetch(`https://api.iconify.design/${id}.svg`);
  if (!response.ok) throw new Error(`${id}: HTTP ${response.status}`);
  const svg = await response.text();
  if (!svg.startsWith('<svg ') || /<script\b|<foreignObject\b|https?:\/\//i.test(svg.replace('http://www.w3.org/2000/svg', ''))) {
    throw new Error(`${id}: unexpected SVG content`);
  }
  const folder = path.join(iconRoot, collection);
  await mkdir(folder, { recursive: true });
  await writeFile(path.join(folder, `${icon}.svg`), `${svg}\n`);
  encoded.set(id, Buffer.from(svg).toString('base64'));
}));

for (const id of ids) {
  const source = `data:image/svg+xml;base64,${encoded.get(id)}`;
  rules.push(`iconify-icon[icon="${id}"] { --icon: url("${source}"); }`);
}
await writeFile(path.join(iconRoot, 'icons.css'), `${rules.join('\n')}\n`);
console.log(`Bundled ${ids.length} icons.`);
