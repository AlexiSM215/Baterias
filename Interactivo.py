"""
Laboratorio interactivo de baterías
Materiales utilizados en baterías y almacenamiento de energía
Ingeniería de Materiales · Grupo 05 · Semestre 2027-1

Ejecutar con:
    pip install -r requirements.txt
    streamlit run Interactivo.py
"""

import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Laboratorio de Baterías", layout="wide")

# Interruptor de mantenimiento: True = la app solo muestra un aviso; False = funciona normal
MANTENIMIENTO = False

if MANTENIMIENTO:
    st.title("Laboratorio de Baterías")
    st.info("El laboratorio no está disponible por el momento. Vuelve pronto.")
    st.stop()

# --------------------------------------------------------------------------
# Estilos de la página
# --------------------------------------------------------------------------
st.markdown("""
<style>
.card {border-radius: 16px; padding: 18px 20px; margin-bottom: 12px;
       border: 1px solid rgba(128,128,128,.25); background: rgba(128,128,128,.06);}
.card h3 {margin: 0 0 6px 0; font-size: 1.15rem;}
.card p {margin: 0; font-size: .98rem; line-height: 1.45;}
.idea {border-left: 6px solid #16a34a; padding: 10px 16px; border-radius: 8px;
       background: rgba(22,163,74,.10); margin: 8px 0 14px 0; font-size: 1.02rem;}
.stat {text-align:center; border-radius: 14px; padding: 14px 8px; background: rgba(37,99,235,.08);
       border: 1px solid rgba(37,99,235,.25);}
.stat .v {font-size: 1.7rem; font-weight: 700;}
.stat .l {font-size: .88rem; opacity: .8;}
</style>
""", unsafe_allow_html=True)


def card(titulo, texto):
    st.markdown(f'<div class="card"><h3>{titulo}</h3><p>{texto}</p></div>', unsafe_allow_html=True)


def idea(texto):
    st.markdown(f'<div class="idea"><b>Idea clave:</b> {texto}</div>', unsafe_allow_html=True)


def stat(col, valor, etiqueta):
    col.markdown(f'<div class="stat"><div class="v">{valor}</div><div class="l">{etiqueta}</div></div>',
                 unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Widgets en tiempo real (HTML + JavaScript dentro de un iframe)
# --------------------------------------------------------------------------
CSS = """
html,body{overflow-x:hidden;scrollbar-width:thin}
::-webkit-scrollbar{width:8px;height:8px}::-webkit-scrollbar-thumb{background:#cbd5e1;border-radius:8px}
*{box-sizing:border-box}
body{margin:0;font-family:'Segoe UI',system-ui,-apple-system,Roboto,Helvetica,Arial,sans-serif;color:#0f172a;background:transparent;-webkit-font-smoothing:antialiased}
button,input{font-family:inherit}
.wrap{background:#f8fafc;border-radius:16px;padding:14px;border:1px solid #e2e8f0}
.row{display:flex;gap:10px;flex-wrap:wrap;align-items:stretch}
.kpi{flex:1;min-width:130px;background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:10px 8px;text-align:center}
.kpi .v{font-size:24px;font-weight:700}
.kpi .l{font-size:13px;color:#475569}
.sl{display:block;font-size:15px;margin:12px 0 4px}
input[type=range]{width:100%;accent-color:#2563eb;height:22px;margin:0}
input[type=text]{font-size:16px;padding:6px 10px;border-radius:8px;border:1px solid #cbd5e1;width:220px}
.msg{padding:10px 14px;border-radius:10px;margin:10px 0;font-size:15px;line-height:1.45}
.ok{background:#dcfce7;color:#14532d}.warn{background:#fef9c3;color:#713f12}
.bad{background:#fee2e2;color:#7f1d1d}.info{background:#dbeafe;color:#1e3a8a}
.b{font-size:15px;padding:8px 14px;border-radius:10px;border:1px solid #cbd5e1;background:#fff;cursor:pointer;color:#0f172a}
.b.on{background:#2563eb;color:#fff;border-color:#2563eb}
.cap{font-size:13px;color:#64748b;margin-top:4px}
canvas{display:block;width:100%;height:auto}
.t{font-size:15px;line-height:1.4;margin-top:4px}
.chip{padding:5px 10px;border-radius:999px;border:1px solid #cbd5e1;font-size:13px;background:#fff;color:#64748b}
.chip.on{background:#2563eb;color:#fff;border-color:#2563eb}
.grid3{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:12px}
"""

COMMON_JS = r"""
// Nitidez en pantallas con escala (Windows 125 %/150 %, Retina): el lienzo se dibuja
// con más píxeles reales pero el código sigue usando las medidas lógicas (960 x 430, etc.).
(function(){
  const S=Math.min(3,Math.max(2,Math.ceil(window.devicePixelRatio||1)));
  const P=HTMLCanvasElement.prototype,dW=Object.getOwnPropertyDescriptor(P,'width'),dH=Object.getOwnPropertyDescriptor(P,'height');
  const gc=P.getContext;
  function prep(cv){if(cv.__hd)return;cv.__hd=1;const w=dW.get.call(cv),h=dH.get.call(cv);
    dW.set.call(cv,w*S);dH.set.call(cv,h*S);
    Object.defineProperty(cv,'width',{get:()=>w,configurable:true});
    Object.defineProperty(cv,'height',{get:()=>h,configurable:true});}
  P.getContext=function(t,o){const first=!this.__hd;if(t==='2d')prep(this);const c=gc.call(this,t,o);
    if(t==='2d'&&first&&c)c.setTransform(S,0,0,S,0,0);return c;};
})();
function niceStep(s){const p=Math.pow(10,Math.floor(Math.log10(s)));const f=s/p;return (f<1.5?1:f<3?2:f<7?5:10)*p;}
function fmtN(v,d){d=d||0;return Number(v).toLocaleString('es-MX',{maximumFractionDigits:d,minimumFractionDigits:d});}
function tickLabel(v,log){if(log){return v>=1?Number(v).toLocaleString('es-MX'):String(+v.toPrecision(2));}
  return String(+v.toFixed(3));}
function range(a,b,n){const r=[];for(let i=0;i<n;i++)r.push(a+(b-a)*i/(n-1));return r;}
function logspace(a,b,n){return range(Math.log10(a),Math.log10(b),n).map(v=>Math.pow(10,v));}
function fmtT(s){const u=[['días',86400],['horas',3600],['minutos',60],['segundos',1]];
  for(const [n,f] of u){if(s>=f)return fmtN(s/f,1)+' '+n;}return fmtN(s,3)+' segundos';}
function chart(cv,o){
  const ctx=cv.getContext('2d'),W=cv.width,H=cv.height,m={l:74,r:22,t:20,b:54};
  ctx.clearRect(0,0,W,H);
  const lx=!!o.logx,ly=!!o.logy,fx=v=>lx?Math.log10(v):v,fy=v=>ly?Math.log10(v):v;
  const X0=fx(o.xmin),X1=fx(o.xmax),Y0=fy(o.ymin),Y1=fy(o.ymax);
  const px=v=>m.l+(fx(v)-X0)/(X1-X0)*(W-m.l-m.r), py=v=>H-m.b-(fy(v)-Y0)/(Y1-Y0)*(H-m.t-m.b);
  function ticks(a,b,log){const r=[];if(log){for(let e=Math.ceil(a-1e-9);e<=Math.floor(b+1e-9);e++)r.push(Math.pow(10,e));return r;}
    const st=niceStep((b-a)/5);for(let v=Math.ceil(a/st-1e-9)*st;v<=b+1e-9;v+=st)r.push(v);return r;}
  ctx.font='14px "Segoe UI",system-ui,sans-serif';ctx.lineWidth=1;
  for(const t of ticks(X0,X1,lx)){const x=px(t);ctx.strokeStyle='#e2e8f0';ctx.beginPath();ctx.moveTo(x,m.t);ctx.lineTo(x,H-m.b);ctx.stroke();
    ctx.fillStyle='#475569';ctx.textAlign='center';ctx.fillText(tickLabel(t,lx),x,H-m.b+20);}
  for(const t of ticks(Y0,Y1,ly)){const y=py(t);ctx.strokeStyle='#e2e8f0';ctx.beginPath();ctx.moveTo(m.l,y);ctx.lineTo(W-m.r,y);ctx.stroke();
    ctx.fillStyle='#475569';ctx.textAlign='right';ctx.fillText(tickLabel(t,ly),m.l-8,y+5);}
  ctx.strokeStyle='#94a3b8';ctx.lineWidth=1.5;ctx.strokeRect(m.l,m.t,W-m.l-m.r,H-m.t-m.b);
  ctx.fillStyle='#0f172a';ctx.textAlign='center';ctx.font='15px "Segoe UI",system-ui,sans-serif';
  if(o.xlabel)ctx.fillText(o.xlabel,(m.l+W-m.r)/2,H-10);
  if(o.ylabel){ctx.save();ctx.translate(18,(m.t+H-m.b)/2);ctx.rotate(-Math.PI/2);ctx.fillText(o.ylabel,0,0);ctx.restore();}
  ctx.save();ctx.beginPath();ctx.rect(m.l,m.t,W-m.l-m.r,H-m.t-m.b);ctx.clip();
  for(const b of (o.bands||[])){ctx.fillStyle=b.color;ctx.fillRect(px(b.x0),m.t,px(b.x1)-px(b.x0),H-m.t-m.b);}
  for(const h of (o.hlines||[])){const y=py(h.y);ctx.setLineDash([6,6]);ctx.strokeStyle='#94a3b8';ctx.lineWidth=1.5;
    ctx.beginPath();ctx.moveTo(m.l,y);ctx.lineTo(W-m.r,y);ctx.stroke();ctx.setLineDash([]);
    if(h.label){ctx.fillStyle='#64748b';ctx.textAlign='right';ctx.font='13px "Segoe UI",system-ui,sans-serif';ctx.fillText(h.label,W-m.r-6,y-5);}}
  for(const s of (o.series||[])){ctx.strokeStyle=s.color;ctx.lineWidth=s.width||3;ctx.beginPath();let f=true;
    for(const [x,y] of s.pts){const X=px(x),Y=py(y);if(f){ctx.moveTo(X,Y);f=false;}else ctx.lineTo(X,Y);}ctx.stroke();}
  for(const v of (o.vlines||[])){const x=px(v.x);ctx.setLineDash([5,5]);ctx.strokeStyle=v.color||'#0f172a';ctx.lineWidth=1.5;
    ctx.beginPath();ctx.moveTo(x,m.t);ctx.lineTo(x,H-m.b);ctx.stroke();ctx.setLineDash([]);}
  ctx.restore();
  for(const p of (o.markers||[])){const X=px(p.x),Y=py(p.y);ctx.fillStyle=p.color||'#dc2626';ctx.beginPath();ctx.arc(X,Y,8,0,7);ctx.fill();
    ctx.strokeStyle='white';ctx.lineWidth=2;ctx.stroke();
    if(p.label){const der=X>W*0.65;ctx.font='bold 14px "Segoe UI",system-ui,sans-serif';ctx.textAlign=der?'right':'left';ctx.fillStyle='#0f172a';
      ctx.fillText(p.label,X+(der?-12:12),Math.max(m.t+14,Y-12));}}
  if(o.legend){let x=m.l+12,y=m.t+22;ctx.font='14px "Segoe UI",system-ui,sans-serif';ctx.textAlign='left';
    for(const s of o.series){if(!s.label)continue;ctx.fillStyle=s.color;ctx.fillRect(x,y-8,20,5);ctx.fillStyle='#0f172a';
      ctx.fillText(s.label,x+26,y-2);x+=ctx.measureText(s.label).width+52;}}
}
"""


def widget(cuerpo, js, alto, datos=None):
    """Inserta un bloque HTML/JS que se actualiza en el navegador mientras se mueven los controles."""
    import json
    if datos is not None:
        js = js.replace("__DATOS__", json.dumps(datos))
    html = ("<!doctype html><html><head><meta charset='utf-8'><style>" + CSS + "</style></head><body>"
            "<div class='wrap'>" + cuerpo + "</div><script>" + COMMON_JS + js + "</script></body></html>")
    if hasattr(st, "iframe"):
        st.iframe(html, height=alto)
    else:
        import streamlit.components.v1 as components
        components.html(html, height=alto)


# --------------------------------------------------------------------------
# Datos (del documento; los marcados "aprox." son órdenes de magnitud didácticos)
# --------------------------------------------------------------------------
CATODOS = {
    "LCO": dict(nombre="Óxido de cobalto (LiCoO₂)", apodo="el de los celulares", q=148, v=3.8, color="#2563eb",
                estructura="Laminar", energia=4, potencia=3, seguridad=2, costo=1, ciclos=800,
                pro="Guarda mucha energía en poco espacio", contra="El cobalto es caro y escaso"),
    "NMC": dict(nombre="Níquel-manganeso-cobalto (NMC 811)", apodo="el de los autos de largo alcance", q=200, v=3.7,
                color="#7c3aed", estructura="Laminar", energia=5, potencia=3, seguridad=2, costo=2, ciclos=1500,
                pro="Muchísima energía, menos cobalto", contra="Menos estable con el calor"),
    "NCA": dict(nombre="Níquel-cobalto-aluminio (NCA)", apodo="el de máxima energía", q=199, v=3.7, color="#db2777",
                estructura="Laminar", energia=5, potencia=3, seguridad=2, costo=2, ciclos=1200,
                pro="Energía muy alta", contra="Estabilidad térmica limitada"),
    "LMO": dict(nombre="Espinela de manganeso (LiMn₂O₄)", apodo="el de las herramientas", q=120, v=4.1,
                color="#ea580c", estructura="Espinela", energia=2, potencia=5, seguridad=4, costo=4, ciclos=700,
                pro="Barato y entrega energía muy rápido", contra="Se desgasta rápido si hace calor"),
    "LFP": dict(nombre="Fosfato de hierro (LiFePO₄)", apodo="el seguro y duradero", q=165, v=3.4, color="#16a34a",
                estructura="Olivino", energia=3, potencia=3, seguridad=5, costo=5, ciclos=4000,
                pro="Seguro, barato, dura muchísimo, sin cobalto ni níquel", contra="Guarda menos energía"),
}
ANODOS = {
    "Grafito": dict(q=372, v=0.1, f_ciclos=1.0, d_seg=0, d_costo=0,
                    desc="el de siempre (como la punta de un lápiz)"),
    "Titanato (LTO)": dict(q=175, v=1.55, f_ciclos=5.0, d_seg=1, d_costo=-1,
                           desc="casi indestructible, pero con menos voltaje"),
    "Silicio": dict(q=3579, v=0.4, f_ciclos=0.15, d_seg=0, d_costo=-1,
                    desc="10 veces más capacidad, pero se infla"),
}


def curva(cat, x):
    caida = np.exp(-(1 - x) * 25)
    if cat == "LFP":
        return 3.42 - 0.04 * x + 0.25 * np.exp(-x * 25) - 0.8 * caida
    if cat == "LMO":
        return 4.15 - 0.15 / (1 + np.exp(-(x - 0.5) * 30)) - 0.1 * x - 0.9 * caida
    if cat == "LCO":
        return 4.2 - 0.35 * x - 0.15 * x ** 4 - 0.7 * caida
    return 4.2 - 0.75 * x - 0.15 * x ** 6 - 0.5 * caida


# ==========================================================================
# Widget: celda de ion-litio con porcentaje de carga
# ==========================================================================
CELDA_BODY = """
<div class="row" style="align-items:center">
  <button id="bD" class="b">Usar (descargar)</button>
  <button id="bC" class="b">Cargar</button>
  <button id="bP" class="b">Pausa</button>
  <span style="margin-left:auto;font-size:15px">Velocidad
    <input id="vel" type="range" min="1" max="10" value="5" style="width:150px;vertical-align:middle"></span>
</div>
<label class="sl">Porcentaje de carga: <b id="socTxt">100 %</b> &nbsp;<span style="color:#64748b">(arrastra para cargarla o descargarla)</span></label>
<input id="soc" type="range" min="0" max="100" value="100">
<canvas id="cv" width="960" height="430"></canvas>
<div class="row">
  <div class="kpi"><div class="v" id="kS">100 %</div><div class="l">carga</div></div>
  <div class="kpi"><div class="v" id="kV">4.15 V</div><div class="l">voltaje de la celda</div></div>
  <div class="kpi"><div class="v" id="kE">15.0 Wh</div><div class="l">energía guardada (celular de 15 Wh)</div></div>
  <div class="kpi"><div class="v" id="kH">10.0 h</div><div class="l">de uso restante (a 1.5 W)</div></div>
</div>
<div id="msg" class="msg info"></div>
<canvas id="ch" width="960" height="300"></canvas>
<div class="cap">Voltaje de la celda según su porcentaje de carga (NMC con grafito, curva esquemática). El punto rojo es el estado actual.</div>
"""

CELDA_JS = r"""
const cv=document.getElementById('cv'),ctx=cv.getContext('2d'),W=cv.width,H=cv.height;
const A={x0:70,x1:330},C={x0:630,x1:890},Y0=120,Y1=400,filas=5,cols=6,N=filas*cols;
const sl=document.getElementById('soc');
function slot(l,i){const r=Math.floor(i/cols),c=i%cols,e=l==='A'?A:C,g=(Y1-Y0)/filas;
  return {x:e.x0+22+c*(e.x1-e.x0-44)/(cols-1),y:Y0+g*(r+0.5)};}
const iones=[];for(let i=0;i<N;i++){const p=slot('A',i);iones.push({lado:'A',i:i,x:p.x,y:p.y,mov:null});}
let modo='pausa',ultimo=0;const eP=[];for(let k=0;k<14;k++)eP.push(k/14);
const vel=()=>+document.getElementById('vel').value;
const btn={descarga:'bD',carga:'bC',pausa:'bP'};
function setModo(m){modo=m;for(const k in btn)document.getElementById(btn[k]).classList.toggle('on',k===m);}
document.getElementById('bD').onclick=()=>setModo('descarga');
document.getElementById('bC').onclick=()=>setModo('carga');
document.getElementById('bP').onclick=()=>setModo('pausa');
setModo('pausa');
const dest=o=>o.mov?o.mov.dest:o.lado;
function libres(l){const oc=new Set(iones.filter(o=>dest(o)===l).map(o=>o.mov?o.mov.i:o.i));const r=[];
  for(let i=0;i<N;i++)if(!oc.has(i))r.push(i);return r;}
function lanzar(de){const a=de==='A'?'C':'A';const cand=iones.filter(o=>!o.mov&&o.lado===de);if(!cand.length)return false;
  const l=libres(a);if(!l.length)return false;const o=cand[Math.floor(Math.random()*cand.length)];
  const i=l[Math.floor(Math.random()*l.length)],p=slot(a,i);o.mov={dest:a,i:i,sx:o.x,sy:o.y,ex:p.x,ey:p.y,k:0};return true;}
function socNow(){let s=0;for(const o of iones){if(!o.mov)s+=o.lado==='A'?1:0;else s+=o.mov.dest==='A'?o.mov.k:1-o.mov.k;}return 100*s/N;}
function irA(p){const want=Math.round(N*p/100);let cur=iones.filter(o=>dest(o)==='A').length,g=0;
  while(cur>want&&g++<N){if(!lanzar('A'))break;cur--;}while(cur<want&&g++<2*N){if(!lanzar('C'))break;cur++;}}
sl.oninput=()=>{setModo('pausa');irA(+sl.value);};
const ocv=s=>3.0+0.55*(1-Math.exp(-s*8))+0.6*s;
function T(s,x,y,size,col,al){ctx.fillStyle=col||'#0f172a';ctx.font=(size||18)+'px "Segoe UI",system-ui,sans-serif';ctx.textAlign=al||'center';ctx.fillText(s,x,y);}
function capas(e,col){ctx.fillStyle=col;const g=(Y1-Y0)/filas;for(let r=0;r<=filas;r++)ctx.fillRect(e.x0,Y0+r*g-5,e.x1-e.x0,10);
  ctx.strokeStyle='#334155';ctx.lineWidth=2;ctx.strokeRect(e.x0,Y0-8,e.x1-e.x0,Y1-Y0+16);}
function wire(f){const p=[[200,112],[200,40],[760,40],[760,112]],L=[72,560,72];let d=f*704;
  for(let s=0;s<3;s++){if(d<=L[s]){const q=d/L[s];return [p[s][0]+(p[s+1][0]-p[s][0])*q,p[s][1]+(p[s+1][1]-p[s][1])*q];}d-=L[s];}return p[3];}
function draw(soc){
  ctx.clearRect(0,0,W,H);
  const haciaC=iones.filter(o=>o.mov&&o.mov.dest==='C').length,haciaA=iones.filter(o=>o.mov&&o.mov.dest==='A').length;
  const desc=haciaC>haciaA,carg=haciaA>haciaC;
  ctx.fillStyle='rgba(250,204,21,0.18)';ctx.fillRect(A.x1,Y0-8,C.x0-A.x1,Y1-Y0+16);
  ctx.setLineDash([8,8]);ctx.strokeStyle='#a16207';ctx.lineWidth=3;ctx.beginPath();ctx.moveTo(480,Y0-8);ctx.lineTo(480,Y1+8);ctx.stroke();ctx.setLineDash([]);
  capas(A,'#475569');capas(C,'#3b82f6');
  T('ÁNODO (–)  grafito',(A.x0+A.x1)/2,Y1+30,17);T('CÁTODO (+)  óxido metálico',(C.x0+C.x1)/2,Y1+30,17);
  T('Electrolito y separador',480,Y1+30,15,'#a16207');
  ctx.strokeStyle='#0f172a';ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(200,112);ctx.lineTo(200,40);ctx.lineTo(760,40);ctx.lineTo(760,112);ctx.stroke();
  if(carg){ctx.fillStyle='#16a34a';ctx.fillRect(420,20,120,40);ctx.strokeStyle='#0f172a';ctx.lineWidth=3;ctx.strokeRect(420,20,120,40);T('CARGADOR',480,47,16,'white');}
  else{ if(desc){const g=ctx.createRadialGradient(480,40,4,480,40,70);g.addColorStop(0,'rgba(250,204,21,0.95)');g.addColorStop(1,'rgba(250,204,21,0)');
      ctx.fillStyle=g;ctx.beginPath();ctx.arc(480,40,70,0,7);ctx.fill();}
    ctx.fillStyle=desc?'#fde047':'white';ctx.beginPath();ctx.arc(480,40,24,0,7);ctx.fill();ctx.strokeStyle='#0f172a';ctx.lineWidth=3;ctx.stroke();
    ctx.lineWidth=2;ctx.beginPath();ctx.moveTo(470,50);ctx.lineTo(475,32);ctx.lineTo(480,46);ctx.lineTo(485,32);ctx.lineTo(490,50);ctx.stroke();
    T('foco',480,86,14,'#334155');}
  if(desc||carg){const dir=desc?1:-1;for(let k=0;k<eP.length;k++){eP[k]=(eP[k]+dir*0.0025*vel()+1)%1;const [x,y]=wire(eP[k]);
      ctx.fillStyle='#ef4444';ctx.beginPath();ctx.arc(x,y,7,0,7);ctx.fill();T('–',x,y+5,13,'white');}
    T(desc?'los electrones (e⁻) viajan por el cable y encienden el foco →':'← el cargador empuja los electrones de regreso',480,104,15,'#b91c1c');}
  for(const o of iones){ctx.fillStyle='#16a34a';ctx.beginPath();ctx.arc(o.x,o.y,11,0,7);ctx.fill();ctx.strokeStyle='white';ctx.lineWidth=2;ctx.stroke();T('Li',o.x,o.y+5,11,'white');}
  const s=Math.round(soc);ctx.strokeStyle='#0f172a';ctx.lineWidth=3;ctx.strokeRect(20,20,120,46);ctx.fillStyle='#0f172a';ctx.fillRect(140,33,8,20);
  ctx.fillStyle=s>50?'#16a34a':(s>20?'#eab308':'#dc2626');ctx.fillRect(24,24,112*s/100,38);T(s+' %',80,51,20,'#0f172a');
  return {desc,carg};
}
const ch=document.getElementById('ch');const curvaPts=range(0,100,101).map(p=>[p,ocv(p/100)]);
function loop(ts){
  if((modo==='descarga'||modo==='carga')&&ts-ultimo>900/vel()){lanzar(modo==='descarga'?'A':'C');ultimo=ts;}
  for(const o of iones)if(o.mov){const m=o.mov;m.k=Math.min(1,m.k+0.004*vel());o.x=m.sx+(m.ex-m.sx)*m.k;
    o.y=m.sy+(m.ey-m.sy)*m.k+Math.sin(m.k*Math.PI*3)*18;if(m.k>=1){o.lado=m.dest;o.i=m.i;o.mov=null;}}
  const quieto=!iones.some(o=>o.mov),soc=(modo==='pausa'&&quieto)?+sl.value:socNow(),st=draw(soc),v=ocv(soc/100),s=Math.round(soc);
  if(modo!=='pausa')sl.value=s;
  document.getElementById('socTxt').textContent=s+' %';
  document.getElementById('kS').textContent=s+' %';
  document.getElementById('kV').textContent=v.toFixed(2)+' V';
  document.getElementById('kE').textContent=fmtN(15*soc/100,1)+' Wh';
  document.getElementById('kH').textContent=fmtN(15*soc/100/1.5,1)+' h';
  const msg=document.getElementById('msg');let t,c='info';
  if(st.desc){t='<b>Descargando (usas la batería):</b> los iones de litio (verdes) salen del grafito y viajan por el electrolito hacia el cátodo. Los electrones (rojos) no pueden cruzar el electrolito, así que dan la vuelta por el cable y encienden el foco. El porcentaje y el voltaje bajan.';c='warn';}
  else if(st.carg){t='<b>Cargando:</b> el cargador obliga a los iones de litio a regresar al ánodo, donde quedan guardados entre las capas del grafito. Así se almacena la energía. El porcentaje y el voltaje suben.';c='ok';}
  else if(s===0){t='<b>Batería vacía.</b> Todo el litio está en el cátodo. Presiona <b>Cargar</b> o mueve el deslizante.';c='bad';}
  else if(s===100){t='<b>Carga completa.</b> Todo el litio está guardado en el grafito. Presiona <b>Usar</b> o mueve el deslizante.';c='ok';}
  else{t='<b>En pausa.</b> El porcentaje de carga es la fracción de litio que está guardada en el ánodo: ahora mismo, '+s+' de cada 100.';}
  msg.className='msg '+c;msg.innerHTML=t;
  chart(ch,{xmin:0,xmax:100,ymin:2.9,ymax:4.3,xlabel:'Porcentaje de carga (%)',ylabel:'Voltaje (V)',
    series:[{pts:curvaPts,color:'#2563eb',width:4}],markers:[{x:soc,y:v,label:s+' %  ·  '+v.toFixed(2)+' V'}]});
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);
"""

# ==========================================================================
# Widget: calculadora de Faraday
# ==========================================================================
FARADAY_BODY = """
<div class="row" style="align-items:center">
  <span>Fórmula: <input id="f" type="text" value="LiFePO4"></span>
  <span class="cap" style="margin:0">Ejemplos:</span>
  <button class="b" data-f="LiFePO4" data-n="1">LiFePO4</button>
  <button class="b" data-f="LiCoO2" data-n="1">LiCoO2</button>
  <button class="b" data-f="LiMn2O4" data-n="1">LiMn2O4</button>
  <button class="b" data-f="C6" data-n="1">C6 (grafito)</button>
  <button class="b" data-f="Si" data-n="3.75">Si</button>
</div>
<label class="sl">Electrones por fórmula (n): <b id="nT">1</b></label>
<input id="n" type="range" min="0.25" max="4" step="0.05" value="1">
<label class="sl">Voltaje promedio (V): <b id="vT">3.40</b></label>
<input id="v" type="range" min="0" max="4.5" step="0.05" value="3.4">
<div class="row" style="margin-top:12px">
  <div class="kpi"><div class="v" id="kM">-</div><div class="l">masa molar M (g/mol)</div></div>
  <div class="kpi"><div class="v" id="kQ">-</div><div class="l">capacidad teórica (mAh/g)</div></div>
  <div class="kpi"><div class="v" id="kE">-</div><div class="l">energía específica (Wh/kg)</div></div>
</div>
<div id="err" class="msg bad" style="display:none"></div>
"""

FARADAY_JS = r"""
const MAS={H:1.008,Li:6.94,C:12.011,O:15.999,Na:22.99,Mg:24.305,Al:26.982,Si:28.085,P:30.974,S:32.06,Ti:47.867,
  Mn:54.938,Fe:55.845,Co:58.933,Ni:58.693,Zr:91.224,La:138.905,Ge:72.63,V:50.942,Cu:63.546,Zn:65.38};
const f=document.getElementById('f'),n=document.getElementById('n'),v=document.getElementById('v');
function masa(s){const re=/([A-Z][a-z]?)(\d*\.?\d*)/g;let m,t=0,usado='';s=s.replace(/\s/g,'');
  while((m=re.exec(s))!==null){if(!(m[1] in MAS))throw 'No conozco el elemento «'+m[1]+'»';t+=MAS[m[1]]*(m[2]?parseFloat(m[2]):1);usado+=m[0];}
  if(!t||usado!==s)throw 'Escribe una fórmula como LiFePO4 (sin paréntesis)';return t;}
function calc(){document.getElementById('nT').textContent=(+n.value).toFixed(2);document.getElementById('vT').textContent=(+v.value).toFixed(2);
  const e=document.getElementById('err');try{const M=masa(f.value),Q=(+n.value)*96485/(3.6*M);e.style.display='none';
    document.getElementById('kM').textContent=fmtN(M,1);document.getElementById('kQ').textContent=fmtN(Q,0);
    document.getElementById('kE').textContent=fmtN(Q*(+v.value),0);}
  catch(x){e.style.display='block';e.textContent=x;['kM','kQ','kE'].forEach(i=>document.getElementById(i).textContent='-');}}
f.oninput=calc;n.oninput=calc;v.oninput=calc;
document.querySelectorAll('button[data-f]').forEach(b=>b.onclick=()=>{f.value=b.dataset.f;n.value=b.dataset.n;calc();});
calc();
"""

# ==========================================================================
# Widget: difusión en las tres estructuras
# ==========================================================================
DIFUSION_BODY = """
<label class="sl">Temperatura: <b id="TT">25 °C</b> &nbsp;<span style="color:#64748b">(más calor = el litio se mueve más rápido)</span></label>
<input id="T" type="range" min="-20" max="60" value="25">
<div class="grid3" style="margin-top:10px">
  <div><canvas id="c1" width="300" height="260"></canvas>
    <div class="t"><b>Laminar (LCO, NMC)</b> · 2D<br>El litio se mueve en <b>planos</b>, como en los pisos de un edificio: puede ir a los lados, pero no subir.</div></div>
  <div><canvas id="c2" width="300" height="260"></canvas>
    <div class="t"><b>Espinela (LMO)</b> · 3D<br>Se mueve en <b>todas direcciones</b>, como coches en las calles de una ciudad. Por eso entrega energía muy rápido.</div></div>
  <div><canvas id="c3" width="300" height="260"></canvas>
    <div class="t"><b>Olivino (LFP)</b> · 1D<br>Se mueve por <b>túneles</b>. Si un defecto (la X roja) tapa un túnel, todo se atora. Por eso se usan partículas muy pequeñas.</div></div>
</div>
<div id="vm" class="msg info"></div>
"""

DIFUSION_JS = r"""
function mk(id){const c=document.getElementById(id);return c.getContext('2d');}
const x1=mk('c1'),x2=mk('c2'),x3=mk('c3'),Ts=document.getElementById('T');
function dot(x,X,Y,col,r){x.fillStyle=col;x.beginPath();x.arc(X,Y,r||8,0,7);x.fill();}
const L=[];for(let k=0;k<14;k++)L.push({y:30+45*(k%5)+29,x:Math.random()*300,v:(Math.random()<.5?-1:1)*(0.6+Math.random())});
const S=[];for(let k=0;k<12;k++){const i=Math.floor(Math.random()*7),j=Math.floor(Math.random()*6);S.push({i,j,ti:i,tj:j,k:1});}
const O=[];for(let k=0;k<15;k++)O.push({c:k%5,y:Math.random()*260,v:0.8+Math.random()*0.6});
const def={c:2,y:130};
function fac(){return Math.exp((+Ts.value-25)/30);}
function f(){
  const F=fac();document.getElementById('TT').textContent=Ts.value+' °C';
  document.getElementById('vm').innerHTML='Velocidad del litio: <b>'+fmtN(F,2)+' veces</b> la velocidad a 25 °C. '+(+Ts.value<5?'En frío la batería entrega menos energía.':(+Ts.value>45?'Con mucho calor el material se degrada más rápido.':''));
  x1.clearRect(0,0,300,260);x1.fillStyle='#3b82f6';for(let r=0;r<6;r++)x1.fillRect(0,30+45*r,300,14);
  for(const p of L){p.x+=p.v*F;if(p.x<8){p.x=8;p.v=Math.abs(p.v);}if(p.x>292){p.x=292;p.v=-Math.abs(p.v);}dot(x1,p.x,p.y,'#16a34a');}
  x2.clearRect(0,0,300,260);for(let i=0;i<8;i++)for(let j=0;j<7;j++)dot(x2,10+40*i,10+40*j,'#fb923c',6);
  x2.strokeStyle='rgba(22,163,74,.25)';x2.lineWidth=2;
  for(let i=0;i<7;i++){x2.beginPath();x2.moveTo(30+40*i,0);x2.lineTo(30+40*i,260);x2.stroke();}
  for(let j=0;j<6;j++){x2.beginPath();x2.moveTo(0,30+40*j);x2.lineTo(300,30+40*j);x2.stroke();}
  for(const p of S){p.k+=0.025*F;if(p.k>=1){p.i=p.ti;p.j=p.tj;p.k=0;const d=[[1,0],[-1,0],[0,1],[0,-1]].filter(d=>p.i+d[0]>=0&&p.i+d[0]<7&&p.j+d[1]>=0&&p.j+d[1]<6);
      const e=d[Math.floor(Math.random()*d.length)];p.ti=p.i+e[0];p.tj=p.j+e[1];}
    dot(x2,30+40*(p.i+(p.ti-p.i)*p.k),30+40*(p.j+(p.tj-p.j)*p.k),'#16a34a');}
  x3.clearRect(0,0,300,260);for(let c=0;c<5;c++){x3.fillStyle='#a16207';x3.fillRect(10+60*c,0,10,260);x3.fillRect(50+60*c,0,10,260);
    x3.fillStyle='rgba(22,163,74,.10)';x3.fillRect(20+60*c,0,30,260);}
  x3.strokeStyle='#dc2626';x3.lineWidth=5;const dx=35+60*def.c;x3.beginPath();x3.moveTo(dx-12,def.y-12);x3.lineTo(dx+12,def.y+12);
  x3.moveTo(dx+12,def.y-12);x3.lineTo(dx-12,def.y+12);x3.stroke();
  for(const p of O){const X=35+60*p.c;let ny=p.y+p.v*F;if(p.c===def.c&&p.y<def.y-18&&ny>=def.y-18)ny=def.y-18;
    if(O.some(q=>q!==p&&q.c===p.c&&q.y>p.y&&q.y-ny<18))ny=p.y;p.y=ny;if(p.y>270)p.y=-10;dot(x3,X,p.y,'#16a34a');}
  requestAnimationFrame(f);}
f();
"""

# ==========================================================================
# Widget: tamaño de partícula y tiempo de difusión
# ==========================================================================
TAMANO_BODY = """
<label class="sl">Tamaño de la partícula: <b id="LT">1 µm</b></label>
<input id="L" type="range" min="0" max="1000" value="667">
<div class="row" style="margin-top:12px">
  <div class="kpi"><div class="v" id="kL">-</div><div class="l">tamaño</div></div>
  <div class="kpi"><div class="v" id="kF" style="color:#16a34a">-</div><div class="l">tiempo para llenarse de litio · LFP (túneles 1D)</div></div>
  <div class="kpi"><div class="v" id="kM" style="color:#ea580c">-</div><div class="l">tiempo para llenarse de litio · LMO (red 3D)</div></div>
</div>
<canvas id="pc" width="960" height="150" style="margin-top:8px"></canvas>
<canvas id="ch" width="960" height="330"></canvas>
<div class="cap">t ≈ L²/D con coeficientes de difusión aproximados. Las líneas punteadas marcan 1 minuto, 1 hora y 1 día.</div>
"""

TAMANO_JS = r"""
const Ls=document.getElementById('L'),DF=1e-17,DM=1e-14;
const tm=(L,D)=>Math.pow(L*1e-9,2)/D;
const fmtL=L=>L<1000?fmtN(L,0)+' nm':fmtN(L/1000,L<10000?1:0)+' µm';
const xs=logspace(10,10000,80);
const pc=document.getElementById('pc'),px=pc.getContext('2d');
function upd(){const L=Math.pow(10,1+(+Ls.value)/1000*3);
  document.getElementById('LT').textContent=fmtL(L);document.getElementById('kL').textContent=fmtL(L);
  document.getElementById('kF').textContent=fmtT(tm(L,DF));document.getElementById('kM').textContent=fmtT(tm(L,DM));
  px.clearRect(0,0,960,150);const r=8+62*(Math.log10(L)-1)/3;
  px.fillStyle='#16a34a';px.globalAlpha=0.25;px.beginPath();px.arc(480,75,r,0,7);px.fill();px.globalAlpha=1;
  px.strokeStyle='#15803d';px.lineWidth=3;px.stroke();
  px.fillStyle='#0f172a';px.font='15px "Segoe UI",system-ui,sans-serif';px.textAlign='left';
  px.fillText('Partícula de '+fmtL(L)+': mientras más grande, más lejos tiene que viajar el litio para llegar al centro.',20,145);
  px.strokeStyle='#dc2626';px.lineWidth=2;px.beginPath();px.moveTo(480+r,75);px.lineTo(480,75);px.stroke();
  px.fillStyle='#dc2626';px.fillText('L',480+r/2-4,68);
  chart(document.getElementById('ch'),{xmin:10,xmax:10000,ymin:1e-4,ymax:1e6,logx:true,logy:true,legend:true,
    xlabel:'Tamaño de la partícula (nm)',ylabel:'Tiempo (minutos)',
    hlines:[{y:1,label:'1 minuto'},{y:60,label:'1 hora'},{y:1440,label:'1 día'}],
    series:[{pts:xs.map(x=>[x,tm(x,DF)/60]),color:'#16a34a',label:'LFP'},{pts:xs.map(x=>[x,tm(x,DM)/60]),color:'#ea580c',label:'LMO'}],
    vlines:[{x:L,color:'#dc2626'}],
    markers:[{x:L,y:tm(L,DF)/60,color:'#16a34a'},{x:L,y:tm(L,DM)/60,color:'#ea580c'}]});}
Ls.oninput=upd;upd();
"""

# ==========================================================================
# Widget: silicio
# ==========================================================================
SILICIO_BODY = """
<label class="sl">Silicio en el ánodo: <b id="sT">10 %</b> &nbsp;<span style="color:#64748b">(el resto es grafito)</span></label>
<input id="si" type="range" min="0" max="100" value="10">
<label class="sl">Número de cargas (ciclos): <b id="cT">0</b></label>
<input id="cy" type="range" min="0" max="1000" step="10" value="0">
<div class="row" style="margin-top:12px">
  <div class="kpi"><div class="v" id="kQ">-</div><div class="l">capacidad inicial (mAh/g)</div></div>
  <div class="kpi"><div class="v" id="kX">-</div><div class="l">cuánto se infla al cargarse</div></div>
  <div class="kpi"><div class="v" id="kR">-</div><div class="l">capacidad que queda (mAh/g)</div></div>
</div>
<canvas id="pc" width="960" height="250" style="margin-top:8px"></canvas>
<div id="msg" class="msg"></div>
<canvas id="ch" width="960" height="320"></canvas>
<div class="cap">Capacidad del ánodo conforme se carga muchas veces (modelo de desgaste ilustrativo).</div>
"""

SILICIO_JS = r"""
const si=document.getElementById('si'),cy=document.getElementById('cy'),pc=document.getElementById('pc'),px=pc.getContext('2d');
const rnd=s=>{const x=Math.sin(s*12.9898)*43758.5453;return x-Math.floor(x);};
const ns=range(0,1000,101);
function upd(){const s=+si.value,c=+cy.value;
  const q=(1-s/100)*372+s/100*3579,ex=(1-s/100)*10+s/100*280,k=0.00015+0.004*Math.pow(s/100,1.3),ret=Math.exp(-k*c);
  document.getElementById('sT').textContent=s+' %';document.getElementById('cT').textContent=c;
  document.getElementById('kQ').textContent=fmtN(q);document.getElementById('kX').textContent='+'+fmtN(ex)+' %';
  document.getElementById('kR').textContent=fmtN(q*ret)+' ('+fmtN(100*ret)+' %)';
  px.clearRect(0,0,960,250);const r0=60,r1=r0*Math.cbrt(1+ex/100);
  px.fillStyle='#94a3b8';px.beginPath();px.arc(230,115,r0,0,7);px.fill();
  px.fillStyle='#0f172a';px.font='16px "Segoe UI",system-ui,sans-serif';px.textAlign='center';px.fillText('Sin litio',230,240);
  px.font='40px "Segoe UI",system-ui,sans-serif';px.fillText('→',440,128);
  px.fillStyle=s<20?'#94a3b8':(s<60?'#d97706':'#b45309');px.globalAlpha=0.9;px.beginPath();px.arc(680,115,r1,0,7);px.fill();px.globalAlpha=1;
  px.setLineDash([6,6]);px.strokeStyle='#0f172a';px.lineWidth=2;px.beginPath();px.arc(680,115,r0,0,7);px.stroke();px.setLineDash([]);
  let n=ex<40?0:(ex<100?2:(ex<180?4:7));if(s>15)n+=Math.floor(c/250);n=Math.min(10,n);
  px.strokeStyle='#0f172a';px.lineWidth=3;
  for(let j=0;j<n;j++){const a=rnd(j+1)*2*Math.PI,xa=680+r1*Math.cos(a),ya=115+r1*Math.sin(a),xb=680+r1*0.35*Math.cos(a+0.3),yb=115+r1*0.35*Math.sin(a+0.3);
    px.beginPath();px.moveTo(xa,ya);px.lineTo((xa+xb)/2+8,(ya+yb)/2);px.lineTo(xb,yb);px.stroke();}
  px.fillStyle='#0f172a';px.font='16px "Segoe UI",system-ui,sans-serif';px.fillText('Cargada (con litio)',680,240);
  const m=document.getElementById('msg');
  if(ex<40){m.className='msg ok';m.innerHTML='<b>Estable.</b> La partícula casi no cambia de tamaño; la batería dura mucho.';}
  else if(ex<100){m.className='msg warn';m.innerHTML='<b>Cuidado.</b> Se infla bastante: la capa protectora (SEI) se rompe y la batería se va desgastando.';}
  else{m.className='msg bad';m.innerHTML='<b>Demasiado.</b> Las partículas se agrietan y pierden contacto. La batería muere pronto.';}
  chart(document.getElementById('ch'),{xmin:0,xmax:1000,ymin:0,ymax:Math.max(420,q*1.08),legend:true,
    xlabel:'Número de cargas',ylabel:'Capacidad (mAh/g)',
    series:[{pts:ns.map(x=>[x,372*Math.exp(-0.00015*x)]),color:'#475569',label:'Sólo grafito'},
            {pts:ns.map(x=>[x,q*Math.exp(-k*x)]),color:'#d97706',width:4,label:'Tu ánodo ('+s+' % de silicio)'}],
    vlines:[{x:c}],markers:[{x:c,y:q*ret,color:'#d97706',label:fmtN(q*ret)+' mAh/g'}]});}
si.oninput=upd;cy.oninput=upd;upd();
"""

# ==========================================================================
# Widgets: procesamiento
# ==========================================================================
ETAPAS_BODY = """
<label class="sl">Recorre la cadena de fabricación: <b id="eT"></b></label>
<input id="e" type="range" min="0" max="8" value="0">
<div class="row" id="chips" style="margin-top:10px"></div>
<div class="msg info" id="eD" style="font-size:16px"></div>
"""

ETAPAS_JS = r"""
const E=__DATOS__,e=document.getElementById('e'),ch=document.getElementById('chips');
E.forEach((x,i)=>{const s=document.createElement('span');s.className='chip';s.textContent=(i+1)+'. '+x[0];s.onclick=()=>{e.value=i;upd();};s.style.cursor='pointer';ch.appendChild(s);});
function upd(){const i=Math.max(0,Math.min(E.length-1,+e.value));document.getElementById('eT').textContent='paso '+(i+1)+' de '+E.length+' · '+E[i][0];
  [...ch.children].forEach((c,j)=>c.classList.toggle('on',j===i));document.getElementById('eD').innerHTML='<b>'+E[i][0]+':</b> '+E[i][1];}
e.oninput=upd;upd();
"""

CALC_BODY = """
<label class="sl">Temperatura del horno: <b id="tT">820 °C</b></label>
<input id="t" type="range" min="500" max="1100" step="5" value="820">
<div class="row" style="margin-top:12px">
  <div class="kpi"><div class="v" id="kG">-</div><div class="l">tamaño de grano aprox.</div></div>
  <div class="kpi"><div class="v" id="kX">-</div><div class="l">níquel en los planos de litio (mezcla catiónica)</div></div>
  <div class="kpi"><div class="v" id="kC">-</div><div class="l">calidad del cristal</div></div>
</div>
<div id="msg" class="msg"></div>
<canvas id="ch" width="960" height="300"></canvas>
<div class="cap">Modelo cualitativo. La franja verde es la ventana industrial (700–950 °C).</div>
"""

CALC_JS = r"""
const t=document.getElementById('t');const cal=T=>100*Math.exp(-Math.pow((T-825)/150,4));
const ts=range(500,1100,121);
function upd(){const T=+t.value,g=0.2*Math.exp((T-700)/120),mx=Math.min(15,2+0.0006*Math.pow(T-820,2)),c=cal(T);
  document.getElementById('tT').textContent=T+' °C';document.getElementById('kG').textContent=fmtN(g,2)+' µm';
  document.getElementById('kX').textContent=fmtN(mx,1)+' %';document.getElementById('kC').textContent=fmtN(c)+' %';
  const m=document.getElementById('msg');
  if(T<700){m.className='msg bad';m.innerHTML='<b>Muy frío:</b> la reacción no termina y el cristal queda desordenado.';}
  else if(T>950){m.className='msg bad';m.innerHTML='<b>Muy caliente:</b> los granos crecen demasiado, se pierde litio y aumenta la mezcla catiónica.';}
  else{m.className='msg ok';m.innerHTML='<b>Dentro de la ventana industrial (700–950 °C):</b> el óxido laminar queda bien ordenado.';}
  chart(document.getElementById('ch'),{xmin:500,xmax:1100,ymin:0,ymax:110,xlabel:'Temperatura de calcinación (°C)',ylabel:'Calidad del cristal (%)',
    bands:[{x0:700,x1:950,color:'rgba(22,163,74,.12)'}],series:[{pts:ts.map(x=>[x,cal(x)]),color:'#2563eb',width:4}],
    vlines:[{x:T}],markers:[{x:T,y:c,label:T+' °C'}]});}
t.oninput=upd;upd();
"""

POROS_BODY = """
<label class="sl">Espacio vacío en el electrodo (porosidad): <b id="pT">30 %</b> &nbsp;<span style="color:#64748b">(los rodillos lo aplastan)</span></label>
<input id="p" type="range" min="5" max="60" value="30">
<canvas id="pc" width="960" height="190" style="margin-top:10px"></canvas>
<div id="msg" class="msg"></div>
<canvas id="ch" width="960" height="300"></canvas>
<div class="cap">Partículas grises sobre la lámina de aluminio; el fondo amarillo es el espacio para el electrolito. La franja verde es el rango típico (20–40 %).</div>
"""

POROS_JS = r"""
const p=document.getElementById('p'),pc=document.getElementById('pc'),px=pc.getContext('2d');
const rnd=s=>{const x=Math.sin(s*78.233)*43758.5453;return x-Math.floor(x);};
const den=q=>100*(1-q/100)/0.7,acc=q=>100*Math.min(1,Math.max(0,(q-10)/20));const qs=range(5,60,56);
function upd(){const q=+p.value;document.getElementById('pT').textContent=q+' %';
  px.clearRect(0,0,960,190);const alto=60+(q-5)*2.2;px.fillStyle='#fef9c3';px.fillRect(0,170-alto,960,alto);
  px.fillStyle='#d4a373';px.fillRect(0,170,960,20);const n=Math.round(900*(1-q/100)*alto/180);
  px.fillStyle='#6b7280';for(let i=0;i<n;i++){px.beginPath();px.arc(rnd(i+1)*960,170-rnd(i+500)*alto,8,0,7);px.fill();}
  px.fillStyle='#0f172a';px.font='14px "Segoe UI",system-ui,sans-serif';px.textAlign='left';px.fillText('Lámina de aluminio',10,186);
  const m=document.getElementById('msg');
  if(q<20){m.className='msg bad';m.innerHTML='<b>Demasiado aplastado:</b> el electrolito no logra entrar y la batería pierde potencia.';}
  else if(q>40){m.className='msg warn';m.innerHTML='<b>Muy poroso:</b> se desperdicia espacio y cabe menos energía.';}
  else{m.className='msg ok';m.innerHTML='<b>Rango típico (20–40 %):</b> buen equilibrio entre energía y paso del electrolito.';}
  chart(document.getElementById('ch'),{xmin:5,xmax:60,ymin:0,ymax:140,legend:true,xlabel:'Porosidad (%)',ylabel:'Valor relativo (%)',
    bands:[{x0:20,x1:40,color:'rgba(22,163,74,.12)'}],
    series:[{pts:qs.map(x=>[x,den(x)]),color:'#2563eb',label:'Energía que cabe'},{pts:qs.map(x=>[x,acc(x)]),color:'#ca8a04',label:'Entrada del electrolito'}],
    vlines:[{x:q}],markers:[{x:q,y:den(q),color:'#2563eb'},{x:q,y:acc(q),color:'#ca8a04'}]});}
p.oninput=upd;upd();
"""

SONORA_BODY = """
<label class="sl">Litio en la arcilla: <b id="pT">2000 ppm</b></label>
<input id="ppm" type="range" min="301" max="5890" value="2000">
<label class="sl">Arcilla procesada: <b id="tT">1 tonelada</b></label>
<input id="ton" type="range" min="0" max="400" value="0">
<div class="row" style="margin-top:12px">
  <div class="kpi"><div class="v" id="kL">-</div><div class="l">de litio</div></div>
  <div class="kpi"><div class="v" id="kC">-</div><div class="l">baterías de celular (aprox.)</div></div>
  <div class="kpi"><div class="v" id="kA">-</div><div class="l">autos eléctricos (aprox.)</div></div>
</div>
<div class="cap">Suponiendo que se recupera todo el litio (~1 g por celular y ~8 kg por auto), algo que todavía no se logra de forma rentable con estas arcillas.</div>
"""

SONORA_JS = r"""
const pp=document.getElementById('ppm'),to=document.getElementById('ton');
function upd(){const ppm=+pp.value,ton=Math.round(Math.pow(10,(+to.value)/100)),g=ton*ppm;
  document.getElementById('pT').textContent=fmtN(ppm)+' ppm';
  document.getElementById('tT').textContent=fmtN(ton)+(ton===1?' tonelada':' toneladas');
  document.getElementById('kL').textContent=g<1000?fmtN(g)+' g':fmtN(g/1000,1)+' kg';
  document.getElementById('kC').textContent=fmtN(g);document.getElementById('kA').textContent=fmtN(g/8000,1);}
pp.oninput=upd;to.oninput=upd;upd();
"""


# --------------------------------------------------------------------------
# Navegación
# --------------------------------------------------------------------------
PASOS = [
    "1. Cómo funciona una celda de ion-litio",
    "2. Arma tu batería",
    "3. Dentro del cristal",
    "4. El problema del silicio",
    "5. Reto: elige la batería",
    "6. De la mina a tu celular",
    "7. Quiz final",
]
if "paso" not in st.session_state:
    st.session_state.paso = PASOS[0]


def ir(delta):
    i = PASOS.index(st.session_state.paso)
    st.session_state.paso = PASOS[max(0, min(len(PASOS) - 1, i + delta))]


with st.sidebar:
    st.title("Laboratorio de Baterías")
    st.radio("Recorrido", PASOS, key="paso", label_visibility="collapsed")
    i_actual = PASOS.index(st.session_state.paso)
    st.progress((i_actual + 1) / len(PASOS), text=f"Paso {i_actual + 1} de {len(PASOS)}")
    st.divider()
    st.caption("Ingeniería de Materiales · Grupo 05 · 2027-1")
    st.caption("Valadez Colin Sebastián · Silvestre Morales Gael Octavio · "
               "Silva Martínez Alexis · Mendoza López Aaron")
    st.caption("Prof. David Eduardo Abad Contreras")


def navegacion():
    st.divider()
    a, _, b = st.columns([1, 3, 1])
    i = PASOS.index(st.session_state.paso)
    if i > 0:
        a.button("← Anterior", on_click=ir, args=(-1,), width="stretch")
    if i < len(PASOS) - 1:
        b.button("Siguiente →", on_click=ir, args=(1,), type="primary", width="stretch")


paso = st.session_state.paso

# --------------------------------------------------------------------------
# 1. Funcionamiento
# --------------------------------------------------------------------------
if paso == PASOS[0]:
    st.title("Cómo funciona una celda de ion-litio")
    st.markdown("Una celda de ion-litio es como un **estacionamiento con dos edificios**: el litio "
                "se va de un edificio al otro y, mientras viaja, la energía sale por el cable. "
                "El **porcentaje de carga** indica cuánto litio sigue guardado en el ánodo.")
    widget(CELDA_BODY, CELDA_JS, 1160)
    c1, c2, c3 = st.columns(3)
    with c1:
        card("Ánodo (–)", "Normalmente grafito. Aquí se <b>guarda</b> el litio cuando la batería está cargada.")
    with c2:
        card("Electrolito", "Deja pasar a los <b>iones</b> de litio, pero <b>no</b> a los electrones.")
    with c3:
        card("Cátodo (+)", "Un óxido o fosfato metálico. Aquí <b>llega</b> el litio cuando usas la batería.")
    idea("El litio va y viene entre dos materiales sin destruirlos (por eso se le llama batería «mecedora»). "
         "<b>Qué tan bien</b> lo hace depende de los materiales.")
    with st.expander("Para los curiosos: las reacciones"):
        st.markdown("Durante la **descarga**:")
        st.latex(r"\text{Ánodo (oxidación): } \mathrm{LiC_6 \rightarrow C_6 + Li^+ + e^-}")
        st.latex(r"\text{Cátodo (reducción): } \mathrm{CoO_2 + Li^+ + e^- \rightarrow LiCoO_2}")
        st.markdown("Una **celda** es una sola unidad; una **batería** son dos o más celdas conectadas.")
    navegacion()

# --------------------------------------------------------------------------
# 2. Arma tu batería
# --------------------------------------------------------------------------
elif paso == PASOS[1]:
    st.title("Arma tu batería")
    st.markdown("Elige un **cátodo** y un **ánodo** y mira qué tan buena sale tu batería en la vida real.")
    c1, c2 = st.columns(2)
    cat = c1.radio("Cátodo (+)", list(CATODOS), format_func=lambda k: f"{k} · {CATODOS[k]['apodo']}", index=1)
    ano = c2.radio("Ánodo (–)", list(ANODOS), format_func=lambda k: f"{k} · {ANODOS[k]['desc']}")
    dc, da = CATODOS[cat], ANODOS[ano]

    q = dc["q"] * da["q"] / (dc["q"] + da["q"])        # mAh/g de materiales activos
    v = dc["v"] - da["v"]
    e_celda = q * v * 0.5                               # aprox. celda real
    horas_cel = e_celda * 0.045 / 1.5                   # batería de 45 g, 1.5 W de consumo
    km = e_celda * 0.75 * 450 / 160                     # paquete de 450 kg, 160 Wh/km
    ciclos = dc["ciclos"] * da["f_ciclos"]
    seguridad = max(1, min(5, dc["seguridad"] + da["d_seg"]))
    costo = max(1, min(5, dc["costo"] + da["d_costo"]))

    st.markdown(f"### Tu batería: **{cat} + {ano}**")
    s1, s2, s3, s4 = st.columns(4)
    stat(s1, f"{v:.1f} V", "voltaje")
    stat(s2, f"{horas_cel:.1f} h", "de pantalla en un celular")
    stat(s3, f"{km:.0f} km", "de autonomía en un auto")
    stat(s4, f"{ciclos / 365:.0f} años" if ciclos >= 365 else f"{ciclos / 30:.0f} meses",
         f"cargándola diario (~{ciclos:,.0f} ciclos)")
    st.write("")
    b1, b2 = st.columns(2)
    b1.progress(seguridad / 5, text=f"Seguridad: {seguridad} de 5")
    b1.progress(costo / 5, text=f"Precio accesible: {costo} de 5")
    b2.markdown(f"**Lo bueno:** {dc['pro']}")
    b2.markdown(f"**Lo malo:** {dc['contra']}")
    if ano == "Silicio":
        st.warning("El silicio puro se infla casi 4 veces al cargarse y se rompe en pocos ciclos. Ve al paso 4 para verlo.")
    if ano == "Titanato (LTO)":
        st.info("El titanato casi no cambia de tamaño: dura muchísimo, pero baja el voltaje a unos 2 V.")

    st.subheader("Curva de descarga")
    st.caption("Mueve el deslizante de la gráfica para ver cómo baja el voltaje mientras usas la batería.")
    comparar = st.checkbox("Comparar con todos los cátodos")
    x = np.linspace(0.001, 0.999, 300)
    fig = go.Figure()
    for k in (CATODOS if comparar else [cat]):
        fig.add_trace(go.Scatter(x=x * 100, y=curva(k, x) - da["v"], name=k, hoverinfo="skip",
                                 line=dict(color=CATODOS[k]["color"], width=5 if k == cat else 2)))

    def v_en(p):
        return float(curva(cat, min(max(p / 100, 0.001), 0.999)) - da["v"])

    pos = list(range(0, 101, 2))
    p0 = 24
    fig.add_trace(go.Scatter(x=[p0], y=[v_en(p0)], mode="markers", showlegend=False, hoverinfo="skip",
                             marker=dict(size=18, color="#dc2626", line=dict(width=2, color="white"))))
    idx = len(fig.data) - 1
    pasos_sl = [dict(method="update", label=str(p),
                     args=[{"x": [[p]], "y": [[v_en(p)]]},
                           {"title.text": f"Batería usada: {p} %   ·   Voltaje: {v_en(p):.2f} V"}, [idx]])
                for p in pos]
    fig.update_layout(
        height=480, margin=dict(t=50, b=10), title=dict(text=f"Batería usada: {p0} %   ·   Voltaje: {v_en(p0):.2f} V"),
        xaxis=dict(title="Batería usada (%)", range=[0, 100]), yaxis_title="Voltaje (V)",
        legend=dict(orientation="h", y=1.12, x=1, xanchor="right"),
        sliders=[dict(active=pos.index(p0), steps=pasos_sl, pad=dict(t=50),
                      currentvalue=dict(prefix="Batería usada (%): ", font=dict(size=15)))])
    st.plotly_chart(fig, width="stretch")
    st.caption("Fíjate en el LFP: su voltaje queda casi plano porque el cristal cambia entre dos fases. Curvas esquemáticas.")

    with st.expander("Para los curiosos: ¿de dónde salen los números? (ley de Faraday)"):
        st.latex(r"Q_{\text{teórica}} = \frac{n\,F}{3.6\,M}\ \mathrm{[mAh/g]} \qquad E = Q \times V")
        st.markdown("**n** = electrones por fórmula, **F** = 96 485 C/mol, **M** = masa molar. "
                    "Escribe una fórmula o mueve los deslizantes:")
        widget(FARADAY_BODY, FARADAY_JS, 360)
        st.caption("Los resultados de arriba son aproximados: una celda real pesa más que sus materiales activos.")
    idea("No existe la batería perfecta: la que guarda más energía no es la más segura ni la más barata.")
    navegacion()

# --------------------------------------------------------------------------
# 3. Dentro del cristal
# --------------------------------------------------------------------------
elif paso == PASOS[2]:
    st.title("Dentro del cristal")
    st.markdown("Los átomos del cátodo forman un **cristal** con caminos por donde viaja el litio. "
                "La forma de esos caminos decide qué tan rápido se carga y descarga la batería.")
    widget(DIFUSION_BODY, DIFUSION_JS, 520)

    st.subheader("Experimento: ¿qué pasa si hago las partículas más pequeñas?")
    widget(TAMANO_BODY, TAMANO_JS, 760)
    idea("El tiempo crece con el <b>cuadrado</b> del tamaño (t ≈ L²/D): una partícula 10 veces más chica "
         "se llena <b>100 veces</b> más rápido. Por eso el LFP se fabrica en nanopartículas recubiertas de carbono.")

    st.subheader("Los cristales en 3D")
    st.caption("Gira el modelo con el ratón y usa el deslizante para llenar el cristal de litio.")
    fam = st.radio("Estructura", ["Laminar (LCO, NMC)", "Espinela (LMO)", "Olivino (LFP)"], horizontal=True)
    rng = np.random.default_rng(7)
    g = np.arange(4)
    fig = go.Figure()
    if fam.startswith("Laminar"):
        X, Y = np.meshgrid(g, g)
        met = np.array([(a, b, z) for z in (0, 2, 4) for a, b in zip(X.ravel(), Y.ravel())])
        li = np.array([(a, b, z) for z in (1, 3) for a, b in zip(X.ravel(), Y.ravel())], dtype=float)
        fig.add_trace(go.Scatter3d(x=met[:, 0], y=met[:, 1], z=met[:, 2], mode="markers",
                                   marker=dict(size=9, color="#2563eb"), name="Metal y oxígeno"))
    elif fam.startswith("Espinela"):
        met = np.array([(i, j, k) for i in g for j in g for k in g])
        li = (met[(met < 3).all(axis=1)] + 0.5).astype(float)
        fig.add_trace(go.Scatter3d(x=met[:, 0], y=met[:, 1], z=met[:, 2], mode="markers",
                                   marker=dict(size=7, color="#ea580c"), name="Manganeso"))
    else:
        X, Z = np.meshgrid(g, g)
        fig.add_trace(go.Scatter3d(x=X.ravel(), y=np.full(16, 1.5), z=Z.ravel(), mode="markers",
                                   marker=dict(size=9, color="#a16207"), name="Hierro y fosfato"))
        li = np.array([(xx, yy, zz) for xx in [0.5, 1.5, 2.5] for zz in [0.0, 1.5, 3.0]
                       for yy in np.linspace(0, 3, 6)], dtype=float)
        for xx in [0.5, 1.5, 2.5]:
            for zz in [0.0, 1.5, 3.0]:
                fig.add_trace(go.Scatter3d(x=[xx, xx], y=[0, 3], z=[zz, zz], mode="lines", hoverinfo="skip",
                                           line=dict(color="rgba(22,163,74,.35)", width=6), showlegend=False))
    li = li[rng.permutation(len(li))]
    fig.add_trace(go.Scatter3d(x=li[:, 0], y=li[:, 1], z=li[:, 2], mode="markers",
                               marker=dict(size=6, color="#16a34a"), name="Litio"))
    idx = len(fig.data) - 1
    pasos_sl = []
    for p in range(0, 101, 10):
        n = round(len(li) * p / 100)
        pasos_sl.append(dict(method="restyle", label=f"{p}",
                             args=[{"x": [li[:n, 0].tolist()], "y": [li[:n, 1].tolist()], "z": [li[:n, 2].tolist()]},
                                   [idx]]))
    fig.update_layout(height=560, margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h"),
                      scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode="cube"),
                      sliders=[dict(active=10, steps=pasos_sl, pad=dict(t=10),
                                    currentvalue=dict(prefix="Litio dentro del cristal (%): ", font=dict(size=15)))])
    st.plotly_chart(fig, width="stretch")
    st.caption("Modelos simplificados. Laminar: R-3m · Espinela: Fd-3m · Olivino: Pnma. "
               "Cargar la batería saca el litio del cátodo; usarla lo vuelve a llenar.")
    navegacion()

# --------------------------------------------------------------------------
# 4. Silicio
# --------------------------------------------------------------------------
elif paso == PASOS[3]:
    st.title("El problema del silicio")
    st.markdown("El silicio guarda **casi 10 veces más** litio que el grafito, pero al llenarse **se infla como un globo**. "
                "¿Cuánto silicio le pondrías a tu ánodo?")
    widget(SILICIO_BODY, SILICIO_JS, 1000)
    idea("Más silicio = más energía al principio, pero se gasta más rápido. Por eso hoy sólo se mezcla "
         "un <b>poquito</b> de silicio con el grafito.")
    navegacion()

# --------------------------------------------------------------------------
# 5. Reto
# --------------------------------------------------------------------------
elif paso == PASOS[4]:
    st.title("Reto: elige la batería correcta")
    st.markdown("Eres ingeniero(a) de materiales. Para cada cliente, elige el **cátodo** que mejor le conviene.")
    RETOS = [
        ("Fabricante de celulares", "Necesito que la batería quepa en un teléfono delgado y dure todo el día.",
         {"LCO": 3, "NMC": 2, "NCA": 2},
         "El LCO guarda mucha energía en poco volumen, ideal para celulares (aunque el cobalto es caro)."),
        ("Auto eléctrico de lujo", "Quiero recorrer la mayor distancia posible con una carga.",
         {"NMC": 3, "NCA": 3, "LCO": 1},
         "NMC o NCA: los cátodos ricos en níquel tienen la mayor energía, ideal para la autonomía."),
        ("Auto eléctrico económico", "Que sea barato, seguro y que dure muchos años.",
         {"LFP": 3, "LMO": 1},
         "El LFP es más de 40 % más barato que el NMC, muy seguro y dura miles de ciclos."),
        ("Planta solar", "Guardar la energía del día para la noche. El peso no importa; quiero que dure 15 años.",
         {"LFP": 3},
         "El LFP domina el almacenamiento en la red (más del 90 % en 2025): barato, seguro y muy duradero."),
        ("Marca de taladros", "Necesito que entregue mucha energía de golpe y que sea barata.",
         {"LMO": 3, "LFP": 1},
         "El LMO (espinela) tiene caminos 3D para el litio: entrega mucha potencia y el manganeso es barato."),
    ]
    puntos = 0
    for i, (cliente, pide, buenas, expl) in enumerate(RETOS):
        with st.container(border=True):
            c1, c2 = st.columns([1, 2])
            c1.markdown(f"**Cliente {i + 1}: {cliente}**")
            c1.markdown(f"*«{pide}»*")
            r = c2.radio("Tu elección", list(CATODOS), index=None, horizontal=True, key=f"reto{i}")
            if r:
                p = buenas.get(r, 0)
                puntos += p
                if p == 3:
                    c2.success(f"¡Excelente elección! {expl}")
                elif p > 0:
                    c2.warning(f"Funciona, pero hay una mejor opción. {expl}")
                else:
                    c2.error(f"No es la mejor. {expl}")
    respondidas = sum(st.session_state.get(f"reto{i}") is not None for i in range(len(RETOS)))
    st.progress(puntos / (3 * len(RETOS)),
                text=f"Puntos: {puntos} de {3 * len(RETOS)} · respondidas {respondidas}/{len(RETOS)}")
    if respondidas == len(RETOS) and puntos == 3 * len(RETOS):
        st.balloons()
        st.success("¡Perfecto! Ya piensas como ingeniero(a) de materiales.")
    idea("Cada aplicación da prioridad a algo distinto (energía, costo, vida, potencia o seguridad), "
         "y eso decide qué material se elige.")
    navegacion()

# --------------------------------------------------------------------------
# 6. De la mina a tu celular
# --------------------------------------------------------------------------
elif paso == PASOS[5]:
    st.title("De la mina a tu celular")
    ETAPAS = [
        ("Extracción", "El litio sale de <b>salmueras</b> (agua salada que se evapora al sol), de <b>roca dura</b> "
                       "(espodumena) o de <b>arcillas</b>, como las de Sonora, México."),
        ("Refinación", "Se purifica hasta obtener carbonato o hidróxido de litio, y sulfatos de níquel, manganeso y "
                       "cobalto. Unas cuantas partes por millón de impurezas pueden arruinar la batería."),
        ("Síntesis", "En un reactor se forman esferitas de unos 10 µm (coprecipitación) y luego se hornean a "
                     "700–950 °C con litio para formar el cristal. Pruébalo abajo."),
        ("Mezclado", "El polvo se mezcla con carbono (para conducir electricidad) y un pegamento, como una pasta."),
        ("Recubrimiento", "La pasta se unta en láminas de aluminio (cátodo) o cobre (ánodo) y se seca en hornos."),
        ("Calandrado", "Unos rodillos aplastan el electrodo para que quepa más energía en menos espacio. Pruébalo abajo."),
        ("Ensamble", "Se enrolla o apila con el separador, se pone el electrolito en cuartos muy secos y se cierra."),
        ("Formación", "Las primeras cargas forman la capa protectora (SEI). Puede tardar días y es de lo más caro."),
        ("Reciclaje", "Al final se recuperan litio, cobalto, níquel y manganeso para hacer baterías nuevas."),
    ]
    widget(ETAPAS_BODY, ETAPAS_JS, 230, datos=ETAPAS)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Prueba: hornea el cátodo NMC")
        widget(CALC_BODY, CALC_JS, 560)
    with c2:
        st.subheader("Prueba: aplasta el electrodo")
        widget(POROS_BODY, POROS_JS, 640)

    st.subheader("¿Cuántas baterías salen del litio de Sonora?")
    st.markdown("En Sonora hay unas **235 000 hectáreas** con posible litio en arcillas (reserva minera desde 2023). "
                "Un estudio del IPN encontró entre **301 y 5 890 ppm** de litio en Bacadéhuachi.")
    widget(SONORA_BODY, SONORA_JS, 330)
    idea("No basta con encontrar el litio: hay que inventar un <b>proceso</b> rentable para sacarlo. "
         "Y fabricar la batería tiene tantos pasos que el procesamiento es tan importante como el material.")
    navegacion()

# --------------------------------------------------------------------------
# 7. Quiz
# --------------------------------------------------------------------------
elif paso == PASOS[6]:
    st.title("Quiz final")
    PREG = [
        ("Cuando **usas** la batería, ¿hacia dónde viajan los iones de litio?",
         ["Del cátodo al ánodo", "Del ánodo al cátodo", "Se quedan quietos"], 1,
         "Al descargar, el litio sale del grafito (ánodo) y llega al cátodo."),
        ("¿Qué indica el porcentaje de carga?",
         ["La temperatura de la batería", "Cuánto litio sigue guardado en el ánodo", "El voltaje máximo"], 1,
         "Al 100 % todo el litio está en el ánodo; al 0 %, todo está en el cátodo."),
        ("¿Por qué los electrones van por el cable y no por el electrolito?",
         ["Porque el electrolito sólo deja pasar iones", "Porque el cable es más corto", "Por la gravedad"], 0,
         "El electrolito conduce iones pero no electrones; eso obliga a los electrones a hacer trabajo por el cable."),
        ("¿Qué material elegirías para una planta solar que debe durar 15 años?", ["LCO", "NCA", "LFP"], 2,
         "LFP: seguro, barato y dura miles de ciclos."),
        ("¿Cuál es el gran problema del silicio en los ánodos?",
         ["Es muy caro", "Se infla ~280 % y se agrieta", "No guarda litio"], 1,
         "Guarda 10 veces más litio, pero se expande tanto que se rompe."),
        ("¿En qué estructura el litio se mueve en las 3 direcciones?", ["Laminar", "Espinela", "Olivino"], 1,
         "La espinela (LMO) tiene una red 3D de caminos: alta potencia."),
        ("Si hago una partícula 10 veces más pequeña, el litio entra…",
         ["10 veces más rápido", "100 veces más rápido", "Igual de rápido"], 1,
         "t ≈ L²/D: el tiempo depende del cuadrado del tamaño."),
        ("¿Qué capa protectora se forma en las primeras cargas?", ["SEI", "PVDF", "DRX"], 0,
         "La SEI deja pasar iones de litio pero no electrones, y protege al electrolito."),
    ]
    correctas = 0
    for i, (q, ops, c, expl) in enumerate(PREG):
        with st.container(border=True):
            r = st.radio(f"**{i + 1}.** {q}", ops, index=None, key=f"quiz{i}")
            if r is not None:
                if r == ops[c]:
                    correctas += 1
                    st.success(f"¡Correcto! {expl}")
                else:
                    st.error(f"Era «{ops[c]}». {expl}")
    resp = sum(st.session_state.get(f"quiz{i}") is not None for i in range(len(PREG)))
    st.progress(correctas / len(PREG), text=f"Aciertos: {correctas} de {len(PREG)} · respondidas {resp}/{len(PREG)}")
    if resp == len(PREG):
        if correctas == len(PREG):
            st.balloons()
            st.success("¡Calificación perfecta!")
        else:
            st.info(f"Terminaste con {correctas}/{len(PREG)}. Repasa los pasos donde fallaste.")
    idea("Voltaje, capacidad, potencia, seguridad y costo se explican con la <b>composición</b>, la "
         "<b>estructura cristalina</b> y el <b>procesamiento</b> de los materiales. ¡Eso es ingeniería de materiales!")
    navegacion()
