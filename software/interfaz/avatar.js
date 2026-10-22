// Prisma — avatar 3D (VRM) con three.js y three-vrm.
// Carga /avatar.vrm (tu personaje en ~/.config/prisma/avatar.vrm o el de muestra) y lo anima:
// respiración, parpadeo, mirada, expresión según el estado y movimiento de labios al hablar.
// API: window.avatar.estado("reposo"|"escucha"|"pensando"|"buscando"|"hablando"|"error")
//      window.avatar.nivel(0..1)   volumen de la voz (cuando haya voz; ahora se simula)
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { VRMLoaderPlugin, VRMUtils } from "@pixiv/three-vrm";

const caja = document.getElementById("lienzo3d");
const FPS = 30;

export async function inicia() {
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  caja.appendChild(renderer.domElement);

  const escena = new THREE.Scene();
  const camara = new THREE.PerspectiveCamera(22, 1, 0.1, 20);
  escena.add(new THREE.AmbientLight(0xffffff, 0.55));
  const clave = new THREE.DirectionalLight(0xffffff, 1.6); clave.position.set(0.6, 1.2, 1.5); escena.add(clave);
  const borde = new THREE.DirectionalLight(0x66e0ff, 0.9); borde.position.set(-1, 1.4, -1.2); escena.add(borde);

  const cargador = new GLTFLoader();
  cargador.register(p => new VRMLoaderPlugin(p));
  const gltf = await cargador.loadAsync("/avatar.vrm");
  const vrm = gltf.userData.vrm;
  VRMUtils.removeUnnecessaryVertices(gltf.scene);
  VRMUtils.combineSkeletons(gltf.scene);
  VRMUtils.rotateVRM0(vrm);                       // los modelos VRM 0.x miran hacia atrás
  vrm.scene.traverse(o => { o.frustumCulled = false; });
  escena.add(vrm.scene);

  // Encuadre: busto, con la cara un poco por encima del centro
  const cabeza = vrm.humanoid.getNormalizedBoneNode("head");
  const pc = new THREE.Vector3(); cabeza.getWorldPosition(pc);
  camara.position.set(0, pc.y + 0.02, 1.7);
  camara.lookAt(0, pc.y - 0.1, 0);

  // Postura relajada (sin brazos en cruz)
  const hueso = n => vrm.humanoid.getNormalizedBoneNode(n);
  hueso("leftUpperArm") && (hueso("leftUpperArm").rotation.z = -1.25);
  hueso("rightUpperArm") && (hueso("rightUpperArm").rotation.z = 1.25);
  hueso("leftLowerArm") && (hueso("leftLowerArm").rotation.z = -0.12);
  hueso("rightLowerArm") && (hueso("rightLowerArm").rotation.z = 0.12);

  const mirada = new THREE.Object3D(); escena.add(mirada);
  if (vrm.lookAt) vrm.lookAt.target = mirada;

  const exp = vrm.expressionManager;
  const tiene = n => exp && exp.getExpression(n);
  const pon = (n, v) => { if (tiene(n)) exp.setValue(n, v); };
  const VISEMAS = ["aa", "ih", "ou", "ee", "oh"];

  let estado = "reposo", nivelVoz = 0, nivelSimulado = false;
  let proxParpadeo = 2, parpadeo = 0, visema = "aa", proxVisema = 0, apertura = 0;
  const animo = { happy: 0, relaxed: 0, sad: 0, surprised: 0 };
  const objetivo = { happy: 0, relaxed: 0, sad: 0, surprised: 0 };
  const reloj = new THREE.Clock();
  let acumulado = 0;

  function ajusta() {
    const w = caja.clientWidth, h = caja.clientHeight;
    renderer.setSize(w, h, false); camara.aspect = w / h; camara.updateProjectionMatrix();
  }
  addEventListener("resize", ajusta); ajusta();

  function bucle() {
    requestAnimationFrame(bucle);
    const dt = reloj.getDelta(); acumulado += dt;
    if (acumulado < 1 / FPS) return;               // 30 fps: suficiente y deja CPU a la IA
    const paso = acumulado; acumulado = 0;
    const t = reloj.elapsedTime;

    // Respiración y pequeños movimientos de cabeza
    const pecho = hueso("chest") || hueso("spine");
    if (pecho) pecho.rotation.x = Math.sin(t * 1.6) * 0.012;
    const cuello = hueso("neck");
    if (cuello) {
      const inclina = estado === "escucha" ? 0.08 : 0;
      cuello.rotation.z += ((Math.sin(t * 0.45) * 0.03 + inclina) - cuello.rotation.z) * 0.08;
      cuello.rotation.y += ((Math.sin(t * 0.3) * 0.05) - cuello.rotation.y) * 0.08;
    }

    // Mirada: a la persona; al pensar, arriba a un lado
    const piensa = estado === "pensando" || estado === "buscando";
    const mx = piensa ? 0.35 : Math.sin(t * 0.37) * 0.06, my = piensa ? 0.35 : Math.sin(t * 0.23) * 0.04;
    mirada.position.lerp(new THREE.Vector3(camara.position.x + mx, camara.position.y + my, camara.position.z), 0.12);

    // Parpadeo
    proxParpadeo -= paso;
    if (proxParpadeo <= 0) { parpadeo = 1; proxParpadeo = 2.5 + Math.random() * 4; }
    parpadeo = Math.max(0, parpadeo - paso * 7);
    pon("blink", piensa ? 0 : Math.sin(parpadeo * Math.PI));

    // Expresión según el estado
    Object.assign(objetivo, { happy: 0, relaxed: 0, sad: 0, surprised: 0 });
    if (estado === "escucha") { objetivo.happy = 0.25; objetivo.surprised = 0.15; }
    else if (piensa) objetivo.relaxed = 0.35;
    else if (estado === "hablando") objetivo.happy = 0.18;
    else if (estado === "error") objetivo.sad = 0.55;
    else objetivo.relaxed = 0.15;
    for (const k in animo) { animo[k] += (objetivo[k] - animo[k]) * 0.1; pon(k, animo[k]); }

    // Labios: con la voz, el volumen; mientras no hay voz, un ritmo de sílabas simulado
    let v = nivelVoz;
    if (estado === "hablando" && nivelSimulado) v = Math.max(0, Math.sin(t * 15) * 0.5 + Math.sin(t * 9.3) * 0.35 + 0.25);
    if (estado !== "hablando") v = 0;
    proxVisema -= paso;
    if (proxVisema <= 0) { visema = VISEMAS[Math.floor(Math.random() * VISEMAS.length)]; proxVisema = 0.09 + Math.random() * 0.08; }
    apertura += (v - apertura) * 0.5;
    for (const n of VISEMAS) pon(n, n === visema ? Math.min(1, apertura) : 0);

    vrm.update(paso);
    renderer.render(escena, camara);
  }
  bucle();

  window.avatar = {
    estado(e) { estado = e; },
    nivel(x) { nivelVoz = x; nivelSimulado = false; },
    simula(si) { nivelSimulado = si; },
  };
  window.avatar.simula(true);
  return true;
}
