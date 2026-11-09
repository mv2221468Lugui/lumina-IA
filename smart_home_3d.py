# Acabamento final: exposição calibrada para preservar cores e detalhes dos ambientes.
import json
import streamlit as st
import streamlit.components.v1 as components


# =========================================================
# LUMINA AI | SMART HOME 2050
# Casa 3D interativa com Three.js
# =========================================================

ROOMS = [
    "Sala de Estar",
    "Cozinha",
    "Quarto Casal",
    "Quarto Solteiro",
    "Banheiro Social",
    "Banheiro Suíte",
    "Hall",
    "Garagem",
    "Quintal",
]

SCENARIOS = {
    "Chegada em casa": ["Sala de Estar", "Cozinha", "Hall"],
    "Saída de casa": [],
    "Noite": ["Quarto Casal", "Quarto Solteiro", "Banheiro Suíte"],
    "Festa": ["Sala de Estar", "Cozinha", "Quintal"],
}

POWER = {
    "Sala de Estar": 24,
    "Cozinha": 30,
    "Quarto Casal": 18,
    "Quarto Solteiro": 15,
    "Banheiro Social": 10,
    "Banheiro Suíte": 10,
    "Hall": 8,
    "Garagem": 20,
    "Quintal": 15,
}


def iniciar_estado():
    if "lumina_luzes" not in st.session_state:
        st.session_state.lumina_luzes = {
            room: False for room in ROOMS
        }

    for room in ROOMS:
        st.session_state.lumina_luzes.setdefault(room, False)

    defaults = {
        "lumina_cenario": "Personalizado",
        "lumina_temperatura": 23,
        "lumina_agua": 12.0,
        "lumina_presenca": True,
        "lumina_aparelhos": True,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def obter_resumo_consumo():
    iniciar_estado()

    luzes = st.session_state.lumina_luzes

    potencia_luzes = sum(
        POWER[room]
        for room in ROOMS
        if luzes.get(room, False)
    )

    potencia_aparelhos = (
        850 if st.session_state.lumina_aparelhos else 0
    )

    return {
        "potencia_luzes_w": potencia_luzes,
        "potencia_aparelhos_w": potencia_aparelhos,
        "potencia_total_w": potencia_luzes + potencia_aparelhos,
        "agua_m3": st.session_state.lumina_agua,
        "temperatura_c": st.session_state.lumina_temperatura,
        "presenca": st.session_state.lumina_presenca,
        "luzes": dict(luzes),
        "origem": "simulacao",
    }


def gerar_casa_3d():
    luzes = json.dumps(st.session_state.lumina_luzes)

    html = r"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    background: #071426;
    color: #eaf6ff;
    font-family: Arial, sans-serif;
    overflow: hidden;
}

#scene {
    width: 100%;
    height: 720px;
    position: relative;
    overflow: hidden;
    border: 1px solid #17486a;
    border-radius: 16px;
    background: linear-gradient(160deg, #d7edf9, #a9cfe6);
}

#toolbar {
    position: absolute;
    top: 12px;
    left: 12px;
    z-index: 5;
    display: flex;
    flex-wrap: wrap;
    gap: 7px;
    max-width: calc(100% - 24px);
}

button {
    background: rgba(10, 39, 64, .94);
    color: #dff6ff;
    border: 1px solid #26749b;
    padding: 9px 12px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 12px;
}

button:hover, button.active {
    background: #087ca8;
    border-color: #54d9ff;
}

#brand-label {
    position:absolute; top:66px; left:14px; z-index:5;
    background:rgba(4,19,35,.76); border:1px solid #26749b;
    border-radius:12px; padding:10px 14px; pointer-events:none;
    display:flex; flex-direction:column; gap:3px;
}
#brand-label strong {color:#8fe8ff; font-size:15px; letter-spacing:2px;}
#brand-label span {color:#b5d4e6; font-size:10px; letter-spacing:1px;}
#room-label {
    position: absolute;
    right: 12px;
    bottom: 12px;
    z-index: 5;
    background: rgba(4, 19, 35, .9);
    border: 1px solid #1b5678;
    padding: 10px 14px;
    border-radius: 10px;
    font-size: 12px;
}

#hint {
    position: absolute;
    left: 12px;
    bottom: 12px;
    z-index: 5;
    color: #9fc9df;
    font-size: 11px;
}

canvas { display: block; }
</style>
</head>

<body>
<div id="scene">

    <div id="toolbar">
        <button id="viewTop">Vista superior</button>
        <button id="view3d" class="active">Vista 3D</button>
        <button id="interior">Explorar interior</button>
        <button id="xray">Raio-X</button>
        <button id="roof">Mostrar telhado</button>
        <button id="smart">Sensores</button>
        <button id="day" class="active">Dia</button>
        <button id="night">Noite</button>
        <button id="reset">Reiniciar câmera</button>
    </div>

    <div id="brand-label"><strong>LUMINA AI</strong><span>SMART HOME 2050 · RESIDÊNCIA CONTEMPORÂNEA</span></div>
    <div id="room-label">Selecione um ambiente</div>
    <div id="hint">Arraste para girar · Scroll para aproximar · Clique nos ambientes</div>
</div>

<!-- Import map: OrbitControls usa o nome interno "three". -->
<script type="importmap">
{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js","three/addons/":"https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"}}
</script>
<script type="module">

import * as THREE from 'three';

import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const initialLights = __LIGHTS__;

const container = document.getElementById("scene");

const scene = new THREE.Scene();
// A maquete é ilustrativa e não representa sensores físicos conectados.
scene.background = new THREE.Color("#d4eafa");
scene.fog = new THREE.FogExp2("#d4eafa", 0.004);

const camera = new THREE.PerspectiveCamera(
    42,
    container.clientWidth / container.clientHeight,
    0.1,
    1000
);

camera.position.set(16, 13, 17);

const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: false
});

renderer.setSize(container.clientWidth, container.clientHeight);
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.72;
renderer.physicallyCorrectLights = true;

container.appendChild(renderer.domElement);

const controls = new OrbitControls(camera, renderer.domElement);
controls.enableDamping = true;
controls.target.set(6, 0, 4);
controls.maxPolarAngle = Math.PI / 2.05;
controls.minDistance = 8;
controls.maxDistance = 32;
controls.enablePan = true;
controls.dampingFactor = 0.075;
controls.maxAzimuthAngle = Infinity;
controls.minPolarAngle = 0.15;

// Iluminação geral
const ambient = new THREE.HemisphereLight(
    0xffffff, 0x8796a0, 0.72
);
scene.add(ambient);

const sun = new THREE.DirectionalLight(0xffe8cd, 1.10);
sun.position.set(-8, 16, 10);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
scene.add(sun);
sun.shadow.camera.left = -18;
sun.shadow.camera.right = 18;
sun.shadow.camera.top = 18;
sun.shadow.camera.bottom = -18;
sun.shadow.bias = -0.0002;
sun.shadow.normalBias = 0.025;
sun.shadow.radius = 3;
const fillLight = new THREE.DirectionalLight(0xd9e5ee, 0.22);
fillLight.position.set(15, 10, -8);
scene.add(fillLight);

// Texturas procedurais locais: sem downloads de imagens ou modelos externos.
function criarTextura(tipo) {
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 256;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = tipo === 'madeira' ? '#b99470' : tipo === 'piso' ? '#dedbd4' : '#c8d3d8';
    ctx.fillRect(0,0,256,256);
    if (tipo === 'madeira') {
        for(let i=0;i<22;i++) {
            const y=i*12;
            ctx.strokeStyle = i%3===0 ? 'rgba(85,48,23,.24)' : 'rgba(255,245,216,.22)';
            ctx.lineWidth = i%3===0 ? 2 : 1;
            ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(256,y+2); ctx.stroke();
        }
        ctx.strokeStyle='rgba(65,44,28,.3)'; ctx.lineWidth=2;
        for(let y=0;y<256;y+=64) {ctx.beginPath();ctx.moveTo(0,y);ctx.lineTo(256,y);ctx.stroke();}
    } else {
        ctx.strokeStyle='rgba(103,117,125,.25)';ctx.lineWidth=2;
        for(let i=0;i<=256;i+=64) {
            ctx.beginPath();ctx.moveTo(i,0);ctx.lineTo(i,256);ctx.stroke();
            ctx.beginPath();ctx.moveTo(0,i);ctx.lineTo(256,i);ctx.stroke();
        }
    }
    const t=new THREE.CanvasTexture(canvas);
    t.wrapS=t.wrapT=THREE.RepeatWrapping;
    t.repeat.set(tipo==='madeira'?3:2,tipo==='madeira'?3:2);
    t.colorSpace=THREE.SRGBColorSpace;
    t.anisotropy=Math.min(renderer.capabilities.getMaxAnisotropy(),8);
    return t;
}
const texMadeira=criarTextura('madeira');
const texPiso=criarTextura('piso');
const texCeramica=criarTextura('ceramica');
// Materiais
const materials = {
    wall: new THREE.MeshStandardMaterial({
        color: "#dce7ed", roughness: 0.85
    }),
    glass: new THREE.MeshPhysicalMaterial({
        color: "#54cfff",
        transparent: true,
        opacity: 0.35,
        roughness: 0.1,
        metalness: 0.1
    }),
    wood: new THREE.MeshStandardMaterial({
        color: "#ffffff", map: texMadeira, roughness: 0.76
    }),
    darkWood: new THREE.MeshStandardMaterial({
        color: "#49382f", roughness: 0.8
    }),
    fabric: new THREE.MeshStandardMaterial({
        color: "#4d91ad", roughness: 1
    }),
    white: new THREE.MeshStandardMaterial({
        color: "#e5edf0", roughness: 0.55
    }),
    metal: new THREE.MeshStandardMaterial({
        color: "#879ba8", metalness: 0.7, roughness: 0.3
    }),
    green: new THREE.MeshStandardMaterial({
        color: "#237b52", roughness: 1
    }),
    grass: new THREE.MeshStandardMaterial({
        color: "#235e49", roughness: 1
    }),
    floor: new THREE.MeshStandardMaterial({
        color: "#ffffff", map: texPiso, roughness: 0.9
    }),
    tile: new THREE.MeshStandardMaterial({
        color: "#ffffff", map: texCeramica, roughness: 0.65
    })
};

const roomObjects = {};
const lightObjects = {};
const raycaster = new THREE.Raycaster();
const mouse = new THREE.Vector2();

function box(parent, x, y, z, w, h, d, material, name="") {
    const geometry = new THREE.BoxGeometry(w, h, d);
    const mesh = new THREE.Mesh(geometry, material);

    mesh.position.set(x, y + h / 2, z);
    mesh.castShadow = true;
    mesh.receiveShadow = true;
    mesh.userData.room = name;

    parent.add(mesh);
    return mesh;
}

function cylinder(parent, x, y, z, radius, height, material) {
    const mesh = new THREE.Mesh(
        new THREE.CylinderGeometry(radius, radius, height, 20),
        material
    );

    mesh.position.set(x, y + height / 2, z);
    mesh.castShadow = true;
    parent.add(mesh);

    return mesh;
}

function sphere(parent, x, y, z, radius, material) {
    const mesh = new THREE.Mesh(
        new THREE.SphereGeometry(radius, 18, 14),
        material
    );

    mesh.position.set(x, y + radius, z);
    mesh.castShadow = true;
    parent.add(mesh);

    return mesh;
}

function roomFloor(name, x, z, w, d, color) {
    const material = new THREE.MeshStandardMaterial({
        color, roughness: 0.85
    });

    const floor = box(
        scene, x + w / 2, 0, z + d / 2,
        w, 0.16, d, material, name
    );

    roomObjects[name] = [floor];
}

const architecturalWalls = [];
function wall(x, z, length, height, thickness, horizontal=true) {
    const mesh = horizontal
        ? box(scene, x + length / 2, 0.16, z, length, height, thickness, materials.wall)
        : box(scene, x, 0.16, z + length / 2, thickness, height, length, materials.wall);
    architecturalWalls.push(mesh);
    return mesh;
}

function furniture(room, x, z, w, h, d, material) {
    const object = box(
        scene, x + w / 2, 0.16, z + d / 2,
        w, h, d, material, room
    );

    if (!roomObjects[room]) roomObjects[room] = [];
    roomObjects[room].push(object);

    return object;
}

function windowGlass(x, z, w, horizontal=true) {
    if (horizontal) {
        box(
            scene, x + w / 2, 1.65, z,
            w, 0.85, 0.08, materials.glass
        );
    } else {
        box(
            scene, x, 1.65, z + w / 2,
            0.08, 0.85, w, materials.glass
        );
    }
}

function makeLight(room, x, z, color="#ffe3a1") {
    const lamp = new THREE.PointLight(color, 0, 5, 2);
    lamp.position.set(x, 2.0, z);
    scene.add(lamp);

    const bulb = new THREE.Mesh(
        new THREE.SphereGeometry(0.11, 12, 12),
        new THREE.MeshBasicMaterial({color})
    );

    bulb.position.set(x, 2.0, z);
    scene.add(bulb);

    if (!lightObjects[room]) lightObjects[room] = [];
    lightObjects[room].push({lamp, bulb});
}

// LUMINA RESIDENCE | arquitetura contemporânea de alto padrão
// Todas as geometrias são geradas localmente para preservar o funcionamento offline da maquete
const P = (color,roughness=.8,metalness=0)=>new THREE.MeshStandardMaterial({color,roughness,metalness});
const finish = {
  limestone:P('#c6c0b5',.92), plaster:P('#d1c7b9',.98), ivory:P('#e6ded0',.91),
  oak:P('#a87b52',.8), walnut:P('#584031',.82), concrete:P('#999d9b',.91),
  slate:P('#444d54',.8), black:P('#20292d',.48,.35), bronze:P('#947655',.42,.65),
  cream:P('#c5b7a6',1), sand:P('#b2a395',1), blue:P('#53778b',1),
  green:P('#2d674a',1), hedge:P('#235d40',1), grass:P('#39704b',1),
  water:new THREE.MeshPhysicalMaterial({color:'#2a9dc0',roughness:.12,metalness:.05,transparent:true,opacity:.82,depthWrite:false}),
  glass:new THREE.MeshPhysicalMaterial({color:'#a4d5de',roughness:.08,transparent:true,opacity:.32,depthWrite:false,side:THREE.DoubleSide}),
  porcelain:P('#c2c6c2',.45), marble:P('#c6c7c1',.28), linen:P('#c7b9a8',1),
  terracotta:P('#aa7157',.95), tv:new THREE.MeshBasicMaterial({color:'#10232e'}),
  lamp:new THREE.MeshStandardMaterial({color:'#f6d6a1',emissive:'#b7772e',emissiveIntensity:.2})
};
// Texturas procedurais PBR: madeira em réguas, pedra, concreto e gramado.
// Cada textura é desenhada no navegador, sem depender de downloads externos.
function texture2050(kind, base, repeatX=1, repeatY=1){
 const cv=document.createElement('canvas');cv.width=cv.height=512;
 const g=cv.getContext('2d');g.fillStyle=base;g.fillRect(0,0,512,512);
 let seed=17;const rnd=()=>{seed=(seed*1664525+1013904223)>>>0;return seed/4294967296;};
 if(kind==='oak'){
  for(let j=0;j<12;j++){
   const y=j*43;g.fillStyle=j%3===0?'rgba(57,34,20,.10)':'rgba(255,231,193,.065)';g.fillRect(0,y,512,42);
   g.strokeStyle='rgba(56,37,25,.35)';g.lineWidth=2;g.beginPath();g.moveTo(0,y);g.lineTo(512,y);g.stroke();
   for(let k=0;k<17;k++){g.strokeStyle=`rgba(57,38,24,${.035+rnd()*.10})`;g.lineWidth=.5+rnd()*1.5;const yy=y+4+rnd()*34;g.beginPath();g.moveTo(rnd()*80,yy);g.bezierCurveTo(170,yy+rnd()*6,320,yy-rnd()*5,512,yy);g.stroke();}
  }
 }else if(kind==='stone'){
  for(let y=0;y<512;y+=128){for(let x=0;x<512;x+=128){g.strokeStyle='rgba(60,63,61,.21)';g.lineWidth=2;g.strokeRect(x+.5,y+.5,127,127);}}
  for(let k=0;k<90;k++){g.strokeStyle=`rgba(85,91,88,${rnd()*.09})`;g.lineWidth=.5+rnd()*2;const x=rnd()*512,y=rnd()*512;g.beginPath();g.moveTo(x,y);g.bezierCurveTo(x+13,y-7,x+21,y+10,x+38,y-3);g.stroke();}
 }else if(kind==='grass'){
  for(let k=0;k<12000;k++){const x=rnd()*512,y=rnd()*512;g.fillStyle=rnd()>.5?'rgba(18,48,27,.16)':'rgba(181,198,105,.13)';g.fillRect(x,y,1+rnd()*3,2+rnd()*4);}
 }else if(kind==='concrete'){
  for(let k=0;k<10000;k++){const x=rnd()*512,y=rnd()*512;g.fillStyle=rnd()>.5?'rgba(20,31,35,.07)':'rgba(255,255,255,.06)';g.fillRect(x,y,1.3,1.3);}
 }
 const t=new THREE.CanvasTexture(cv);t.colorSpace=THREE.SRGBColorSpace;
 t.wrapS=t.wrapT=THREE.RepeatWrapping;t.repeat.set(repeatX,repeatY);
 t.anisotropy=Math.min(8,renderer.capabilities.getMaxAnisotropy());return t;
}
const oakMap=texture2050('oak','#b28d68',2,2);
const stoneMap=texture2050('stone','#c6c3b9',2,2);
const concreteMap=texture2050('concrete','#a5a7a4',3,2);
const lawnMap=texture2050('grass','#557b4b',5,4);
finish.oak=new THREE.MeshStandardMaterial({map:oakMap,roughness:.82});
finish.limestone=new THREE.MeshStandardMaterial({map:stoneMap,roughness:.88});
finish.concrete=new THREE.MeshStandardMaterial({map:concreteMap,roughness:.95});
finish.grass=new THREE.MeshStandardMaterial({map:lawnMap,roughness:1});
// Plataforma paisagística, passeio e gramado
box(scene,5.75,-.58,3.65,15.4,.3,12.8,finish.grass);
box(scene,5.75,-.38,3.35,12.25,.38,8.3,finish.limestone);
box(scene,5.75,-.17,3.35,11.6,.12,7.1,finish.concrete);
for(let i=0;i<10;i++) box(scene,7.75,.01,-.55-i*.34,1.25,.035,.24,finish.limestone);
// Pisos com acabamento e contraste real; manter os nove ambientes e seleção por clique
const roomPalette = {
 'Sala de Estar':finish.oak,'Cozinha':finish.porcelain,'Quarto Casal':finish.oak,
 'Quarto Solteiro':finish.oak,'Banheiro Social':finish.marble,'Banheiro Suíte':finish.marble,
 'Hall':finish.limestone,'Garagem':finish.concrete,'Quintal':finish.grass
};
const roomPlan = [
 ['Sala de Estar',0,0,4,3.5],['Cozinha',4,0,3,3.5],
 ['Quarto Casal',0,3.5,3.2,3],['Quarto Solteiro',3.2,3.5,2.8,3],
 ['Banheiro Social',6,3.5,1.5,1.5],['Banheiro Suíte',6,5,1.5,1.5],
 ['Hall',7,0,1.5,3.5],['Garagem',8.5,0,3,3.5],['Quintal',8.5,3.5,3,3]
];
for(const [name,x,z,w,d] of roomPlan){
 const floor=box(scene,x+w/2,.035,z+d/2,w,.14,d,roomPalette[name],name);
 roomObjects[name]=[floor];
}
// Juntas de madeira e placas de pedra: linhas sutis que conferem escala
for(const [name,x,z,w,d] of roomPlan){
 if(['Sala de Estar','Quarto Casal','Quarto Solteiro'].includes(name)){
   for(let zz=z+.28;zz<z+d-.1;zz+=.34) box(scene,x+w/2,.18,zz,w-.08,.008,.014,finish.walnut,name);
 }else if(['Cozinha','Hall','Garagem'].includes(name)){
   for(let xx=x+.75;xx<x+w;xx+=.75) box(scene,xx,.18,z+d/2,.009,.006,d-.08,finish.slate,name);
 }
}
// Paredes em tom quente com rodapés; mantém a transparência do modo Raio-X
materials.wall.color.set('#c9c0b3');
// Fachada com vãos reais: vidro não fica escondido atrás de paredes sólidas.
// Aberturas entre os trechos de alvenaria preservam o efeito de corte da vista superior.
function wallSegments(z, start, end, windows){
 let cursor=start;
 for(const [a,b] of windows){
  if(a>cursor+.02)wall(cursor,z,a-cursor,2.25,.14,true);
  // Peitoril e verga: janela panorâmica de 1,2 m de altura.
  box(scene,(a+b)/2,.16,z,b-a,.52,.14,materials.wall);
  box(scene,(a+b)/2,1.88,z,b-a,.53,.14,materials.wall);
  cursor=b;
 }
 if(cursor<end-.02)wall(cursor,z,end-cursor,2.25,.14,true);
}
wallSegments(0,0,11.5,[[.65,3.3],[4.4,6.55],[7.25,8.2],[8.8,11.15]]);
wallSegments(6.5,0,11.5,[[.5,2.65],[3.55,5.5],[8.85,11.15]]);
wall(0,0,6.5,2.25,.14,false);
wall(11.5,0,3.95,2.25,.14,false);
wall(11.5,5.9,.6,2.25,.14,false);
// Abertura lateral para o jardim.
box(scene,11.5,.16,4.95,.14,.48,1.9,materials.wall);
box(scene,11.5,1.9,4.95,.14,.51,1.9,materials.wall);
// Divisórias internas com passagens para circulação.
function partitionX(x,z0,z1,doorCenter,doorWidth=.76){
 const a=doorCenter-doorWidth/2,b=doorCenter+doorWidth/2;
 if(a>z0)wall(x,z0,a-z0,2.12,.12,false);
 if(z1>b)wall(x,b,z1-b,2.12,.12,false);
 box(scene,x,1.99,doorCenter,.12,.30,doorWidth,materials.wall);
}
function partitionZ(z,x0,x1,doorCenter,doorWidth=.75){
 const a=doorCenter-doorWidth/2,b=doorCenter+doorWidth/2;
 if(a>x0)wall(x0,z,a-x0,2.12,.12,true);
 if(x1>b)wall(b,z,x1-b,2.12,.12,true);
 box(scene,doorCenter,1.99,z,doorWidth,.30,.12,materials.wall);
}
partitionX(4,0,3.5,2.75);
partitionX(7,0,3.5,2.8);
partitionZ(3.5,0,6,3.0);
partitionX(3.2,3.5,6.5,5.95);
partitionX(6,3.5,6.5,4.75);
partitionX(7.5,3.5,6.5,4.45);
partitionZ(5,6,7.5,6.72,.56);
// Frisos escuros e rodapés baixos, sem bloquear portas.
for(const [x,z,w,d] of [[2,0,4,.07],[5.5,0,3,.07],[1.6,6.5,3.2,.07],[4.6,6.5,2.8,.07]]){
 box(scene,x,.18,z,w,.08,d,finish.walnut);
}
// Esquadrias panorâmicas, perfis metálicos e reflexo discreto
function glazing(x,z,w,horizontal=true){
 if(horizontal){
   box(scene,x+w/2,1.1,z,w,1.15,.035,finish.glass);
   box(scene,x+w/2,1.06,z,w,.045,.085,finish.black);
   box(scene,x+w/2,2.23,z,w,.045,.085,finish.black);
   for(const xx of [x,x+w/2,x+w])box(scene,xx,1.1,z,.045,1.22,.09,finish.black);
 }else{
   box(scene,x,1.1,z+w/2,.035,1.15,w,finish.glass);
   for(const zz of [z,z+w/2,z+w])box(scene,x,1.1,zz,.09,1.22,.045,finish.black);
 }
}
glazing(.65,0,2.65);glazing(4.4,0,2.15);glazing(8.8,0,2.35);glazing(.5,6.5,2.15);
glazing(3.55,6.5,1.95);glazing(11.5,4.0,1.9,false);
// Entrada social em madeira ripada e puxador metálico
box(scene,7.7,.16,-.07,.95,1.96,.10,finish.walnut,'Hall');
for(let i=0;i<7;i++)box(scene,7.28+i*.14,.19,-.135,.028,1.9,.025,finish.oak,'Hall');
box(scene,8.02,1.04,-.16,.025,.53,.035,finish.bronze,'Hall');
// Mobiliário: geometria em camadas, pés e superfícies distintas
function sofa(x,z){
 box(scene,x,.24,z,2.4,.26,.88,finish.walnut,'Sala de Estar');
 box(scene,x,.48,z,2.32,.22,.76,finish.cream,'Sala de Estar');
 box(scene,x,.68,z-.33,2.36,.57,.17,finish.cream,'Sala de Estar');
 for(const xx of [x-1.09,x+1.09])box(scene,xx,.48,z,.18,.52,.91,finish.cream,'Sala de Estar');
 for(const xx of [x-.74,x,x+.74]){
   box(scene,xx,.71,z-.17,.63,.32,.19,finish.linen,'Sala de Estar');
   box(scene,xx,.73,z+.18,.58,.09,.38,finish.sand,'Sala de Estar');
 }
}
sofa(1.65,.91);
box(scene,2.08,.19,2.35,2.1,.018,1.05,finish.sand,'Sala de Estar');
for(const xx of [1.58,2.58])for(const zz of [2.05,2.56])cylinder(scene,xx,.19,zz,.035,.34,finish.black);
box(scene,2.08,.53,2.31,1.35,.075,.65,finish.marble,'Sala de Estar');
box(scene,3.79,.54,1.55,.13,1.15,1.3,finish.walnut,'Sala de Estar');
box(scene,3.68,1.04,1.55,.04,.73,1.06,finish.tv,'Sala de Estar');
// Sala: luminária, vaso e quadro de parede
cylinder(scene,.48,.2,2.72,.14,.5,finish.terracotta);
sphere(scene,.48,.73,2.72,.27,finish.green);
// Cozinha planejada com ilha, armários, eletrodomésticos e cooktop
box(scene,5.48,.19,.39,2.75,.78,.58,finish.walnut,'Cozinha');
box(scene,5.48,.97,.39,2.8,.075,.64,finish.marble,'Cozinha');
for(const xx of [4.58,5.25,5.92,6.58]){
 box(scene,xx,1.55,.30,.57,.69,.43,finish.ivory,'Cozinha');
 box(scene,xx,1.58,.55,.24,.022,.026,finish.bronze,'Cozinha');
}
box(scene,5.45,.2,2.02,1.8,.7,.85,finish.walnut,'Cozinha');
box(scene,5.45,.9,2.02,1.91,.085,.96,finish.marble,'Cozinha');
for(const xx of [4.88,5.92]){
 cylinder(scene,xx,.18,3.02,.14,.54,finish.black);
 cylinder(scene,xx,.72,3.02,.24,.065,finish.oak);
}
box(scene,6.64,.19,.62,.47,1.76,.65,finish.ivory,'Cozinha');
box(scene,6.64,1.25,.28,.31,.025,.03,finish.bronze,'Cozinha');
for(const xx of [4.65,4.93])for(const zz of [.33,.58])cylinder(scene,xx,1.065,zz,.09,.008,finish.black);
box(scene,5.75,1.065,.4,.5,.012,.32,finish.slate,'Cozinha');
// Dormitórios com cabeceiras, colchões, edredons e criados-mudos
function bed(room,x,z,w,d){
 box(scene,x,.19,z,w,.26,d,finish.walnut,room);
 box(scene,x,.45,z,w-.09,.22,d-.09,finish.ivory,room);
 box(scene,x,.67,z+d*.23,w-.16,.08,d*.35,finish.linen,room);
 box(scene,x,.67,z-d*.22,w-.16,.07,d*.43,finish.blue,room);
 box(scene,x,.38,z-d/2-.065,w,.95,.12,finish.walnut,room);
 for(const xx of [x-w*.24,x+w*.24])box(scene,xx,.76,z+d*.25,w*.38,.095,d*.23,finish.cream,room);
}
bed('Quarto Casal',1.25,4.95,1.85,1.65);
bed('Quarto Solteiro',4.25,4.94,1.25,1.75);
for(const [room,x,z] of [['Quarto Casal',.36,4.75],['Quarto Casal',2.78,4.75],['Quarto Solteiro',5.55,4.85]]){
 box(scene,x,.18,z,.42,.49,.45,finish.oak,room);
 sphere(scene,x,.72,z,.12,finish.lamp);
}
box(scene,2.89,.19,5.85,.43,1.8,.5,finish.walnut,'Quarto Casal');
box(scene,5.72,.19,5.8,.43,1.8,.5,finish.walnut,'Quarto Solteiro');
// Banheiros: bancadas, louças, espelhos e divisórias de vidro
for(const [room,z] of [['Banheiro Social',4.25],['Banheiro Suíte',5.73]]){
 box(scene,6.35,.2,z-.37,.6,.74,.43,finish.walnut,room);
 box(scene,6.35,.95,z-.37,.64,.055,.48,finish.marble,room);
 cylinder(scene,6.36,1.01,z-.37,.19,.085,finish.ivory);
 box(scene,6.35,1.46,z-.73,.58,.75,.04,finish.glass,room);
 cylinder(scene,6.93,.19,z+.33,.21,.45,finish.ivory);
 box(scene,7.34,.19,z+.35,.035,1.55,.64,finish.glass,room);
}
// Hall com painel de madeira, aparador e vaso
box(scene,7.45,.18,1.62,.45,.72,1.3,finish.oak,'Hall');
box(scene,7.45,.91,1.62,.49,.06,1.35,finish.marble,'Hall');
box(scene,7.45,1.08,2.1,.24,.36,.08,finish.black,'Hall');
// Carro com carroceria, cabine envidraçada, rodas verticais e faróis
const carBody=P('#245b77',.34,.42);
box(scene,10.0,.23,1.66,1.55,.46,2.22,carBody,'Garagem');
box(scene,10.0,.68,1.53,1.3,.52,1.22,carBody,'Garagem');
box(scene,10.0,.83,1.12,1.17,.33,.045,finish.glass,'Garagem');
box(scene,10.0,.83,1.99,1.17,.33,.045,finish.glass,'Garagem');
for(const xx of [9.22,10.78])for(const zz of [.95,2.31]){
 const tire=new THREE.Mesh(new THREE.CylinderGeometry(.24,.24,.15,24),finish.black);
 tire.rotation.z=Math.PI/2;tire.position.set(xx,.35,zz);tire.castShadow=true;scene.add(tire);
 const hub=new THREE.Mesh(new THREE.CylinderGeometry(.105,.105,.158,18),finish.bronze);
 hub.rotation.z=Math.PI/2;hub.position.copy(tire.position);scene.add(hub);
}
for(const xx of [9.46,10.54])box(scene,xx,.45,.53,.23,.11,.05,finish.lamp,'Garagem');
// Quintal: piscina rebaixada visualmente, deck ripado, espreguiçadeiras e vegetação
box(scene,10.03,.18,5.1,2.42,.1,1.74,finish.ivory,'Quintal');
box(scene,10.03,.285,5.1,2.1,.035,1.43,finish.water,'Quintal');
for(let i=0;i<12;i++)box(scene,8.66+i*.24,.19,3.75,.16,.028,.72,finish.oak,'Quintal');
for(const xx of [8.95,11.18]){
 box(scene,xx,.2,6.0,.39,.14,.85,finish.ivory,'Quintal');
 box(scene,xx,.35,6.31,.39,.32,.13,finish.cream,'Quintal');
}
function tree(x,z,s=1){
 cylinder(scene,x,.15,z,.10*s,.65*s,finish.walnut);
 for(const [dx,dy,dz,r] of [[0,.73,0,.32],[.18,.63,.06,.26],[-.15,.67,-.08,.25]]){
 sphere(scene,x+dx*s,.62*s+dy*s*.35,z+dz*s,r*s,finish.green);
 }
}
for(const [x,z,s] of [[8.65,4.05,.85],[11.18,4.02,.8],[11.2,6.2,.85],[8.63,6.23,.75]])tree(x,z,s);
for(let i=0;i<9;i++)sphere(scene,8.54+i*.35,.22,6.48,.15,finish.hedge);
// Jardineiras externas e iluminação de percurso
for(const [x,z] of [[-.45,.25],[-.4,5.9],[11.9,5.95]]){
 cylinder(scene,x,.03,z,.27,.33,finish.concrete);
 sphere(scene,x,.35,z,.28,finish.green);
}
// Design de interiores: quadros, cadeiras, objetos e detalhes de acabamento.
const artFrame=P('#252b2c',.55,.25), artCanvas=P('#c3ad8e',.95);
function artwork(x,y,z,w,h,room){
 box(scene,x,y,z,w,h,.045,artFrame,room);
 box(scene,x,y+.055,z+.027,w-.10,h-.12,.015,artCanvas,room);
 for(let k=0;k<4;k++)box(scene,x-w*.27+k*w*.18,y+.17+k*.04,z+.044,w*.08,.09,.015,finish.terracotta,room);
}
artwork(.28,1.03,1.7,.045,1.0,'Sala de Estar');
// Mesa de jantar com quatro cadeiras e assentos estofados na cozinha.
box(scene,5.47,.61,2.73,1.05,.065,.46,finish.walnut,'Cozinha');
for(const xx of [4.99,5.94]){
 box(scene,xx,.24,3.17,.36,.10,.34,finish.cream,'Cozinha');
 box(scene,xx,.43,3.33,.36,.42,.08,finish.walnut,'Cozinha');
 for(const zz of [3.04,3.3])cylinder(scene,xx,.18,zz,.025,.21,finish.black);
}
// Livros e decoração de estante no hall.
for(let i=0;i<6;i++)box(scene,7.38+i*.045,1.01,1.31,.038,.13+(i%3)*.05,.19,i%2?finish.ivory:finish.terracotta,'Hall');
// Tapetes têxteis nos dormitórios, com contraste suave.
const rug2050=P('#8b958e',1);
box(scene,1.55,.18,5.82,2.12,.012,.64,rug2050,'Quarto Casal');
box(scene,4.42,.18,5.87,1.45,.012,.55,finish.sand,'Quarto Solteiro');
// Guarda-roupas com portas, divisórias e puxadores.
for(const [room,x,z,w] of [['Quarto Casal',2.91,4.32,.39],['Quarto Solteiro',5.77,4.33,.35]]){
 box(scene,x,.19,z,w,1.84,.70,finish.walnut,room);
 for(const dz of [-.2,.2])box(scene,x+w*.18,1.15,z+dz,.02,.29,.018,finish.bronze,room);
}
// Espelhos com superfície metálica suave, toalhas e registros dos banheiros.
for(const [room,z] of [['Banheiro Social',4.25],['Banheiro Suíte',5.73]]){
 box(scene,6.35,1.42,z-.7,.55,.73,.025,finish.black,room);
 box(scene,6.35,1.46,z-.678,.49,.65,.008,finish.glass,room);
 box(scene,7.14,.74,z+.4,.07,.38,.30,finish.ivory,room);
}
// Faixas de LED sob armários e luz de apoio, visíveis no modo noite.
const stripMat=new THREE.MeshStandardMaterial({color:'#e8cda1',emissive:'#ffb45a',emissiveIntensity:.34});
box(scene,5.48,1.52,.58,2.5,.018,.025,stripMat,'Cozinha');
box(scene,3.63,.28,1.52,.02,.035,1.15,stripMat,'Sala de Estar');
// Lâminas da fachada e jardim frontal.
for(let i=0;i<11;i++)box(scene,8.38+i*.08,.18,-.14,.035,2.07,.065,finish.walnut,'Hall');
for(let i=0;i<16;i++){
 const x=-.55+i*.32;
 if(x>3.7)break;
 sphere(scene,x,.04,-.7,.11+(i%3)*.025,finish.hedge);
}
// Piscina com linhas de borda, escada e lâmina de água.
for(const zz of [4.31,5.88])box(scene,10.03,.30,zz,2.42,.06,.10,finish.limestone,'Quintal');
for(const xx of [8.83,11.23])box(scene,xx,.30,5.1,.10,.06,1.65,finish.limestone,'Quintal');
for(let i=0;i<3;i++)box(scene,9.18,.29+i*.015,4.62+i*.17,.52,.025,.10,finish.ivory,'Quintal');
// ================================================================
// REFINAMENTO VISUAL 2050 | detalhes externos sem mudar a planta
// ================================================================
// Passeio frontal em placas de concreto com juntas e gramado lateral.
const landscape = {
  paver: P('#b9b6a9',.94),
  gravel: P('#8e938b',1),
  olive: P('#44694a',1),
  leafLight: P('#68865c',1),
  wood: P('#82664c',.77),
  led: new THREE.MeshStandardMaterial({color:'#f4d5a2',emissive:'#e9a74d',emissiveIntensity:.30}),
  waterHighlight: new THREE.MeshBasicMaterial({color:'#b1f1ed',transparent:true,opacity:.24,depthWrite:false})
};
// O caminho fica fora da planta: não encobre pisos nem móveis.
for(let i=0;i<9;i++){
  const xx=.15+i*.82;
  box(scene,xx,-.13,-.87,.70,.055,.49,landscape.paver);
}
// Bordas com pedras e vegetação rasteira no jardim frontal.
for(let i=0;i<26;i++){
  const xx=-.45+i*.47;
  if(xx>11.65)break;
  box(scene,xx,-.12,-1.33,.23,.045,.18,landscape.gravel);
  if(i%2===0) sphere(scene,xx,-.09,-1.58,.12+(i%3)*.018,landscape.olive);
}
// Jardineiras de arquitetura contemporânea, longe das aberturas.
for(const [xx,zz] of [[.25,-.30],[3.52,-.30],[11.78,3.1]]){
  box(scene,xx,-.02,zz,.45,.37,.38,finish.concrete);
  for(let j=0;j<3;j++){
    const leaf=new THREE.Mesh(new THREE.ConeGeometry(.12,.56,7),j===1?landscape.leafLight:landscape.olive);
    leaf.position.set(xx+(j-1)*.11,.46,zz);leaf.castShadow=true;scene.add(leaf);
  }
}
// Balizadores de caminho: luz suave à noite e volume legível de dia.
const pathLamps=[];
for(const xx of [1.0,3.4,6.0,8.7,11.0]){
  box(scene,xx,-.10,-1.95,.10,.36,.10,finish.black);
  box(scene,xx,.25,-1.95,.11,.075,.11,landscape.led);
  const glow=new THREE.PointLight(0xffc58c,0,1.6,2);
  glow.position.set(xx,.35,-1.95);scene.add(glow);pathLamps.push(glow);
}
// Ripas discretas na borda do deck, reforçando o acabamento da piscina.
for(let i=0;i<9;i++){
  const xx=8.77+i*.30;
  box(scene,xx,.19,3.83,.20,.023,.50,landscape.wood,'Quintal');
}
// Reflexos rasos sobre a água: não exigem texturas externas nem shaders.
const waterGlints=[];
for(let i=0;i<8;i++){
  const xx=9.25+(i%4)*.43;
  const zz=4.72+Math.floor(i/4)*.66;
  const glint=box(scene,xx,.328,zz,.24,.002,.014,landscape.waterHighlight.clone(),'Quintal');
  glint.rotation.y=(i%3-1)*.22;
  waterGlints.push(glint);
}
// Iluminação indireta arquitetônica no muro externo frontal.
const facadeAccent=P('#80684e',.8);
for(const xx of [3.68,6.84,11.30]){
  box(scene,xx,1.08,-.105,.07,.46,.09,facadeAccent);
  box(scene,xx,1.52,-.13,.10,.035,.11,landscape.led);
}

// Telhado contemporâneo plano, com platibanda, removível para exploração
const roofGroup=new THREE.Group();scene.add(roofGroup);
const roofMat=P('#626b6b',.75);
box(roofGroup,5.75,2.44,3.25,12.05,.16,7.05,roofMat);
for(const [x,z,w,d] of [[5.75,-.31,12.1,.17],[5.75,6.81,12.1,.17],[-.26,3.25,.17,7.1],[11.76,3.25,.17,7.1]]){
 box(roofGroup,x,2.48,z,w,.35,d,finish.slate);
}
// Pergolado da garagem, como detalhe de fachada
for(let i=0;i<8;i++)box(roofGroup,8.62+i*.41,2.84,1.7,.10,.12,3.65,finish.walnut);
roofGroup.visible=false;
// Marcadores de automação e iluminação preservados
const sensorMarkers=[];
const sensorMaterial=new THREE.MeshBasicMaterial({color:'#00c8ff'});
// Centros dos ambientes
const roomCenters = {
    "Sala de Estar": [2, 1.7],
    "Cozinha": [5.5, 1.7],
    "Quarto Casal": [1.6, 5],
    "Quarto Solteiro": [4.6, 5],
    "Banheiro Social": [6.7, 4.2],
    "Banheiro Suíte": [6.7, 5.7],
    "Hall": [7.7, 1.7],
    "Garagem": [10, 1.7],
    "Quintal": [10, 5.1]
};

for (const [room, center] of Object.entries(roomCenters)) {
    makeLight(room, center[0], center[1]);
    const marker = new THREE.Mesh(new THREE.SphereGeometry(.14,12,10), sensorMaterial);
    marker.position.set(center[0],2.48,center[1]);
    marker.visible = false;
    marker.userData.room = room;
    scene.add(marker);
    sensorMarkers.push(marker);
}

// Atualização das luzes
function atualizarLuzes() {
    for (const [room, objects] of Object.entries(lightObjects)) {
        const on = !!initialLights[room];

        for (const item of objects) {
            item.lamp.intensity = on ? 2.5 : 0;
            item.bulb.material.color.set(
                on ? "#fff0b2" : "#526575"
            );
        }
    }
}

atualizarLuzes();

const label = document.getElementById("room-label");

renderer.domElement.addEventListener("click", (event) => {
    const rect = renderer.domElement.getBoundingClientRect();

    mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

    raycaster.setFromCamera(mouse, camera);

    const hits = raycaster.intersectObjects(scene.children, true);
    let selected = null;

    for (const hit of hits) {
        if (hit.object.userData.room) {
            selected = hit.object.userData.room;
            break;
        }
    }

    if (selected) {
        label.textContent = "Ambiente: " + selected + (initialLights[selected] ? " · Luz ligada" : " · Luz desligada");
    }
});

// Controles de visualização da casa.
const raioXMaterial = new THREE.MeshPhysicalMaterial({
    color: '#89d8ef', transparent: true, opacity: .20,
    depthWrite: false, side: THREE.DoubleSide, roughness: .35
});
let raioXAtivo = false;
let sensoresAtivos = false;
let telhadoAtivo = false;
let interiorAtivo = false;
function atualizarModos() {
    for (const parede of architecturalWalls) {
        parede.material = raioXAtivo ? raioXMaterial : materials.wall;
        parede.castShadow = !raioXAtivo;
    }
    roofGroup.visible = telhadoAtivo && !raioXAtivo && !interiorAtivo;
    for (const marcador of sensorMarkers) marcador.visible = sensoresAtivos;
    document.getElementById('xray').classList.toggle('active', raioXAtivo);
    document.getElementById('smart').classList.toggle('active', sensoresAtivos);
    document.getElementById('roof').classList.toggle('active', telhadoAtivo && !interiorAtivo);
    document.getElementById('interior').classList.toggle('active', interiorAtivo);
    document.getElementById('roof').textContent = telhadoAtivo ? 'Ocultar telhado' : 'Mostrar telhado';
}
document.getElementById('xray').onclick = () => { raioXAtivo = !raioXAtivo; atualizarModos(); };
document.getElementById('smart').onclick = () => { sensoresAtivos = !sensoresAtivos; atualizarModos(); };
document.getElementById('roof').onclick = () => {
    telhadoAtivo = !telhadoAtivo;
    interiorAtivo = false;
    atualizarModos();
};
document.getElementById('interior').onclick = () => {
    interiorAtivo = !interiorAtivo;
    if (interiorAtivo) {
        telhadoAtivo = false;
        camera.position.set(11, 12.5, 13);
        controls.target.set(5.6, 0.35, 3.6);
        controls.update();
    } else {
        definirVista3D();
    }
    atualizarModos();
};

// Câmera
function definirVista3D() {
    camera.position.set(16, 13, 17);
    controls.target.set(6, 0, 4);
    controls.update();
}

document.getElementById("viewTop").onclick = () => {
    // Vista superior sempre exibe os cômodos, sem cobertura bloqueando.
    interiorAtivo = true;
    atualizarModos();
    camera.position.set(6, 22, 4);
    controls.target.set(6, 0, 4);
    controls.update();
};

document.getElementById("view3d").onclick = () => {
    telhadoAtivo = false;
    interiorAtivo = false;
    atualizarModos();
    definirVista3D();
};
document.getElementById("reset").onclick = definirVista3D;

// Dia e noite
document.getElementById("day").onclick = () => {
    scene.background.set("#d4eafa");
    scene.fog.color.set("#d4eafa");
    ambient.intensity = 0.72;
    fillLight.intensity = 0.22;
    renderer.toneMappingExposure = 0.72;
    sun.intensity = 1.10;
    for(const lamp of pathLamps) lamp.intensity=0;
    document.getElementById('day').classList.add('active');
    document.getElementById('night').classList.remove('active');
};

document.getElementById("night").onclick = () => {
    scene.background.set("#071426");
    scene.fog.color.set("#071426");
    ambient.intensity = 0.40;
    fillLight.intensity = .13;
    renderer.toneMappingExposure = 0.88;
    sun.intensity = 0.20;
    for(const lamp of pathLamps) lamp.intensity=.55;
    document.getElementById('night').classList.add('active');
    document.getElementById('day').classList.remove('active');
};

// Animação
function animate() {
    requestAnimationFrame(animate);
    controls.update();
    const tick=performance.now()*.00065;
    for(let i=0;i<waterGlints.length;i++){
      waterGlints[i].material.opacity=.14+.09*Math.sin(tick*2+i*.9);
    }
    renderer.render(scene, camera);
}

animate();

// Redimensionamento
window.addEventListener("resize", () => {
    const width = container.clientWidth;
    const height = container.clientHeight;

    camera.aspect = width / height;
    camera.updateProjectionMatrix();
    renderer.setSize(width, height);
});

</script>
</body>
</html>
"""

    return html.replace("__LIGHTS__", luzes)


def exibir_smart_home_3d():
    iniciar_estado()

    st.markdown("""
    <div style="
        background:linear-gradient(120deg,#07152b,#0b3454);
        border:1px solid #1b5c80;
        border-radius:16px;
        padding:20px;
        margin-bottom:15px;
    ">
        <div style="color:#43d5ff;font-size:12px;font-weight:800;
        letter-spacing:2px;">LUMINA AI | SMART HOME 2050</div>
        <h2 style="color:#f1f8ff;margin:6px 0;">
            🏠 Residência inteligente em 3D
        </h2>
        <p style="color:#b9d3e8;margin:0;">
            Explore a arquitetura, visualize os ambientes e acompanhe
            a automação residencial.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.caption(
        "Modelo arquitetônico demonstrativo. Os sensores e consumos "
        "ainda são simulados."
    )

    st.markdown("### 🎛️ Cenários da residência")

    cols = st.columns(4)

    for col, (scenario, rooms_on) in zip(cols, SCENARIOS.items()):
        with col:
            if st.button(
                scenario,
                key=f"cenario_3d_{scenario}",
                use_container_width=True,
            ):
                for room in ROOMS:
                    st.session_state.lumina_luzes[room] = (
                        room in rooms_on
                    )

                st.session_state.lumina_cenario = scenario
                st.rerun()

    st.caption(
        f"Cenário selecionado: {st.session_state.lumina_cenario}"
    )

    st.markdown("### 🏡 Explore sua casa")
    st.caption("Novo: Raio-X para enxergar os cômodos, Mostrar telhado para ver a fachada e Sensores para destacar a automação. O modo Dia usa iluminação arquitetônica equilibrada.")

    html = gerar_casa_3d()

    components.html(
        html,
        height=730,
        scrolling=False,
    )

    st.caption(
        "Use o mouse para girar a casa, aproximar a câmera e selecionar "
        "os ambientes."
    )

    st.divider()

    st.markdown("### 💡 Controle de iluminação")

    cols = st.columns(3)

    for index, room in enumerate(ROOMS):
        with cols[index % 3]:
            chave = f"controle_3d_{room}"
            # A sincronização acontece antes de instanciar o widget.
            # Assim, botões de cenário e interruptores mostram o mesmo estado.
            if st.session_state.get("lumina_ultimo_cenario_sync") != st.session_state.lumina_cenario:
                st.session_state[chave] = st.session_state.lumina_luzes[room]
            estado = st.toggle(room, key=chave)
            st.session_state.lumina_luzes[room] = estado

    st.session_state.lumina_ultimo_cenario_sync = st.session_state.lumina_cenario

    st.divider()

    st.markdown("### 📡 Sensores virtuais")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.slider(
            "Temperatura interna (°C)",
            15,
            40,
            key="lumina_temperatura",
        )

    with c2:
        st.slider(
            "Consumo de água (m³)",
            0.0,
            50.0,
            step=0.5,
            key="lumina_agua",
        )

    with c3:
        st.toggle(
            "Presença detectada",
            key="lumina_presenca",
        )

    st.toggle(
        "Aparelhos domésticos ligados",
        key="lumina_aparelhos",
    )

    resumo = obter_resumo_consumo()

    a, b, c, d = st.columns(4)

    a.metric(
        "💡 Iluminação",
        f"{resumo['potencia_luzes_w']} W"
    )

    b.metric(
        "🔌 Aparelhos",
        f"{resumo['potencia_aparelhos_w']} W"
    )

    c.metric(
        "⚡ Potência estimada",
        f"{resumo['potencia_total_w']} W"
    )

    d.metric(
        "🌡️ Temperatura",
        f"{resumo['temperatura_c']} °C"
    )

    if resumo["temperatura_c"] >= 30:
        st.warning("Temperatura elevada na simulação.")

    if resumo["agua_m3"] >= 20:
        st.warning("Consumo de água elevado na simulação.")

    if resumo["potencia_total_w"] > 1000:
        st.warning(
            "Potência estimada acima de 1.000 W. "
            "Verifique os aparelhos simulados."
        )

    st.info(
        "Os controles de iluminação e sensores desta versão são "
        "demonstrativos. A conexão com dispositivos físicos será "
        "uma etapa futura do projeto."
    )
