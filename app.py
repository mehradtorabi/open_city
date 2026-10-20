from flask import Flask, Response

app = Flask(__name__)

HTML = r"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
<title>3D City · Toon UI</title>
<style>
:root{
 --toon-bg: rgba(15,25,40,.85);
 --toon-border: rgba(255,255,255,.15);
 --toon-accent: #5cf0be;
 --toon-yellow: #ffd966;
 --toon-pink: #ff6b9d;
 --toon-blue: #7fd8ff;
 --toon-shadow: 0 8px 32px rgba(0,0,0,.5);
 --toon-radius: 16px;
}
*{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
html,body{margin:0;overflow:hidden;background:#0a1420;color:#e8f0fa;
 font-family:'Segoe UI',Tahoma,Arial,sans-serif;height:100%;width:100%}
canvas#gl{display:block;position:fixed;inset:0}

/* === HUD top-center: 4 separate toon cards === */
#hud{
 position:fixed;top:12px;left:50%;transform:translateX(-50%);
 z-index:10;display:flex;gap:10px;pointer-events:none;
}
.hud-card{
 background:var(--toon-bg);border:2px solid var(--toon-border);
 border-radius:var(--toon-radius);padding:8px 14px;
 backdrop-filter:blur(20px);box-shadow:var(--toon-shadow);
 display:flex;flex-direction:column;align-items:center;
 min-width:70px;transition:transform .2s,border-color .2s;
}
.hud-card:hover{transform:translateY(-2px);border-color:var(--toon-accent)}
.hud-card .label{
 font-size:9px;text-transform:uppercase;letter-spacing:.8px;
 opacity:.7;margin-bottom:2px;color:var(--toon-blue);
}
.hud-card .value{
 font-size:22px;font-weight:800;line-height:1.1;
 font-variant-numeric:tabular-nums;color:var(--toon-accent);
}
.hud-card .value small{font-size:11px;font-weight:400;color:#9fb0c0}
.hud-card.gear .value{color:var(--toon-yellow)}
.hud-card.mode .value{font-size:13px;color:#fff}
.hud-card.vehicle .value{font-size:12px;color:var(--toon-blue)}
.rpm-bar{
 width:100%;height:5px;background:#1a2530;border-radius:99px;
 overflow:hidden;margin-top:4px;
}
.rpm-bar>div{
 height:100%;width:0%;
 background:linear-gradient(90deg,var(--toon-accent),var(--toon-yellow),var(--toon-pink));
 transition:width .08s linear;
}

/* === Left panel (moved #right to left side) === */
#right{
 position:fixed;top:80px;left:12px;right:auto;width:210px;
 max-height:calc(100dvh - 160px);overflow-y:auto;
 background:var(--toon-bg);border:2px solid var(--toon-border);
 border-radius:var(--toon-radius);padding:12px;
 backdrop-filter:blur(20px);box-shadow:var(--toon-shadow);
 z-index:8;font-size:11px;
}
#right h4{
 margin:0 0 8px;font-size:10px;color:var(--toon-blue);
 text-transform:uppercase;letter-spacing:1px;font-weight:700;
}
#rightToggle{
 position:absolute;top:8px;inset-inline-end:8px;
 width:26px;height:26px;padding:0;border-radius:8px;font-size:13px;z-index:1;
}
#right.collapsed{width:auto;padding:0}
#right.collapsed>*:not(#rightToggle){display:none}
.row{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:10px}

button{
 background:#182838;color:#e8f0fa;border:1.5px solid var(--toon-border);
 border-radius:10px;padding:5px 9px;cursor:pointer;
 font-family:inherit;font-size:11px;font-weight:600;
 transition:all .15s;touch-action:manipulation;
}
button:hover{background:#223650;border-color:var(--toon-accent)}
button.active{
 background:var(--toon-accent);border-color:var(--toon-accent);
 color:#0a1420;
}
.swatch{
 display:inline-block;width:18px;height:18px;border-radius:6px;
 border:2px solid var(--toon-border);cursor:pointer;transition:transform .1s;
}
.swatch:hover{transform:scale(1.2)}
.swatch.sel{border-color:var(--toon-accent);box-shadow:0 0 10px var(--toon-accent)}

/* Radio stations */
#radio{margin-top:4px}
.station{
 display:flex;justify-content:space-between;align-items:center;
 padding:6px 10px;border-radius:10px;background:#101d2b;
 border:1px solid var(--toon-border);margin-bottom:3px;
 cursor:pointer;font-size:11px;transition:.15s;
}
.station:hover{background:#16283a}
.station.active{background:#0a5a4a;border-color:var(--toon-accent)}
.eq{display:none;gap:2px;align-items:end;height:12px;width:16px}
.station.active .eq{display:inline-flex}
.eq span{display:block;width:2px;background:var(--toon-accent);border-radius:1px;
 animation:eq .6s ease-in-out infinite}
.eq span:nth-child(2){animation-delay:.15s}
.eq span:nth-child(3){animation-delay:.3s}
@keyframes eq{0%,100%{height:20%}50%{height:100%}}

/* === Minimap bottom-right === */
#minimap-wrap{
 position:fixed;bottom:14px;right:14px;z-index:9;
 width:200px;height:200px;border-radius:18px;overflow:hidden;
 border:3px solid var(--toon-border);background:#1a2418;
 box-shadow:var(--toon-shadow);backdrop-filter:blur(10px);
}
#map{width:100%;height:100%;display:block;border-radius:14px}
#minimap-label{
 position:absolute;top:6px;left:50%;transform:translateX(-50%);
 background:rgba(15,25,40,.9);padding:2px 10px;border-radius:99px;
 font-size:9px;font-weight:700;color:var(--toon-accent);
 letter-spacing:.5px;border:1px solid var(--toon-border);
 pointer-events:none;z-index:1;
}

/* === Help (bottom-left) === */
#help{
 position:fixed;bottom:14px;left:12px;z-index:7;
 font-size:10px;line-height:1.7;max-width:210px;padding:8px 10px;
 background:var(--toon-bg);border-radius:12px;
 border:1px solid var(--toon-border);opacity:.85;
}
#help kbd{
 background:#223650;border-radius:4px;padding:1px 5px;
 font-size:10px;border:1px solid var(--toon-border);font-family:monospace;
}

/* === Message (top-center under HUD) === */
#msg{
 position:fixed;top:100px;left:50%;transform:translateX(-50%);
 background:rgba(15,25,40,.9);padding:6px 16px;border-radius:99px;
 font-size:11px;border:1px solid var(--toon-border);z-index:6;
 display:none;white-space:nowrap;
}
#msg.show{display:block}

/* === Action (center) === */
#action{
 position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);
 z-index:15;background:rgba(15,25,40,.95);padding:14px 28px;
 border-radius:16px;border:2px solid var(--toon-accent);
 display:none;font-size:14px;font-weight:600;text-align:center;
 box-shadow:0 0 40px var(--toon-accent)44;
}

/* === Clock (mid-right) === */
#clock{
 position:fixed;top:50%;right:20px;transform:translateY(-50%);
 z-index:6;background:var(--toon-bg);border:2px solid var(--toon-border);
 border-radius:50%;width:50px;height:50px;
 display:grid;place-items:center;font-size:10px;font-weight:700;
 color:var(--toon-yellow);
}

/* === Touch controls === */
#touchControls{
 position:fixed;inset:auto 0 14px 0;z-index:9;display:none;
 justify-content:space-between;align-items:end;padding:0 14px;
 pointer-events:none;
}
.touch-cluster{display:flex;flex-direction:column;gap:6px;pointer-events:auto}
.touch-row{display:flex;gap:6px;justify-content:center}
.touch-btn{
 width:52px;height:52px;border-radius:16px;
 background:rgba(15,25,40,.85);border:2px solid var(--toon-border);
 font-size:18px;font-weight:bold;box-shadow:var(--toon-shadow);
 user-select:none;touch-action:none;display:grid;place-items:center;color:#fff;
}
.touch-btn.pressed,.touch-btn:active{
 background:var(--toon-accent);border-color:var(--toon-accent);
 color:#0a1420;transform:scale(.94);
}

/* === Start screen === */
#start{
 position:fixed;inset:0;z-index:30;
 background:linear-gradient(180deg,#0a1420ee,#0a1420cc);
 display:grid;place-items:center;
}
#startbox{
 background:linear-gradient(145deg,#172b42,#0c1929);
 border:2px solid var(--toon-border);border-radius:24px;
 padding:30px 36px;text-align:center;max-width:440px;
 margin:16px;line-height:1.9;box-shadow:0 20px 80px #000a;
}
#startbox h2{margin:0 0 8px;color:var(--toon-accent);font-size:24px}
#startbox p{opacity:.8;margin:8px 0;font-size:13px}
#go{
 background:var(--toon-accent);color:#0a1420;
 padding:12px 44px;font-size:15px;border-radius:12px;
 margin-top:12px;font-weight:800;border:none;
}
#go:hover{background:#00ffb0}
#error{color:var(--toon-pink);font-size:11px;min-height:16px;white-space:pre-wrap}

/* === Shop modal === */
#shopModal{
 position:fixed;inset:0;z-index:20;background:#000a;
 display:none;place-items:center;padding:16px;
}
#shopModal.open{display:grid}
#shopBox{
 background:linear-gradient(145deg,#1e1e3a,#12122a);
 border:2px solid var(--toon-border);border-radius:20px;
 padding:22px;max-width:440px;width:100%;box-shadow:0 20px 60px #000c;
}
#shopBox h2{margin:0 0 14px;color:var(--toon-accent);font-size:18px}
#shopItems{display:grid;gap:8px}
.shopItem{
 background:#12121f;border:1.5px solid var(--toon-border);
 border-radius:12px;padding:10px 14px;
 display:flex;justify-content:space-between;align-items:center;
 font-size:12px;gap:10px;
}
.shopItem b{color:var(--toon-yellow)}
#shopExit{
 width:100%;margin-top:12px;padding:10px;
 background:#a13535;border-color:var(--toon-pink);font-weight:700;
}
#shopExit:hover{background:#c14040}

/* === Language button (top-right) === */
#langBtn{
 position:fixed;top:12px;right:14px;z-index:12;
 background:var(--toon-bg);border:2px solid var(--toon-border);
 padding:5px 14px;border-radius:99px;
 font-size:11px;font-weight:700;color:#fff;cursor:pointer;
 backdrop-filter:blur(20px);
}
#langBtn:hover{background:#223650;border-color:var(--toon-accent)}

/* === Responsive === */
@media (pointer:coarse),(max-width:900px){
 #touchControls{display:flex}
 #help{display:none}
 #right{width:160px;max-height:40dvh;padding:8px;font-size:10px;top:70px}
 #right h4{font-size:9px}
 #right button{font-size:9px;padding:3px 5px}
 #hud{gap:6px;top:8px}
 .hud-card{padding:5px 9px;min-width:55px}
 .hud-card .value{font-size:17px}
 .hud-card .label{font-size:8px}
 #minimap-wrap{width:130px;height:130px;bottom:80px;right:8px}
 #minimap-label{display:none}
 #msg{display:none}
 #clock{display:none}
 #langBtn{font-size:10px;padding:4px 10px;top:8px;right:8px}
}
@media (max-width:600px){
 #right{width:140px}
 #minimap-wrap{width:110px;height:110px}
}
</style>
</head>
<body>

<canvas id="gl"></canvas>

<button id="langBtn">EN</button>

<!-- HUD: 4 toon cards top-center -->
<div id="hud">
 <div class="hud-card">
  <div class="label" data-i18n="speed">سرعت</div>
  <div class="value"><span id="speed">0</span> <small>km/h</small></div>
  <div class="rpm-bar"><div id="rpmBar"></div></div>
 </div>
 <div class="hud-card gear">
  <div class="label" data-i18n="gear">دنده</div>
  <div class="value" id="gear">N</div>
 </div>
 <div class="hud-card mode">
  <div class="label" data-i18n="mode">وضعیت</div>
  <div class="value" id="mode" data-i18n="inCar">داخل خودرو</div>
 </div>
 <div class="hud-card vehicle">
  <div class="label" data-i18n="veh">وسیله</div>
  <div class="value" id="vname">اسپرت</div>
 </div>
</div>

<!-- Left panel: vehicles, colors, radio -->
<div id="right">
 <button id="rightToggle" title="toggle">☰</button>
 <h4 data-i18n="vehicles">وسایل نقلیه</h4>
 <div class="row">
  <button data-v="sport" class="active" data-i18n="vSport">اسپرت</button>
  <button data-v="moto" data-i18n="vMoto">موتور</button>
  <button data-v="sedan" data-i18n="vSedan">سواری</button>
  <button data-v="bus" data-i18n="vBus">اتوبوس</button>
  <button data-v="offroad" data-i18n="vOff">آفرود</button>
  <button data-v="taxi" data-i18n="vTaxi">تاکسی</button>
  <button data-v="truck" data-i18n="vTruck">کامیون</button>
  <button data-v="police" data-i18n="vPolice">پلیس</button>
  <button data-v="ambulance" data-i18n="vAmb">آمبولانس</button>
  <button data-v="plane">✈️</button>
 </div>
 <h4 data-i18n="color">رنگ</h4>
 <div id="palette" style="display:flex;flex-wrap:wrap;gap:3px;margin-bottom:10px"></div>
 <h4 data-i18n="radio">رادیو</h4>
 <div id="radio">
  <div class="station" data-station="0"><span>🎵 Synth</span><span class="eq"><span></span><span></span><span></span></span></div>
  <div class="station" data-station="1"><span>🌙 Chill</span><span class="eq"><span></span><span></span><span></span></span></div>
  <div class="station" data-station="2"><span>🥁 Techno</span><span class="eq"><span></span><span></span><span></span></span></div>
 </div>
</div>

<!-- Minimap bottom-right -->
<div id="minimap-wrap">
 <div id="minimap-label">MAP</div>
 <canvas id="map" width="240" height="240"></canvas>
</div>

<div id="help">
 <kbd>W</kbd><kbd>S</kbd><kbd>A</kbd><kbd>D</kbd> ·
 <kbd>Shift</kbd> <span data-i18n="boost">شتاب</span> ·
 <kbd>E</kbd> <span data-i18n="interact">تعامل</span> ·
 <kbd>R</kbd> <span data-i18n="reset">ریست</span> ·
 <kbd>C</kbd> <span data-i18n="cam">دوربین</span> ·
 <kbd>H</kbd> <span data-i18n="horn">بوق</span>
</div>

<div id="msg"></div>

<div id="clock"><span id="clockTxt">۰۸:۰۰</span></div>

<div id="touchControls">
 <div class="touch-cluster">
  <div class="touch-row"><button class="touch-btn" data-key="w">▲</button></div>
  <div class="touch-row">
   <button class="touch-btn" data-key="a">◀</button>
   <button class="touch-btn" data-key="s">▼</button>
   <button class="touch-btn" data-key="d">▶</button>
  </div>
 </div>
 <div class="touch-cluster">
  <div class="touch-row">
   <button class="touch-btn" data-key="shift">⚡</button>
   <button class="touch-btn" data-action="interact">E</button>
   <button class="touch-btn" data-action="reset">↺</button>
  </div>
 </div>
</div>

<div id="action"></div>

<div id="shopModal">
 <div id="shopBox">
  <h2 id="shopTitle">فروشگاه</h2>
  <div id="shopItems"></div>
  <button id="shopExit">خروج</button>
 </div>
</div>

<div id="start">
 <div id="startbox">
  <h2 data-i18n="title">🏙 شهر سه‌بعدی</h2>
  <p data-i18n="subtitle">دو شهر، پل، رودخانه، سد، فرودگاه و نیروگاه. ترافیک زنده.</p>
  <p id="error"></p>
  <button id="go" data-i18n="start">شروع بازی</button>
 </div>
</div>

<script>
window.gameReady=false;window.startRequested=false;
document.getElementById('go').onclick=()=>{
 if(!window.gameReady){document.getElementById('error').textContent='...';return}
 window.startRequested=true;
 document.getElementById('start').style.display='none';
 if(window.initAudio) window.initAudio();
};
window.addEventListener('error',e=>{
 if(!window.gameReady)document.getElementById('error').textContent='خطا: '+(e.message||'');
});
</script>

<script type="module">
import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

try {

// ============================================================
// i18n
// ============================================================
const I18N={
 fa:{
  title:'🏙 شهر سه‌بعدی', subtitle:'دو شهر، پل، رودخانه، سد، فرودگاه و نیروگاه. ترافیک زنده.',
  start:'شروع بازی', speed:'سرعت', gear:'دنده', mode:'وضعیت', veh:'وسیله',
  inCar:'داخل خودرو', onFoot:'پیاده', vehicles:'وسایل نقلیه', color:'رنگ',
  radio:'رادیو', welcome:'به شهر خوش آمدی!', boost:'شتاب', interact:'تعامل',
  reset:'ریست', cam:'دوربین', horn:'بوق',
  vSport:'اسپرت',vMoto:'موتور',vSedan:'سواری',vBus:'اتوبوس',vOff:'آفرود',vTaxi:'تاکسی',
  vTruck:'کامیون',vPolice:'پلیس',vAmb:'آمبولانس',
  buy:'خرید', shopTitle:'فروشگاه', noMoney:'پول کافی نیست',
 },
 en:{
  title:'🏙 3D City', subtitle:'Two cities, bridge, river, dam, airport, power plant. Live traffic.',
  start:'Start Game', speed:'Speed', gear:'Gear', mode:'Mode', veh:'Vehicle',
  inCar:'In Car', onFoot:'On Foot', vehicles:'Vehicles', color:'Color',
  radio:'Radio', welcome:'Welcome to the city!', boost:'Boost', interact:'Interact',
  reset:'Reset', cam:'Camera', horn:'Horn',
  vSport:'Sport',vMoto:'Moto',vSedan:'Sedan',vBus:'Bus',vOff:'Offroad',vTaxi:'Taxi',
  vTruck:'Truck',vPolice:'Police',vAmb:'Ambulance',
  buy:'Buy', shopTitle:'Shop', noMoney:'Not enough money',
 }
};
let lang='fa';
const t=k=>I18N[lang][k]||k;
function applyLang(){
 document.documentElement.dir=lang==='fa'?'rtl':'ltr';
 document.documentElement.lang=lang;
 document.querySelectorAll('[data-i18n]').forEach(el=>{el.textContent=t(el.dataset.i18n)});
 document.getElementById('mode').textContent=t(onFoot?'onFoot':'inCar');
 document.getElementById('langBtn').textContent=lang==='fa'?'EN':'فا';
}

// ============================================================
// THREE setup
// ============================================================
const $=id=>document.getElementById(id);
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));

const scene=new THREE.Scene();
scene.fog=new THREE.Fog(0xc4d8e8,900,3200);

const camera=new THREE.PerspectiveCamera(68,innerWidth/innerHeight,.1,6000);
const renderer=new THREE.WebGLRenderer({canvas:$('gl'),antialias:false,powerPreference:'high-performance'});
renderer.setSize(innerWidth,innerHeight);
renderer.setPixelRatio(Math.min(devicePixelRatio,1));
renderer.outputColorSpace=THREE.SRGBColorSpace;

addEventListener('resize',()=>{
 camera.aspect=innerWidth/innerHeight;camera.updateProjectionMatrix();
 renderer.setSize(innerWidth,innerHeight);
});

// Sky
const skyMat=new THREE.ShaderMaterial({
 side:THREE.BackSide,depthWrite:false,fog:false,
 uniforms:{top:{value:new THREE.Color(0x3b7ac4)},bot:{value:new THREE.Color(0xd8e8f2)},
   sunDir:{value:new THREE.Vector3(0,1,0)}},
 vertexShader:'varying vec3 vP;void main(){vP=position;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.);}',
 fragmentShader:`varying vec3 vP;uniform vec3 top;uniform vec3 bot;uniform vec3 sunDir;
 void main(){vec3 d=normalize(vP);float h=d.y;
  vec3 c=mix(bot,top,smoothstep(-0.15,0.7,h));
  float s=max(0.,dot(d,normalize(sunDir)));
  c+=vec3(1.,.8,.4)*pow(s,120.)*1.3;gl_FragColor=vec4(c,1.);}`
});
scene.add(new THREE.Mesh(new THREE.SphereGeometry(3500,24,12),skyMat));

// Stars
const starGeo=new THREE.BufferGeometry();
const sPos=[];
for(let i=0;i<600;i++){
 const th=Math.random()*Math.PI*2,ph=Math.acos(2*Math.random()-1),r=3200;
 sPos.push(r*Math.sin(ph)*Math.cos(th),r*Math.cos(ph)*.6+300,r*Math.sin(ph)*Math.sin(th));
}
starGeo.setAttribute('position',new THREE.Float32BufferAttribute(sPos,3));
const starMat=new THREE.PointsMaterial({color:0xffffff,size:3,transparent:true,opacity:0,fog:false});
scene.add(new THREE.Points(starGeo,starMat));

// Lights
const hemi=new THREE.HemisphereLight(0xffffff,0x6b7a55,1.1);scene.add(hemi);
const ambient=new THREE.AmbientLight(0xffffff,.35);scene.add(ambient);
const sun=new THREE.DirectionalLight(0xfff4e0,1.7);sun.position.set(-150,260,120);scene.add(sun);
const moon=new THREE.DirectionalLight(0xa0c0ff,.4);moon.position.set(200,180,-100);scene.add(moon);

// Clouds
const cloudGeo=new THREE.SphereGeometry(1,6,5);
const cloudMat=new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:.55,fog:false});
const clouds=[];
for(let i=0;i<14;i++){
 const g=new THREE.Group();
 for(let j=0;j<4;j++){
  const m=new THREE.Mesh(cloudGeo,cloudMat);
  m.position.set((Math.random()-.5)*46,(Math.random()-.5)*9,(Math.random()-.5)*36);
  m.scale.set(14+Math.random()*14,6+Math.random()*5,14+Math.random()*10);
  g.add(m);
 }
 g.position.set((Math.random()-.5)*4000,300+Math.random()*100,(Math.random()-.5)*4000);
 scene.add(g);clouds.push(g);
}

// ============================================================
// Geometry helpers
// ============================================================
function whiteCol(g){
 const n=g.attributes.position.count;
 g.setAttribute('color',new THREE.BufferAttribute(new Float32Array(n*3).fill(1),3));
 return g;
}
const boxGeo=whiteCol(new THREE.BoxGeometry(1,1,1));
const sphereGeo=whiteCol(new THREE.SphereGeometry(1,10,7));
const cylGeo=whiteCol(new THREE.CylinderGeometry(1,1,1,12));
const pyramidGeo=whiteCol(new THREE.CylinderGeometry(0,1,1,4));
const planeGeo=whiteCol(new THREE.PlaneGeometry(1,1));
const lampGeo=whiteCol(new THREE.SphereGeometry(1,6,4));

const mat=(c,r=.85)=>new THREE.MeshStandardMaterial({color:c,roughness:r});
const instMat=()=>new THREE.MeshStandardMaterial({vertexColors:true,roughness:.85});
const instMatShiny=()=>new THREE.MeshStandardMaterial({vertexColors:true,roughness:.35,metalness:.4});

function add(parent,geo,material,x,y,z,sx,sy,sz,ry=0,rx=0){
 const o=new THREE.Mesh(geo,material);
 o.position.set(x,y,z);o.scale.set(sx,sy,sz);
 o.rotation.y=ry;o.rotation.x=rx;
 parent.add(o);return o;
}
function instances(geo,material,items,colored=false){
 if(!items||!items.length)return null;
 const m=new THREE.InstancedMesh(geo,colored?instMat():material,items.length);
 const d=new THREE.Object3D();
 items.forEach((o,i)=>{
  d.position.set(o.x,o.y,o.z);
  d.rotation.set(o.rx||0,o.ry||0,o.rz||0);
  d.scale.set(o.sx,o.sy,o.sz);d.updateMatrix();
  m.setMatrixAt(i,d.matrix);
  if(colored&&o.color)m.setColorAt(i,new THREE.Color(o.color));
 });
 m.instanceMatrix.needsUpdate=true;
 if(m.instanceColor)m.instanceColor.needsUpdate=true;
 scene.add(m);return m;
}

// ============================================================
// Layout
// ============================================================
const ROAD_W=30, HR=15;
const RIVER_Z0=700, RIVER_Z1=900;
const HWY_X=60;

const roadsA=[-540,-420,-300,-180,-60,60,180,300,420,540];
const blocksA=[];
for(let bi=-4;bi<=4;bi++)for(let bj=-4;bj<=4;bj++)
 blocksA.push({x:bi*120,z:bj*120});

const roadsBX=[-240,-120,0,120,240];
const roadsBZ=[1320,1440,1560,1680,1800];
const blocksB=[];
for(const bx of [-180,-60,60,180])for(const bz of [1380,1500,1620,1740])
 blocksB.push({x:bx,z:bz});

const BLOCK_HALF=41;

const allRoadX=[],allRoadZ=[];
for(const r of roadsA){
 allRoadX.push({pos:r,z0:-540,z1:540});
 allRoadZ.push({pos:r,x0:-540,x1:540});
}
for(const r of roadsBX)allRoadX.push({pos:r,z0:1300,z1:1820});
for(const r of roadsBZ)allRoadZ.push({pos:r,x0:-240,x1:240});
allRoadX.push({pos:HWY_X,z0:-540,z1:1820});

// ============================================================
// Ground, river, dam
// ============================================================
add(scene,boxGeo,mat(0x6d9354),0,-.5,-1400,8000,1,2800);
add(scene,boxGeo,mat(0x6d9354),0,-.5,1600,8000,1,1700);
add(scene,boxGeo,new THREE.MeshStandardMaterial({color:0x1a4a7a,roughness:.15,metalness:.6}),
 0,-1.6,(RIVER_Z0+RIVER_Z1)/2,8000,1.2,RIVER_Z1-RIVER_Z0);
add(scene,boxGeo,mat(0x4a6a3a),0,-.4,RIVER_Z0-2,8000,.2,4);
add(scene,boxGeo,mat(0x4a6a3a),0,-.4,RIVER_Z1+2,8000,.2,4);

const damZ=790;
const concreteMat=mat(0xb8bcc0,.9);
add(scene,boxGeo,concreteMat,-380,-1,damZ,560,8,10);
add(scene,boxGeo,concreteMat,360,-1,damZ,560,8,10);
for(let i=0;i<6;i++){
 add(scene,boxGeo,mat(0x7a8288),-380+i*35,2.6,damZ-5.2,26,.6,1);
}
for(const x of [-380,360]){
 add(scene,boxGeo,mat(0xd0d4d8),x,6,damZ,5,14,7);
 add(scene,boxGeo,mat(0x2a4a6a),x,6.5,damZ+3.6,3,2,.2);
}
add(scene,boxGeo,new THREE.MeshStandardMaterial({color:0x2a6aa0,roughness:.2,metalness:.5,
 transparent:true,opacity:.7}),0,-.6,damZ+40,7000,.6,60);

// ============================================================
// Roads
// ============================================================
const ROAD_Y=0.03,ROAD_H=0.06;
const SIDEWALK_Y=0.11,SIDEWALK_H=0.22;
const LINE_Y=0.09,LINE_H=0.02;

const roadMat=mat(0x08080c,.95);
const walkMat=mat(0xa5a8ac,.9);
const whiteLine=mat(0xf5f5f0,.9);
const yellowLine=mat(0xf5c518,.9);

const roadItems=[],walkItems=[],whiteItems=[],yellowItems=[],crossItems=[];

function addRoadSegment(axis,pos,min,max){
 if(axis==='x'){
  roadItems.push({x:pos,y:ROAD_Y,z:(min+max)/2,sx:ROAD_W,sy:ROAD_H,sz:max-min});
  for(const s of [-1,1]){
   walkItems.push({x:pos+s*(HR+2),y:SIDEWALK_Y,z:(min+max)/2,sx:3.5,sy:SIDEWALK_H,sz:max-min});
   whiteItems.push({x:pos+s*(HR-1),y:LINE_Y,z:(min+max)/2,sx:.3,sy:LINE_H,sz:max-min});
  }
  yellowItems.push({x:pos-.6,y:LINE_Y,z:(min+max)/2,sx:.25,sy:LINE_H,sz:max-min});
  yellowItems.push({x:pos+.6,y:LINE_Y,z:(min+max)/2,sx:.25,sy:LINE_H,sz:max-min});
  for(let p=min+12;p<max-12;p+=16)
   for(const s of [-1,1])
    whiteItems.push({x:pos+s*7.5,y:LINE_Y,z:p,sx:.2,sy:LINE_H,sz:5});
 } else {
  roadItems.push({x:(min+max)/2,y:ROAD_Y,z:pos,sx:max-min,sy:ROAD_H,sz:ROAD_W});
  for(const s of [-1,1]){
   walkItems.push({x:(min+max)/2,y:SIDEWALK_Y,z:pos+s*(HR+2),sx:max-min,sy:SIDEWALK_H,sz:3.5});
   whiteItems.push({x:(min+max)/2,y:LINE_Y,z:pos+s*(HR-1),sx:max-min,sy:LINE_H,sz:.3});
  }
  yellowItems.push({x:(min+max)/2,y:LINE_Y,z:pos-.6,sx:max-min,sy:LINE_H,sz:.25});
  yellowItems.push({x:(min+max)/2,y:LINE_Y,z:pos+.6,sx:max-min,sy:LINE_H,sz:.25});
  for(let p=min+12;p<max-12;p+=16)
   for(const s of [-1,1])
    whiteItems.push({x:p,y:LINE_Y,z:pos+s*7.5,sx:5,sy:LINE_H,sz:.2});
 }
}
for(const r of roadsA){addRoadSegment('x',r,-540,540);addRoadSegment('z',r,-540,540)}
for(const r of roadsBX)addRoadSegment('x',r,1300,1820);
for(const r of roadsBZ)addRoadSegment('z',r,-240,240);
addRoadSegment('x',HWY_X,-540,1820);

const allIntersections=[];
for(const rx of roadsA)for(const rz of roadsA)allIntersections.push({x:rx,z:rz});
for(const rx of roadsBX)for(const rz of roadsBZ)allIntersections.push({x:rx,z:rz});
for(const it of allIntersections){
 for(let i=-3;i<=3;i++){
  crossItems.push({x:it.x-HR+2.5+i*2.5,y:LINE_Y,z:it.z-HR-2,sx:1.7,sy:LINE_H,sz:.9});
  crossItems.push({x:it.x-HR+2.5+i*2.5,y:LINE_Y,z:it.z+HR+2,sx:1.7,sy:LINE_H,sz:.9});
  crossItems.push({x:it.x-HR-2,y:LINE_Y,z:it.z-HR+2.5+i*2.5,sx:.9,sy:LINE_H,sz:1.7});
  crossItems.push({x:it.x+HR+2,y:LINE_Y,z:it.z-HR+2.5+i*2.5,sx:.9,sy:LINE_H,sz:1.7});
 }
}

instances(boxGeo,roadMat,roadItems);
instances(boxGeo,walkMat,walkItems);
instances(boxGeo,whiteLine,whiteItems);
instances(boxGeo,yellowLine,yellowItems);
instances(boxGeo,whiteLine,crossItems);

// Bridge railings
const railItems=[];
for(let z=RIVER_Z0-40;z<RIVER_Z1+40;z+=5){
 for(const s of [-1,1]){
  railItems.push({x:HWY_X+s*(HR-1),y:.7,z:z+2.5,sx:.15,sy:.8,sz:5});
  railItems.push({x:HWY_X+s*(HR-1),y:1.15,z:z+2.5,sx:.25,sy:.12,sz:5});
 }
}
instances(boxGeo,mat(0x555a60,.5),railItems);
for(let z=RIVER_Z0+15;z<RIVER_Z1;z+=25)
 for(const s of [-1,1])
  add(scene,cylGeo,mat(0x6a7078),HWY_X+s*(HR-5),-1,z,1.4,3.5,1.4);

// ============================================================
// Street lamps
// ============================================================
const lampPositions=[];
function addLampsAlong(axis,pos,min,max){
 for(let p=min+20;p<max-20;p+=50)
  for(const side of [-1,1]){
   const x=axis==='x'?pos+side*(HR+3.5):p;
   const z=axis==='x'?p:pos+side*(HR+3.5);
   lampPositions.push({x,z});
  }
}
for(const r of roadsA){addLampsAlong('x',r,-540,540);addLampsAlong('z',r,-540,540)}
for(const r of roadsBX)addLampsAlong('x',r,1300,1820);
for(const r of roadsBZ)addLampsAlong('z',r,-240,240);
addLampsAlong('x',HWY_X,-540,1820);

const lampPoles=[],lampHeads=[];
for(const L of lampPositions){
 lampPoles.push({x:L.x,y:3,z:L.z,sx:.18,sy:6,sz:.18});
 lampHeads.push({x:L.x,y:5.85,z:L.z,sx:.7,sy:.35,sz:.7});
}
instances(cylGeo,mat(0x33383d,.55),lampPoles);
instances(boxGeo,mat(0x22262a,.4),lampHeads);
const lampGlowMat=new THREE.MeshBasicMaterial({color:0xffee88,transparent:true,opacity:0,fog:false});
{
 const m=new THREE.InstancedMesh(sphereGeo,lampGlowMat,lampPositions.length);
 const d=new THREE.Object3D();
 lampPositions.forEach((L,i)=>{
  d.position.set(L.x,5.7,L.z);d.scale.setScalar(.55);d.updateMatrix();
  m.setMatrixAt(i,d.matrix);
 });
 m.instanceMatrix.needsUpdate=true;scene.add(m);
}

// ============================================================
// Buildings
// ============================================================
let seed=83171;
const rnd=()=>{seed=seed*16807%2147483647;return(seed-1)/2147483646};
const rr=(a,b)=>a+Math.random()*(b-a);

const paletteA=[0xead9be,0xdcc8a8,0xc9b28e,0xbba280,0xe8d5b4,0xd8ccb8,0xc6bca8,
 0xe2cfb2,0xd0c2aa,0xdfd3b6,0x8a9aaa,0x6a8aaa,0xb0c0d0,0xd0c0b0];
const paletteB=[0xe8b8a0,0xd8a888,0xc89878,0xe0c8a8,0xf0d8c0,0xa8b888];
const roofColors=[0x8a4a3a,0x7a5a4a,0x6a3a2a,0x5a3a2e,0x4a4a52,0x3a5a4a];
const glassColors=[0x4a6a8a,0x5a7a9a,0x6a8aaa];

const buildingTypes=[
 {key:'hospital',label:'بیمارستان',labelEn:'Hospital',bg:'#c9252c',fg:'#fff'},
 {key:'school',label:'مدرسه',labelEn:'School',bg:'#2461a8',fg:'#fff'},
 {key:'bank',label:'بانک',labelEn:'Bank',bg:'#0f6538',fg:'#f5d76e'},
 {key:'hotel',label:'هتل',labelEn:'Hotel',bg:'#5e3b1e',fg:'#f0d27a'},
 {key:'restaurant',label:'رستوران',labelEn:'Restaurant',bg:'#c9401a',fg:'#fff'},
 {key:'shop',label:'فروشگاه',labelEn:'Shop',bg:'#6e2f99',fg:'#fff'},
 {key:'office',label:'اداره',labelEn:'Office',bg:'#2a3b52',fg:'#e0e0e0'},
 {key:'cafe',label:'کافه',labelEn:'Cafe',bg:'#7d4a25',fg:'#fff0c8'},
 {key:'market',label:'سوپر',labelEn:'Market',bg:'#b52e2e',fg:'#fff'}
];
const signMats={};
function getSignMat(type){
 if(signMats[type.key])return signMats[type.key];
 const c=document.createElement('canvas');c.width=512;c.height=128;
 const ctx=c.getContext('2d');
 ctx.fillStyle='#0d0d0d';ctx.fillRect(0,0,512,128);
 ctx.fillStyle=type.bg;ctx.fillRect(6,6,500,116);
 ctx.fillStyle='rgba(255,255,255,.18)';ctx.fillRect(6,6,500,14);
 ctx.fillStyle=type.fg;ctx.font='bold 68px Tahoma,Arial';
 ctx.textAlign='center';ctx.textBaseline='middle';
 ctx.fillText(lang==='fa'?type.label:type.labelEn,256,68);
 const tex=new THREE.CanvasTexture(c);tex.colorSpace=THREE.SRGBColorSpace;
 const m=new THREE.MeshBasicMaterial({map:tex,fog:false});
 signMats[type.key]=m;return m;
}

const buildings=[],winFrames=[],winGlows=[],trees=[],crowns=[];
const acs=[],tanks=[],antennas=[],parapets=[],roofPyramids=[];
const awnings=[],shopFronts=[],doorBits=[],pillars=[],steps=[],balconies=[];
const bushes=[],benches=[],hydrants=[],cornices=[],sills=[],ledges=[];
const shops=[];
const signSlots={};for(const ty of buildingTypes)signSlots[ty.key]=[];
const grid=new Map();const GS=40;
function addColl(c){
 const k=Math.floor(c.x/GS)+','+Math.floor(c.z/GS);
 if(!grid.has(k))grid.set(k,[]);grid.get(k).push(c);
}
const awningColors=[0xb03535,0x2f6ea8,0x2f8a5c,0xc9991f,0x8a4ba0,0xd06030];
const shopColors=[0x357d96,0xa76b46,0x427c61,0x8d526a,0x8a5a30,0x2e6b55];

function onRoad(x,z,rx,rz){
 for(const r of allRoadX){
  if(z-rz<r.z1&&z+rz>r.z0){
   if(x-rx<r.pos+HR&&x+rx>r.pos-HR)return true;
  }
 }
 for(const r of allRoadZ){
  if(x-rx<r.x1&&x+rx>r.x0){
   if(z-rz<r.pos+HR&&z+rz>r.pos-HR)return true;
  }
 }
 return false;
}

function genBuildingBlock(bx,bz,isResidential){
 const half=BLOCK_HALF;
 const n=isResidential?(2+(rnd()*2|0)):(1+(rnd()*2.4|0));
 const quads=[[-half*.55,-half*.55],[half*.55,-half*.55],[-half*.55,half*.55],[half*.55,half*.55]];
 for(let i=quads.length-1;i>0;i--){const j=(rnd()*(i+1))|0;[quads[i],quads[j]]=[quads[j],quads[i]]}
 for(let k=0;k<n;k++){
  const [qx,qz]=quads[k];
  const maxSize=isResidential?half*.6:(n===1?half*1.2:half*.8);
  const w=rr(maxSize*.7,maxSize);
  const d=rr(maxSize*.7,maxSize);
  let x=bx+qx+rr(-2,2);
  let z=bz+qz+rr(-2,2);
  const h=isResidential?rr(6,11):(rnd()>.5?rr(22,55):rr(12,20));
  const tall=h>18;

  if(w/2<half-4){
   x=clamp(x,bx-half+w/2+4,bx+half-w/2-4);
   z=clamp(z,bz-half+d/2+4,bz+half-d/2-4);
  }else{x=bx;z=bz;}
  const rx=w/2+.8,rz=d/2+.8;
  if(onRoad(x,z,rx,rz))continue;

  const isGlass=tall&&rnd()>.55&&!isResidential;
  const color=isGlass?glassColors[(rnd()*glassColors.length)|0]
    :(isResidential?paletteB[(rnd()*paletteB.length)|0]:paletteA[(rnd()*paletteA.length)|0]);
  const roofColor=roofColors[(rnd()*roofColors.length)|0];
  buildings.push({x,y:h/2,z,sx:w,sy:h,sz:d,color});
  addColl({x,z,rx,rz});

  cornices.push({x,y:h+.15,z,sx:w+.5,sy:.35,sz:d+.5,color:0x8a8470});
  if(tall){
   for(let ly=8;ly<h-4;ly+=10){
    ledges.push({x,y:ly,z:z-d/2-.1,sx:w+.15,sy:.18,sz:.35,color:0xa09880});
    ledges.push({x,y:ly,z:z+d/2+.1,sx:w+.15,sy:.18,sz:.35,color:0xa09880});
    ledges.push({x:x-w/2-.1,y:ly,z,sx:.35,sy:.18,sz:d+.15,color:0xa09880});
    ledges.push({x:x+w/2+.1,y:ly,z,sx:.35,sy:.18,sz:d+.15,color:0xa09880});
   }
  }

  if(isResidential||rnd()<.45){
   roofPyramids.push({x,y:h+Math.min(w,d)*.2,z,sx:w*.72,sy:Math.min(w,d)*.4,sz:d*.72,color:roofColor});
  } else {
   parapets.push({x,y:h+.3,z:z-d/2+.15,sx:w+.4,sy:.6,sz:.3,color:roofColor});
   parapets.push({x,y:h+.3,z:z+d/2-.15,sx:w+.4,sy:.6,sz:.3,color:roofColor});
   parapets.push({x:x-w/2+.15,y:h+.3,z,sx:.3,sy:.6,sz:d+.4,color:roofColor});
   parapets.push({x:x+w/2-.15,y:h+.3,z,sx:.3,sy:.6,sz:d+.4,color:roofColor});
  }

  const wy=tall?3.8:3.2;
  const winSp=isResidential?4.5:3.8;
  for(let yy=2.6;yy<h-1.8;yy+=wy){
   for(let xx=x-w/2+2;xx<x+w/2-1.6;xx+=winSp){
    const glow=rnd()>.88?0xffd98a:0x94c4e0;
    winFrames.push({x:xx,y:yy,z:z-d/2-.04,sx:1.2,sy:1.6,sz:.06,color:isGlass?0x2a3a4a:0x333333});
    winFrames.push({x:xx,y:yy,z:z+d/2+.04,sx:1.2,sy:1.6,sz:.06,color:isGlass?0x2a3a4a:0x333333});
    sills.push({x:xx,y:yy-.85,z:z-d/2-.06,sx:1.4,sy:.1,sz:.2,color:0xb0a890});
    sills.push({x:xx,y:yy-.85,z:z+d/2+.06,sx:1.4,sy:.1,sz:.2,color:0xb0a890});
    if(rnd()>.45){
     winGlows.push({x:xx,y:yy,z:z-d/2-.07,sx:1,sy:1.35,sz:.05,color:glow});
     winGlows.push({x:xx,y:yy,z:z+d/2+.07,sx:1,sy:1.35,sz:.05,color:glow});
    }
   }
   for(let zz=z-d/2+2;zz<z+d/2-1.6;zz+=winSp){
    const glow=rnd()>.88?0xffd98a:0x94c4e0;
    winFrames.push({x:x-w/2-.04,y:yy,z:zz,sx:.06,sy:1.6,sz:1.2,color:isGlass?0x2a3a4a:0x333333});
    winFrames.push({x:x+w/2+.04,y:yy,z:zz,sx:.06,sy:1.6,sz:1.2,color:isGlass?0x2a3a4a:0x333333});
    if(rnd()>.45){
     winGlows.push({x:x-w/2-.07,y:yy,z:zz,sx:.05,sy:1.35,sz:1,color:glow});
     winGlows.push({x:x+w/2+.07,y:yy,z:zz,sx:.05,sy:1.35,sz:1,color:glow});
    }
   }
  }
  if(tall&&isGlass){
   for(let yy=8;yy<h-4;yy+=8)
    balconies.push({x,y:yy,z:z-d/2-.5,sx:w*.7,sy:.12,sz:.9,color:0x8a90a0});
  }
  const rY=h+.4;
  if(rnd()>.5&&!isResidential)acs.push({x:x+rr(-w/3,w/3),y:rY+.35,z:z+rr(-d/3,d/3),sx:.9,sy:.7,sz:.9});
  if(rnd()>.55&&!isResidential)tanks.push({x:x+rr(-w/3,w/3),y:rY+.95,z:z+rr(-d/3,d/3),sx:.85,sy:1.9,sz:.85});
  if((tall||rnd()>.6)&&!isResidential)antennas.push({x:x+rr(-w/3,w/3),y:rY+2.5,z:z+rr(-d/3,d/3),sx:.08,sy:5,sz:.08});

  if(!isResidential&&rnd()>.4){
   const type=buildingTypes[(rnd()*buildingTypes.length)|0];
   const doorZ=z-d/2-2.5;
   if(!onRoad(x,doorZ,w*.4,1)){
    steps.push({x,y:.15,z:z-d/2-.8,sx:3,sy:.3,sz:1.6,color:0xa09888});
    pillars.push({x:x-2,y:1.8,z:doorZ+.6,sx:.5,sy:3.6,sz:.5,color:0xd8d0c0});
    pillars.push({x:x+2,y:1.8,z:doorZ+.6,sx:.5,sy:3.6,sz:.5,color:0xd8d0c0});
    awnings.push({x,y:3.4,z:z-d/2-1.2,sx:w*.75,sy:.18,sz:2.2,
      color:awningColors[(rnd()*awningColors.length)|0]});
    shopFronts.push({x,y:1.6,z:z-d/2-.08,sx:w*.72,sy:2.8,sz:.1,
      color:shopColors[(rnd()*shopColors.length)|0]});
    doorBits.push({x,y:1.2,z:doorZ,sx:1.3,sy:2.4,sz:.15,color:0x3a2418});
    signSlots[type.key].push({x,y:4.7,z:z-d/2-.15,sx:w*.78,sy:1.1});
    shops.push({x,z:doorZ+1.5,type:type.key,
      label:lang==='fa'?type.label:type.labelEn});
   }
  }
 }
 for(const dx of [-1,1]){
  const tx=bx+dx*(half-2);
  const tz=bz+rr(-half+4,half-4);
  if(!onRoad(tx,tz,.6,.6)){
   trees.push({x:tx,y:1.3,z:tz,sx:.5,sy:2.8,sz:.5});
   crowns.push({x:tx,y:4.3,z:tz,sx:2.6,sy:2.8,sz:2.6,
     color:[0x3e7a3a,0x4c8a3f,0x365f2f][(rnd()*3)|0]});
  }
 }
 if(rnd()>.3){
  const bx2=bx+rr(-half+6,half-6),bz2=bz+rr(-half+6,half-6);
  bushes.push({x:bx2,y:.5,z:bz2,sx:1.2,sy:.9,sz:1.2,color:0x4a7a3a});
 }
 if(rnd()>.7&&!isResidential){
  hydrants.push({x:bx+rr(-half+6,half-6),y:.6,z:bz+rr(-half+6,half-6),sx:.4,sy:1.2,sz:.4});
 }
}

const landmarks=[
 {x:0,z:0,type:'park'},
 {x:0,z:240,type:'mosque'},
 {x:240,z:0,type:'tower'},
 {x:-240,z:240,type:'stadium'},
 {x:120,z:120,type:'mall'},
 {x:-120,z:-120,type:'bazaar'}
];
for(const b of blocksA){
 const isLM=landmarks.some(l=>l.x===b.x&&l.z===b.z);
 if(!isLM)genBuildingBlock(b.x,b.z,false);
}
for(const b of blocksB)genBuildingBlock(b.x,b.z,true);

instances(boxGeo,null,buildings,true);
instances(boxGeo,mat(0x333333),winFrames);
instances(boxGeo,null,winGlows,true);
instances(cylGeo,mat(0x6b4628),trees);
instances(sphereGeo,null,crowns,true);
instances(boxGeo,null,parapets,true);
instances(pyramidGeo,null,roofPyramids,true);
instances(boxGeo,mat(0xb0b4b8),acs);
instances(cylGeo,mat(0x909498),tanks);
instances(boxGeo,mat(0xc8ccd0),antennas);
instances(boxGeo,null,shopFronts,true);
instances(boxGeo,null,doorBits,true);
instances(boxGeo,null,pillars,true);
instances(boxGeo,null,steps,true);
instances(boxGeo,null,balconies,true);
instances(sphereGeo,null,bushes,true);
instances(cylGeo,mat(0xb83a2a),hydrants);
instances(boxGeo,null,cornices,true);
instances(boxGeo,null,sills,true);
instances(boxGeo,null,ledges,true);

const awnGroups={};
for(const a of awnings){(awnGroups[a.color]||(awnGroups[a.color]=[])).push(a)}
for(const k in awnGroups)instances(boxGeo,mat(+k),awnGroups[k]);

for(const type of buildingTypes){
 const items=signSlots[type.key];if(!items.length)continue;
 const m=new THREE.InstancedMesh(planeGeo,getSignMat(type),items.length);
 const d=new THREE.Object3D();
 items.forEach((o,i)=>{
  d.position.set(o.x,o.y,o.z);
  d.rotation.set(0,Math.PI,0);
  d.scale.set(o.sx,o.sy,1);
  d.updateMatrix();m.setMatrixAt(i,d.matrix);
 });
 m.instanceMatrix.needsUpdate=true;scene.add(m);
}

// ============================================================
// Landmarks
// ============================================================
function buildPark(x,z){
 add(scene,boxGeo,mat(0xa9c090),x,0,z,64,.05,64);
 add(scene,boxGeo,mat(0xd4c8a8),x,0,z,58,.1,3);
 add(scene,boxGeo,mat(0xd4c8a8),x,0,z,3,.1,58);
 add(scene,cylGeo,mat(0xb8bcc0),x,.3,z,3.5,.6,3.5);
 add(scene,cylGeo,mat(0x5fa3c8),x,.65,z,3,.3,3);
 add(scene,cylGeo,mat(0xa8bcc8),x,1.1,z,.5,1,.5);
 for(let i=0;i<12;i++){
  const a=i/12*Math.PI*2,r=20;
  const tx=x+Math.cos(a)*r,tz=z+Math.sin(a)*r;
  trees.push({x:tx,y:1.3,z:tz,sx:.55,sy:3,sz:.55});
  crowns.push({x:tx,y:4.6,z:tz,sx:3,sy:3.2,sz:3,color:[0x3e7a3a,0x4c8a3f,0x365f2f][i%3]});
 }
 for(let i=0;i<8;i++){
  const a=i/8*Math.PI*2,r=32;
  benches.push({x:x+Math.cos(a)*r,y:.5,z:z+Math.sin(a)*r,sx:2.6,sy:.2,sz:.8,ry:-a});
  benches.push({x:x+Math.cos(a)*r,y:.85,z:z+Math.sin(a)*r,sx:2.6,sy:.6,sz:.15,ry:-a});
 }
}
function buildMosque(x,z){
 add(scene,boxGeo,mat(0xe8dcc0),x,7,z,26,14,26);
 add(scene,sphereGeo,mat(0x2a8a8a),x,16,z,10,6.5,10);
 add(scene,cylGeo,mat(0x2a8a8a),x,20.5,z,1,2,1);
 for(const[dx,dz] of [[-14,-14],[14,-14],[-14,14],[14,14]]){
  add(scene,cylGeo,mat(0xe8dcc0),x+dx,15,z+dz,1.4,30,1.4);
  add(scene,sphereGeo,mat(0x2a8a8a),x+dx,30,z+dz,2,2.6,2);
 }
 addColl({x,z,rx:15,rz:15});
}
function buildTower(x,z){
 add(scene,cylGeo,mat(0xb0b4bc),x,2,z,8,4,8);
 add(scene,cylGeo,mat(0xc8c8d0),x,28,z,2.2,52,2.2);
 add(scene,cylGeo,mat(0x88c8e8),x,42,z,7,3,7);
 add(scene,cylGeo,mat(0xe0e8f0),x,58,z,.5,28,.5);
 add(scene,boxGeo,new THREE.MeshBasicMaterial({color:0xff3030,fog:false}),
   x,73,z,.4,.4,.4);
 addColl({x,z,rx:10,rz:10});
}
function buildStadium(x,z){
 add(scene,cylGeo,mat(0x4a8a3a),x,.1,z,25,.2,25);
 const ringGeo=new THREE.CylinderGeometry(27,29,10,20,1,true);
 const ringMat=new THREE.MeshStandardMaterial({color:0xb8bcc0,side:THREE.DoubleSide,roughness:.8});
 const ring=new THREE.Mesh(ringGeo,ringMat);ring.position.set(x,5,z);scene.add(ring);
 add(scene,cylGeo,mat(0x3a5a8a),x,3.2,z,26,1,26);
 addColl({x,z,rx:29,rz:29});
}
function buildMall(x,z){
 add(scene,boxGeo,mat(0xd8d0c0),x,5,z,44,10,34);
 add(scene,boxGeo,mat(0x88c8e8),x,10.5,z,46,1.2,36);
 add(scene,boxGeo,mat(0xffd54a),x,8,z-18,10,2,.4);
 addColl({x,z,rx:23,rz:18});
}
function buildBazaar(x,z){
 add(scene,boxGeo,mat(0xd8c0a0),x,5,z,50,10,30);
 add(scene,sphereGeo,mat(0x8a6a4a),x,13,z,8,5,8);
 for(let i=-3;i<=3;i++)add(scene,cylGeo,mat(0x8a6a4a),x+i*6,3,z+16,1.5,6,1.5);
 addColl({x,z,rx:26,rz:16});
}
for(const lm of landmarks){
 const x=lm.x,z=lm.z;
 if(lm.type==='park')buildPark(x,z);
 else if(lm.type==='mosque')buildMosque(x,z);
 else if(lm.type==='tower')buildTower(x,z);
 else if(lm.type==='stadium')buildStadium(x,z);
 else if(lm.type==='mall')buildMall(x,z);
 else if(lm.type==='bazaar')buildBazaar(x,z);
}
instances(sphereGeo,null,crowns,true);
instances(boxGeo,null,benches,true);

// ============================================================
// Airport
// ============================================================
function makeAirplane(color=0xf2f4f6){
 const g=new THREE.Group();
 const body=mat(color),winM=mat(0x2a4a70),dark=mat(0x3a3f45);
 add(g,sphereGeo,body,0,0,-4,.9,.9,1.8);
 add(g,boxGeo,body,0,0,0,1.6,1.6,8);
 add(g,boxGeo,winM,0,.45,.3,1.62,.35,5.5);
 add(g,boxGeo,body,0,-.45,-3.5,1.2,.6,1.3);
 add(g,boxGeo,body,0,.5,-3.5,.6,.8,1.3);
 add(g,boxGeo,body,0,-.05,-.3,16,.25,2.5);
 add(g,boxGeo,body,0,1.2,3.5,5,.22,1.3);
 add(g,boxGeo,body,0,2.2,3.7,.28,2,1.2);
 for(const x of[-5,5])add(g,boxGeo,dark,x,-.6,-.3,1,.8,2.5);
 return g;
}
function buildAirport(){
 const ax=850,az=-200;
 add(scene,boxGeo,mat(0xc8d0d8),ax,4,az,44,8,24);
 add(scene,boxGeo,mat(0x88c8e8),ax,8.5,az,46,1.2,26);
 add(scene,boxGeo,mat(0x2a4a6a),ax,5,az-5,22,6,.3);
 add(scene,cylGeo,mat(0xd0d4d8),ax+55,10,az+10,3,20,3);
 add(scene,cylGeo,mat(0x88c8e8),ax+55,21,az+10,5,3,5);
 add(scene,boxGeo,mat(0x2a2e34),ax-40,.05,az,300,.15,44);
 for(let x=ax-190;x<ax+110;x+=30)
  add(scene,boxGeo,mat(0xf0e2b0),x,.12,az,8,.02,1.5);
 add(scene,boxGeo,mat(0xf5f5f0),ax-190,.12,az,3,.02,42);
 add(scene,boxGeo,mat(0xf5f5f0),ax+110,.12,az,3,.02,42);
 for(let i=0;i<3;i++){
  add(scene,boxGeo,mat(0x7a8288),ax-100+i*40,3,az-50,30,6,24);
  add(scene,cylGeo,mat(0x7a8288),ax-100+i*40,6,az-50,15,.6,15);
 }
 for(let i=0;i<3;i++){
  const pg=makeAirplane(0xe8e8e8);
  pg.scale.setScalar(1.4);
  pg.position.set(ax-100+i*40,0,az);
  pg.rotation.y=Math.PI/2;
  scene.add(pg);
 }
 addColl({x:ax,z:az,rx:24,rz:14});
 addColl({x:ax+55,z:az+10,rx:4,rz:4});
 for(let i=0;i<3;i++)addColl({x:ax-100+i*40,z:az-50,rx:16,rz:13});
}
buildAirport();

// ============================================================
// Power plant
// ============================================================
function buildPowerPlant(){
 const px=-850,pz=-200;
 for(const dx of [-40,40]){
  const g=new THREE.CylinderGeometry(14,22,50,20,1,true);
  const m=new THREE.MeshStandardMaterial({color:0xc8ccd0,roughness:.9,
    side:THREE.DoubleSide,transparent:true,opacity:.9});
  const tower=new THREE.Mesh(g,m);
  tower.position.set(px+dx,25,pz);scene.add(tower);
  const cap=new THREE.Mesh(new THREE.CylinderGeometry(18,14,4,20),
    new THREE.MeshStandardMaterial({color:0xdcdfe2}));
  cap.position.set(px+dx,52,pz);scene.add(cap);
  const steam=new THREE.Mesh(sphereGeo,
    new THREE.MeshBasicMaterial({color:0xffffff,transparent:true,opacity:.35,fog:false}));
  steam.position.set(px+dx,62,pz);steam.scale.set(16,10,16);scene.add(steam);
  addColl({x:px+dx,z:pz,rx:22,rz:22});
 }
 add(scene,boxGeo,mat(0x9a9a9a),px,8,pz+50,60,16,30);
 add(scene,boxGeo,mat(0x2a4a6a),px,8.5,pz+50+15.2,50,3,.2);
 for(const dx of [-20,0,20]){
  add(scene,cylGeo,mat(0xa84848),px+dx,30,pz+70,2,60,2);
  add(scene,cylGeo,mat(0xff4444),px+dx,60.5,pz+70,2.1,.5,2.1);
 }
 for(let i=0;i<20;i++){
  add(scene,cylGeo,mat(0x7a8288),px-60+i*6,1,pz-10,.1,2,.1);
 }
 addColl({x:px,z:pz+50,rx:32,rz:16});
}
buildPowerPlant();

// ============================================================
// Tunnel
// ============================================================
function buildTunnel(){
 const tx=HWY_X,tz=-460;
 add(scene,boxGeo,mat(0x6a6a70),tx-22,3.5,tz,4,7,40);
 add(scene,boxGeo,mat(0x6a6a70),tx+22,3.5,tz,4,7,40);
 add(scene,boxGeo,mat(0x50505a),tx,7.5,tz,48,2,40);
 add(scene,boxGeo,new THREE.MeshBasicMaterial({color:0x05080c,fog:false,transparent:true,opacity:.5}),
   tx,6,tz,40,.2,38);
 addColl({x:tx-22,z:tz,rx:2.5,rz:20});
 addColl({x:tx+22,z:tz,rx:2.5,rz:20});
}
buildTunnel();

// ============================================================
// Traffic lights
// ============================================================
const tlPoleItems=[],tlArmItems=[],tlHeadItems=[],tlLampData=[];
function addTL(poleX,poleZ,headX,headZ,axis){
 tlPoleItems.push({x:poleX,y:2.5,z:poleZ,sx:.16,sy:5,sz:.16});
 const midX=(poleX+headX)/2,midZ=(poleZ+headZ)/2;
 tlArmItems.push({x:midX,y:4.8,z:midZ,
  sx:Math.max(.15,Math.abs(headX-poleX)),sy:.15,sz:Math.max(.15,Math.abs(headZ-poleZ))});
 tlHeadItems.push({x:headX,y:4.2,z:headZ,sx:.5,sy:1.4,sz:.5});
 for(let r=0;r<3;r++)tlLampData.push({x:headX,y:4.65-r*.45,z:headZ,axis,row:r});
}
for(const it of allIntersections){
 addTL(it.x+HR+3,it.z+HR+3,it.x+5,it.z+HR+3,'NS');
 addTL(it.x-HR-3,it.z-HR-3,it.x-5,it.z-HR-3,'NS');
 addTL(it.x+HR+3,it.z-HR-3,it.x+HR+3,it.z-5,'EW');
 addTL(it.x-HR-3,it.z+HR+3,it.x-HR-3,it.z+5,'EW');
}
instances(cylGeo,mat(0x33383d,.6),tlPoleItems);
instances(boxGeo,mat(0x33383d,.6),tlArmItems);
instances(boxGeo,mat(0x1a1e24,.6),tlHeadItems);

const tlLampMesh=new THREE.InstancedMesh(lampGeo,new THREE.MeshBasicMaterial({fog:false}),tlLampData.length);
{
 const d=new THREE.Object3D();
 tlLampData.forEach((L,i)=>{
  d.position.set(L.x,L.y,L.z);d.scale.setScalar(.14);d.updateMatrix();
  tlLampMesh.setMatrixAt(i,d.matrix);
  tlLampMesh.setColorAt(i,new THREE.Color(0x181818));
 });
 tlLampMesh.instanceMatrix.needsUpdate=true;
 tlLampMesh.instanceColor.needsUpdate=true;
 scene.add(tlLampMesh);
}
function getLightState(t){
 const c=t%16;
 if(c<7)return'NS';if(c<8)return'NS_Y';
 if(c<15)return'EW';return'EW_Y';
}
let lastLightState='';
const _dimColor=new THREE.Color(0x181818);
const _brightColors=[new THREE.Color(0xff2828),new THREE.Color(0xffcc22),new THREE.Color(0x22dd55)];
function updateSignals(t){
 const st=getLightState(t);
 if(st===lastLightState)return;
 lastLightState=st;
 for(let i=0;i<tlLampData.length;i++){
  const L=tlLampData[i];
  const active=L.axis==='NS'?(st==='NS'?2:st==='NS_Y'?1:0):(st==='EW'?2:st==='EW_Y'?1:0);
  tlLampMesh.setColorAt(i,L.row===active?_brightColors[L.row]:_dimColor);
 }
 tlLampMesh.instanceColor.needsUpdate=true;
}
function isRedFor(axis,t){
 const st=getLightState(t);
 return axis==='NS'?(st!=='NS'&&st!=='NS_Y'):(st!=='EW'&&st!=='EW_Y');
}

// ============================================================
// Parked cars
// ============================================================
const parkBodyColors=[0x3c7cb1,0xc7cbd0,0xa94840,0x3f5149,0xe0b34f,
 0x2c4f77,0x8e2f2f,0x505b63,0xd9d9d9,0x445a3a,0xd18d30,0x9c5fa8,
 0x2b8a8f,0xe8e0c8,0x1f2124,0x6b3d3d,0xb0a89a,0x7a5a3a];
const parkedData=[];
let pIdx=0;
const parkedGrid=new Map();
function addParked(x,z,ry,color){
 const p={x,z,ry,color,w:1.75,l:3.6,h:.65};
 parkedData.push(p);
 const key=Math.floor(x/GS)+','+Math.floor(z/GS);
 if(!parkedGrid.has(key))parkedGrid.set(key,[]);
 parkedGrid.get(key).push(p);
}
function nearIntersection(p,positions){
 for(const np of positions)if(Math.abs(p-np)<32)return true;
 return false;
}
for(const n of roadsA){
 for(let p=-530;p<540;p+=70){
  if(nearIntersection(p,roadsA))continue;
  addParked(n+HR+3,p,0,parkBodyColors[pIdx++%18]);
  addParked(n-HR-3,p,Math.PI,parkBodyColors[pIdx++%18]);
 }
}
for(const n of roadsA){
 for(let p=-530;p<540;p+=70){
  if(nearIntersection(p,roadsA))continue;
  addParked(p,n+HR+3,Math.PI/2,parkBodyColors[pIdx++%18]);
  addParked(p,n-HR-3,-Math.PI/2,parkBodyColors[pIdx++%18]);
 }
}
for(const n of roadsBX){
 for(let p=1360;p<1780;p+=80){
  if(nearIntersection(p,roadsBZ))continue;
  addParked(n+HR+3,p,0,parkBodyColors[pIdx++%18]);
  addParked(n-HR-3,p,Math.PI,parkBodyColors[pIdx++%18]);
 }
}

const parkedBodyMesh=new THREE.InstancedMesh(boxGeo,instMat(),parkedData.length);
const parkedCabinMesh=new THREE.InstancedMesh(boxGeo,instMat(),parkedData.length);
const parkedWheelMesh=new THREE.InstancedMesh(cylGeo,mat(0x1a1c1e),parkedData.length*4);
{
 const d=new THREE.Object3D();
 parkedData.forEach((p,i)=>{
  d.position.set(p.x,p.h,p.z);d.rotation.set(0,p.ry,0);
  d.scale.set(p.w,p.h,p.l);d.updateMatrix();
  parkedBodyMesh.setMatrixAt(i,d.matrix);
  parkedBodyMesh.setColorAt(i,new THREE.Color(p.color));
  d.position.y=p.h+.5;d.scale.set(p.w*.9,.5,p.l*.5);d.updateMatrix();
  parkedCabinMesh.setMatrixAt(i,d.matrix);
  parkedCabinMesh.setColorAt(i,new THREE.Color(0x202228));
  const c=Math.cos(p.ry),s=Math.sin(p.ry);
  for(let j=0;j<4;j++){
   const [dx,dz]=[[-.85,-1.15],[.85,-1.15],[-.85,1.15],[.85,1.15]][j];
   d.position.set(p.x+dx*c+dz*s,.35,p.z-dx*s+dz*c);
   d.rotation.set(0,p.ry,Math.PI/2);
   d.scale.set(.32,.55,.55);d.updateMatrix();
   parkedWheelMesh.setMatrixAt(i*4+j,d.matrix);
  }
 });
 parkedBodyMesh.instanceMatrix.needsUpdate=true;
 parkedBodyMesh.instanceColor.needsUpdate=true;
 parkedCabinMesh.instanceMatrix.needsUpdate=true;
 parkedCabinMesh.instanceColor.needsUpdate=true;
 parkedWheelMesh.instanceMatrix.needsUpdate=true;
 scene.add(parkedBodyMesh,parkedCabinMesh,parkedWheelMesh);
}

// ============================================================
// Traffic
// ============================================================
const CARS_PER_LANE=4;
const trafficLanes=[];
for(const rx of roadsA)
 for(const dir of [-1,1])
  for(const off of [-5,5])
   trafficLanes.push({axis:'x',roadN:rx,offset:off,dir,zMin:-540,zMax:540});
for(const rz of roadsA)
 for(const dir of [-1,1])
  for(const off of [-5,5])
   trafficLanes.push({axis:'z',roadN:rz,offset:off,dir,zMin:-540,zMax:540});
for(const rx of roadsBX)
 for(const dir of [-1,1])
  trafficLanes.push({axis:'x',roadN:rx,offset:dir*4.5,dir,zMin:1300,zMax:1820});
for(const rz of roadsBZ)
 for(const dir of [-1,1])
  trafficLanes.push({axis:'z',roadN:rz,offset:dir*4.5,dir,zMin:-240,zMax:240});
for(const dir of [-1,1])
 trafficLanes.push({axis:'x',roadN:HWY_X,offset:dir*5,dir,zMin:-540,zMax:1820});

const trafficData=[];
const trafficColors=[0xd23d3d,0x2a7ec9,0xe8b63b,0x59a05a,0xc7cbd0,
 0x343a44,0x9b3eb0,0xe07a2a,0x2b9aa8,0x8a2b2b,0x3d7a3d,0x6a6adc,
 0xf0f0f0,0x1a1a1a,0xa07850,0xd0a878,0x556677,0x7a3a3a,0x20a870,0xe85a90,
 0x1a3d5a,0x8a2050,0xd0c8a8,0x405060];

for(const lane of trafficLanes){
 const range=lane.zMax-lane.zMin;
 for(let k=0;k<CARS_PER_LANE;k++){
  const pos=lane.zMin+range/CARS_PER_LANE*(k+Math.random()*.4);
  const roll=Math.random();
  let w=1.7,h=.6,l=3.4;
  if(roll>.92){w=2.3;h=1.1;l=6.5}
  else if(roll>.85){w=2.5;h=1.2;l=7}
  else if(roll>.7){w=1.9;h=.7;l=3.8}
  trafficData.push({...lane,pos,
   baseSpeed:8+Math.random()*6,speed:8,w,h,l,
   color:trafficColors[(Math.random()*trafficColors.length)|0]});
 }
}

const laneKeyOf=c=>c.axis+'|'+c.roadN+'|'+c.offset+'|'+c.dir;
const laneGroups=new Map();
trafficData.forEach((c,i)=>{
 const k=laneKeyOf(c);
 if(!laneGroups.has(k))laneGroups.set(k,[]);
 laneGroups.get(k).push(i);
});
const trafficLaneIdx=trafficData.map(c=>laneGroups.get(laneKeyOf(c)));

const tBody=new THREE.InstancedMesh(boxGeo,instMatShiny(),trafficData.length);
const tCabin=new THREE.InstancedMesh(boxGeo,instMat(),trafficData.length);
const tWheels=new THREE.InstancedMesh(cylGeo,mat(0x1a1c1e),trafficData.length*4);
const tHeads=new THREE.InstancedMesh(boxGeo,mat(0xfff8b0),trafficData.length*2);
const tTails=new THREE.InstancedMesh(boxGeo,mat(0xd03028),trafficData.length*2);
scene.add(tBody,tCabin,tWheels,tHeads,tTails);

const trafficColors3=trafficData.map(c=>new THREE.Color(c.color));
const cabinColor=new THREE.Color(0x1a1e26);
for(let i=0;i<trafficData.length;i++){
 tBody.setColorAt(i,trafficColors3[i]);
 tCabin.setColorAt(i,cabinColor);
}
tBody.instanceColor.needsUpdate=true;
tCabin.instanceColor.needsUpdate=true;

const _o=new THREE.Object3D();
function updateTraffic(dt,t){
 const redNS=isRedFor('NS',t);
 const redEW=isRedFor('EW',t);
 for(let i=0;i<trafficData.length;i++){
  const c=trafficData[i];
  let target=c.baseSpeed;
  const isX=c.axis==='x';
  const isRed=isX?redEW:redNS;
  const checkPositions=(c.zMin<-100)?roadsA:(isX?roadsA:roadsBZ);
  let nearestStop=null,nearestDist=Infinity;
  for(const ip of checkPositions){
   const d=(ip-c.pos)*c.dir;
   if(d>0&&d<nearestDist){nearestDist=d;nearestStop=ip}
  }
  if(nearestStop!==null&&nearestDist<50&&isRed)
   target=Math.min(target,Math.max(0,(nearestDist-3)*.85));
  const sameLane=trafficLaneIdx[i];
  if(target>.5){
   let minGap=Infinity;
   for(const j of sameLane){
    if(j===i)continue;
    const d=(trafficData[j].pos-c.pos)*c.dir;
    if(d>0&&d<minGap)minGap=d;
   }
   if(minGap<28)target=Math.min(target,Math.max(0,(minGap-7)*.9));
  }
  const accel=target>c.speed?7:18;
  c.speed+=clamp(target-c.speed,-accel*dt,accel*dt);
  c.pos+=c.speed*c.dir*dt;
  const range=c.zMax-c.zMin;
  if(c.pos>c.zMax)c.pos-=range;
  if(c.pos<c.zMin)c.pos+=range;
  let x,z,ry;
  if(isX){x=c.roadN+c.offset;z=c.pos;ry=c.dir>0?0:Math.PI}
  else{x=c.pos;z=c.roadN+c.offset;ry=c.dir>0?Math.PI/2:-Math.PI/2}
  _o.position.set(x,c.h,z);_o.rotation.set(0,ry,0);
  _o.scale.set(c.w,c.h,c.l);_o.updateMatrix();
  tBody.setMatrixAt(i,_o.matrix);
  _o.position.y=c.h+c.h*.8;_o.scale.set(c.w*.9,.4,c.l*.45);_o.updateMatrix();
  tCabin.setMatrixAt(i,_o.matrix);
  const cf=Math.cos(ry),sf=Math.sin(ry);
  const fwdX=-sf,fwdZ=-cf;
  for(let j=0;j<4;j++){
   const [dx,dz]=[[-.82,-1.05],[.82,-1.05],[-.82,1.05],[.82,1.05]][j];
   _o.position.set(x+dx*cf+dz*sf,.35,z-dx*sf+dz*cf);
   _o.rotation.set(0,ry,Math.PI/2);
   _o.scale.set(.3,.55,.55);_o.updateMatrix();
   tWheels.setMatrixAt(i*4+j,_o.matrix);
  }
  _o.rotation.set(0,ry,0);
  _o.position.set(x+fwdX*c.l*.45-.5*cf,.65,z+fwdZ*c.l*.45-.5*sf);
  _o.scale.set(.3,.2,.06);_o.updateMatrix();tHeads.setMatrixAt(i*2,_o.matrix);
  _o.position.set(x+fwdX*c.l*.45+.5*cf,.65,z+fwdZ*c.l*.45+.5*sf);
  _o.updateMatrix();tHeads.setMatrixAt(i*2+1,_o.matrix);
  _o.position.set(x-fwdX*c.l*.45-.5*cf,.65,z-fwdZ*c.l*.45-.5*sf);
  _o.updateMatrix();tTails.setMatrixAt(i*2,_o.matrix);
  _o.position.set(x-fwdX*c.l*.45+.5*cf,.65,z-fwdZ*c.l*.45+.5*sf);
  _o.updateMatrix();tTails.setMatrixAt(i*2+1,_o.matrix);
 }
 tBody.instanceMatrix.needsUpdate=true;
 tCabin.instanceMatrix.needsUpdate=true;
 tWheels.instanceMatrix.needsUpdate=true;
 tHeads.instanceMatrix.needsUpdate=true;
 tTails.instanceMatrix.needsUpdate=true;
}

// ============================================================
// Pedestrians
// ============================================================
const PED_N=260;
const pedHead=new THREE.InstancedMesh(sphereGeo,instMat(),PED_N);
const pedBody=new THREE.InstancedMesh(boxGeo,instMat(),PED_N);
const pedLegL=new THREE.InstancedMesh(boxGeo,instMat(),PED_N);
const pedLegR=new THREE.InstancedMesh(boxGeo,instMat(),PED_N);
const pedArmL=new THREE.InstancedMesh(boxGeo,instMat(),PED_N);
const pedArmR=new THREE.InstancedMesh(boxGeo,instMat(),PED_N);
scene.add(pedHead,pedBody,pedLegL,pedLegR,pedArmL,pedArmR);

const skinColors=[0xe8c8a0,0xd4a47a,0xa87850,0x8a5a38,0xf0d8b8,0xc89878];
const shirtColors=[0x3b78b7,0xa44c42,0x438455,0xd2a54b,0x7359a4,
 0xc75a3a,0x2b6b6b,0x8a3d5e,0xe8e8e8,0x2c3e5c,0x505a68,0x8a6a3a];
const pantsColors=[0x2c3540,0x3a3a3a,0x4a3020,0x5a5a6a,0x2a4a3a,0x1a1a1a];

const pedData=[];
for(let i=0;i<PED_N;i++){
 const inB=i%4===0;
 const axis=i%2;
 if(inB){
  if(axis===0){
   const roadZ=roadsBZ[Math.floor(i/2)%roadsBZ.length];
   const side=(i%4<2)?1:-1;
   pedData.push({axis:0,roadN:roadZ,side,zMin:-220,zMax:220,
    pos:rr(-200,200),dir:Math.random()>.5?1:-1,
    speed:.8+Math.random()*1.3,phase:Math.random()*6,height:.88+Math.random()*.22});
  } else {
   const roadX=roadsBX[Math.floor(i/2)%roadsBX.length];
   const side=(i%4<2)?1:-1;
   pedData.push({axis:1,roadN:roadX,side,zMin:1320,zMax:1800,
    pos:rr(1340,1780),dir:Math.random()>.5?1:-1,
    speed:.8+Math.random()*1.3,phase:Math.random()*6,height:.88+Math.random()*.22});
  }
 } else {
  const roadN=roadsA[Math.floor(i/2)%roadsA.length];
  const side=(i%4<2)?1:-1;
  pedData.push({axis,roadN,side,zMin:-530,zMax:530,
   pos:rr(-520,520),dir:Math.random()>.5?1:-1,
   speed:.8+Math.random()*1.3,phase:Math.random()*6,height:.88+Math.random()*.22});
 }
 pedHead.setColorAt(i,new THREE.Color(skinColors[(Math.random()*skinColors.length)|0]));
 pedBody.setColorAt(i,new THREE.Color(shirtColors[(Math.random()*shirtColors.length)|0]));
 const pc=pantsColors[(Math.random()*pantsColors.length)|0];
 pedLegL.setColorAt(i,new THREE.Color(pc));
 pedLegR.setColorAt(i,new THREE.Color(pc));
 const sc=shirtColors[(Math.random()*shirtColors.length)|0];
 pedArmL.setColorAt(i,new THREE.Color(sc));
 pedArmR.setColorAt(i,new THREE.Color(sc));
}
[pedHead,pedBody,pedLegL,pedLegR,pedArmL,pedArmR].forEach(m=>m.instanceColor.needsUpdate=true);

function updatePeds(dt,t){
 for(let i=0;i<PED_N;i++){
  const p=pedData[i];
  p.pos+=p.speed*p.dir*dt;
  if(p.pos>p.zMax-10)p.dir=-1;
  if(p.pos<p.zMin+10)p.dir=1;
  let x,z,ry;
  const walkLine=p.roadN+p.side*(HR+4);
  if(p.axis===0){x=p.pos;z=walkLine;ry=p.dir>0?-Math.PI/2:Math.PI/2}
  else{x=walkLine;z=p.pos;ry=p.dir>0?0:Math.PI}
  const walk=t*p.speed*7+p.phase;
  const swing=Math.sin(walk)*.5;
  const bob=Math.abs(Math.sin(walk))*.04;
  const H=p.height;
  _o.rotation.set(0,ry,0);
  _o.position.set(x,1.55*H+bob,z);_o.scale.set(.22,.24,.22);
  _o.updateMatrix();pedHead.setMatrixAt(i,_o.matrix);
  _o.position.set(x,.95*H+bob,z);_o.scale.set(.5,.7,.3);
  _o.updateMatrix();pedBody.setMatrixAt(i,_o.matrix);
  _o.rotation.set(swing,ry,0);
  _o.position.set(x-Math.sin(ry+Math.PI/2)*.14,.48*H+bob,z-Math.cos(ry+Math.PI/2)*.14);
  _o.scale.set(.18,.9,.22);_o.updateMatrix();pedLegL.setMatrixAt(i,_o.matrix);
  _o.rotation.set(-swing,ry,0);
  _o.position.set(x-Math.sin(ry-Math.PI/2)*.14,.48*H+bob,z-Math.cos(ry-Math.PI/2)*.14);
  _o.updateMatrix();pedLegR.setMatrixAt(i,_o.matrix);
  _o.rotation.set(-swing,ry,0);
  _o.position.set(x-Math.sin(ry+Math.PI/2)*.35,1.15*H+bob,z-Math.cos(ry+Math.PI/2)*.35);
  _o.scale.set(.14,.55,.18);_o.updateMatrix();pedArmL.setMatrixAt(i,_o.matrix);
  _o.rotation.set(swing,ry,0);
  _o.position.set(x-Math.sin(ry-Math.PI/2)*.35,1.15*H+bob,z-Math.cos(ry-Math.PI/2)*.35);
  _o.updateMatrix();pedArmR.setMatrixAt(i,_o.matrix);
 }
 [pedHead,pedBody,pedLegL,pedLegR,pedArmL,pedArmR].forEach(m=>m.instanceMatrix.needsUpdate=true);
}

// NPC plane
const npcPlane1=makeAirplane(0xf2f4f6);
npcPlane1.scale.setScalar(2);
scene.add(npcPlane1);
let planeAng1=0;
const PLANE_R1=600,PLANE_Y1=140;

// ============================================================
// Vehicle specs
// ============================================================
const vehicleSpecs={
 sport:{name:'اسپرت',nameEn:'Sport',max:55,power:30,brake:45,turn:1.9,default:0xe63946,type:'car'},
 moto:{name:'موتور',nameEn:'Moto',max:60,power:35,brake:50,turn:2.2,default:0xf0b52b,type:'moto'},
 sedan:{name:'سواری',nameEn:'Sedan',max:42,power:22,brake:35,turn:1.5,default:0x607d8b,type:'car'},
 bus:{name:'اتوبوس',nameEn:'Bus',max:28,power:12,brake:22,turn:.8,default:0x1e88e5,type:'car'},
 offroad:{name:'آفرود',nameEn:'Offroad',max:45,power:25,brake:40,turn:1.6,default:0x43a047,type:'car'},
 taxi:{name:'تاکسی',nameEn:'Taxi',max:48,power:24,brake:38,turn:1.5,default:0xfbc02d,type:'car'},
 truck:{name:'کامیون',nameEn:'Truck',max:32,power:14,brake:26,turn:.9,default:0x455a64,type:'car'},
 police:{name:'پلیس',nameEn:'Police',max:60,power:32,brake:48,turn:1.9,default:0xffffff,type:'car'},
 ambulance:{name:'آمبولانس',nameEn:'Ambulance',max:55,power:28,brake:42,turn:1.6,default:0xffffff,type:'car'},
 plane:{name:'هواپیما',nameEn:'Plane',max:90,power:40,brake:28,turn:1.2,default:0xf0f4f8,type:'plane'}
};
const colorPalette=[0xe63946,0xf77f00,0xf9c74f,0x90be6d,0x43aa8b,
 0x277da1,0x4d908e,0x577590,0x5773a8,0x9d4edd,
 0xd90429,0xff006e,0x2b2d42,0x8d99ae,0xffffff,
 0xc9ada7,0xf08080,0x333d29];

let currentColor=vehicleSpecs.sport.default;
const carGroup=new THREE.Group();
const carBody=new THREE.Group();
carGroup.add(carBody);
scene.add(carGroup);

const carBeacon=new THREE.Group();
{
 const m=new THREE.Mesh(new THREE.ConeGeometry(.8,1.6,4),
   new THREE.MeshBasicMaterial({color:0x22ffbb,fog:false}));
 m.rotation.x=Math.PI;carBeacon.add(m);carBeacon.visible=false;scene.add(carBeacon);
}

const person=new THREE.Group();scene.add(person);person.visible=false;
let humanParts=null;
function buildHuman(){
 const g=new THREE.Group();
 const skin=mat(0xd4a47a),shirt=mat(0x2c5db8),pants=mat(0x2c3540),shoe=mat(0x1a1a1a);
 add(g,sphereGeo,skin,0,1.65,0,.24,.26,.24);
 add(g,sphereGeo,mat(0x2a2a2a),0,1.82,0,.25,.16,.25);
 add(g,boxGeo,shirt,0,1.15,0,.55,.65,.32);
 const armL=new THREE.Group();armL.position.set(-.35,1.5,0);
 {const m=new THREE.Mesh(boxGeo,shirt);m.position.y=-.25;m.scale.set(.16,.55,.22);armL.add(m);
  const h=new THREE.Mesh(sphereGeo,skin);h.position.y=-.55;h.scale.setScalar(.1);armL.add(h)}
 g.add(armL);
 const armR=new THREE.Group();armR.position.set(.35,1.5,0);
 {const m=new THREE.Mesh(boxGeo,shirt);m.position.y=-.25;m.scale.set(.16,.55,.22);armR.add(m);
  const h=new THREE.Mesh(sphereGeo,skin);h.position.y=-.55;h.scale.setScalar(.1);armR.add(h)}
 g.add(armR);
 const legL=new THREE.Group();legL.position.set(-.16,.95,0);
 {const m=new THREE.Mesh(boxGeo,pants);m.position.y=-.45;m.scale.set(.19,.9,.22);legL.add(m);
  const f=new THREE.Mesh(boxGeo,shoe);f.position.set(0,-.87,-.05);f.scale.set(.2,.16,.32);legL.add(f)}
 g.add(legL);
 const legR=new THREE.Group();legR.position.set(.16,.95,0);
 {const m=new THREE.Mesh(boxGeo,pants);m.position.y=-.45;m.scale.set(.19,.9,.22);legR.add(m);
  const f=new THREE.Mesh(boxGeo,shoe);f.position.set(0,-.87,-.05);f.scale.set(.2,.16,.32);legR.add(f)}
 g.add(legR);
 return {group:g,armL,armR,legL,legR};
}
humanParts=buildHuman();person.add(humanParts.group);

function makeWheel(r,w,isFront){
 const pivot=new THREE.Object3D();
 const spin=new THREE.Object3D();
 const m=new THREE.Mesh(cylGeo,mat(0x1a1c1e,.7));
 m.scale.set(r,w,r);m.rotation.z=Math.PI/2;
 const rim=new THREE.Mesh(cylGeo,mat(0xd0d4d8,.25));
 rim.scale.set(r*.55,w*1.05,r*.55);rim.rotation.z=Math.PI/2;
 spin.add(m);spin.add(rim);pivot.add(spin);
 return {pivot,spin,isFront};
}

let vehicleWheels=[],vehiclePropellers=[],vehicleType='sport';

function buildVehicle(type,color){
 const g=new THREE.Group();
 const spec=vehicleSpecs[type];
 const paint=new THREE.MeshStandardMaterial({color,roughness:.35,metalness:.5});
 const dark=mat(0x1a1c1e,.4);
 const glassM=new THREE.MeshStandardMaterial({color:0x88c2de,roughness:.1,metalness:.6,
   transparent:true,opacity:.7});
 const chrome=mat(0xf0f4f8,.15);
 const red=mat(0xd32e29);
 const plateMat=mat(0xf5e8c0);
 const wheels=[],headLights=[],tailLights=[],propellers=[];

 if(spec.type==='plane'){
  const body=new THREE.MeshStandardMaterial({color,roughness:.4,metalness:.35});
  const winM=new THREE.MeshStandardMaterial({color:0x2a4a70,roughness:.1,metalness:.6});
  add(g,sphereGeo,body,0,0,-4,.85,.85,1.7);
  add(g,boxGeo,body,0,0,0,1.5,1.5,8);
  add(g,boxGeo,winM,0,.42,.3,1.52,.32,5.5);
  add(g,boxGeo,body,0,-.42,-3.5,1.1,.55,1.3);
  add(g,boxGeo,body,0,.55,-3.5,.55,.8,1.3);
  add(g,boxGeo,body,0,-.05,-.3,17,.25,2.6);
  add(g,boxGeo,body,0,1.15,3.5,5,.22,1.4);
  add(g,boxGeo,body,0,2.1,3.7,.28,1.9,1.3);
  add(g,boxGeo,mat(0x5a5f66),0,-.85,.2,1.6,.4,4);
  for(const x of[-4.5,4.5]){
   add(g,boxGeo,mat(0x6a7078),x,-.6,-.3,1,.8,2.6);
   const prop=new THREE.Group();prop.position.set(x,-.6,-1.8);
   const hub=new THREE.Mesh(cylGeo,mat(0x2a2d32));
   hub.scale.set(.14,.35,.14);hub.rotation.x=Math.PI/2;prop.add(hub);
   for(let i=0;i<3;i++){
    const b=new THREE.Mesh(boxGeo,mat(0x2a2d32));
    b.scale.set(.1,1.3,.04);
    b.rotation.z=i*Math.PI*2/3;
    b.position.set(Math.sin(b.rotation.z)*.65,0,0);prop.add(b);
   }
   g.add(prop);propellers.push(prop);
  }
  for(const[px,pz]of[[-1.2,1.5],[1.2,1.5]]){
   add(g,cylGeo,dark,px,-1.2,pz,.12,.5,.12);
   const w=makeWheel(.22,.12,false);
   w.pivot.position.set(px,-1.45,pz);g.add(w.pivot);wheels.push(w);
  }
  return {group:g,wheels,headLights,tailLights,propellers,spec};
 }
 if(type==='moto'){
  add(g,boxGeo,dark,0,.55,0,.16,.5,1.8);
  add(g,boxGeo,paint,0,.85,-.15,.5,.55,1.2);
  add(g,boxGeo,dark,0,1.05,.55,.32,.18,.7);
  add(g,cylGeo,chrome,0,1.15,-.55,.35,.12,.35).rotation.z=Math.PI/2;
  add(g,boxGeo,glassM,0,1.22,-.55,.28,.28,.05);
  const w1=makeWheel(.38,.14,true);w1.pivot.position.set(0,.4,-.9);g.add(w1.pivot);wheels.push(w1);
  const w2=makeWheel(.38,.14,false);w2.pivot.position.set(0,.4,.9);g.add(w2.pivot);wheels.push(w2);
  headLights.push(add(g,boxGeo,mat(0xfff8d0),0,1.05,-.95,.28,.2,.06));
  add(g,sphereGeo,mat(0x1e2026),0,1.72,.1,.28,.32,.3);
  add(g,boxGeo,mat(0xd0d0d0),0,1.74,-.1,.42,.28,.1);
  add(g,boxGeo,mat(0x2c3540),0,1.28,.1,.42,.6,.35);
  return {group:g,wheels,headLights,tailLights,propellers,spec};
 }
 let width=1.9,length=4,cabW=1.6,cabL=2,bodyH=.6,bodyY=.65;
 if(type==='bus'){width=2.5;length=7;cabW=2.4;cabL=5.5;bodyH=1.2;bodyY=.8}
 if(type==='offroad'){width=2.2;length=4.4;cabW=1.9;cabL=2.6;bodyH=.75;bodyY=.78}
 if(type==='taxi'){width=1.9;length=4.3;cabW=1.7;cabL=2.4;bodyH=.62;bodyY=.7}
 if(type==='truck'){width=2.4;length=6.5;cabW=2.2;cabL=2;bodyH=1;bodyY=.9}
 if(type==='police'){width=1.95;length=4.3;cabW=1.75;cabL=2.4;bodyH=.62;bodyY=.7}
 if(type==='ambulance'){width=2.3;length=5.5;cabW=2.1;cabL=4;bodyH=.9;bodyY=.8}
 if(type==='sedan'){width=1.95;length=4.4;cabW=1.75;cabL=2.5;bodyH=.6;bodyY=.68}
 add(g,boxGeo,paint,0,bodyY,0,width,bodyH,length);
 add(g,boxGeo,dark,-width/2-.01,bodyY,0,.02,.5,length*.7);
 add(g,boxGeo,dark,width/2+.01,bodyY,0,.02,.5,length*.7);
 if(type!=='bus'&&type!=='truck'&&type!=='ambulance'){
  add(g,boxGeo,paint,0,bodyY+bodyH/2+.02,-length/2+1,width*.95,.15,1.6);
  add(g,boxGeo,paint,0,bodyY+bodyH/2+.02,length/2-1,width*.95,.15,1.6);
 }
 const cabY=bodyY+bodyH/2+(type==='bus'||type==='truck'||type==='ambulance'?1.05:.32);
 add(g,boxGeo,paint,0,cabY,-.15,cabW,type==='bus'?1.3:.55,cabL);
 add(g,boxGeo,glassM,0,cabY,length*.35,cabW*.95,.45,.15);
 for(const x of[-cabW/2-.02,cabW/2+.02])
  add(g,boxGeo,glassM,x,cabY,-.15,.08,.4,cabL*.85);
 if(type==='bus')add(g,boxGeo,glassM,0,cabY-.15,0,cabW+.03,.65,cabL*.95);
 add(g,boxGeo,glassM,0,cabY,-cabL/2-.16,cabW*.85,.4,.08);
 add(g,boxGeo,dark,-width/2-.25,cabY+.1,-length*.3,.2,.15,.35);
 add(g,boxGeo,dark,width/2+.25,cabY+.1,-length*.3,.2,.15,.35);
 for(const x of[-width*.35,width*.35]){
  headLights.push(add(g,boxGeo,mat(0xfff8d0),x,bodyY+.15,-length/2-.02,.32,.22,.06));
  tailLights.push(add(g,boxGeo,red,x,bodyY+.15,length/2+.02,.3,.2,.06));
 }
 add(g,boxGeo,plateMat,0,bodyY-.1,-length/2-.06,.6,.25,.03);
 add(g,boxGeo,plateMat,0,bodyY-.1,length/2+.06,.6,.25,.03);
 if(type==='offroad'){
  add(g,boxGeo,dark,0,cabY+.4,-.15,cabW*.9,.12,cabL*.9);
  add(g,boxGeo,mat(0xf0f0c8),0,cabY+.5,-.15,.6,.12,.06);
 }
 if(type==='taxi')add(g,boxGeo,mat(0xf0c419),0,cabY+.45,-.15,.7,.25,.15);
 if(type==='police'){
  add(g,boxGeo,mat(0x1a3d80),0,bodyY-.35,0,width*.95,.2,length*.95);
  add(g,boxGeo,mat(0xff3030),-.3,cabY+.5,-.15,.35,.12,.15);
  add(g,boxGeo,mat(0x3060ff),.3,cabY+.5,-.15,.35,.12,.15);
 }
 if(type==='ambulance')add(g,boxGeo,mat(0xd32e29),0,cabY+.55,.2,.6,.15,1.2);
 if(type==='truck')add(g,boxGeo,mat(0x3a3f45),0,bodyY+.9,length*.1,width*.95,1.4,length*.5);
 const wr=type==='bus'?.42:.36;
 for(const x of[-width*.53,width*.53])
  for(const z of[-length*.33,length*.33]){
   const w=makeWheel(wr,.28,z<0);
   w.pivot.position.set(x,.4,z);g.add(w.pivot);wheels.push(w);
  }
 return {group:g,wheels,headLights,tailLights,propellers:[],spec};
}

function createVehicle(type,color){
 while(carBody.children.length)carBody.remove(carBody.children[0]);
 const r=buildVehicle(type,color||vehicleSpecs[type].default);
 carBody.add(r.group);
 vehicleWheels=r.wheels;
 vehiclePropellers=r.propellers||[];
 vehicleType=type;
 currentColor=color||vehicleSpecs[type].default;
 $('vname').textContent=lang==='fa'?vehicleSpecs[type].name:vehicleSpecs[type].nameEn;
 document.querySelectorAll('[data-v]').forEach(b=>
  b.classList.toggle('active',b.dataset.v===type));
}

const palEl=$('palette');
colorPalette.forEach(c=>{
 const s=document.createElement('span');
 s.className='swatch';
 s.style.background='#'+c.toString(16).padStart(6,'0');
 s.onclick=()=>{
  currentColor=c;createVehicle(vehicleType,c);
  document.querySelectorAll('.swatch').forEach(x=>x.classList.remove('sel'));
  s.classList.add('sel');
 };
 palEl.appendChild(s);
});
palEl.firstChild.classList.add('sel');
document.querySelectorAll('[data-v]').forEach(b=>
 b.addEventListener('click',()=>createVehicle(b.dataset.v,currentColor)));

// ============================================================
// Player state
// ============================================================
let onFoot=false;
let heading=Math.PI;
let speed=0;
let steerAngle=0;
let flightY=0;
let walkPhase=0;
let camMode=0;
let money=5000;

carGroup.position.set(60,0,100);
carGroup.rotation.y=heading;
createVehicle('sport');

// ============================================================
// Audio + Radio
// ============================================================
let audioCtx=null;
let musicOn=true;
let engineOsc=null,engineGain=null,engineStarted=false;

const radio={
 on:false,
 station:-1,
 ctx:null,
 master:null,
 timer:null,
 start(ctx,out){
  this.ctx=ctx;this.master=ctx.createGain();
  this.master.gain.value=0.18;this.master.connect(out);
 },
 play(idx){
  this.stop();
  if(!this.ctx||idx<0)return;
  this.station=idx;this.on=true;
  this.master.gain.setTargetAtTime(0.18,this.ctx.currentTime,0.1);
  if(idx===0)this.stationSynth();
  else if(idx===1)this.stationChill();
  else if(idx===2)this.stationTechno();
  updateRadioUI();
 },
 stop(){
  if(this.timer){clearInterval(this.timer);this.timer=null}
  if(this.master&&this.ctx)this.master.gain.setTargetAtTime(0,this.ctx.currentTime,0.1);
  this.on=false;
  updateRadioUI();
 },
 stationSynth(){
  const ctx=this.ctx,out=this.master;
  const notes=[220,277,330,440,330,277,220,165];
  let i=0;
  this.timer=setInterval(()=>{
   if(!this.on)return;
   const o=ctx.createOscillator(),g=ctx.createGain();
   o.type='square';o.frequency.value=notes[i%notes.length];
   const now=ctx.currentTime;
   g.gain.setValueAtTime(0,now);
   g.gain.linearRampToValueAtTime(0.06,now+0.01);
   g.gain.exponentialRampToValueAtTime(0.001,now+0.28);
   o.connect(g);g.connect(out);o.start();o.stop(now+0.3);
   i++;
  },220);
 },
 stationChill(){
  const ctx=this.ctx,out=this.master;
  const chords=[[220,277,330],[196,247,294],[262,330,392],[175,220,262]];
  let i=0;
  this.timer=setInterval(()=>{
   if(!this.on)return;
   const ch=chords[i%chords.length];
   ch.forEach(f=>{
    const o=ctx.createOscillator(),g=ctx.createGain();
    o.type='sine';o.frequency.value=f;
    const now=ctx.currentTime;
    g.gain.setValueAtTime(0,now);
    g.gain.linearRampToValueAtTime(0.035,now+0.6);
    g.gain.exponentialRampToValueAtTime(0.001,now+2.4);
    o.connect(g);g.connect(out);o.start();o.stop(now+2.5);
   });
   i++;
  },2000);
 },
 stationTechno(){
  const ctx=this.ctx,out=this.master;
  let beat=0;
  this.timer=setInterval(()=>{
   if(!this.on)return;
   const now=ctx.currentTime;
   if(beat%4===0){
    const o=ctx.createOscillator(),g=ctx.createGain();
    o.frequency.setValueAtTime(150,now);
    o.frequency.exponentialRampToValueAtTime(45,now+0.08);
    g.gain.setValueAtTime(0.15,now);
    g.gain.exponentialRampToValueAtTime(0.001,now+0.18);
    o.connect(g);g.connect(out);o.start();o.stop(now+0.2);
   }
   if(beat%2===1){
    const o=ctx.createOscillator(),g=ctx.createGain();
    o.type='sawtooth';o.frequency.value=55+((beat%8)*15);
    g.gain.setValueAtTime(0.05,now);
    g.gain.exponentialRampToValueAtTime(0.001,now+0.25);
    o.connect(g);g.connect(out);o.start();o.stop(now+0.26);
   }
   beat++;
  },250);
 }
};

function updateRadioUI(){
 document.querySelectorAll('.station').forEach(s=>{
  s.classList.toggle('active',radio.on&&+s.dataset.station===radio.station);
 });
}

document.querySelectorAll('.station').forEach(s=>{
 s.addEventListener('click',()=>{
  if(!audioCtx){initAudio();if(!audioCtx)return}
  const idx=+s.dataset.station;
  if(radio.on&&radio.station===idx)radio.stop();
  else radio.play(idx);
 });
});

function initAudio(){
 if(audioCtx)return;
 try{
  audioCtx=new (window.AudioContext||window.webkitAudioContext)();
  radio.start(audioCtx,audioCtx.destination);
 }catch(e){}
}
window.initAudio=initAudio;

function updateEngineSound(ratio,reversing){
 if(!audioCtx)return;
 if(!engineStarted){
  engineOsc=audioCtx.createOscillator();
  engineOsc.type='sawtooth';engineOsc.frequency.value=60;
  engineGain=audioCtx.createGain();engineGain.gain.value=0;
  const filt=audioCtx.createBiquadFilter();
  filt.type='lowpass';filt.frequency.value=420;
  engineOsc.connect(filt);filt.connect(engineGain);engineGain.connect(audioCtx.destination);
  engineOsc.start();engineStarted=true;
 }
 const now=audioCtx.currentTime;
 engineGain.gain.setTargetAtTime(onFoot?0:(0.02+ratio*0.06),now,0.1);
 engineOsc.frequency.setTargetAtTime(
   reversing?60+ratio*100:50+ratio*220,now,0.1);
}

function honk(){
 try{
  if(!audioCtx)return;
  const o=audioCtx.createOscillator(),g=audioCtx.createGain();
  o.type='square';
  o.frequency.value=vehicleType==='truck'?180:vehicleType==='moto'?600:420;
  g.gain.setValueAtTime(.1,audioCtx.currentTime);
  g.gain.exponentialRampToValueAtTime(.001,audioCtx.currentTime+.3);
  o.connect(g);g.connect(audioCtx.destination);
  o.start();o.stop(audioCtx.currentTime+.3);
 }catch(e){}
}

// ============================================================
// Helpers
// ============================================================
const dist2=(x1,z1,x2,z2)=>Math.hypot(x1-x2,z1-z2);
function showAction(text,ms=1400){
 const el=$('action');
 if(!el)return;
 el.textContent=text;el.style.display='block';
 clearTimeout(el._t);
 el._t=setTimeout(()=>el.style.display='none',ms);
}
function flashMsg(txt){
 const el=$('msg');
 if(!el)return;
 el.textContent=txt;
 el.classList.add('show');
 clearTimeout(el._t);
 el._t=setTimeout(()=>el.classList.remove('show'),1800);
}

let interactCooldown=0;
function exitVehicle(){
 if(!onFoot){
  person.position.set(
    carGroup.position.x+Math.sin(heading)*3.2,0,
    carGroup.position.z+Math.cos(heading)*3.2);
  person.rotation.y=heading;
  person.visible=true;onFoot=true;speed=0;
  $('mode').textContent=t('onFoot');
 }
}
function enterVehicle(){
 if(!onFoot)return;
 if(dist2(person.position.x,person.position.z,carGroup.position.x,carGroup.position.z)<10){
  onFoot=false;person.visible=false;carBeacon.visible=false;
  heading=person.rotation.y;speed=0;
  $('mode').textContent=t('inCar');
 }
}
function nearestShop(){
 const px=person.position.x,pz=person.position.z;
 let best=null,bd=64;
 for(const s of shops){
  const d=(px-s.x)**2+(pz-s.z)**2;
  if(d<bd){bd=d;best=s}
 }
 return best;
}
let currentShop=null;
function openShop(shop){
 currentShop=shop;
 document.getElementById('shopTitle').textContent=shop.label||t('shopTitle');
 const items=document.getElementById('shopItems');
 const goods=[
  {n:'☕ '+({fa:'قهوه',en:'Coffee'}[lang]),p:8},
  {n:'🥪 '+({fa:'ساندویچ',en:'Sandwich'}[lang]),p:15},
  {n:'🍎 '+({fa:'سیب',en:'Apple'}[lang]),p:3},
  {n:'🔑 '+({fa:'کلید',en:'Key'}[lang]),p:25},
  {n:'⛽ '+({fa:'بنزین',en:'Gas'}[lang]),p:40}
 ];
 items.innerHTML='';
 goods.forEach(g=>{
  const el=document.createElement('div');
  el.className='shopItem';
  el.innerHTML=`<span>${g.n}</span><b>$${g.p}</b>
   <button>${t('buy')}</button>`;
  el.querySelector('button').onclick=()=>{
   if(money>=g.p){money-=g.p;showAction('✓ '+t('buy'),800)}
   else showAction(t('noMoney'),1000);
  };
  items.appendChild(el);
 });
 document.getElementById('shopModal').classList.add('open');
}
function closeShop(){
 document.getElementById('shopModal').classList.remove('open');
 currentShop=null;
}
document.getElementById('shopExit').onclick=closeShop;

function toggleVehicle(){
 if(interactCooldown>0)return;
 interactCooldown=.3;
 if(onFoot){
  const shop=nearestShop();
  if(shop&&!currentShop)openShop(shop);
  else enterVehicle();
 } else exitVehicle();
}
function resetVehicle(){
 carGroup.position.set(60,0,100);
 heading=Math.PI;speed=0;steerAngle=0;flightY=0;
 carBody.rotation.x=0;carBody.rotation.z=0;
 onFoot=false;person.visible=false;carBeacon.visible=false;
 $('mode').textContent=t('inCar');
 flashMsg('Reset');
}

// ============================================================
// Controls
// ============================================================
const keys=Object.create(null);
const used=['w','a','s','d','arrowup','arrowdown','arrowleft','arrowright',
 'shift',' ','e','f','h','c','m','r'];
document.addEventListener('keydown',e=>{
 const k=e.key.toLowerCase();
 if(used.includes(k))e.preventDefault();
 if(currentShop&&k==='escape'){closeShop();return}
 if(!keys[k]){
  if(k==='e'&&window.startRequested)toggleVehicle();
  if(k==='f'&&window.startRequested&&onFoot)enterVehicle();
  if(k==='h'&&window.startRequested&&!onFoot)honk();
  if(k==='c'&&window.startRequested)camMode=(camMode+1)%3;
  if(k==='r'&&window.startRequested)resetVehicle();
  if(window.startRequested&&['1','2','3','4','5','6','7','8','9','0'].includes(k)){
   const list=['sport','moto','sedan','bus','offroad','taxi','truck','police','ambulance','plane'];
   const i=k==='0'?9:Number(k)-1;
   if(list[i])createVehicle(list[i],currentColor);
  }
 }
 keys[k]=true;
});
document.addEventListener('keyup',e=>keys[e.key.toLowerCase()]=false);
window.addEventListener('blur',()=>{for(const k in keys)keys[k]=false});

document.querySelectorAll('[data-key]').forEach(btn=>{
 const key=btn.dataset.key;
 const down=e=>{e.preventDefault();if(!window.startRequested)return;
  keys[key]=true;btn.classList.add('pressed');
  try{btn.setPointerCapture(e.pointerId)}catch(_){}};
 const up=e=>{e.preventDefault();keys[key]=false;btn.classList.remove('pressed')};
 btn.addEventListener('pointerdown',down);
 btn.addEventListener('pointerup',up);
 btn.addEventListener('pointercancel',up);
 btn.addEventListener('lostpointercapture',up);
 btn.addEventListener('contextmenu',e=>e.preventDefault());
});
document.querySelector('[data-action="interact"]').addEventListener('pointerdown',
 e=>{e.preventDefault();if(window.startRequested)toggleVehicle()});
document.querySelector('[data-action="reset"]').addEventListener('pointerdown',
 e=>{e.preventDefault();if(window.startRequested)resetVehicle()});

document.getElementById('langBtn').onclick=()=>{
 lang=lang==='fa'?'en':'fa';
 for(const k in signMats)delete signMats[k];
 applyLang();
 if(vehicleSpecs[vehicleType])
  $('vname').textContent=lang==='fa'?vehicleSpecs[vehicleType].name:vehicleSpecs[vehicleType].nameEn;
 for(const s of shops){
  const type=buildingTypes.find(t=>t.key===s.type);
  if(type)s.label=lang==='fa'?type.label:type.labelEn;
 }
};
document.getElementById('rightToggle').onclick=()=>{
 document.getElementById('right').classList.toggle('collapsed');
};

// ============================================================
// Day / night
// ============================================================
const DAY_LEN=600,START_HOUR=8;
function updateDayNight(t){
 const phase=((t/DAY_LEN)+START_HOUR/24)%1;
 const a=(phase-0.25)*Math.PI*2;
 const sunY=Math.sin(a);
 sun.position.set(Math.cos(a)*350,sunY*400,-200);
 skyMat.uniforms.sunDir.value.copy(sun.position).normalize();
 const dayAmt=clamp(sunY*1.6+.45,0,1);
 const duskAmt=clamp(1-Math.abs(sunY)*3.5,0,1);
 const dayTop=new THREE.Color(0x3b7ac4),dayBot=new THREE.Color(0xd8e8f2);
 const nightTop=new THREE.Color(0x060a1e),nightBot=new THREE.Color(0x121a30);
 const duskTop=new THREE.Color(0x6a3050),duskBot=new THREE.Color(0xff6a20);
 const top=new THREE.Color().lerpColors(nightTop,dayTop,dayAmt);
 const bot=new THREE.Color().lerpColors(nightBot,dayBot,dayAmt);
 top.lerp(duskTop,duskAmt*.7);bot.lerp(duskBot,duskAmt*.7);
 skyMat.uniforms.top.value.copy(top);skyMat.uniforms.bot.value.copy(bot);
 scene.fog.color.copy(bot);
 sun.intensity=dayAmt*1.7;moon.intensity=(1-dayAmt)*.5;
 lampGlowMat.opacity=(1-dayAmt)*.9;
 ambient.intensity=.1+dayAmt*.3;
 starMat.opacity=(1-dayAmt)*.85;
 const hours=phase*24;
 const hh=Math.floor(hours),mm=Math.floor((hours-hh)*60);
 $('clockTxt').textContent=String(hh).padStart(2,'0')+':'+String(mm).padStart(2,'0');
}

// ============================================================
// Minimap
// ============================================================
const MAP_S=240;
const mapCtx=$('map').getContext('2d');
const MAP_MIN_X=-900,MAP_MAX_X=900,MAP_MIN_Z=-700,MAP_MAX_Z=1900;
const MAP_W=MAP_MAX_X-MAP_MIN_X,MAP_H=MAP_MAX_Z-MAP_MIN_Z;
const mapScale=MAP_S/Math.max(MAP_W,MAP_H);
const mapBase=document.createElement('canvas');
mapBase.width=MAP_S;mapBase.height=MAP_S;
{
 const x=mapBase.getContext('2d');
 x.fillStyle='#3e5a2e';x.fillRect(0,0,MAP_S,MAP_S);
 const offset=(MAP_S-MAP_W*mapScale)/2;
 x.translate(offset,0);
 x.fillStyle='#2a6a9a';
 const wY=(RIVER_Z0-MAP_MIN_Z)*mapScale;
 x.fillRect(0,wY,MAP_S,(RIVER_Z1-RIVER_Z0)*mapScale);
 x.fillStyle='#0a0a0f';
 for(const r of roadsA){
  const px=(r-MAP_MIN_X)*mapScale;
  x.fillRect(px-ROAD_W/2*mapScale,0,ROAD_W*mapScale,MAP_S);
  const pz=(r-MAP_MIN_Z)*mapScale;
  x.fillRect(0,pz-ROAD_W/2*mapScale,MAP_S,ROAD_W*mapScale);
 }
 for(const r of roadsBX){
  const px=(r-MAP_MIN_X)*mapScale;
  const pz0=(1300-MAP_MIN_Z)*mapScale;
  const pz1=(1820-MAP_MIN_Z)*mapScale;
  x.fillRect(px-ROAD_W/2*mapScale,pz0,ROAD_W*mapScale,pz1-pz0);
 }
 for(const r of roadsBZ){
  const pz=(r-MAP_MIN_Z)*mapScale;
  const px0=(-240-MAP_MIN_X)*mapScale;
  const px1=(240-MAP_MIN_X)*mapScale;
  x.fillRect(px0,pz-ROAD_W/2*mapScale,px1-px0,ROAD_W*mapScale);
 }
 const hx=(HWY_X-MAP_MIN_X)*mapScale;
 x.fillRect(hx-ROAD_W/2*mapScale,(540-MAP_MIN_Z)*mapScale,ROAD_W*mapScale,(1300-540)*mapScale);
 x.fillStyle='#555a60';
 x.fillRect((750-MAP_MIN_X)*mapScale,(100-MAP_MIN_Z)*mapScale,260*mapScale,40*mapScale);
 x.fillStyle='#a89880';
 for(const b of buildings){
  x.fillRect((b.x-b.sx/2-MAP_MIN_X)*mapScale,(b.z-b.sz/2-MAP_MIN_Z)*mapScale,
   b.sx*mapScale,b.sz*mapScale);
 }
}
const MAP_OFFSET_X=(MAP_S-MAP_W*mapScale)/2;
function drawMap(){
 mapCtx.clearRect(0,0,MAP_S,MAP_S);
 mapCtx.drawImage(mapBase,0,0);
 mapCtx.fillStyle='#e0e0e0';
 for(let i=0;i<trafficData.length;i++){
  const c=trafficData[i];
  const x=c.axis==='x'?c.roadN+c.offset:c.pos;
  const z=c.axis==='x'?c.pos:c.roadN+c.offset;
  mapCtx.fillRect(MAP_OFFSET_X+(x-MAP_MIN_X)*mapScale-1,(z-MAP_MIN_Z)*mapScale-1,2,2);
 }
 const p=onFoot?person.position:carGroup.position;
 const px=MAP_OFFSET_X+(p.x-MAP_MIN_X)*mapScale,py=(p.z-MAP_MIN_Z)*mapScale;
 mapCtx.save();
 mapCtx.translate(px,py);
 mapCtx.rotate(-heading);
 mapCtx.fillStyle='#22ffbb';mapCtx.strokeStyle='#003a25';mapCtx.lineWidth=1.2;
 mapCtx.beginPath();
 mapCtx.moveTo(0,-7);mapCtx.lineTo(5,6);mapCtx.lineTo(0,3);mapCtx.lineTo(-5,6);
 mapCtx.closePath();mapCtx.fill();mapCtx.stroke();
 mapCtx.restore();
}

// ============================================================
// Collision
// ============================================================
const PLAYER_R=1.4;
const WATER_MARGIN=2;

function isWater(x,z){
 if(z<RIVER_Z0+WATER_MARGIN||z>RIVER_Z1-WATER_MARGIN)return false;
 if(Math.abs(x-HWY_X)<HR+2)return false;
 return true;
}
function isOnRoad(x,z){
 for(const r of allRoadX)
  if(Math.abs(x-r.pos)<HR-1&&z>r.z0+1&&z<r.z1-1)return true;
 for(const r of allRoadZ)
  if(Math.abs(z-r.pos)<HR-1&&x>r.x0+1&&x<r.x1-1)return true;
 return false;
}
function isSolid(x,z){
 if(isOnRoad(x,z)&&!isWater(x,z))return false;
 if(isWater(x,z))return true;
 const gx=Math.floor(x/GS),gz=Math.floor(z/GS);
 for(let i=-1;i<=1;i++)for(let j=-1;j<=1;j++){
  const list=grid.get((gx+i)+','+(gz+j));
  if(!list)continue;
  for(const b of list)
   if(Math.abs(x-b.x)<b.rx+PLAYER_R&&Math.abs(z-b.z)<b.rz+PLAYER_R)return true;
 }
 for(let i=-1;i<=1;i++)for(let j=-1;j<=1;j++){
  const list=parkedGrid.get((gx+i)+','+(gz+j));
  if(!list)continue;
  for(const p of list){
   const dx=x-p.x,dz=z-p.z;
   const c=Math.cos(-p.ry),s=Math.sin(-p.ry);
   const lx=dx*c-dz*s,lz=dx*s+dz*c;
   if(Math.abs(lx)<p.w/2+PLAYER_R&&Math.abs(lz)<p.l/2+PLAYER_R)return true;
  }
 }
 return false;
}
function unstick(){
 const cx=carGroup.position.x,cz=carGroup.position.z;
 if(!isSolid(cx,cz))return false;
 for(let r=2;r<80;r+=2)
  for(let a=0;a<24;a++){
   const ang=a/24*Math.PI*2;
   const tx=cx+Math.cos(ang)*r;
   const tz=cz+Math.sin(ang)*r;
   if(!isSolid(tx,tz)){
    carGroup.position.x=tx;carGroup.position.z=tz;speed=0;return true;
   }
  }
 return false;
}

// ============================================================
// Main loop
// ============================================================
const clock=new THREE.Clock();
const camTarget=new THREE.Vector3();
let mapClock=0,simTime=0,stuckTimer=0;

function animate(){
 requestAnimationFrame(animate);
 const dt=Math.min(clock.getDelta(),1/30);
 simTime+=dt;

 updateSignals(simTime);
 updateDayNight(simTime);
 if(interactCooldown>0)interactCooldown-=dt;

 if(onFoot&&!currentShop){
  const shop=nearestShop();
  if(shop)flashMsg('E · '+shop.label);
  else flashMsg(t('welcome'));
 }

 if(window.startRequested&&!currentShop){
  const throttle=keys.w||keys.arrowup?1:0;
  const brake=keys.s||keys.arrowdown?1:0;
  const steerL=keys.a||keys.arrowleft?1:0;
  const steerR=keys.d||keys.arrowright?1:0;
  const steerInput=steerL-steerR;

  if(onFoot){
   heading+=steerInput*2.8*dt;
   const walk=6*dt*(keys.shift?1.9:1);
   let dx=0,dz=0;
   if(throttle){dx-=Math.sin(heading)*walk;dz-=Math.cos(heading)*walk}
   if(brake){dx+=Math.sin(heading)*walk;dz+=Math.cos(heading)*walk}
   const nx=person.position.x+dx,nz=person.position.z+dz;
   if(!isSolid(nx,person.position.z))person.position.x=nx;
   if(!isSolid(person.position.x,nz))person.position.z=nz;
   person.rotation.y=heading;
   $('speed').textContent=String((throttle||brake)?20:0);
   $('gear').textContent='P';
   const moving=throttle||brake;
   if(moving){
    walkPhase+=dt*(keys.shift?14:9);
    const s=Math.sin(walkPhase);
    humanParts.legL.rotation.x=s*.75;
    humanParts.legR.rotation.x=-s*.75;
    humanParts.armL.rotation.x=-s*.55;
    humanParts.armR.rotation.x=s*.55;
    humanParts.group.position.y=Math.abs(s)*.07;
   }else{
    const k=Math.max(0,1-dt*10);
    humanParts.legL.rotation.x*=k;humanParts.legR.rotation.x*=k;
    humanParts.armL.rotation.x*=k;humanParts.armR.rotation.x*=k;
    humanParts.group.position.y*=k;
   }
  } else {
   const spec=vehicleSpecs[vehicleType];
   const isPlane=spec.type==='plane';
   const targetSteer=steerInput*.62;
   steerAngle+=(targetSteer-steerAngle)*(1-Math.exp(-8*dt));
   const maxRev=spec.max*.28;
   if(throttle){
    if(speed<0)speed=Math.min(0,speed+spec.brake*1.15*dt);
    else speed=Math.min(spec.max,speed+spec.power*(1-.22*speed/spec.max)*dt);
   }
   if(brake){
    if(speed>0)speed=Math.max(0,speed-spec.brake*1.35*dt);
    else speed=Math.max(-maxRev,speed-spec.power*.48*dt);
   }
   if(!throttle&&!brake){
    const drag=isPlane?.10:.72;
    speed*=Math.exp(-drag*dt);
    if(Math.abs(speed)<.12)speed=0;
   }
   const speedRatio=clamp(Math.abs(speed)/Math.max(spec.max,1),0,1);
   if(Math.abs(speed)>.35){
    const reverseSign=speed>=0?1:-1;
    const steeringAuthority=.25+.75*speedRatio;
    heading+=steerInput*spec.turn*steeringAuthority*reverseSign*dt;
   }
   if(isPlane){
    const climb=keys.shift?1:(keys[' ']?-1:0);
    const autoLift=speed>20?Math.min(1,(speed-20)/40)*3:0;
    flightY+=climb*9*dt+autoLift*dt*.5;
    if(speed<20)flightY=Math.max(0,flightY-9*dt);
    flightY=clamp(flightY,0,240);
    carGroup.position.y=flightY;
    carBody.rotation.z=steerAngle*1.2*(Math.abs(speed)/spec.max);
    carBody.rotation.x=-climb*.15;
   }else{
    carGroup.position.y=0;
    carBody.rotation.z+=( -steerInput*speedRatio*.10-carBody.rotation.z)*(1-Math.exp(-4*dt));
    carBody.rotation.x+=(throttle*.025-brake*.018-carBody.rotation.x)*(1-Math.exp(-3*dt));
   }
   if(isPlane&&flightY<3&&isWater(carGroup.position.x,carGroup.position.z)){
    carGroup.position.set(60,0,100);
    heading=Math.PI;speed=0;flightY=0;
    flashMsg('✈ crashed! reset.');
   }
   const dx=-Math.sin(heading)*speed*dt;
   const dz=-Math.cos(heading)*speed*dt;
   const skipColl=isPlane&&flightY>3;
   const steps=Math.max(1,Math.ceil(Math.hypot(dx,dz)/1));
   let collided=false;
   for(let step=0;step<steps;step++){
    const sx=dx/steps,sz=dz/steps;
    const nx=carGroup.position.x+sx;
    const nz=carGroup.position.z+sz;
    if(skipColl){carGroup.position.x=nx;carGroup.position.z=nz;continue}
    let moved=false;
    if(!isSolid(nx,carGroup.position.z)){carGroup.position.x=nx;moved=true}
    if(!isSolid(carGroup.position.x,nz)){carGroup.position.z=nz;moved=true}
    if(!moved){collided=true;break}
   }
   if(collided){speed*=-.12;stuckTimer+=dt}
   else stuckTimer=0;
   if(stuckTimer>3){if(unstick())flashMsg('unstuck');stuckTimer=0}
   carGroup.rotation.y=heading;
   if(!skipColl&&isSolid(carGroup.position.x,carGroup.position.z))unstick();

   vehicleWheels.forEach(w=>{
    w.spin.rotation.x+=speed*dt*2.4;
    if(w.isFront)w.pivot.rotation.y=-steerAngle;
   });
   vehiclePropellers.forEach(p=>p.rotation.z+=dt*22);

   $('speed').textContent=String(Math.round(Math.abs(speed)*3.6));
   $('rpmBar').style.width=Math.min(100,Math.abs(speed)/spec.max*100)+'%';
   let gear='N';
   if(speed<-.4)gear='R';
   else if(speed>spec.max*.05)gear='D';
   $('gear').textContent=gear;
   updateEngineSound(Math.abs(speed)/spec.max,speed<-.4);
  }
 } else {
  updateEngineSound(0,false);
 }

 updateTraffic(dt,simTime);
 updatePeds(dt,simTime);

 planeAng1+=dt*.16;
 npcPlane1.position.set(
  Math.cos(planeAng1)*PLANE_R1,
  PLANE_Y1+Math.sin(planeAng1*2)*3,
  Math.sin(planeAng1)*PLANE_R1
 );
 npcPlane1.rotation.y=-planeAng1;
 npcPlane1.rotation.z=Math.sin(planeAng1*3)*.08;

 for(const c of clouds){c.position.x+=dt*2.5;if(c.position.x>2000)c.position.x=-2000}

 if(onFoot){
  carBeacon.visible=true;
  carBeacon.position.set(carGroup.position.x,
    carGroup.position.y+4.5+Math.sin(simTime*3)*.3,carGroup.position.z);
  carBeacon.rotation.y+=dt*2;
 } else carBeacon.visible=false;

 const p=onFoot?person.position:carGroup.position;
 let target,lookAt;
 if(camMode===1&&!onFoot){
  target=new THREE.Vector3(p.x-Math.sin(heading)*.2,p.y+1.4,p.z-Math.cos(heading)*.2);
  lookAt=new THREE.Vector3(p.x-Math.sin(heading)*5,p.y+1.2,p.z-Math.cos(heading)*5);
 }else if(camMode===2&&!onFoot){
  const ca=simTime*.5;
  target=new THREE.Vector3(p.x+Math.cos(ca)*12,p.y+3,p.z+Math.sin(ca)*12);
  lookAt=new THREE.Vector3(p.x,p.y+1,p.z);
 }else{
  target=new THREE.Vector3(p.x+Math.sin(heading)*9,p.y+5,p.z+Math.cos(heading)*9);
  lookAt=new THREE.Vector3(p.x-Math.sin(heading)*2,p.y+1.1,p.z-Math.cos(heading)*2);
 }
 camTarget.copy(target);
 camera.position.lerp(camTarget,1-Math.exp(-5*dt));
 camera.lookAt(lookAt);

 mapClock+=dt;
 if(mapClock>.15){drawMap();mapClock=0}

 renderer.render(scene,camera);
}

applyLang();
drawMap();
updateSignals(0);
updateDayNight(0);
window.gameReady=true;
$('error').textContent='';
animate();

} catch(err){
 document.getElementById('error').textContent='خطا: '+(err&&err.message?err.message:'?');
 console.error(err);
}
</script>
</body>
</html>"""


@app.route("/")
def home():
    return Response(HTML, mimetype="text/html")


if __name__ == "__main__":
  app.run()