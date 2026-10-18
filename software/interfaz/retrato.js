// Prisma — avatar 2,5D: retrato ilustrado animado (WebGL, sin librerías).
// Lee /retrato/retrato.json (lo crea herramientas/prepara_retrato.py) y dibuja la imagen base con
// las capas encima (ojos cerrados, bocas, pensativa…). Todas pasan por la misma deformación suave:
// la cabeza se balancea y se inclina, y los hombros suben y bajan al respirar.
// API común con el avatar 3D: window.avatar.estado(e), .nivel(0..1), .simula(si)

const caja = document.getElementById("lienzo3d");
const FPS = 30;
const MALLA = 28;                       // subdivisiones de la imagen base (las capas, menos)
const BOCAS = ["boca_a", "boca_e", "boca_o", "boca_i", "boca_u"];
const EXPRESION = { escucha: "sonrisa", pensando: "piensa", buscando: "piensa", error: "triste" };
const MINIMO = 2.0;                     // segundos que dura como poco una expresión (pensar suele ser muy breve)

const VS = `
attribute vec2 aPos; attribute vec2 aUv;
uniform vec2 uCentro, uEscala, uCaja;           // encuadre: imagen → píxeles de la caja
uniform vec3 uCabeza; uniform float uCuello, uAng, uRespira;
uniform vec2 uMueve; uniform float uFijo;            // uFijo = 1: el decorado no se deforma
varying vec2 vUv;
void main() {
  vec2 p = aPos;
  float d = length(p - uCabeza.xy) / uCabeza.z;
  float alto = uCabeza.z * 0.35;
  float w = (1.0 - smoothstep(0.55, 1.0, d)) * (1.0 - smoothstep(uCuello - alto, uCuello + alto * 0.4, p.y));
  vec2 piv = vec2(uCabeza.x, uCuello);
  vec2 r = p - piv; float a = uAng * w;
  vec2 q = piv + vec2(r.x * cos(a) - r.y * sin(a), r.x * sin(a) + r.y * cos(a)) + uMueve * w;
  // respiración: sube lo que está por encima de la cintura, más cerca del cuello
  float cuerpo = clamp(1.0 - abs(p.x - uCabeza.x) / (uCabeza.z * 1.6), 0.0, 1.0);
  float sube = max(w, cuerpo * smoothstep(uCuello + uCabeza.z * 1.6, uCuello, p.y));
  q.y -= uRespira * sube;
  if (uFijo > 0.5) q = p;
  vec2 s = (q - uCentro) * uEscala + uCaja * 0.5;
  gl_Position = vec4(s.x / uCaja.x * 2.0 - 1.0, 1.0 - s.y / uCaja.y * 2.0, 0.0, 1.0);
  vUv = aUv;
}`;
const FS = `
precision mediump float;
uniform sampler2D uTex; uniform float uAlfa; varying vec2 vUv;
void main() { vec4 c = texture2D(uTex, vUv); gl_FragColor = vec4(c.rgb, c.a * uAlfa); }`;

function carga(src) {
  return new Promise((ok, mal) => { const i = new Image(); i.onload = () => ok(i); i.onerror = () => mal(new Error("No carga " + src)); i.src = src; });
}

export async function inicia(raiz = "/retrato/") {
  const datos = await (await fetch(raiz + "retrato.json", { cache: "no-store" })).json();
  const lienzo = document.createElement("canvas");
  const gl = lienzo.getContext("webgl", { alpha: true, premultipliedAlpha: false, antialias: false });
  if (!gl) throw new Error("Sin WebGL");
  caja.appendChild(lienzo);

  const sh = (t, s) => { const o = gl.createShader(t); gl.shaderSource(o, s); gl.compileShader(o);
    if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o)); return o; };
  const prog = gl.createProgram();
  gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS)); gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS));
  gl.linkProgram(prog); gl.useProgram(prog);
  const U = n => gl.getUniformLocation(prog, n);
  const aPos = gl.getAttribLocation(prog, "aPos"), aUv = gl.getAttribLocation(prog, "aUv");
  gl.enable(gl.BLEND);   // el alfa del lienzo se queda opaco: si no, las capas dejan ver el fondo de la página
  gl.blendFuncSeparate(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA, gl.ONE, gl.ONE_MINUS_SRC_ALPHA);

  // Una capa = textura + malla de su rectángulo en coordenadas de la imagen base
  function capa(img, x, y, w, h, n) {
    const tex = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, tex);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
    for (const [k, v] of [[gl.TEXTURE_MIN_FILTER, gl.LINEAR], [gl.TEXTURE_MAG_FILTER, gl.LINEAR],
                          [gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE], [gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE]])
      gl.texParameteri(gl.TEXTURE_2D, k, v);
    const v = [];
    for (let j = 0; j < n; j++) for (let i = 0; i < n; i++) {
      const q = [[i, j], [i + 1, j], [i, j + 1], [i, j + 1], [i + 1, j], [i + 1, j + 1]];
      for (const [a, b] of q) v.push(x + w * a / n, y + h * b / n, a / n, b / n);
    }
    const buf = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(v), gl.STATIC_DRAW);
    return { tex, buf, n: n * n * 6, alfa: 0, meta: 0 };
  }

  const base = capa(await carga(raiz + datos.base), 0, 0, datos.ancho, datos.alto, MALLA);
  base.alfa = 1;
  // Decorado aparte (la persona va recortada delante): no se deforma y tiene su propio encuadre
  const df = datos.fondo;
  const fondo = df ? capa(await carga(raiz + df.archivo), 0, 0, df.ancho, df.alto, 1) : null;
  if (fondo) fondo.alfa = 1;
  const centroF = df ? { ...(df.centro || { x: df.ancho / 2, y: df.alto / 2 }) } : null;
  const capas = {};
  await Promise.all(Object.entries(datos.capas || {}).map(async ([nombre, c]) => {
    try { capas[nombre] = capa(await carga(raiz + c.archivo), c.x, c.y, c.w, c.h, 6); }
    catch (e) { console.warn(e.message); }
  }));
  const bocas = BOCAS.filter(b => capas[b]);
  const orden = ["sonrisa", "triste", "piensa", "ojos_cerrados", ...BOCAS].filter(n => capas[n]);

  const cab = datos.cabeza, cuello = datos.cuello_y;
  const centro = datos.centro || { x: cab.x, y: cab.y + cab.r * 0.55 };
  const sustituyen = Object.keys(datos.capas || {}).filter(n => datos.capas[n].sustituye && capas[n]);
  let W = 1, H = 1, esc = 1, escF = 1;
  function ajusta() {
    W = caja.clientWidth; H = caja.clientHeight;
    lienzo.width = W; lienzo.height = H; gl.viewport(0, 0, W, H);
    // Cubre la caja, con la cara un poco por encima del centro, sin dejar huecos
    esc = Math.max(W / datos.ancho, H / datos.alto) * (datos.zoom || 1);
    if (df) escF = Math.max(W / df.ancho, H / df.alto) * (df.zoom || 1);
  }
  addEventListener("resize", ajusta); ajusta();

  let estado = "reposo", nivelVoz = 0, simulado = false;
  let proxParpadeo = 2, parpadeo = 0, apertura = 0, visema = bocas[0], proxVisema = 0;
  const desde = {};
  let frase = 1, ang = 0, mx = 0, my = 0, acumulado = 0, ultimo = performance.now();
  const t0 = performance.now();

  function dibuja(c) {
    if (c.alfa < 0.01) return;
    gl.bindTexture(gl.TEXTURE_2D, c.tex);
    gl.bindBuffer(gl.ARRAY_BUFFER, c.buf);
    gl.enableVertexAttribArray(aPos); gl.vertexAttribPointer(aPos, 2, gl.FLOAT, false, 16, 0);
    gl.enableVertexAttribArray(aUv); gl.vertexAttribPointer(aUv, 2, gl.FLOAT, false, 16, 8);
    gl.uniform1f(U("uAlfa"), Math.min(1, c.alfa));
    gl.drawArrays(gl.TRIANGLES, 0, c.n);
  }

  function bucle(ahora) {
    requestAnimationFrame(bucle);
    acumulado += (ahora - ultimo) / 1000; ultimo = ahora;
    if (acumulado < 1 / FPS) return;
    const paso = Math.min(acumulado, 0.2); acumulado = 0;
    const t = (ahora - t0) / 1000;
    const piensa = estado === "pensando" || estado === "buscando";

    // Cabeza: balanceo lento; al escuchar se inclina; al pensar se ladea hacia arriba
    const angObj = Math.sin(t * 0.45) * 0.012 + Math.sin(t * 1.1) * 0.004 + (estado === "escucha" ? 0.035 : 0) + (piensa ? -0.025 : 0);
    const habla = estado === "hablando" ? Math.sin(t * 2.1) * 0.006 : 0;   // acompaña la frase
    ang += (angObj + habla - ang) * Math.min(1, paso * 3);
    mx += ((Math.sin(t * 0.3) * 0.006) * cab.r - mx) * Math.min(1, paso * 3);
    my += (((piensa ? -0.02 : 0) + Math.sin(t * 0.7) * 0.003) * cab.r - my) * Math.min(1, paso * 3);
    const respira = (Math.sin(t * 1.55) * 0.5 + 0.5) * cab.r * 0.012;

    // Parpadeo (no al pensar si hay imagen «piensa»)
    proxParpadeo -= paso;
    if (proxParpadeo <= 0) { parpadeo = 1; proxParpadeo = 2.5 + Math.random() * 4; }
    parpadeo = Math.max(0, parpadeo - paso * 6);
    if (capas.ojos_cerrados) capas.ojos_cerrados.alfa = (piensa && capas.piensa) ? 0 : (parpadeo > 0.15 ? 1 : 0);

    // Expresión del estado, con fundido
    for (const n of ["sonrisa", "triste", "piensa"]) if (capas[n]) {
      if (EXPRESION[estado] === n && !(n in desde)) desde[n] = t;      // empieza la expresión
      const sigue = n in desde && t - desde[n] < MINIMO;                // aunque el estado ya haya cambiado
      if (EXPRESION[estado] !== n && !sigue) delete desde[n];
      const meta = EXPRESION[estado] === n || sigue ? 1 : 0;
      // Las que cambian la postura se funden rápido (≈0,25 s): un fundido lento deja ver dos manos a la vez
      const vel = datos.capas[n].sustituye ? 9 : 3.5;
      capas[n].alfa += (meta - capas[n].alfa) * Math.min(1, paso * vel);
    }

    // Labios. Para que parezca habla y no gesticulación:
    // - ritmo de sílabas (≈4 por segundo) con pausas entre palabras, no un temblor rápido;
    // - la boca solo cambia de forma cuando está casi cerrada (abierta → cerrada → otra forma),
    //   así nunca se funden dos bocas abiertas distintas;
    // - las bocas abiertas del todo («a») salen menos que las medias («e», «o»).
    let v = 0;
    if (estado === "hablando") {
      if (simulado) {
        const silaba = Math.pow(Math.max(0, Math.sin(t * 2 * Math.PI * 4.1)), 0.8);
        const palabra = Math.sin(t * 1.9) + Math.sin(t * 0.83 + 1) > -0.7 ? 1 : 0;
        frase += (palabra - frase) * Math.min(1, paso * 8);
        v = silaba * frase * (0.55 + 0.45 * Math.sin(t * 0.9 + 2) ** 2);
      } else v = nivelVoz;
    }
    apertura += (v - apertura) * Math.min(1, paso * 14);
    if (apertura < 0.12 && bocas.length) {
      const r = Math.random();
      visema = r < 0.45 && capas.boca_e ? "boca_e" : r < 0.75 && capas.boca_o ? "boca_o" : bocas[Math.floor(Math.random() * bocas.length)];
    }
    for (const b of bocas) {
      const otraPostura = sustituyen.reduce((m, n) => Math.max(m, capas[n].alfa), 0);
      const meta = b === visema ? Math.min(1, Math.max(0, (apertura - 0.12) * 1.6)) * (1 - otraPostura) : 0;
      capas[b].alfa += (meta - capas[b].alfa) * Math.min(1, paso * 12);
    }

    gl.clearColor(0, 0, 0, 0); gl.clear(gl.COLOR_BUFFER_BIT);
    gl.uniform2f(U("uCentro"), centro.x, centro.y);
    gl.uniform2f(U("uEscala"), esc, esc);
    gl.uniform2f(U("uCaja"), W, H);
    gl.uniform3f(U("uCabeza"), cab.x, cab.y, cab.r);
    gl.uniform1f(U("uCuello"), cuello);
    gl.uniform1f(U("uAng"), ang);
    gl.uniform2f(U("uMueve"), mx, my);
    gl.uniform1f(U("uRespira"), respira);
    if (fondo) {
      gl.uniform1f(U("uFijo"), 1); gl.uniform2f(U("uCentro"), centroF.x, centroF.y); gl.uniform2f(U("uEscala"), escF, escF);
      dibuja(fondo);
      gl.uniform1f(U("uFijo"), 0); gl.uniform2f(U("uCentro"), centro.x, centro.y); gl.uniform2f(U("uEscala"), esc, esc);
    }
    // Una variante con otra postura (p. ej. «piensa» con la mano) tapa a la base solo cuando ya es opaca
    base.alfa = sustituyen.some(n => capas[n].alfa > 0.99) ? 0 : 1;
    dibuja(base);
    for (const n of orden) dibuja(capas[n]);
  }

  // El encuadre no debe dejar ver bordes vacíos: limita el centro
  const lim = () => {
    const mw = W / esc / 2, mh = H / esc / 2;
    centro.x = Math.min(Math.max(centro.x, mw), datos.ancho - mw);
    centro.y = Math.min(Math.max(centro.y, mh), datos.alto - mh);
    if (df) {
      const fw = W / escF / 2, fh = H / escF / 2;
      centroF.x = Math.min(Math.max(centroF.x, fw), df.ancho - fw);
      centroF.y = Math.min(Math.max(centroF.y, fh), df.alto - fh);
    }
  };
  lim(); addEventListener("resize", lim);
  requestAnimationFrame(bucle);

  window.avatar = {
    estado(e) { estado = e; },
    nivel(x) { nivelVoz = x; simulado = false; },
    simula(si) { simulado = si; },
    info: () => ({ estado, apertura, visema, bocas, capas: Object.fromEntries(Object.entries(capas).map(([k, c]) => [k, +c.alfa.toFixed(2)])) }),
  };
  window.avatar.simula(true);
  return true;
}
