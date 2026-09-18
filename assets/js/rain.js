/* Portable Cadence adapter. Shader and layered CSS are the original project assets.
 * API: AsimovRain.mount(element) -> { refresh(), pause(bool), destroy() }
 * A root with data-rain is mounted automatically. No imports, network or build. */
(function () {
  'use strict';
  const instances = new Map();
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const streaks = [[8,5,90,3.5,0],[20,72,60,4.2,1.2],[45,10,70,3.8,2.8],[5,40,50,4.5,.7],[30,82,85,3.2,2],[60,25,55,5,3.5],[12,58,75,3.9,1.8],[38,33,65,4.1,.4],[52,68,48,3.6,2.4],[72,12,80,4.8,1.1],[18,22,58,3.3,3.2],[65,48,72,4.4,.9],[28,8,44,3.1,2.6],[78,78,62,4.6,1.5],[42,88,52,3.7,3.8],[55,3,68,4.3,.2],[85,35,56,3.4,2.1],[15,92,42,4.9,3]];
  function mount(root) {
    if (instances.has(root)) return instances.get(root);
    root.classList.add('cadence-rain-bg');
    root.setAttribute('aria-hidden','true');
    const canvas = document.createElement('canvas');
    canvas.className = 'cadence-rain-bg__canvas';
    root.append(canvas);
    const layers = document.createElement('div');
    layers.innerHTML = '<div class="cadence-rain-bg__orbs">'+[1,2,3].map(i=>'<div class="cadence-rain-bg__orb cadence-rain-bg__orb--'+i+'"></div>').join('')+'</div><div class="cadence-rain-bg__stars">'+streaks.map(([top,left,w,d,delay])=>'<div class="cadence-rain-bg__star" style="top:'+top+'%;left:'+left+'%;width:'+w+'px;animation-duration:'+d+'s;animation-delay:-'+delay+'s"></div>').join('')+'</div><div class="cadence-rain-bg__fade"></div><div class="cadence-rain-bg__lighten"></div><div class="cadence-rain-bg__accent-glow"></div>';
    root.append(layers);
    let gl, program, buffer, shaders=[], raf=0, visible=true, paused=false, last=0, elapsed=0, previous=0, disposed=false;
    let colors=[], intensity=1, alpha=.5, glow=.12, uniforms={};
    const number=(style,key,fallback)=>{const n=parseFloat(style.getPropertyValue(key));return Number.isFinite(n)?n:fallback;};
    const rgb=hex=>{const h=hex.trim().replace('#','');return /^[\da-f]{6}$/i.test(h)?[0,2,4].map(i=>parseInt(h.slice(i,i+2),16)/255):[.05,.58,.51];};
    function refresh(){const style=getComputedStyle(root);colors=['--ui-accent-dark','--ui-accent','--ui-accent-light'].map(k=>rgb(style.getPropertyValue(k)));intensity=number(style,'--cadence-rain-shader-intensity',1);alpha=number(style,'--cadence-rain-shader-alpha',.5);glow=number(style,'--cadence-rain-center-glow',.12);if(gl) draw();}
    function draw(){if(!gl||!program||gl.isContextLost())return;gl.viewport(0,0,canvas.width,canvas.height);gl.clearColor(0,0,0,0);gl.clear(gl.COLOR_BUFFER_BIT);gl.useProgram(program);gl.uniform1f(uniforms.u_t,elapsed);gl.uniform2f(uniforms.u_r,canvas.width,canvas.height);colors.forEach((c,i)=>gl.uniform3fv(uniforms['u_c'+(i+1)],c));gl.uniform1f(uniforms.u_intensity,intensity);gl.uniform1f(uniforms.u_alpha,alpha);gl.uniform1f(uniforms.u_center_glow,glow);gl.drawArrays(gl.TRIANGLE_STRIP,0,4);root.dataset.webglReady='true';}
    function size(){const dpr=Math.min(devicePixelRatio||1,1.5);canvas.width=Math.max(1,Math.round(root.clientWidth*dpr));canvas.height=Math.max(1,Math.round(root.clientHeight*dpr));draw();}
    function frame(t){raf=0;if(disposed||paused||reduced.matches||document.hidden||!visible||!gl)return;if(t-last>=1000/30){elapsed+=previous?Math.min((t-previous)/1000,.1):0;previous=t;last=t;draw();}raf=requestAnimationFrame(frame);}
    function sync(){cancelAnimationFrame(raf);raf=0;previous=0;const stop=paused||reduced.matches||document.hidden||!visible;root.classList.toggle('cadence-rain-bg--css-paused',stop);root.classList.toggle('cadence-rain-bg--reduced-motion',reduced.matches);if(!stop&&gl)raf=requestAnimationFrame(frame);}
    function init(){if(gl||reduced.matches)return;try{gl=canvas.getContext('webgl',{alpha:true,antialias:false,premultipliedAlpha:false});if(!gl)throw new Error('WebGL unavailable');program=gl.createProgram();for(const [type,src] of [[gl.VERTEX_SHADER,window.AsimovRainShaders.vertex],[gl.FRAGMENT_SHADER,window.AsimovRainShaders.fragment]]){const shader=gl.createShader(type);gl.shaderSource(shader,src);gl.compileShader(shader);if(!gl.getShaderParameter(shader,gl.COMPILE_STATUS))throw new Error(gl.getShaderInfoLog(shader));shaders.push(shader);gl.attachShader(program,shader);}gl.linkProgram(program);if(!gl.getProgramParameter(program,gl.LINK_STATUS))throw new Error(gl.getProgramInfoLog(program));gl.useProgram(program);buffer=gl.createBuffer();gl.bindBuffer(gl.ARRAY_BUFFER,buffer);gl.bufferData(gl.ARRAY_BUFFER,new Float32Array([-1,-1,1,-1,-1,1,1,1]),gl.STATIC_DRAW);const pos=gl.getAttribLocation(program,'p');gl.enableVertexAttribArray(pos);gl.vertexAttribPointer(pos,2,gl.FLOAT,false,0,0);['u_t','u_r','u_c1','u_c2','u_c3','u_intensity','u_alpha','u_center_glow'].forEach(k=>uniforms[k]=gl.getUniformLocation(program,k));gl.enable(gl.BLEND);gl.blendFunc(gl.SRC_ALPHA,gl.ONE);root.classList.remove('cadence-rain-bg--no-webgl');refresh();size();}catch(error){root.classList.add('cadence-rain-bg--no-webgl');root.dataset.webglReady='false';if(gl){shaders.forEach(s=>gl.deleteShader(s));if(program)gl.deleteProgram(program);if(buffer)gl.deleteBuffer(buffer);}gl=null;}}
    function motionChange(){if(!reduced.matches)init();sync();}
    function lost(event){event.preventDefault();cancelAnimationFrame(raf);root.classList.add('cadence-rain-bg--no-webgl');root.dataset.webglReady='false';}
    function restored(){gl=null;shaders=[];init();sync();}
    const ro=new ResizeObserver(size);ro.observe(root);
    const io=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;sync();});io.observe(root);
    reduced.addEventListener('change',motionChange);document.addEventListener('visibilitychange',sync);canvas.addEventListener('webglcontextlost',lost);canvas.addEventListener('webglcontextrestored',restored);
    const api={refresh,pause(value=true){paused=value;sync();},destroy(){disposed=true;cancelAnimationFrame(raf);ro.disconnect();io.disconnect();reduced.removeEventListener('change',motionChange);document.removeEventListener('visibilitychange',sync);canvas.removeEventListener('webglcontextlost',lost);canvas.removeEventListener('webglcontextrestored',restored);if(gl){shaders.forEach(s=>gl.deleteShader(s));gl.deleteBuffer(buffer);gl.deleteProgram(program);}canvas.remove();layers.remove();instances.delete(root);delete root.dataset.webglReady;}};
    instances.set(root,api);refresh();init();sync();return api;
  }
  window.AsimovRain={mount,instances};
  document.querySelectorAll('[data-rain]').forEach(mount);
})();
