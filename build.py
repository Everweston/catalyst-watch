#!/usr/bin/env python3
"""Catalyst Watch — site generator.
Reads data/catalysts.json (+ data/universe.json) and writes a self-contained index.html
(data embedded, so it works opened as a local file AND deployed to GitHub Pages).
Run:  python3 build.py
"""
import json, os, html, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
def load(p, default):
    fp = os.path.join(ROOT, p)
    if os.path.exists(fp):
        return json.load(open(fp))
    return default

cat = load("data/catalysts.json", {"generated": "", "catalysts": []})
uni = load("data/universe.json", {"coverage": [], "watchlist": []})
catalysts = cat.get("catalysts", [])
generated = cat.get("generated", "") or datetime.date(2026,6,25).isoformat()

# sort: dated first (ascending), undated/TBD last
def keyfn(c):
    d = (c.get("date_iso") or "").strip()
    return (0, d) if (len(d) == 10 and d[:4].isdigit()) else (1, "9999")
catalysts = sorted(catalysts, key=keyfn)

payload = {
    "generated": generated,
    "coverage": uni.get("coverage", []),
    "watchlist": uni.get("watchlist", []),
    "catalysts": catalysts,
}
DATA_JSON = json.dumps(payload, ensure_ascii=False)

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Catalyst Watch</title>
<style>
:root{
  --navy:#0E2841; --navy2:#16395c; --yellow:#FFD400; --ink:#1a1a1a; --muted:#6b7785;
  --line:#e3e8ee; --bg:#eef1f5; --card:#ffffff; --soon:#fff8db;
}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;color:var(--ink);background:var(--bg);}
a{color:inherit}
.wrap{max-width:1060px;margin:0 auto;padding:0 16px}

/* header */
header{background:var(--navy);color:#fff;border-bottom:4px solid var(--yellow);}
.hd{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;padding:18px 0 14px}
.logo{font-size:26px;font-weight:800;letter-spacing:2px}
.logo .dot{color:var(--yellow)}
.tag{font-size:12.5px;color:#b9c6d6}
.asof{margin-left:auto;font-size:12px;color:#9fb0c4;white-space:nowrap}
.lead{font-size:12.5px;color:#cdd8e4;padding:0 0 16px;line-height:1.5;max-width:760px}

/* controls */
.controls{position:sticky;top:0;z-index:20;background:var(--bg);border-bottom:1px solid var(--line);padding:10px 0;}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
#q{flex:1;min-width:180px;padding:9px 12px;border:1px solid #cfd8e3;border-radius:8px;font-size:14px;background:#fff}
.chip{font-size:12px;padding:6px 11px;border:1px solid #cfd8e3;border-radius:999px;background:#fff;color:#33414f;cursor:pointer;user-select:none;white-space:nowrap}
.chip.on{background:var(--navy);color:#fff;border-color:var(--navy)}
.chip.tf.on{background:var(--navy)}
.count{font-size:12px;color:var(--muted);margin-left:auto;white-space:nowrap}

/* month divider */
.mdiv{font-size:12px;font-weight:800;letter-spacing:1.5px;color:var(--muted);margin:20px 2px 8px;text-transform:uppercase}

/* card */
.card{display:flex;gap:12px;background:var(--card);border:1px solid var(--line);border-left:4px solid var(--navy);border-radius:9px;padding:11px 13px;margin:8px 0;}
.card.soon{border-left-color:var(--yellow);background:linear-gradient(90deg,var(--soon),#fff 60%)}
.when{flex:0 0 92px;text-align:left}
.date{font-size:13px;font-weight:800;color:var(--navy);line-height:1.15}
.dow{font-size:11px;color:var(--muted)}
.until{display:inline-block;margin-top:4px;font-size:10.5px;font-weight:700;padding:2px 7px;border-radius:999px;background:#eaf0f6;color:#3a4a5a}
.until.imm{background:var(--yellow);color:#3a2c00}
.until.past{background:#f1d6d6;color:#7a2020}
.body{flex:1;min-width:0}
.top{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.tkr{font-family:ui-monospace,Menlo,Consolas,monospace;font-weight:800;font-size:13px;background:var(--navy);color:#fff;padding:1px 7px;border-radius:5px;letter-spacing:.5px}
.tkr.wl{background:#5a4b00;}
.co{font-size:12.5px;color:var(--muted)}
.ty{font-size:10.5px;font-weight:800;letter-spacing:.5px;text-transform:uppercase;padding:2px 7px;border-radius:5px;color:#fff}
.est{font-size:10px;color:#9a6a00;background:#fff3cf;border:1px solid #f0dca0;padding:1px 6px;border-radius:5px;font-weight:700}
.ttl{font-size:14px;font-weight:600;margin:5px 0 2px;line-height:1.3}
.why{font-size:12.5px;color:#41505f;line-height:1.45}
.meta{margin-top:5px;font-size:11px;color:var(--muted);display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.conf{display:inline-flex;align-items:center;gap:4px}
.cdot{width:8px;height:8px;border-radius:50%}
.src{color:#2c5d99;text-decoration:none}
.src:hover{text-decoration:underline}
.empty{padding:40px 8px;text-align:center;color:var(--muted)}

footer{margin:26px 0 40px;font-size:11.5px;color:var(--muted);line-height:1.5;border-top:1px solid var(--line);padding-top:14px}
footer b{color:#33414f}
@media (max-width:560px){ .when{flex-basis:74px} .logo{font-size:22px} .asof{margin-left:0;flex-basis:100%} }
</style>
</head>
<body>
<header><div class="wrap">
  <div class="hd">
    <div class="logo">CATALYST<span class="dot">·</span>WATCH</div>
    <div class="tag">upcoming catalysts across coverage</div>
    <div class="asof" id="asof"></div>
  </div>
  <div class="lead">Date-sorted feed of upcoming, potentially stock-moving events across the coverage list &amp; watchlist — earnings, investor days, FDA / data readouts, product launches, deal &amp; vote dates, lockups. Each shows <b>why it matters</b>. Dates are web-sourced (no live terminal) — <b>verify before trading</b>; <span class="est">~ est</span> = estimated date.</div>
</div></header>

<div class="controls"><div class="wrap">
  <div class="row">
    <input id="q" placeholder="Filter by ticker, company, or keyword…" autocomplete="off">
    <span class="count" id="count"></span>
  </div>
  <div class="row" style="margin-top:8px" id="types"></div>
  <div class="row" style="margin-top:7px" id="tfs"></div>
</div></div>

<div class="wrap"><div id="feed"></div></div>

<footer><div class="wrap" id="foot"></div></footer>

<script>
const PAYLOAD = __DATA__;
const TYPES = {
  earnings:{label:"Earnings",c:"#0E2841"}, "investor-day":{label:"Investor Day",c:"#0f766e"},
  fda:{label:"FDA / Data",c:"#b91c1c"}, product:{label:"Product",c:"#6d28d9"},
  deal:{label:"Deal / M&A",c:"#c2410c"}, regulatory:{label:"Regulatory",c:"#92600a"},
  lockup:{label:"Lockup",c:"#475569"}, index:{label:"Index",c:"#15803d"},
  guidance:{label:"Guidance",c:"#1d4ed8"}, other:{label:"Other",c:"#475569"}
};
const CONF = {high:"#16a34a", medium:"#d99000", low:"#b0381f"};
const cov = new Set(PAYLOAD.coverage||[]);
const cats = PAYLOAD.catalysts||[];

function fmtDate(iso){
  if(!iso || iso.length<10 || !/^\d{4}-\d{2}-\d{2}/.test(iso)) return null;
  const [y,m,d]=iso.slice(0,10).split('-').map(Number);
  return new Date(y, m-1, d);
}
function dayDiff(iso){
  const dt=fmtDate(iso); if(!dt) return null;
  const now=new Date(); now.setHours(0,0,0,0);
  return Math.round((dt-now)/86400000);
}
function untilLabel(n){
  if(n===null) return ["",""];
  if(n<0) return [(-n)+"d ago","past"];
  if(n===0) return ["TODAY","imm"];
  if(n===1) return ["tomorrow","imm"];
  if(n<=7) return ["in "+n+"d","imm"];
  if(n<=31) return ["in "+Math.round(n/7)+"w",""];
  return ["in "+Math.round(n/30)+"mo",""];
}
const MON=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];
const DOW=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];

let activeTypes=new Set(), tf="all", q="";

function passes(c){
  if(q){ const s=(c.ticker+" "+c.company+" "+c.title+" "+c.why+" "+(TYPES[c.type]?.label||"")).toLowerCase();
    if(!s.includes(q)) return false; }
  if(activeTypes.size && !activeTypes.has(c.type)) return false;
  if(tf!=="all"){
    const n=dayDiff(c.date_iso);
    if(n===null) return tf==="tbd";
    if(tf==="week" && (n<0||n>7)) return false;
    if(tf==="month" && (n<0||n>31)) return false;
    if(tf==="quarter" && (n<0||n>93)) return false;
    if(tf==="tbd") return false;
  }
  return true;
}

function render(){
  const feed=document.getElementById('feed');
  const list=cats.filter(passes);
  document.getElementById('count').textContent=list.length+" of "+cats.length+" catalysts";
  if(!list.length){ feed.innerHTML='<div class="empty">No catalysts match these filters.</div>'; return; }
  let html='', curMon='';
  for(const c of list){
    const dt=fmtDate(c.date_iso);
    const mon = dt ? (MON[dt.getMonth()]+" "+dt.getFullYear()) : "Undated / TBD";
    if(mon!==curMon){ html+='<div class="mdiv">'+mon+'</div>'; curMon=mon; }
    const n=dayDiff(c.date_iso); const [ul,uc]=untilLabel(n);
    const soon = (n!==null && n>=0 && n<=7);
    const ty=TYPES[c.type]||TYPES.other;
    const dnum = dt ? dt.getDate() : "";
    const dlab = dt ? (MON[dt.getMonth()]+" "+dnum) : "TBD";
    const dow = dt ? DOW[dt.getDay()] : "";
    const wl = !cov.has(c.ticker);
    html+='<div class="card'+(soon?' soon':'')+'">'+
      '<div class="when"><div class="date">'+esc(dlab)+'</div>'+(dow?'<div class="dow">'+dow+'</div>':'')+
        (ul?'<div class="until '+uc+'">'+ul+'</div>':'')+'</div>'+
      '<div class="body"><div class="top">'+
        '<span class="tkr'+(wl?' wl':'')+'">'+esc(c.ticker)+'</span>'+
        '<span class="co">'+esc(c.company)+'</span>'+
        '<span class="ty" style="background:'+ty.c+'">'+ty.label+'</span>'+
        (c.date_confirmed?'':'<span class="est">~ est</span>')+
      '</div>'+
      '<div class="ttl">'+esc(c.title)+'</div>'+
      '<div class="why">'+esc(c.why)+'</div>'+
      '<div class="meta"><span class="conf"><span class="cdot" style="background:'+(CONF[c.confidence]||'#888')+'"></span>'+esc(c.confidence||'')+' conf.</span>'+
        (c.source?('<a class="src" href="'+(/^https?:/.test(c.source)?esc(c.source):'#')+'" target="_blank" rel="noopener">source</a>'):'')+
      '</div></div></div>';
  }
  feed.innerHTML=html;
}
function esc(s){return (s==null?'':String(s)).replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));}

// build type chips (only types present)
const present=[...new Set(cats.map(c=>c.type))];
const tw=document.getElementById('types');
tw.innerHTML='<span class="chip on" data-t="">All types</span>'+
  Object.keys(TYPES).filter(t=>present.includes(t)).map(t=>'<span class="chip" data-t="'+t+'" style="border-color:'+TYPES[t].c+'33">'+TYPES[t].label+'</span>').join('');
tw.querySelectorAll('.chip').forEach(ch=>ch.onclick=()=>{
  const t=ch.dataset.t;
  if(t===''){ activeTypes.clear(); tw.querySelectorAll('.chip').forEach(x=>x.classList.toggle('on',x.dataset.t==='')); }
  else{ ch.classList.toggle('on'); ch.classList.contains('on')?activeTypes.add(t):activeTypes.delete(t);
        tw.querySelector('.chip[data-t=""]').classList.toggle('on',activeTypes.size===0); }
  render();
});
// timeframe chips
const TF=[["all","All"],["week","This week"],["month","This month"],["quarter","Next 3 mo"],["tbd","Undated"]];
const tfw=document.getElementById('tfs');
tfw.innerHTML=TF.map(([k,l],i)=>'<span class="chip tf'+(i===0?' on':'')+'" data-k="'+k+'">'+l+'</span>').join('');
tfw.querySelectorAll('.chip').forEach(ch=>ch.onclick=()=>{ tf=ch.dataset.k;
  tfw.querySelectorAll('.chip').forEach(x=>x.classList.toggle('on',x===ch)); render(); });
document.getElementById('q').oninput=e=>{ q=e.target.value.trim().toLowerCase(); render(); };

// header / footer
const gd=PAYLOAD.generated||'';
document.getElementById('asof').textContent='data as of '+gd;
const soonN=cats.filter(c=>{const n=dayDiff(c.date_iso);return n!==null&&n>=0&&n<=7;}).length;
document.getElementById('foot').innerHTML=
  '<b>'+cats.length+'</b> catalysts tracked across <b>'+(PAYLOAD.coverage||[]).length+'</b> coverage names'+
  ((PAYLOAD.watchlist||[]).length?(' + <b>'+PAYLOAD.watchlist.length+'</b> watchlist'):'')+
  ' &middot; <b>'+soonN+'</b> in the next 7 days &middot; data as of '+gd+'.<br>'+
  'Dates are sourced from public web research (company IR, earnings calendars, FDA, SEC filings) — best-effort, <b>not a live terminal feed</b>. Confirm any date before acting. Yellow / "~ est" = estimated or unconfirmed. Refresh on demand.';
render();
</script>
</body>
</html>"""

out = TEMPLATE.replace("__DATA__", DATA_JSON)
open(os.path.join(ROOT, "index.html"), "w").write(out)
print("wrote index.html  ·  %d catalysts  ·  generated %s" % (len(catalysts), generated))
