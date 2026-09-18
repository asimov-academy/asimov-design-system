/**
 * Aurora WebGL Cadence (cadence-landing-19) — sem interação de cursor.
 * Baseado em lp.asimov.academy/templates/cadence-landing-19.aura.build/assets/js/interactions.js
 */
const VERT = `attribute vec2 p;void main(){gl_Position=vec4(p,0,1);}`;

const FRAG = `
precision highp float;
uniform float u_t;
uniform vec2 u_r;
uniform vec3 u_c1;
uniform vec3 u_c2;
uniform vec3 u_c3;
uniform float u_intensity;
uniform float u_alpha;
uniform float u_center_glow;

vec3 mod289(vec3 x){return x-floor(x*(1./289.))*289.;}
vec4 mod289(vec4 x){return x-floor(x*(1./289.))*289.;}
vec4 perm(vec4 x){return mod289(((x*34.)+1.)*x);}
float snoise(vec3 v){
  const vec2 C=vec2(1./6.,1./3.);
  const vec4 D=vec4(0,.5,1,2);
  vec3 i=floor(v+dot(v,C.yyy));
  vec3 x0=v-i+dot(i,C.xxx);
  vec3 g=step(x0.yzx,x0.xyz);
  vec3 l=1.-g;
  vec3 i1=min(g,l.zxy);
  vec3 i2=max(g,l.zxy);
  vec3 x1=x0-i1+C.xxx;
  vec3 x2=x0-i2+C.yyy;
  vec3 x3=x0-D.yyy;
  i=mod289(i);
  vec4 p=perm(perm(perm(i.z+vec4(0,i1.z,i2.z,1))+i.y+vec4(0,i1.y,i2.y,1))+i.x+vec4(0,i1.x,i2.x,1));
  float n_=1./7.;
  vec3 ns=n_*D.wyz-D.xzx;
  vec4 j=p-49.*floor(p*ns.z*ns.z);
  vec4 x_=floor(j*ns.z);
  vec4 y_=floor(j-7.*x_);
  vec4 x=x_*ns.x+ns.yyyy;
  vec4 y=y_*ns.x+ns.yyyy;
  vec4 h=1.-abs(x)-abs(y);
  vec4 b0=vec4(x.xy,y.xy);
  vec4 b1=vec4(x.zw,y.zw);
  vec4 s0=floor(b0)*2.+1.;
  vec4 s1=floor(b1)*2.+1.;
  vec4 sh=-step(h,vec4(0));
  vec4 a0=b0.xzyw+s0.xzyw*sh.xxyy;
  vec4 a1=b1.xzyw+s1.xzyw*sh.zzww;
  vec3 p0=vec3(a0.xy,h.x);
  vec3 p1=vec3(a0.zw,h.y);
  vec3 p2=vec3(a1.xy,h.z);
  vec3 p3=vec3(a1.zw,h.w);
  vec4 norm=1.79284291400159-.85373472095314*vec4(dot(p0,p0),dot(p1,p1),dot(p2,p2),dot(p3,p3));
  p0*=norm.x;p1*=norm.y;p2*=norm.z;p3*=norm.w;
  vec4 m=max(.6-vec4(dot(x0,x0),dot(x1,x1),dot(x2,x2),dot(x3,x3)),0.);
  m=m*m;
  return 42.*dot(m*m,vec4(dot(p0,x0),dot(p1,x1),dot(p2,x2),dot(p3,x3)));
}

float fbm(vec3 p){
  float v=0.,a=.5;
  for(int i=0;i<5;i++){
    v+=a*snoise(p);
    p*=2.1;
    a*=.48;
  }
  return v;
}

void main(){
  vec2 uv=(gl_FragCoord.xy)/u_r;
  vec2 p=uv*2.-1.;
  p.x*=u_r.x/u_r.y;

  float t=u_t*0.25;
  float n1=fbm(vec3(p*1.2+vec2(t*0.4,t*0.3),t*0.2));
  float n2=fbm(vec3(p*2.5+vec2(-t*0.6,t*0.5),t*0.35+5.));
  float wave=sin(length(p)*4.0-t*2.0)*0.5+0.5;
  float n4=fbm(vec3(p*0.8+vec2(t*0.2,-t*0.15),t*0.1+20.))*wave;

  float n=n1*0.55+n2*0.3+n4*0.35;

  vec3 c1=u_c1;
  vec3 c2=u_c2;
  vec3 c3=u_c3;

  float intensity=smoothstep(-0.2,0.8,n);
  vec3 col=mix(c1,c2,intensity);
  col=mix(col,c3,smoothstep(0.5,1.0,intensity)*0.6);

  float vig=1.-smoothstep(0.4,1.5,length(uv*2.-1.));
  float alpha=intensity*u_alpha*u_intensity*vig;
  float centerGlow=exp(-dot(p,p)*0.6)*u_center_glow*u_intensity;
  alpha+=centerGlow;

  gl_FragColor=vec4(col,alpha);
}
`;

export type CadenceRainPerfOptions = {
  /** Cap de devicePixelRatio do canvas. Default 1.5 (comportamento atual). */
  maxDpr?: number;
  /** Pausa rAF quando a aba está oculta. Default false. */
  pauseWhenHidden?: boolean;
  /**
   * Opt-in: CSS selector do âncora (ex. `#hero`). Anima só enquanto intersecta a viewport.
   * Não observar o root `position:fixed` do fundo. Default undefined = sempre anima.
   */
  activeWhenSelector?: string;
  /**
   * Com `activeWhenSelector`: `stop` = 0 rAF fora do âncora (último frame); `throttle` = ~30 FPS.
   * Default `stop`.
   */
  outsideMode?: 'stop' | 'throttle';
  /** FPS alvo no modo throttle. Default 30. */
  outsideFps?: number;
  /**
   * Opt-in: teto de FPS mesmo com âncora visível (repouso desktop / INP).
   * Default undefined = sem teto (legado full rAF).
   */
  maxFps?: number;
};

function prefersReducedMotion() {
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}

function hexToVec3(hex: string): [number, number, number] {
  const h = hex.replace('#', '').trim();
  if (h.length !== 6) return [0.05, 0.58, 0.51];
  return [
    parseInt(h.slice(0, 2), 16) / 255,
    parseInt(h.slice(2, 4), 16) / 255,
    parseInt(h.slice(4, 6), 16) / 255,
  ];
}

function readCssNumber(el: Element, prop: string, fallback: number): number {
  const raw = getComputedStyle(el).getPropertyValue(prop).trim();
  const value = parseFloat(raw);
  return Number.isFinite(value) ? value : fallback;
}

function readThemeColors(root: Element): [number, number, number][] {
  const style = getComputedStyle(root);
  return [
    hexToVec3(style.getPropertyValue('--ui-accent-dark')),
    hexToVec3(style.getPropertyValue('--ui-accent')),
    hexToVec3(style.getPropertyValue('--ui-accent-light')),
  ];
}

function readPerfFromRoot(root: HTMLElement): Required<
  Pick<CadenceRainPerfOptions, 'maxDpr' | 'pauseWhenHidden' | 'outsideMode' | 'outsideFps'>
> & { activeWhenSelector: string | undefined; maxFps: number | undefined } {
  const maxDprRaw = parseFloat(root.dataset.maxDpr || '');
  const outsideFpsRaw = parseFloat(root.dataset.outsideFps || '');
  const maxFpsRaw = parseFloat(root.dataset.maxFps || '');
  const mode = root.dataset.outsideMode;
  return {
    maxDpr: Number.isFinite(maxDprRaw) && maxDprRaw > 0 ? maxDprRaw : 1.5,
    pauseWhenHidden: root.dataset.pauseHidden === '1',
    activeWhenSelector: root.dataset.activeWhen?.trim() || undefined,
    outsideMode: mode === 'throttle' ? 'throttle' : 'stop',
    outsideFps: Number.isFinite(outsideFpsRaw) && outsideFpsRaw > 0 ? outsideFpsRaw : 30,
    maxFps: Number.isFinite(maxFpsRaw) && maxFpsRaw > 0 ? maxFpsRaw : undefined,
  };
}

export function initCadenceRainBackground(
  canvasId = 'cadenceRainCanvas',
  options?: CadenceRainPerfOptions,
) {
  const canvas = document.getElementById(canvasId) as HTMLCanvasElement | null;
  if (!canvas || canvas.dataset.bound === 'true') return;
  const root = canvas.parentElement as HTMLElement | null;
  if (!root) return;

  if (prefersReducedMotion()) {
    root.classList.add('cadence-rain-bg--reduced-motion');
    return;
  }

  const gl = canvas.getContext('webgl', { alpha: true, antialias: false, premultipliedAlpha: false });
  if (!gl) {
    root.classList.add('cadence-rain-bg--no-webgl');
    return;
  }

  canvas.dataset.bound = 'true';

  const fromRoot = readPerfFromRoot(root);
  const maxDpr = options?.maxDpr ?? fromRoot.maxDpr;
  const pauseWhenHidden = options?.pauseWhenHidden ?? fromRoot.pauseWhenHidden;
  const activeWhenSelector = options?.activeWhenSelector ?? fromRoot.activeWhenSelector;
  const outsideMode = options?.outsideMode ?? fromRoot.outsideMode;
  const outsideFps = options?.outsideFps ?? fromRoot.outsideFps;
  const maxFps = options?.maxFps ?? fromRoot.maxFps;
  const throttleIntervalMs = 1000 / outsideFps;
  const maxFpsIntervalMs = maxFps && maxFps > 0 ? 1000 / maxFps : 0;

  function compile(type: number, src: string) {
    const s = gl.createShader(type)!;
    gl.shaderSource(s, src);
    gl.compileShader(s);
    return s;
  }

  const prog = gl.createProgram()!;
  gl.attachShader(prog, compile(gl.VERTEX_SHADER, VERT));
  gl.attachShader(prog, compile(gl.FRAGMENT_SHADER, FRAG));
  gl.linkProgram(prog);
  gl.useProgram(prog);

  const buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 1, -1, -1, 1, 1, 1]), gl.STATIC_DRAW);
  const pLoc = gl.getAttribLocation(prog, 'p');
  gl.enableVertexAttribArray(pLoc);
  gl.vertexAttribPointer(pLoc, 2, gl.FLOAT, false, 0, 0);

  const u_t = gl.getUniformLocation(prog, 'u_t');
  const u_r = gl.getUniformLocation(prog, 'u_r');
  const u_c1 = gl.getUniformLocation(prog, 'u_c1');
  const u_c2 = gl.getUniformLocation(prog, 'u_c2');
  const u_c3 = gl.getUniformLocation(prog, 'u_c3');
  const u_intensity = gl.getUniformLocation(prog, 'u_intensity');
  const u_alpha = gl.getUniformLocation(prog, 'u_alpha');
  const u_center_glow = gl.getUniformLocation(prog, 'u_center_glow');

  const [c1, c2, c3] = readThemeColors(root);
  const shaderIntensity = readCssNumber(root, '--cadence-rain-shader-intensity', 1);
  const shaderAlpha = readCssNumber(root, '--cadence-rain-shader-alpha', 0.32);
  const centerGlow = readCssNumber(root, '--cadence-rain-center-glow', 0.12);

  let rafId = 0;
  let throttleTimer = 0;
  let running = false;
  let pageHidden = false;
  /** true enquanto o âncora intersecta (ou quando não há seletor). */
  let anchorInView = true;
  let lastDrawTs = 0;
  /** Fade do canvas só na 1ª entrada — nunca limpa em resize/stop/retorno ao hero. */
  let webglReadyMarked = false;

  function markWebglReady() {
    if (webglReadyMarked) return;
    webglReadyMarked = true;
    root.dataset.webglReady = 'true';
  }

  let resizeTimer = 0;
  let lastCssW = -1;
  let lastCssH = -1;

  function resize() {
    const dpr = Math.min(window.devicePixelRatio || 1, maxDpr);
    const W = root.clientWidth;
    const H = root.clientHeight;
    // Evita writes + redraw quando o layout não mudou (resize debounce residual).
    if (W === lastCssW && H === lastCssH && canvas.width === Math.floor(W * dpr)) return;
    lastCssW = W;
    lastCssH = H;
    canvas.width = W * dpr;
    canvas.height = H * dpr;
    canvas.style.width = `${W}px`;
    canvas.style.height = `${H}px`;
    gl.viewport(0, 0, canvas.width, canvas.height);
    // Resize limpa o buffer — redesenha um frame estático se o loop estiver parado.
    // Não remove data-webgl-ready (evita re-fade).
    if (!running) drawOnce(performance.now());
  }

  function scheduleResize() {
    if (resizeTimer) return;
    resizeTimer = window.setTimeout(() => {
      resizeTimer = 0;
      resize();
    }, 120);
  }

  function shouldAnimateFull() {
    if (pauseWhenHidden && pageHidden) return false;
    if (activeWhenSelector && !anchorInView) return false;
    return true;
  }

  /** Aba oculta: sempre parado. Fora do hero: stop ou throttle conforme modo. */
  function shouldRunLoop() {
    if (pauseWhenHidden && pageHidden) return false;
    if (activeWhenSelector && !anchorInView && outsideMode === 'stop') return false;
    return true;
  }

  /** Pausa orbs/streaks CSS quando WebGL também deve estar parado (repouso desktop). */
  function syncCssLayers() {
    const pauseCss = !shouldAnimateFull();
    root.classList.toggle('cadence-rain-bg--css-paused', pauseCss);
  }

  function drawOnce(t: number) {
    gl.clearColor(0, 0, 0, 0);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.enable(gl.BLEND);
    gl.blendFunc(gl.SRC_ALPHA, gl.ONE);
    gl.useProgram(prog);
    gl.uniform1f(u_t, t * 0.001);
    gl.uniform2f(u_r, canvas.width, canvas.height);
    gl.uniform3f(u_c1, c1[0], c1[1], c1[2]);
    gl.uniform3f(u_c2, c2[0], c2[1], c2[2]);
    gl.uniform3f(u_c3, c3[0], c3[1], c3[2]);
    gl.uniform1f(u_intensity, shaderIntensity);
    gl.uniform1f(u_alpha, shaderAlpha);
    gl.uniform1f(u_center_glow, centerGlow);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
    lastDrawTs = t;
    // Só após desenho real — fallback CSS permanece; fade uma única vez.
    markWebglReady();
  }

  function scheduleFrame() {
    if (!running) return;
    rafId = requestAnimationFrame(frame);
  }

  function frame(t: number) {
    if (!running) return;

    const fullSpeed = shouldAnimateFull();
    const minInterval = fullSpeed ? maxFpsIntervalMs : throttleIntervalMs;
    if (minInterval > 0) {
      const wait = Math.max(0, minInterval - (t - lastDrawTs));
      if (wait > 0) {
        throttleTimer = window.setTimeout(() => {
          throttleTimer = 0;
          scheduleFrame();
        }, wait);
        return;
      }
    }

    drawOnce(t);
    scheduleFrame();
  }

  function start() {
    if (running || !shouldRunLoop()) return;
    running = true;
    scheduleFrame();
  }

  function stop() {
    if (!running && !throttleTimer && !rafId) return;
    running = false;
    if (rafId) {
      cancelAnimationFrame(rafId);
      rafId = 0;
    }
    if (throttleTimer) {
      window.clearTimeout(throttleTimer);
      throttleTimer = 0;
    }
  }

  function sync() {
    syncCssLayers();
    if (shouldRunLoop()) start();
    else stop();
  }

  resize();
  window.addEventListener('resize', scheduleResize, { passive: true });

  if (pauseWhenHidden) {
    pageHidden = document.hidden;
    document.addEventListener('visibilitychange', () => {
      pageHidden = document.hidden;
      sync();
    });
  }

  if (activeWhenSelector) {
    const anchor = document.querySelector(activeWhenSelector);
    if (anchor) {
      // Hero AF começa na dobra — assume in-view até o 1º callback do IO
      // (evita getBoundingClientRect forçado no boot).
      anchorInView = true;
      const io = new IntersectionObserver(
        (entries) => {
          anchorInView = entries[0]?.isIntersecting ?? false;
          sync();
        },
        { root: null, threshold: 0 },
      );
      io.observe(anchor);
    } else {
      anchorInView = false;
    }
  }

  sync();
}
