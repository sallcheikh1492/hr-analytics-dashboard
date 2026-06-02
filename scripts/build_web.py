"""
Génère un dashboard web interactif autonome : docs/index.html
- Données nettoyées embarquées en JSON (fonctionne en local et sur GitHub Pages)
- Graphiques Plotly recalculés selon les filtres (département / sexe / âge)
Usage : python scripts/build_web.py
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "processed" / "hr_clean.csv"
OUT = ROOT / "docs" / "index.html"
OUT.parent.mkdir(exist_ok=True)

df = pd.read_csv(SRC, encoding="utf-8-sig")
cols = ["EmpID", "Department", "Position", "GenderLabel", "Age", "AgeBand", "TenureYears",
        "TenureBand", "Salary", "Attrition", "AttritionFlag", "IsVoluntary", "EmpSatisfaction",
        "EngagementSurvey", "PerformanceScore", "Absences", "RecruitmentSource",
        "SpecialProjectsCount", "ManagerName"]
records = df[cols].to_dict(orient="records")
DATA_JSON = json.dumps(records, ensure_ascii=False)

HTML = """<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard RH — Analyse des employés</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js" charset="utf-8"></script>
<style>
  :root{--blue:#2E86AB;--red:#E4572E;--ink:#1B3A4B;--bg:#f4f7fa;--card:#fff;--line:#e2e8f0;}
  *{box-sizing:border-box;}
  body{margin:0;font-family:'Segoe UI',Roboto,Arial,sans-serif;background:var(--bg);color:#243b4a;}
  header{background:linear-gradient(120deg,#1B3A4B,#2E86AB);color:#fff;padding:22px 28px;}
  header h1{margin:0;font-size:24px;}
  header p{margin:4px 0 0;opacity:.85;font-size:13px;}
  .wrap{max-width:1280px;margin:0 auto;padding:18px 22px 50px;}
  .filters{display:flex;flex-wrap:wrap;gap:14px;align-items:end;background:var(--card);
    border:1px solid var(--line);border-radius:12px;padding:14px 18px;margin:18px 0;}
  .filters label{display:block;font-size:11px;font-weight:600;color:#64748b;margin-bottom:4px;text-transform:uppercase;letter-spacing:.4px;}
  .filters select{padding:7px 10px;border:1px solid var(--line);border-radius:8px;font-size:14px;background:#fff;min-width:150px;}
  .filters button{padding:8px 16px;border:none;border-radius:8px;background:var(--blue);color:#fff;font-weight:600;cursor:pointer;}
  .filters button:hover{background:#256d8c;}
  .kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:14px;margin-bottom:8px;}
  .kpi{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px 18px;box-shadow:0 1px 3px rgba(0,0,0,.04);}
  .kpi .v{font-size:28px;font-weight:700;color:var(--ink);line-height:1.1;}
  .kpi .l{font-size:12px;color:#64748b;margin-top:4px;}
  .kpi.alert .v{color:var(--red);}
  .grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-top:16px;}
  .panel{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 14px 4px;box-shadow:0 1px 3px rgba(0,0,0,.04);}
  .panel h3{margin:6px 4px 0;font-size:14px;color:var(--ink);}
  .panel .sub{margin:2px 4px 6px;font-size:11px;color:#94a3b8;}
  .full{grid-column:1 / -1;}
  footer{max-width:1280px;margin:0 auto;padding:0 22px 40px;color:#94a3b8;font-size:12px;}
  @media(max-width:820px){.grid{grid-template-columns:1fr;}}
</style>
</head>
<body>
<header>
  <h1>📊 Dashboard RH — Analyse des employés</h1>
  <p>People Analytics · 311 employés · dataset HRDataset_v14 · dashboard interactif</p>
</header>

<div class="wrap">
  <div class="filters">
    <div><label>Département</label><select id="fDept"></select></div>
    <div><label>Sexe</label><select id="fGender"></select></div>
    <div><label>Tranche d'âge</label><select id="fAge"></select></div>
    <div><label>Source de recrutement</label><select id="fSrc"></select></div>
    <button onclick="resetFilters()">Réinitialiser</button>
  </div>

  <div class="kpis" id="kpis"></div>

  <div class="grid">
    <div class="panel"><h3>Attrition globale</h3><div class="sub">Part des employés ayant quitté l'entreprise</div><div id="c_donut" style="height:300px"></div></div>
    <div class="panel"><h3>Effectif par département</h3><div class="sub">Répartition des employés</div><div id="c_dept" style="height:300px"></div></div>
    <div class="panel"><h3>Taux d'attrition par département</h3><div class="sub">% de départs</div><div id="c_attr_dept" style="height:300px"></div></div>
    <div class="panel"><h3>Taux d'attrition par ancienneté</h3><div class="sub">Le signal le plus fort : les départs sont précoces</div><div id="c_attr_ten" style="height:300px"></div></div>
    <div class="panel"><h3>Taux d'attrition par tranche d'âge</h3><div id="c_attr_age" style="height:300px"></div></div>
    <div class="panel"><h3>Taux d'attrition par source de recrutement</h3><div class="sub">Prédicteur majeur</div><div id="c_attr_src" style="height:300px"></div></div>
    <div class="panel"><h3>Salaire selon l'attrition</h3><div class="sub">Distribution des salaires annuels</div><div id="c_salary" style="height:300px"></div></div>
    <div class="panel"><h3>Répartition des performances</h3><div id="c_perf" style="height:300px"></div></div>
    <div class="panel full"><h3>Absentéisme moyen — Département × Tranche d'âge</h3><div class="sub">Nombre moyen de jours d'absence</div><div id="c_heat" style="height:340px"></div></div>
  </div>
</div>

<footer>
  Source : <a href="https://www.kaggle.com/datasets/rhuebner/human-resources-data-set">Kaggle — HR Dataset (rhuebner)</a>.
  Taux d'attrition cumulé sur l'historique (non annualisé). Construit avec Plotly.js.
  Code &amp; rapport : <a href="https://github.com/kheuch1492/hr-analytics-dashboard">github.com/kheuch1492/hr-analytics-dashboard</a>.
</footer>

<script>
const DATA = __DATA__;
const BLUE="#2E86AB", RED="#E4572E", GREY="#94a3b8";
const AGE_ORDER=["<30","30-39","40-49","50+"];
const TEN_ORDER=["0-2 ans","3-5 ans","6-8 ans","9+ ans"];
const PERF_ORDER=["PIP","Needs Improvement","Fully Meets","Exceeds"];
const PLOT_CFG={displayModeBar:false,responsive:true};
const FONT={family:"Segoe UI, Arial",size:12,color:"#243b4a"};

function uniq(key){return [...new Set(DATA.map(d=>d[key]).filter(v=>v!==null&&v!==""&&v!==undefined))];}
function fillSelect(id,key,sortFn){
  const el=document.getElementById(id);
  let vals=uniq(key); if(sortFn) vals.sort(sortFn); else vals.sort();
  el.innerHTML='<option value="__all__">Tous</option>'+vals.map(v=>`<option value="${v}">${v}</option>`).join('');
  el.onchange=render;
}
function resetFilters(){['fDept','fGender','fAge','fSrc'].forEach(i=>document.getElementById(i).value='__all__');render();}

function filtered(){
  const d=document.getElementById('fDept').value, g=document.getElementById('fGender').value,
        a=document.getElementById('fAge').value, s=document.getElementById('fSrc').value;
  return DATA.filter(r=>(d==='__all__'||r.Department===d)&&(g==='__all__'||r.GenderLabel===g)
    &&(a==='__all__'||r.AgeBand===a)&&(s==='__all__'||r.RecruitmentSource===s));
}
const mean=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:0;
function rateBy(rows,key,order){
  const m={};
  rows.forEach(r=>{const k=r[key]; if(k===null||k===undefined||k==='')return; (m[k]=m[k]||[]).push(r.AttritionFlag);});
  let keys=Object.keys(m); if(order) keys=order.filter(k=>m[k]); else keys.sort((x,y)=>mean(m[y])-mean(m[x]));
  return {labels:keys, rates:keys.map(k=>+(mean(m[k])*100).toFixed(1)), counts:keys.map(k=>m[k].length)};
}

function kpiCard(v,l,alert){return `<div class="kpi ${alert?'alert':''}"><div class="v">${v}</div><div class="l">${l}</div></div>`;}

function render(){
  const R=filtered(); const n=R.length||1;
  const attr=mean(R.map(r=>r.AttritionFlag))*100;
  const absRate=mean(R.map(r=>r.Absences))/261*100;
  const kpis=[
    kpiCard(R.length,"Effectif"),
    kpiCard(attr.toFixed(1)+" %","Taux d'attrition",true),
    kpiCard(R.filter(r=>r.AttritionFlag===1).length,"Départs",true),
    kpiCard(mean(R.map(r=>r.EmpSatisfaction)).toFixed(2)+" /5","Satisfaction moy."),
    kpiCard(absRate.toFixed(1)+" %","Taux d'absentéisme"),
    kpiCard(Math.round(mean(R.map(r=>r.Salary))).toLocaleString('fr-FR')+" $","Salaire annuel moy."),
    kpiCard(mean(R.map(r=>r.TenureYears)).toFixed(1)+" ans","Ancienneté moy."),
  ];
  document.getElementById('kpis').innerHTML=kpis.join('');

  const lay=(extra={})=>Object.assign({margin:{t:10,r:10,b:40,l:90},font:FONT,paper_bgcolor:'rgba(0,0,0,0)',plot_bgcolor:'rgba(0,0,0,0)'},extra);

  // Donut
  const left=R.filter(r=>r.AttritionFlag===1).length, stay=R.length-left;
  Plotly.newPlot('c_donut',[{type:'pie',hole:.55,values:[stay,left],labels:['Restés','Partis'],
    marker:{colors:[BLUE,RED]},textinfo:'label+percent',sort:false}],lay({margin:{t:10,r:10,b:10,l:10},showlegend:false}),PLOT_CFG);

  // Effectif par dept
  const byd={}; R.forEach(r=>byd[r.Department]=(byd[r.Department]||0)+1);
  const dk=Object.keys(byd).sort((a,b)=>byd[a]-byd[b]);
  Plotly.newPlot('c_dept',[{type:'bar',orientation:'h',y:dk,x:dk.map(k=>byd[k]),marker:{color:BLUE},
    text:dk.map(k=>byd[k]),textposition:'auto'}],lay(),PLOT_CFG);

  // Attrition par dept
  let g=rateBy(R,'Department'); g.labels.reverse();g.rates.reverse();
  Plotly.newPlot('c_attr_dept',[{type:'bar',orientation:'h',y:g.labels,x:g.rates,marker:{color:RED},
    text:g.rates.map(v=>v+'%'),textposition:'auto'}],lay({xaxis:{ticksuffix:'%'}}),PLOT_CFG);

  // Attrition par anciennete
  g=rateBy(R,'TenureBand',TEN_ORDER);
  Plotly.newPlot('c_attr_ten',[{type:'bar',x:g.labels,y:g.rates,marker:{color:RED},
    text:g.rates.map(v=>v+'%'),textposition:'auto'}],lay({margin:{t:10,r:10,b:40,l:45},yaxis:{ticksuffix:'%'}}),PLOT_CFG);

  // Attrition par age
  g=rateBy(R,'AgeBand',AGE_ORDER);
  Plotly.newPlot('c_attr_age',[{type:'bar',x:g.labels,y:g.rates,marker:{color:RED},
    text:g.rates.map(v=>v+'%'),textposition:'auto'}],lay({margin:{t:10,r:10,b:40,l:45},yaxis:{ticksuffix:'%'}}),PLOT_CFG);

  // Attrition par source
  g=rateBy(R,'RecruitmentSource'); g.labels.reverse();g.rates.reverse();
  Plotly.newPlot('c_attr_src',[{type:'bar',orientation:'h',y:g.labels,x:g.rates,marker:{color:RED},
    text:g.rates.map(v=>v+'%'),textposition:'auto'}],lay({margin:{t:10,r:10,b:40,l:150},xaxis:{ticksuffix:'%'}}),PLOT_CFG);

  // Salaire box
  Plotly.newPlot('c_salary',[
    {type:'box',name:'Restés',y:R.filter(r=>r.Attrition==='No').map(r=>r.Salary),marker:{color:BLUE},boxmean:true},
    {type:'box',name:'Partis',y:R.filter(r=>r.Attrition==='Yes').map(r=>r.Salary),marker:{color:RED},boxmean:true}
  ],lay({margin:{t:10,r:10,b:30,l:70},showlegend:false}),PLOT_CFG);

  // Performance
  const bp={}; R.forEach(r=>bp[r.PerformanceScore]=(bp[r.PerformanceScore]||0)+1);
  const pl=PERF_ORDER.filter(k=>bp[k]);
  Plotly.newPlot('c_perf',[{type:'bar',x:pl,y:pl.map(k=>bp[k]),
    marker:{color:[RED,'#F3A712',BLUE,'#3A7D44'].slice(0,pl.length)},text:pl.map(k=>bp[k]),textposition:'auto'}],
    lay({margin:{t:10,r:10,b:40,l:45}}),PLOT_CFG);

  // Heatmap absences dept x age
  const depts=[...new Set(R.map(r=>r.Department))].sort();
  const z=depts.map(dp=>AGE_ORDER.map(ab=>{
    const sub=R.filter(r=>r.Department===dp&&r.AgeBand===ab).map(r=>r.Absences);
    return sub.length?+mean(sub).toFixed(1):null;}));
  Plotly.newPlot('c_heat',[{type:'heatmap',z:z,x:AGE_ORDER,y:depts,colorscale:'YlOrRd',
    hoverongaps:false,showscale:true,colorbar:{title:'Abs.'},
    text:z,texttemplate:'%{text}',textfont:{size:11}}],
    lay({margin:{t:10,r:10,b:40,l:130}}),PLOT_CFG);
}

fillSelect('fDept','Department');
fillSelect('fGender','GenderLabel');
fillSelect('fAge','AgeBand',(a,b)=>AGE_ORDER.indexOf(a)-AGE_ORDER.indexOf(b));
fillSelect('fSrc','RecruitmentSource');
render();
window.addEventListener('resize',()=>render());
</script>
</body>
</html>
"""

OUT.write_text(HTML.replace("__DATA__", DATA_JSON), encoding="utf-8")
size = OUT.stat().st_size // 1024
print(f"Dashboard web généré : {OUT} ({size} Ko, {len(records)} employés embarqués)")
