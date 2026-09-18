/* Asimov Design System — local interactions. No analytics, APIs or remote assets.
 * Plain deferred script, compatible with file:// and arbitrary subdirectories. */
(function () {
  'use strict';
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  document.documentElement.classList.add('js');
  const $ = (selector, scope=document) => scope.querySelector(selector);
  const $$ = (selector, scope=document) => [...scope.querySelectorAll(selector)];
  let toastTimer;
  function toast(message){const el=$('#toast');if(!el)return;clearTimeout(toastTimer);el.textContent=message;el.classList.add('is-visible');toastTimer=setTimeout(()=>el.classList.remove('is-visible'),3200);}
  function dialog(title,description){const el=$('#demo-dialog');if(!el)return;$('#dialog-title',el).textContent=title;$('[data-dialog-copy]',el).textContent=description||'Este é um componente de demonstração. Conecte esta ação à lógica do seu produto.';el.showModal();}
  async function copyText(value){try{if(navigator.clipboard&&window.isSecureContext){await navigator.clipboard.writeText(value);}else{const field=document.createElement('textarea');field.value=value;field.style.cssText='position:fixed;left:-9999px;top:0';document.body.append(field);const previous=document.activeElement;field.select();const ok=document.execCommand('copy');field.remove();previous?.focus();if(!ok)throw new Error('copy unavailable');}toast('Copiado. Pronto para usar no seu projeto.');}catch{dialog('Copie o conteúdo abaixo',value);}}
  document.addEventListener('click',event=>{
    const el=event.target.closest('button,a');if(!el)return;
    if(el.hasAttribute('data-copy-text'))copyText(el.dataset.copyText);
    if(el.dataset.copyToken)copyText(getComputedStyle(document.documentElement).getPropertyValue(el.dataset.copyToken).trim());
    if(el.dataset.toast){toast(el.dataset.toast);el.closest('details.demo-dropdown')?.removeAttribute('open');}
    if(el.dataset.dialog){event.preventDefault();dialog(el.dataset.dialog,el.classList.contains('help-fab')?'Explore Layouts para ver a identidade em contexto. Em Components, consulte os exemplos e experimente as interações. O guia para IA está no arquivo AGENTS.md; o modelo inicial está em starter.html.':undefined);}
    if(el.hasAttribute('data-close-dialog'))$('#demo-dialog')?.close();
    if(el.dataset.plan)dialog('Plano '+el.dataset.plan,'Esta seleção demonstra o fluxo de um plano. Os preços são ilustrativos e não há checkout ou cobrança neste design system.');
    if(el.getAttribute('role')==='switch')el.setAttribute('aria-checked',String(el.getAttribute('aria-checked')!=='true'));
    if(el.dataset.page){const parent=el.closest('.pagination');$$('[data-page]',parent).forEach(btn=>btn.removeAttribute('aria-current'));el.setAttribute('aria-current','page');$('[data-page-status]',parent).textContent='Página '+el.dataset.page+' selecionada';toast('Página '+el.dataset.page+' selecionada no exemplo de paginação.');}
    if(el.hasAttribute('data-loading-button')){const original=el.innerHTML;el.disabled=true;el.setAttribute('aria-busy','true');el.innerHTML='<span class="spinner" aria-hidden="true"></span> Salvando…';setTimeout(()=>{el.innerHTML=original;el.disabled=false;el.removeAttribute('aria-busy');toast('Alterações de demonstração salvas.');},900);}
  });
  const modal=$('#demo-dialog');
  modal?.addEventListener('click',event=>{if(event.target===modal){const r=modal.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)modal.close();}});
  document.addEventListener('click',event=>$$('.demo-dropdown[open]').forEach(menu=>{if(!menu.contains(event.target))menu.open=false;}));
  document.addEventListener('keydown',event=>{if(event.key==='Escape')$$('.demo-dropdown[open]').forEach(menu=>{menu.open=false;$('summary',menu)?.focus();});});

  // Only offscreen sections are hidden; HTML remains readable without JavaScript.
  const observer = new IntersectionObserver(entries=>entries.forEach(entry=>{if(entry.isIntersecting){entry.target.removeAttribute('data-reveal-pending');entry.target.classList.add('in-view');observer.unobserve(entry.target);}}),{threshold:.06});
  $$('.reveal').forEach(el=>{if(!reduced.matches&&el.getBoundingClientRect().top>innerHeight)el.setAttribute('data-reveal-pending','');observer.observe(el);});
  $('[data-replay]')?.addEventListener('click',()=>{$$('[data-replay-target]').forEach(el=>{el.classList.remove('replay-demo');void el.offsetWidth;el.classList.add('replay-demo');});});

  // Accordion retains the original grid-template-rows animation.
  $$('.faq-trigger').forEach(trigger=>trigger.addEventListener('click',()=>{const item=trigger.closest('.faq-item');const open=trigger.getAttribute('aria-expanded')!=='true';trigger.setAttribute('aria-expanded',String(open));item.classList.toggle('is-open',open);document.getElementById(trigger.getAttribute('aria-controls')).inert=!open;}));
  function activateTab(button){const list=button.closest('[role="tablist"]');$$('[role="tab"]',list).forEach(tab=>{const active=tab===button;tab.setAttribute('aria-selected',String(active));tab.tabIndex=active?0:-1;if(list.closest('[data-tabs]'))document.getElementById(tab.getAttribute('aria-controls')).hidden=!active;});}
  $$('[role="tablist"]').forEach(list=>{list.addEventListener('keydown',event=>{const tabs=$$('[role="tab"]',list);let n=tabs.indexOf(document.activeElement);if(n<0)return;if(event.key==='ArrowRight'||event.key==='ArrowDown')n=(n+1)%tabs.length;else if(event.key==='ArrowLeft'||event.key==='ArrowUp')n=(n-1+tabs.length)%tabs.length;else if(event.key==='Home')n=0;else if(event.key==='End')n=tabs.length-1;else return;event.preventDefault();tabs[n].focus();tabs[n].click();});});
  $$('[data-tabs] [role="tab"]').forEach(button=>button.addEventListener('click',()=>activateTab(button)));
  $$('[data-carousel-next],[data-carousel-prev]').forEach(button=>button.addEventListener('click',()=>{const strip=$('.instructor-strip',button.closest('.instructors-section'));strip.scrollBy({left:button.hasAttribute('data-carousel-next')?256:-256,behavior:reduced.matches?'instant':'smooth'});}));

  $$('[data-pricing]').forEach(root=>$$('[data-billing]',root).forEach(button=>button.addEventListener('click',()=>{const annual=button.dataset.billing==='annual';$$('[data-billing]',root).forEach(btn=>btn.setAttribute('aria-pressed',String(btn===button)));$$('[data-monthly]',root).forEach(price=>price.textContent=annual?price.dataset.annual:price.dataset.monthly);$$('[data-billing-note]',root).forEach(note=>note.textContent=annual?'Cobrado anualmente · valor ilustrativo':'Cobrado mensalmente · valor ilustrativo');})));
  const chartScenarios={
    '7':{values:['840','32','91,2%'],labels:['Seg','Ter','Qua','Qui','Sex','Sáb'],path:'M0 155 C40 160 70 140 100 135 S160 120 200 125 S260 80 300 90 S355 60 400 68 S480 30 500 40 S570 35 600 24',max:1000,end:'840'},
    '30':{values:['2.840','128','94,8%'],labels:['01 set','06 set','11 set','16 set','21 set','26 set'],path:'M0 145 C30 145 35 122 65 128 S100 144 125 105 S170 125 200 91 S230 97 260 73 S300 105 325 63 S370 80 400 51 S455 75 480 35 S520 40 550 20 S585 28 600 10',max:3000,end:'2.840'},
    '90':{values:['8.420','386','96,4%'],labels:['Jul 01','Jul 16','Ago 01','Ago 16','Set 01','Set 30'],path:'M0 164 C40 158 60 153 100 151 S150 122 200 128 S260 111 300 115 S350 90 400 96 S465 72 500 64 S555 32 600 14',max:9000,end:'8.420'}
  };
  $$('[data-dashboard]').forEach(root=>{
    $$('[data-period]',root).forEach(button=>button.addEventListener('click',()=>{const s=chartScenarios[button.dataset.period];$$('[data-period]',root).forEach(b=>b.setAttribute('aria-pressed',String(b===button)));$$('[data-metric]',root).forEach((el,i)=>el.textContent=s.values[i]);$('[data-chart-line]',root).setAttribute('d',s.path);$('[data-chart-area]',root).setAttribute('d',s.path+' V180 H0Z');$$('[data-chart-labels] span',root).forEach((el,i)=>el.textContent=s.labels[i]);$$('.chart-scale span',root).forEach((el,i)=>el.textContent=Math.round(s.max*(3-i)/3).toLocaleString('pt-BR'));$('.chart-svg',root).setAttribute('aria-label',`Gráfico ilustrativo de crescimento: ${s.end} alunos ativos em ${button.dataset.period} dias.`);}));
    $$('[data-dashboard-view]',root).forEach(button=>button.addEventListener('click',()=>{activateTab(button);const view=button.dataset.dashboardView;$('.dashboard-body',root).setAttribute('aria-labelledby',button.id);$('[data-dashboard-chart]',root).hidden=view!=='overview';$('[data-dashboard-table]',root).hidden=view!=='projects';$('[data-dashboard-team]',root).hidden=view!=='team';$('[data-dashboard-title]',root).textContent={overview:'Visão geral do workspace',projects:'Projetos do workspace',team:'Membros do workspace'}[view];$('[data-dashboard-subtitle]',root).textContent={overview:'Indicadores do período selecionado.',projects:'Acompanhe o progresso dos seus projetos.',team:'Membros e participação no workspace.'}[view];}));
  });

  $$('[data-demo-form]').forEach(form=>form.addEventListener('submit',event=>{event.preventDefault();let firstInvalid;$$('input[required]',form).forEach(input=>{const invalid=!input.validity.valid||(input.name==='project'&&input.value.trim().length<3);input.setAttribute('aria-invalid',String(invalid));const help=document.getElementById(input.getAttribute('aria-describedby'));help.classList.toggle('error',invalid);help.textContent=input.name==='project'?(invalid?'Digite pelo menos 3 caracteres.':'Nome válido.'):(invalid?'Digite um e-mail válido.':'E-mail válido.');if(invalid&&!firstInvalid)firstInvalid=input;});const status=$('[data-form-status]',form);status.hidden=false;if(firstInvalid){status.textContent='Revise os campos indicados para continuar.';status.style.color='var(--danger)';firstInvalid.focus();}else{status.textContent='Projeto de exemplo criado. Esta demonstração não armazena nem envia os dados.';status.style.color='var(--ui-accent-light)';toast('Pronto! Formulário validado localmente.');}}));

  function applyTheme(root,key){const theme=window.AsimovThemes[key];if(!theme)return;Object.entries(theme).forEach(([token,value])=>root.style.setProperty('--ui-'+token,value));const hex=theme.accent.slice(1);root.style.setProperty('--ui-accent-rgb-space',[0,2,4].map(i=>parseInt(hex.slice(i,i+2),16)).join(' '));window.AsimovRain?.instances.forEach(api=>api.refresh());window.AsimovAurora?.instances.forEach(api=>api.refresh());}
  $$('[data-theme-select]').forEach(select=>{
    const update=()=>{
      applyTheme(document.documentElement,select.value);
      $$('[data-token-label]').forEach(el=>el.textContent=getComputedStyle(document.documentElement).getPropertyValue(el.dataset.tokenLabel).trim());
      const status=$('[data-theme-status]');
      if(status)status.textContent='Tema: '+select.selectedOptions[0].textContent;
    };
    select.value='teal_asimov';
    update();
    select.addEventListener('change',update);
  });
  const normal=s=>s.normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const search=$('#component-search');
  if(search){const sections=$$('[data-library-section]').map(el=>({el,text:normal(el.textContent)}));search.addEventListener('input',()=>{const q=normal(search.value.trim());let hits=0;sections.forEach(({el,text})=>{const show=!q||text.includes(q);el.hidden=!show;if(show)hits++;const link=$(`.library-sidebar a[href="#${el.id}"]`);if(link)link.hidden=!show;});$('#library-no-results').hidden=hits!==0;});const tracker=new IntersectionObserver(entries=>{for(const entry of entries){if(!entry.isIntersecting)continue;$$('.library-sidebar a').forEach(a=>{if(a.hash==='#'+entry.target.id)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});}},{rootMargin:'-90px 0px -65% 0px'});sections.forEach(({el})=>tracker.observe(el));}

  reduced.addEventListener('change',()=>{if(reduced.matches)$$('[data-reveal-pending]').forEach(el=>el.removeAttribute('data-reveal-pending'));});

  $$('[data-background-example]').forEach(example=>{
    const kind=example.dataset.backgroundExample;
    const root=$('[data-aura],[data-rain]',example);
    const toggle=$('[data-background-pause]',example);
    const status=$('[data-background-status]',example);
    const title=$('.background-lab__copy h3',example).textContent;
    let paused=false;
    const api=()=>kind==='rain'?window.AsimovRain?.instances.get(root):window.AsimovAurora?.instances.get(root);
    function updateStatus(){
      if(kind==='landscape'){status.textContent='Imagem original · transparência, gradiente e glow · sem animação.';return;}
      if(reduced.matches){status.textContent='Movimento reduzido ativo: composição estática, sem animação WebGL.';return;}
      if(paused){status.textContent='Animação pausada.';return;}
      if(kind==='rain'){status.textContent=root.dataset.webglReady==='false'?'WebGL indisponível neste dispositivo. Camadas de fallback preservadas.':'Cadence Rain · shader original · 30 fps · pausa fora da área visível.';return;}
      const state=root.dataset.auraStatus;
      status.textContent=state==='fallback'?'Aurora indisponível neste dispositivo. Iluminação estática preservada.':state==='running'?'Aura · Unicorn Studio local · 30 fps'+(kind==='aura-landscape'?' · paisagem original mesclada.':' · sem imagem.'):state==='paused'||state==='idle'?'Aurora em espera fora da área visível.':'Aurora boreal · carregando a cena local…';
    }
    function sync(){
      if(toggle){
        toggle.disabled=reduced.matches;
        toggle.setAttribute('aria-pressed',String(paused));
        toggle.textContent=paused?'Retomar':'Pausar';
        toggle.setAttribute('aria-label',(paused?'Retomar ':'Pausar ')+title);
        api()?.pause(paused);
      }
      updateStatus();
    }
    toggle?.addEventListener('click',()=>{paused=!paused;sync();});
    $('[data-rain-intensity]',example)?.addEventListener('input',event=>{
      $('[data-intensity-output]',example).value=Number(event.target.value).toFixed(1);
      root.style.setProperty('--cadence-rain-shader-intensity',event.target.value);
      api()?.refresh();
    });
    example.addEventListener('asimov:aurora-status',updateStatus);
    reduced.addEventListener('change',sync);
    document.addEventListener('visibilitychange',updateStatus);
    sync();
  });

  $$('[data-countdown]').forEach(root=>{const end=Date.now()+Number(root.dataset.seconds)*1000;const tick=()=>{const n=Math.max(0,Math.ceil((end-Date.now())/1000));const values=[Math.floor(n/86400),Math.floor(n/3600)%24,Math.floor(n/60)%60,n%60];$$('span',root).forEach((el,i)=>el.textContent=String(values[i]).padStart(2,'0')+['d','h','m','s'][i]);if(n===0)clearInterval(timer);};const timer=setInterval(tick,1000);tick();});
  window.AsimovDS={applyTheme,toast,dialog,copyText};
})();
