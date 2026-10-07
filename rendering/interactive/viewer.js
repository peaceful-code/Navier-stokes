import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import flow from '../../output/immersive/flow_data.json';

const $ = id => document.getElementById(id);
const canvas = $('scene');
const reduced = matchMedia('(prefers-reduced-motion: reduce)').matches;
const state = {playing:!reduced,time:0,phase:0,auto:true,magnified:true,slice:false,markers:false};
const duration=30, h=.0005;
let renderer;
try { renderer=new THREE.WebGLRenderer({canvas,antialias:true,alpha:true,preserveDrawingBuffer:true,powerPreference:'high-performance'}); }
catch(e){ $('loading').textContent='La 3D WebGL est indisponible dans ce navigateur. Ouvre la scène Blender ou la vidéo du même dossier.'; throw e; }
renderer.setPixelRatio(Math.min(devicePixelRatio,1.25));
renderer.setClearColor(0x000000,0);
const scene=new THREE.Scene();
const camera=new THREE.PerspectiveCamera(37,1,.02,300);
camera.up.set(0,0,1);
const controls=new OrbitControls(camera,canvas);
controls.enableDamping=true; controls.dampingFactor=.065; controls.enablePan=false;
controls.minDistance=3; controls.maxDistance=50; controls.rotateSpeed=.5;
const initial=new THREE.Vector3(6.3,-8.8,5.92);
function resetCamera(){camera.position.copy(initial);controls.target.set(0,0,0);controls.update();}
resetCamera();
const scaleRoot=new THREE.Group();scene.add(scaleRoot);
let maxOmega=0;
for(const curve of flow.omega) for(const value of curve) maxOmega=Math.max(maxOmega,value);
const count=flow.positions.reduce((n,pts)=>n+2*(pts.length/3-1),0);
const position=new Float32Array(count*3), color=new Float32Array(count*3), progress=new Float32Array(count), ids=new Float32Array(count);
const cyan=new THREE.Color('#3bc5d4'), pale=new THREE.Color('#97e3e6'), gold=new THREE.Color('#e5b677');
let k=0;
for(let c=0;c<flow.positions.length;c++){
 const pts=flow.positions[c], n=pts.length/3;
 for(let i=0;i<n-1;i++) for(let j=i;j<=i+1;j++){
  const w=Math.max(0,flow.omega[c][j]/maxOmega);
  const mix=new THREE.Color().copy(w<=.8?cyan:pale);
  if(w<=.8) mix.lerp(pale,w/.8); else mix.lerp(gold,Math.pow((w-.8)/.2,.75));
  position.set(pts.slice(j*3,j*3+3),k*3);color.set([mix.r,mix.g,mix.b],k*3);
  progress[k]=j/(n-1);ids[k]=c;k++;
 }
}
const geometry=new THREE.BufferGeometry();
geometry.setAttribute('position',new THREE.BufferAttribute(position,3));
geometry.setAttribute('color',new THREE.BufferAttribute(color,3));
geometry.setAttribute('pathT',new THREE.BufferAttribute(progress,1));
geometry.setAttribute('curveId',new THREE.BufferAttribute(ids,1));
const uniforms={uPhase:{value:0},uSlice:{value:0},uMotion:{value:1}};
const material=new THREE.ShaderMaterial({uniforms,transparent:true,depthWrite:false,blending:THREE.NormalBlending,
 vertexShader:`attribute vec3 color;attribute float pathT;attribute float curveId;varying vec3 vColor;varying vec3 vPosition;varying float vT;varying float vId;
 void main(){vColor=color;vPosition=position;vT=pathT;vId=curveId;gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0);}`,
 fragmentShader:`precision highp float;uniform float uPhase;uniform float uSlice;uniform float uMotion;varying vec3 vColor;varying vec3 vPosition;varying float vT;varying float vId;
 void main(){if(uSlice>.5 && vPosition.y<0.)discard;float p=fract(vT*3.0-uPhase+vId*.618034);float head=smoothstep(.915,.977,p)*(1.-smoothstep(.978,1.,p));float edge=smoothstep(0.,.06,vT)*(1.-smoothstep(.94,1.,vT));float pulse=head*uMotion;vec3 c=mix(vColor,vec3(.82,.95,1.),pulse*.78);gl_FragColor=vec4(c,(.7+.3*pulse)*edge);
 #include <colorspace_fragment>
 }`});
scaleRoot.add(new THREE.LineSegments(geometry,material));
const reference=new THREE.Group();scaleRoot.add(reference);reference.visible=false;
const ringMaterial=new THREE.LineBasicMaterial({color:0x9dbac4,transparent:true,opacity:.22,depthWrite:false});
for(const radius of [1,2,3,4]){
 const pts=[];for(let i=0;i<=192;i++){const a=i*Math.PI*2/192;pts.push(new THREE.Vector3(radius*Math.cos(a),radius*Math.sin(a),0));}
 reference.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints(pts),ringMaterial));
}
reference.add(new THREE.Line(new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,-3.7),new THREE.Vector3(0,0,3.7)]),ringMaterial));
const stages=[
 {end:7,title:'Le fluide se rapproche de l’axe.',body:'Les spirales guident le regard vers le centre du vortex.'},
 {end:15,title:'Il tourne, puis s’évacue.',body:'Le mouvement se prolonge vers le haut et vers le bas.'},
 {end:23,title:'Le cœur se concentre.',body:'La vue agrandie suit la région qui rétrécit. Son rayon relatif est affiché.'},
 {end:31,title:'La rotation se renforce.',body:'La séquence reste avant τ = 0. Les traces indiquent seulement une direction.'}
];
let lastStage=-1;
const format=new Intl.NumberFormat('fr-FR',{maximumFractionDigits:1});
function update(){
 const tau=Math.pow(10,-4*state.time/duration), r=Math.sqrt(tau), axial=Math.pow(tau,.5-h);
 const zoom=state.magnified?1/r:1;
 scaleRoot.scale.set(r*zoom,r*zoom,axial*zoom);
 uniforms.uPhase.value=state.phase;uniforms.uSlice.value=state.slice?1:0;
 $('time').textContent=String(Math.floor(state.time)).padStart(2,'0')+' / 30 s';
 $('timeline').value=state.time;
 $('timeline').setAttribute('aria-valuetext',`${format.format(state.time)} secondes de présentation sur 30`);
 $('radius').textContent=format.format(100*r)+' %';
 $('tau').textContent=tau.toExponential(2).replace('.',',');
 $('magfactor').textContent=state.magnified?'× '+format.format(zoom):'× 1';
 $('viewlabel').textContent=state.magnified?'VUE AGRANDIE':'ÉCHELLE SPATIALE FIXE';
 $('play').textContent=state.playing?'Pause':'Lecture';$('play').setAttribute('aria-label',state.playing?'Mettre en pause':'Lire l’animation');
 $('play').setAttribute('aria-pressed',String(state.playing));
 $('mag').setAttribute('aria-pressed',String(state.magnified));
 $('auto').setAttribute('aria-pressed',String(state.auto));
 $('cut').setAttribute('aria-pressed',String(state.slice));
 $('markers').setAttribute('aria-pressed',String(state.markers));
 reference.visible=state.markers;
 const stage=stages.findIndex(s=>state.time<s.end);
 if(stage!==lastStage){$('caption').textContent=stages[stage].title;$('explain').textContent=stages[stage].body;lastStage=stage;}
 $('scene').setAttribute('aria-label',`Vortex en trois dimensions. ${flow.positions.length} lignes de courant d’un modèle pédagogique. Rayon ${format.format(100*r)} pour cent du départ.`);
}
function fit(){const box=canvas.parentElement.getBoundingClientRect();renderer.setSize(box.width,box.height,false);camera.aspect=box.width/box.height;camera.updateProjectionMatrix();}
new ResizeObserver(fit).observe(canvas.parentElement);fit();
$('loading').hidden=true;
controls.addEventListener('start',()=>{state.auto=false;update();});
$('play').onclick=()=>{if(state.time>=duration){state.time=0;state.phase=0;}state.playing=!state.playing;update();};
$('reset').onclick=()=>{state.time=0;state.phase=0;state.auto=true;state.magnified=true;state.slice=false;state.markers=false;state.playing=!reduced;resetCamera();update();};
$('auto').onclick=()=>{state.auto=!state.auto;update();};
$('mag').onclick=()=>{state.magnified=!state.magnified;update();};
$('cut').onclick=()=>{state.slice=!state.slice;update();};
$('markers').onclick=()=>{state.markers=!state.markers;update();};
$('timeline').oninput=e=>{state.time=+e.target.value;state.phase=state.time*.18;state.playing=false;update();};
const dialog=$('scope');
$('info').onclick=()=>dialog.showModal();$('closeinfo').onclick=()=>dialog.close();
dialog.addEventListener('click',e=>{if(e.target===dialog)dialog.close();});
let exportURL;
$('closeexport').onclick=()=>$('exportDialog').close();
$('snapshot').onclick=()=>{
 renderer.render(scene,camera);
 const image=document.createElement('canvas');image.width=canvas.width;image.height=canvas.height;
 const ctx=image.getContext('2d'),w=image.width,v=image.height;
 const bg=ctx.createRadialGradient(w/2,v*.43,0,w/2,v*.43,w*.6);
 bg.addColorStop(0,'#0d202b');bg.addColorStop(1,'#050c12');ctx.fillStyle=bg;ctx.fillRect(0,0,w,v);ctx.drawImage(canvas,0,0);
 const size=Math.max(14,w/85);ctx.fillStyle='#c0d3df';ctx.font=`${size}px sans-serif`;
 ctx.fillText('Illustration cinématique · profils simplifiés',w*.025,v*.95);
 ctx.fillText(`Rayon ${$('radius').textContent} · grossissement ${$('magfactor').textContent}`,w*.025,v*.95+size*1.5);
 image.toBlob(blob=>{if(!blob)return;if(exportURL)URL.revokeObjectURL(exportURL);exportURL=URL.createObjectURL(blob);$('exportImage').src=exportURL;$('downloadImage').href=exportURL;$('exportDialog').showModal();},'image/png');
};
addEventListener('keydown',e=>{if(e.code==='Space'&&!['INPUT','BUTTON','SELECT'].includes(document.activeElement.tagName)&&!dialog.open){e.preventDefault();$('play').click();}});
let prev=performance.now(), lastUI=0;
function animate(now){
 const dt=Math.min((now-prev)/1000,.05);prev=now;
 if(state.playing){state.time=Math.min(duration,state.time+dt);state.phase+=dt*(.13+.1*state.time/duration);if(state.time>=duration)state.playing=false;}
 uniforms.uPhase.value=state.phase;
 if(state.auto && state.playing){const a=.025*dt, p=camera.position;const x=p.x*Math.cos(a)-p.y*Math.sin(a);p.y=p.x*Math.sin(a)+p.y*Math.cos(a);p.x=x;}
 if(now-lastUI>90){update();lastUI=now;}
 controls.update();renderer.render(scene,camera);requestAnimationFrame(animate);
}
update();requestAnimationFrame(animate);
$('curveCount').textContent=String(flow.positions.length);
$('version').textContent=`Three.js ${THREE.REVISION} · ${flow.positions.length} courbes · ${flow.positions[0].length/3} points / courbe`;
