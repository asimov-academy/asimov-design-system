// Verify the portability contract, using only Node built-ins.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const issues=[];
let refs=0;
async function check(from,reference){
  if(!reference||reference.startsWith('data:'))return;
  if(/^(?:https?:)?\/\//.test(reference)||reference.startsWith('/')){issues.push(`${from}: non-portable reference ${reference}`);return;}
  const [pathname,fragment]=reference.split('#');
  const file=path.resolve(path.dirname(from),decodeURIComponent(pathname.split('?')[0]||path.basename(from)));
  if(!file.startsWith(root+path.sep)){issues.push(`${from}: escapes package: ${reference}`);return;}
  try{await fs.access(file);refs++;if(fragment&&file.endsWith('.html')){const html=await fs.readFile(file,'utf8');if(!html.includes(`id="${fragment}"`))issues.push(`${from}: missing anchor ${reference}`);}}catch{issues.push(`${from}: missing ${reference}`);}
}
for(const name of ['index.html','components.html','starter.html','cadence-rain.html']){
  const file=path.join(root,name);const html=await fs.readFile(file,'utf8');
  const ids=[...html.matchAll(/\bid="([^"\s]+)"/g)].map(m=>m[1]);
  const repeated=[...new Set(ids.filter((id,i)=>ids.indexOf(id)!==i))];
  if(repeated.length)issues.push(`${name}: duplicate IDs ${repeated.join(', ')}`);
  for(const match of html.matchAll(/\b(?:src|href)="([^"\s]+)"/g))await check(file,match[1]);
  for(const match of html.matchAll(/\bsrcset="([^"]+)"/g))for(const candidate of match[1].split(','))await check(file,candidate.trim().split(/\s+/)[0]);
  for(const match of html.matchAll(/\baria-(?:controls|labelledby|describedby)="([^"]+)"/g))for(const id of match[1].split(' '))if(!ids.includes(id))issues.push(`${name}: missing ARIA target ${id}`);
}
for(const name of await fs.readdir(path.join(root,'assets/css'))){
  const file=path.join(root,'assets/css',name);const css=await fs.readFile(file,'utf8');
  for(const match of css.matchAll(/url\(\s*(['"]?)([^)'"\s]+)\1\s*\)/g))await check(file,match[2]);
  if(/@apply\s|@reference\s/.test(css.replace(/\/\*[\s\S]*?\*\//g,'')))issues.push(`${name}: uncompiled Tailwind directive`);
}
// Lazy-loaded local scene and SDK must travel with the package too.
for(const file of ['assets/js/aurora.js','assets/css/aurora.css','assets/js/aura-scene.js','assets/vendor/unicornStudio.umd.js','assets/source/aura-default.json','AGENTS.md','tokens.json'])await check(path.join(root,'index.html'),file);
for(const name of ['index.html','starter.html']){
  const html=await fs.readFile(path.join(root,name),'utf8');
  if(!html.includes('data-aura')||html.includes('data-rain'))issues.push(`${name}: Aurora must be the default background`);
  if(!html.includes('aura-background--composite')||!html.includes('class="landscape-layer__image"'))issues.push(`${name}: default background must include the original landscape composition`);
}
const components=await fs.readFile(path.join(root,'components.html'),'utf8');
if(/Copiar HTML|\bdata-copy=/.test(components))issues.push('components.html: HTML copy buttons must not return');
if(/EDITORIAL LEGADO|Tipografia editorial|class="space-scale"/.test(components))issues.push('components.html: removed editorial and spacing demonstrations must not return');
const componentShell=components.split('<main id="main">')[0];
if(!componentShell.includes('class="aura-background aura-background--composite" data-aura')||!componentShell.includes('class="landscape-layer__image"'))issues.push('components.html: page background must include Aura and the original landscape');
if(componentShell.includes('data-rain'))issues.push('components.html: Cadence Rain must remain a preview, not the page background');
if((components.match(/data-theme-select/g)||[]).length!==1||!components.includes('id="component-theme"'))issues.push('components.html: expected one global color selector');
if(!/<header class="ds-nav">[\s\S]*?id="component-theme"[\s\S]*?<\/header>/.test(components))issues.push('components.html: global color selector must be inside the sticky navbar');
if(components.includes('id="background-theme"'))issues.push('components.html: background must inherit the global palette');
if(!/<select id="component-theme"[^>]*>\s*<option value="teal_asimov">/.test(components))issues.push('components.html: Asimov must be the default palette');
const colorSelect=components.match(/<select id="component-theme"[^>]*>([\s\S]*?)<\/select>/)?.[1]||'';
const colorOptions=[...colorSelect.matchAll(/<option value="([^"]+)">([^<]+)<\/option>/g)];
if(colorOptions.map(match=>match[2]).join(',')!=='Teal,Ciano,Laranja,Azul,Vermelho,Verde,Terracota,Roxo')issues.push('components.html: expected consolidated color names, not campaign identifiers');
const themeTokens=JSON.parse(await fs.readFile(path.join(root,'tokens.json'),'utf8')).themes;
const colorValues=colorOptions.map(match=>themeTokens[match[1]]?.accent);
if(colorValues.includes(undefined)||new Set(colorValues).size!==colorValues.length)issues.push('components.html: color selector must use valid, unique accent colors');
if(/--card-accent:#[\da-f]+/i.test(components))issues.push('components.html: demo course cards must inherit the global palette');
const cadenceLayout=await fs.readFile(path.join(root,'cadence-rain.html'),'utf8');
if(!cadenceLayout.includes('class="cadence-rain-bg" data-rain')||cadenceLayout.includes('data-aura'))issues.push('cadence-rain.html: alternative layout must use only Cadence Rain');
if(!cadenceLayout.includes('data-dashboard'))issues.push('cadence-rain.html: workspace example must include the interactive dashboard');
const home=await fs.readFile(path.join(root,'index.html'),'utf8');
if(!home.includes('href="cadence-rain.html"'))issues.push('index.html: missing link to the Cadence Rain layout');
for(const name of ['index.html','cadence-rain.html','starter.html']){
  const html=await fs.readFile(path.join(root,name),'utf8');
  if((html.match(/data-theme-select/g)||[]).length!==1||!/<header class="ds-nav">[\s\S]*?data-theme-select[\s\S]*?<\/header>/.test(html))issues.push(`${name}: expected one color selector in the sticky navbar`);
  if(!html.includes('<body class="library-themed">'))issues.push(`${name}: missing shared theme and responsive navbar styles`);
  if((html.match(/<select id="component-theme"[^>]*>([\s\S]*?)<\/select>/)?.[1]||'')!==colorSelect)issues.push(`${name}: color options and Asimov default must match Components`);
  if(/--card-accent:#[\da-f]+/i.test(html))issues.push(`${name}: example cards must inherit the global palette`);
}
if(components.includes('id="background-kind"'))issues.push('components.html: backgrounds must be rendered separately, not hidden behind a selector');
const backgroundExamples=[...components.matchAll(/<div class="specimen background-example" data-background-example="([^"]+)">([\s\S]*?)<template id="([^"]+)" data-snippet>/g)];
if(backgroundExamples.map(match=>match[1]).join(',')!=='aura-landscape,rain,aura,landscape')issues.push('components.html: expected four separate background previews in order');
for(const [,kind,preview] of backgroundExamples){
  if(!preview.includes('data-background-preview')||/\shidden(?:[\s>])/.test(preview))issues.push(`components.html: ${kind} preview must render immediately`);
  const hasAura=preview.includes('data-aura'),hasRain=preview.includes('data-rain '),hasLandscape=preview.includes('class="landscape-layer"');
  if(hasAura!==['aura-landscape','aura'].includes(kind)||hasRain!==(kind==='rain')||hasLandscape!==['aura-landscape','landscape'].includes(kind))issues.push(`components.html: incorrect layers for ${kind}`);
}
if((components.match(/data-background-pause/g)||[]).length!==3)issues.push('components.html: animated backgrounds must each have their own pause control');
for(const id of ['home-background-snippet','rain-snippet','aurora-snippet','landscape-snippet'])if(!components.includes(`<template id="${id}" data-snippet>`))issues.push(`components.html: missing reusable background ${id}`);
for(const name of ['index.html','components.html','starter.html','cadence-rain.html','assets/js/system.js','AGENTS.md']){
  const content=await fs.readFile(path.join(root,name),'utf8');
  if(/data-spark|spark\.js|AsimovSpark|spark-host/.test(content))issues.push(`${name}: retired particle effect is still referenced`);
}
if(issues.length){console.error(issues.join('\n'));process.exitCode=1;}else console.log(`PASS: ${refs} local references, unique IDs, ARIA targets, compiled CSS and portable effects.`);
