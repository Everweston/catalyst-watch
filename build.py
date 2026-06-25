#!/usr/bin/env python3
"""Catalyst Watch — site generator (v2: 4 sections + analyst ratings).
Reads data/catalysts.json (+ data/universe.json) and writes a self-contained index.html
(data embedded, so it works opened as a local file AND deployed to GitHub Pages).
Each catalyst carries: section (coverage|portfolio|ideas|biotech) + rating
(impact, lean, odds_positive, take). Run:  python3 build.py
"""
import json, os, datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
def load(p, default):
    fp = os.path.join(ROOT, p)
    return json.load(open(fp)) if os.path.exists(fp) else default

cat = load("data/catalysts.json", {"generated": "", "catalysts": []})
uni = load("data/universe.json", {"coverage": [], "watchlist": [], "portfolio": []})
catalysts = cat.get("catalysts", [])
generated = cat.get("generated", "") or datetime.date(2026,6,25).isoformat()

# defaults / normalisation so a missing field never breaks the page
SECT = {"coverage","portfolio","ideas","biotech"}
for c in catalysts:
    if c.get("section") not in SECT: c["section"] = "coverage"
    c.setdefault("impact","medium"); c.setdefault("lean","neutral")
    c.setdefault("odds_positive", None); c.setdefault("take","")

def keyfn(c):
    d = (c.get("date_iso") or "").strip()
    return (0, d) if (len(d) == 10 and d[:4].isdigit()) else (1, "9999")
catalysts = sorted(catalysts, key=keyfn)

payload = {
    "generated": generated,
    "coverage": uni.get("coverage", []),
    "portfolio": uni.get("portfolio", []),
    "watchlist": uni.get("watchlist", []),
    "catalysts": catalysts,
}
DATA_JSON = json.dumps(payload, ensure_ascii=False)

TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Catalyst Watch</title>
<style>
:root{--navy:#0E2841;--navy2:#1b4368;--yellow:#FFD400;--ink:#1a1a1a;--muted:#6b7785;--line:#e3e8ee;--bg:#eef1f5;--card:#fff;--soon:#fff8db;}
*{box-sizing:border-box}
body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;color:var(--ink);background:var(--bg)}
a{color:inherit}
.wrap{max-width:1080px;margin:0 auto;padding:0 16px}
header{background:var(--navy);color:#fff}
.hd{display:flex;align-items:baseline;gap:14px;flex-wrap:wrap;padding:16px 0 12px}
.logo{font-size:25px;font-weight:800;letter-spacing:2px}.logo .dot{color:var(--yellow)}
.tag{font-size:12.5px;color:#b9c6d6}.asof{margin-left:auto;font-size:12px;color:#9fb0c4;white-space:nowrap}
/* tabs */
.tabs{display:flex;gap:4px;flex-wrap:wrap;border-top:1px solid #1b3a5a}
.tab{padding:9px 14px 8px;font-size:13px;font-weight:700;color:#bcd0e6;cursor:pointer;border-bottom:3px solid transparent;white-space:nowrap}
.tab .n{font-size:11px;font-weight:700;color:#7f96b0;margin-left:5px}
.tab.on{color:#fff;border-bottom-color:var(--yellow)}
.tab.on .n{color:var(--yellow)}
.tabs{border-bottom:4px solid var(--yellow)}
.sdesc{font-size:12.5px;color:#41505f;padding:12px 0 4px;line-height:1.5}
.sdesc b{color:var(--navy)}
/* controls */
.controls{position:sticky;top:0;z-index:20;background:var(--bg);border-bottom:1px solid var(--line);padding:9px 0}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
#q{flex:1;min-width:170px;padding:9px 12px;border:1px solid #cfd8e3;border-radius:8px;font-size:14px;background:#fff}
.chip{font-size:12px;padding:6px 11px;border:1px solid #cfd8e3;border-radius:999px;background:#fff;color:#33414f;cursor:pointer;user-select:none;white-space:nowrap}
.chip.on{background:var(--navy);color:#fff;border-color:var(--navy)}
.count{font-size:12px;color:var(--muted);margin-left:auto;white-space:nowrap}
.mdiv{font-size:12px;font-weight:800;letter-spacing:1.5px;color:var(--muted);margin:18px 2px 8px;text-transform:uppercase}
/* card */
.card{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--navy);border-radius:9px;padding:11px 13px;margin:8px 0}
.card.soon{border-left-color:var(--yellow);background:linear-gradient(90deg,var(--soon),#fff 55%)}
.crow{display:flex;gap:12px}
.when{flex:0 0 88px}
.date{font-size:13px;font-weight:800;color:var(--navy);line-height:1.15}.dow{font-size:11px;color:var(--muted)}
.until{display:inline-block;margin-top:4px;font-size:10.5px;font-weight:700;padding:2px 7px;border-radius:999px;background:#eaf0f6;color:#3a4a5a}
.until.imm{background:var(--yellow);color:#3a2c00}.until.past{background:#f1d6d6;color:#7a2020}
.body{flex:1;min-width:0}
.top{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.tkr{font-family:ui-monospace,Menlo,Consolas,monospace;font-weight:800;font-size:13px;background:var(--navy);color:#fff;padding:1px 7px;border-radius:5px;letter-spacing:.5px}
.tkr.gold{background:#7a5c00}
.co{font-size:12.5px;color:var(--muted)}
.ty{font-size:10.5px;font-weight:800;letter-spacing:.5px;text-transform:uppercase;padding:2px 7px;border-radius:5px;color:#fff}
.est{font-size:10px;color:#9a6a00;background:#fff3cf;border:1px solid #f0dca0;padding:1px 6px;border-radius:5px;font-weight:700}
.ttl{font-size:14px;font-weight:600;margin:5px 0 2px;line-height:1.3}
.why{font-size:12.5px;color:#41505f;line-height:1.45}
/* rating strip */
.rate{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-top:8px;padding-top:7px;border-top:1px dashed #e6ebf1}
.rpill{font-size:10.5px;font-weight:800;letter-spacing:.3px;text-transform:uppercase;padding:2px 8px;border-radius:999px;border:1px solid}
.imp-high{color:#7a1f1f;background:#fde7e7;border-color:#f3c9c9}
.imp-medium{color:#8a5a00;background:#fff2d6;border-color:#f0dca0}
.imp-low{color:#48555f;background:#eef1f5;border-color:#dde3ea}
.lean-bullish{color:#13703a;background:#e2f5ea;border-color:#bfe6cf}
.lean-bearish{color:#a02525;background:#fbe4e4;border-color:#f0c4c4}
.lean-neutral{color:#48555f;background:#eef1f5;border-color:#dde3ea}
.odds{display:flex;align-items:center;gap:6px;margin-left:2px}
.odds-label{font-size:10.5px;font-weight:700;color:var(--muted)}
.odds-bar{width:74px;height:8px;border-radius:5px;background:#e6ebf1;overflow:hidden}
.odds-fill{display:block;height:100%}
.odds-num{font-size:12px;font-weight:800}
.take{font-size:12px;color:#2c3a47;margin-top:5px;line-height:1.4}
.take b{color:var(--navy)}
.meta{margin-top:6px;font-size:11px;color:var(--muted);display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.conf{display:inline-flex;align-items:center;gap:4px}.cdot{width:8px;height:8px;border-radius:50%}
.src{color:#2c5d99;text-decoration:none}.src:hover{text-decoration:underline}
.empty{padding:36px 8px;text-align:center;color:var(--muted)}
footer{margin:24px 0 40px;font-size:11.5px;color:var(--muted);line-height:1.5;border-top:1px solid var(--line);padding-top:14px}
footer b{color:#33414f}
@media (max-width:560px){.when{flex-basis:72px}.logo{font-size:21px}.asof{margin-left:0;flex-basis:100%}.crow{flex-direction:column;gap:4px}.when{flex-basis:auto}}
</style></head>
<body>
<header><div class="wrap">
  <div class="hd"><div class="logo">CATALYST<span class="dot">·</span>WATCH</div>
    <div class="tag">upcoming catalysts, rated</div><div class="asof" id="asof"></div></div>
  <div class="tabs" id="tabs"></div>
</div></header>
<div class="wrap"><div class="sdesc" id="sdesc"></div></div>
<div class="controls"><div class="wrap">
  <div class="row"><input id="q" placeholder="Filter by ticker, company, or keyword…" autocomplete="off"><span class="count" id="count"></span></div>
  <div class="row" style="margin-top:8px" id="types"></div>
  <div class="row" style="margin-top:7px" id="tfs"></div>
</div></div>
<div class="wrap"><div id="feed"></div></div>
<footer><div class="wrap" id="foot"></div></footer>
<script>
const PAYLOAD=__DATA__;
const TYPES={earnings:{label:"Earnings",c:"#0E2841"},"investor-day":{label:"Investor Day",c:"#0f766e"},fda:{label:"FDA / Decision",c:"#b91c1c"},product:{label:"Product",c:"#6d28d9"},deal:{label:"Deal / M&A",c:"#c2410c"},regulatory:{label:"Regulatory",c:"#92600a"},lockup:{label:"Lockup",c:"#475569"},index:{label:"Index",c:"#15803d"},guidance:{label:"Guidance",c:"#1d4ed8"},other:{label:"Data / Other",c:"#475569"}};
const CONF={high:"#16a34a",medium:"#d99000",low:"#b0381f"};
const SECTIONS=[
 ["coverage","Coverage","The book we cover — catalysts across all names. Tickers get added as we pick up coverage."],
 ["portfolio","My Portfolio","Current holdings (NVDA, RDDT, DVN, AMD, VERA, GDOT, VBNK, COMP) and their next catalysts."],
 ["ideas","Catalyst Ideas","Stocks I've researched and think have an upcoming catalyst that can add value — <b>not</b> coverage or holdings. My picks."],
 ["biotech","Biotech","Biotechs with a significant binary catalyst. <b>Odds = my success prediction (PoS)</b> for the readout/decision."]];
const cats=PAYLOAD.catalysts||[];
let activeSection="coverage", activeTypes=new Set(), tf="all", q="";

function fmtDate(iso){if(!iso||iso.length<10||!/^\d{4}-\d{2}-\d{2}/.test(iso))return null;const[y,m,d]=iso.slice(0,10).split('-').map(Number);return new Date(y,m-1,d);}
function dayDiff(iso){const dt=fmtDate(iso);if(!dt)return null;const n=new Date();n.setHours(0,0,0,0);return Math.round((dt-n)/86400000);}
function untilLabel(n){if(n===null)return["",""];if(n<0)return[(-n)+"d ago","past"];if(n===0)return["TODAY","imm"];if(n===1)return["tomorrow","imm"];if(n<=7)return["in "+n+"d","imm"];if(n<=31)return["in "+Math.round(n/7)+"w",""];return["in "+Math.round(n/30)+"mo",""];}
const MON=["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"],DOW=["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
function esc(s){return(s==null?'':String(s)).replace(/[&<>"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[m]));}
function oddsColor(o){return o>=60?'#16a34a':o>=40?'#d99000':'#b0381f';}

function inSection(c){return (c.section||'coverage')===activeSection;}
function passes(c){
  if(!inSection(c))return false;
  if(q){const s=(c.ticker+" "+c.company+" "+c.title+" "+c.why+" "+(c.take||"")+" "+(TYPES[c.type]?.label||"")).toLowerCase();if(!s.includes(q))return false;}
  if(activeTypes.size&&!activeTypes.has(c.type))return false;
  if(tf!=="all"){const n=dayDiff(c.date_iso);if(n===null)return tf==="tbd";if(tf==="week"&&(n<0||n>7))return false;if(tf==="month"&&(n<0||n>31))return false;if(tf==="quarter"&&(n<0||n>93))return false;if(tf==="tbd")return false;}
  return true;
}
function ratingHTML(c){
  const imp=(c.impact||'medium'), lean=(c.lean||'neutral'), o=c.odds_positive;
  const leanTxt={bullish:'▲ Bullish',bearish:'▼ Bearish',neutral:'▬ Neutral'}[lean]||lean;
  const oLabel=activeSection==='biotech'?'Success':'Odds +';
  let oh='';
  if(typeof o==='number'){oh='<span class="odds"><span class="odds-label">'+oLabel+'</span><span class="odds-bar"><span class="odds-fill" style="width:'+Math.max(3,Math.min(100,o))+'%;background:'+oddsColor(o)+'"></span></span><span class="odds-num" style="color:'+oddsColor(o)+'">'+Math.round(o)+'%</span></span>';}
  return '<div class="rate"><span class="rpill imp-'+imp+'">Impact '+imp+'</span>'+
    '<span class="rpill lean-'+lean+'">'+leanTxt+'</span>'+oh+'</div>'+
    (c.take?'<div class="take"><b>My take:</b> '+esc(c.take)+'</div>':'');
}
function render(){
  const feed=document.getElementById('feed');
  const list=cats.filter(passes);
  const total=cats.filter(inSection).length;
  document.getElementById('count').textContent=list.length+' of '+total;
  if(!list.length){feed.innerHTML='<div class="empty">No catalysts match these filters.</div>';return;}
  let h='',curMon='';
  for(const c of list){
    const dt=fmtDate(c.date_iso),mon=dt?(MON[dt.getMonth()]+" "+dt.getFullYear()):"Undated / TBD";
    if(mon!==curMon){h+='<div class="mdiv">'+mon+'</div>';curMon=mon;}
    const n=dayDiff(c.date_iso),[ul,uc]=untilLabel(n),soon=(n!==null&&n>=0&&n<=7),ty=TYPES[c.type]||TYPES.other;
    const dlab=dt?(MON[dt.getMonth()]+" "+dt.getDate()):"TBD",dow=dt?DOW[dt.getDay()]:"";
    const gold=(c.section==='portfolio'||c.section==='ideas'||c.section==='biotech');
    h+='<div class="card'+(soon?' soon':'')+'"><div class="crow">'+
      '<div class="when"><div class="date">'+esc(dlab)+'</div>'+(dow?'<div class="dow">'+dow+'</div>':'')+(ul?'<div class="until '+uc+'">'+ul+'</div>':'')+'</div>'+
      '<div class="body"><div class="top">'+
        '<span class="tkr'+(gold?' gold':'')+'">'+esc(c.ticker)+'</span><span class="co">'+esc(c.company)+'</span>'+
        '<span class="ty" style="background:'+ty.c+'">'+ty.label+'</span>'+(c.date_confirmed?'':'<span class="est">~ est</span>')+'</div>'+
        '<div class="ttl">'+esc(c.title)+'</div><div class="why">'+esc(c.why)+'</div>'+
        ratingHTML(c)+
        '<div class="meta"><span class="conf"><span class="cdot" style="background:'+(CONF[c.confidence]||'#888')+'"></span>'+esc(c.confidence||'')+' conf.</span>'+
          (c.source?('<a class="src" href="'+(/^https?:/.test(c.source)?esc(c.source):'#')+'" target="_blank" rel="noopener">source</a>'):'')+'</div>'+
      '</div></div></div>';
  }
  feed.innerHTML=h;
}
// tabs
const tabw=document.getElementById('tabs');
tabw.innerHTML=SECTIONS.map(([k,l])=>'<div class="tab'+(k==='coverage'?' on':'')+'" data-s="'+k+'">'+l+'<span class="n">'+cats.filter(c=>(c.section||'coverage')===k).length+'</span></div>').join('');
function setSection(k){activeSection=k;activeTypes.clear();tf="all";
  tabw.querySelectorAll('.tab').forEach(t=>t.classList.toggle('on',t.dataset.s===k));
  document.getElementById('sdesc').innerHTML=(SECTIONS.find(s=>s[0]===k)||[])[2]||'';
  buildTypeChips();tfw.querySelectorAll('.chip').forEach((x,i)=>x.classList.toggle('on',i===0));render();}
tabw.querySelectorAll('.tab').forEach(t=>t.onclick=()=>setSection(t.dataset.s));
// type chips (rebuilt per section)
const tw=document.getElementById('types');
function buildTypeChips(){
  const present=[...new Set(cats.filter(inSection).map(c=>c.type))];
  tw.innerHTML='<span class="chip on" data-t="">All types</span>'+Object.keys(TYPES).filter(t=>present.includes(t)).map(t=>'<span class="chip" data-t="'+t+'" style="border-color:'+TYPES[t].c+'33">'+TYPES[t].label+'</span>').join('');
  tw.querySelectorAll('.chip').forEach(ch=>ch.onclick=()=>{const t=ch.dataset.t;
    if(t===''){activeTypes.clear();tw.querySelectorAll('.chip').forEach(x=>x.classList.toggle('on',x.dataset.t===''));}
    else{ch.classList.toggle('on');ch.classList.contains('on')?activeTypes.add(t):activeTypes.delete(t);tw.querySelector('.chip[data-t=""]').classList.toggle('on',activeTypes.size===0);}render();});
}
// timeframe chips
const TF=[["all","All"],["week","This week"],["month","This month"],["quarter","Next 3 mo"],["tbd","Undated"]];
const tfw=document.getElementById('tfs');
tfw.innerHTML=TF.map(([k,l],i)=>'<span class="chip tf'+(i===0?' on':'')+'" data-k="'+k+'">'+l+'</span>').join('');
tfw.querySelectorAll('.chip').forEach(ch=>ch.onclick=()=>{tf=ch.dataset.k;tfw.querySelectorAll('.chip').forEach(x=>x.classList.toggle('on',x===ch));render();});
document.getElementById('q').oninput=e=>{q=e.target.value.trim().toLowerCase();render();};
// header/footer
document.getElementById('asof').textContent='data as of '+(PAYLOAD.generated||'');
const soonN=cats.filter(c=>{const n=dayDiff(c.date_iso);return n!==null&&n>=0&&n<=7;}).length;
document.getElementById('foot').innerHTML='<b>'+cats.length+'</b> catalysts across 4 sections &middot; <b>'+soonN+'</b> in the next 7 days &middot; data as of '+(PAYLOAD.generated||'')+'.<br>'+
  '<b>Ratings (Impact / Lean / Odds / Take) are the analyst’s own judgment</b> — in Biotech, "Success" is a predicted probability of a positive readout/decision (PoS). Dates are public-web-sourced (company IR, earnings calendars, FDA, SEC), <b>not a live terminal</b> — confirm before trading. "~ est" = estimated date. Refresh on demand.';
document.getElementById('sdesc').innerHTML=SECTIONS[0][2];
buildTypeChips();render();
</script></body></html>"""

out = TEMPLATE.replace("__DATA__", DATA_JSON)
open(os.path.join(ROOT, "index.html"), "w").write(out)
# tiny stats
from collections import Counter
bs = Counter(c.get("section","coverage") for c in catalysts)
print("wrote index.html · %d catalysts · sections=%s · generated %s" % (len(catalysts), dict(bs), generated))
