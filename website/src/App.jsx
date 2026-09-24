import React, { lazy, Suspense, useEffect, useRef, useState } from 'react';
import data from './data/study.json';
const Scene = lazy(() => import('./Scene.jsx'));
const REPO = 'https://github.com/mehedihasan722/Thesis-Defense-Project-XAI-ids-Update';
const asset = path => import.meta.env.BASE_URL + path;
const names = { DecisionTree:'Decision tree', RandomForest:'Random forest', XGBoost:'XGBoost', SoftVoting:'Soft voting', ShallowMLP:'Shallow MLP', DeepMLP:'Deep MLP', FeatureCNN:'Feature CNN' };
const models = Object.keys(names);
const colors = ['#b16d43','#657991','#365c48','#9b9c91','#5f98a0','#8c80a8','#b27d98'];
const dataset = x => x === 'unsw' ? 'NF-UNSW-NB15-v2' : 'NF-CSE-CIC-IDS2018-v2';
const short = x => x === 'unsw' ? 'UNSW' : 'IDS2018';
const format = n => Number(n).toFixed(4);
const Arrow = ({diagonal=false}) => <span aria-hidden="true">{diagonal ? '↗' : '↗'}</span>;
function downloadCSV(rows, filename) {
  const keys=[...new Set(rows.flatMap(Object.keys))];
  const quote=v=>'"'+String(v??'').replaceAll('"','""')+'"';
  const csv=[keys.map(quote).join(','),...rows.map(r=>keys.map(k=>quote(r[k])).join(','))].join('\r\n');
  const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8;'}));
  const a=document.createElement('a');a.href=url;a.download=filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
function Select({label,value,onChange,children}) {return <label className="field"><span>{label}</span><select aria-label={label} value={value} onChange={e=>onChange(e.target.value)}>{children}</select></label>}
function DataExplorer({preset}) {
  const [mode,setMode]=useState('detection');const [source,setSource]=useState('unsw');const [target,setTarget]=useState('ids2018');
  const [task,setTask]=useState('binary');const [metric,setMetric]=useState('macro_f1');const [xmetric,setXmetric]=useState('jaccard5_mean');
  const [kind,setKind]=useState('detector');const [auditModel,setAuditModel]=useState('DecisionTree');
  const [active,setActive]=useState(null);const [pinned,setPinned]=useState(false);const [showTable,setShowTable]=useState(false);
  useEffect(()=>{
    if(!preset)return;
    const id=preset.file.replace('.png','');
    if(id.startsWith('audit_')){setMode('audit');setAuditModel(id.slice(6));}
    else if(id.startsWith('llm_')){setMode('llm');setKind(id.slice(4));}
    else if(id.startsWith('transfer_')){setMode('transfer');setSource(id.split('_')[1]);}
    else if(id.startsWith('xai_')){const [,s,t,...m]=id.split('_');setMode('xai');setSource(s);setTarget(t);setXmetric(m.join('_'));}
    else{const [t,s,...m]=id.split('_');setMode('detection');setTask(t);setSource(s);setMetric(m.join('_'));}
  },[preset]);
  useEffect(()=>{setActive(null);setPinned(false)},[mode,source,target,task,metric,xmetric,kind,auditModel]);
  const modes=[['detection','Detection'],['transfer','Network transfer'],['xai','Explanation quality'],['llm','Language models'],['audit','Historical audit']];
  let rows=[],caption='',title='',unit='',sourcePath='',figureId='';
  if(mode==='detection'||mode==='transfer'){
    const dest=mode==='transfer'?(source==='unsw'?'ids2018':'unsw'):source;
    const measure=mode==='transfer'?'macro_f1':metric;
    rows=models.map(model=>data.detection.find(r=>r.source===source&&r.target===dest&&r.task===(mode==='transfer'?'binary':task)&&r.model===model)).filter(Boolean).map(r=>({...r,label:names[r.model],value:r[measure+'_mean'],sd:r[measure+'_sd'],low:r[measure+'_mean']-r[measure+'_sd'],high:r[measure+'_mean']+r[measure+'_sd']}));
    unit=measure==='macro_f1'?'Macro-F1':'False-alarm rate';
    title=mode==='transfer'?`${short(source)} → ${short(dest)}`:`${short(source)} · ${task} detection`;
    caption=`Mean ± sample SD over training seeds 7, 42 and 1337. Each evaluation uses 80,000 test flows. ${mode==='transfer'?'Models are frozen after source-only training.':'Feature-group-disjoint protocol; not directly comparable with historical random-split results.'}`;
    sourcePath='results/study/across_seed_summary.csv';figureId=mode==='transfer'?`transfer_${source}_${dest}`:`${task}_${source}_${metric}`;
  }else if(mode==='xai'){
    rows=models.map(model=>data.xai.find(r=>r.source===source&&r.target===target&&r.model===model)).filter(Boolean).map(r=>({...r,label:names[r.model],value:r[xmetric],low:xmetric==='advantage_mean'?r.ci95_low:null,high:xmetric==='advantage_mean'?r.ci95_high:null}));
    unit=xmetric==='jaccard5_mean'?'Jaccard@5':'LIME minus random probability drop';title=`${short(source)} → ${short(target)} · LIME`;
    caption='20 balanced unique-group cases per model; three LIME seeds; detector training seed 42. Source-median masking, absolute rankings. Intervals are 95% stratified bootstrap intervals over cases, not training-seed uncertainty.';
    sourcePath='results/study/xai/aggregate.csv';figureId=`xai_${source}_${target}_${xmetric}`;
  }else if(mode==='llm'){
    rows=['Qwen/Qwen2.5-0.5B-Instruct','TinyLlama/TinyLlama-1.1B-Chat-v1.0','HuggingFaceTB/SmolLM2-1.7B-Instruct'].map((model,i)=>{
      const matches=data.llm.filter(r=>r.model===model&&r.kind===kind);const valid=matches.reduce((a,r)=>a+r.valid,0),total=matches.reduce((a,r)=>a+r.total,0);
      return {model,label:['Qwen 2.5','TinyLlama','SmolLM2'][i],value:valid/total,valid,total};
    });
    title=kind==='own'?'Explaining their own decisions':'Explaining the detector';unit='Valid explanation fraction';
    caption='All 80 requested outputs per model, aggregated across four dataset directions. Invalid outputs stay in the denominator. A missing conditional masking score is not a measured zero.';
    sourcePath='results/study/llm/masking_coverage.csv';figureId=`llm_${kind}`;
  }else{
    rows=data.audit[auditModel].map((r,i)=>({...r,label:`Case ${i+1}`,value:r.advantage,x:r.jaccard_at_5}));
    title=`${names[auditModel]} · matched historical cases`;unit='LIME minus random probability drop';
    caption='483 matched cases. Jaccard@5 measures repeatability; the vertical axis measures the random-controlled masking effect. Descriptive within-model association does not establish causation. Original feature rankings were not retained.';
    sourcePath=`results/study/audit/${auditModel}_matched.csv`;figureId=`audit_${auditModel}`;
  }
  const chosen=active===null?null:rows[active];
  const min=Math.min(0,...rows.map(r=>r.low??r.value));const max=mode==='audit'?Math.max(.01,...rows.map(r=>r.value)):Math.max(mode==='xai'&&xmetric==='advantage_mean'?.1:1,...rows.map(r=>r.high??r.value));
  const extent=max-min||1;const pos=n=>((n-min)/extent)*100;const zero=pos(0);
  const focus=i=>{if(!pinned)setActive(i)};
  const pin=i=>{if(active===i&&pinned){setPinned(false);setActive(null)}else{setActive(i);setPinned(true)}};
  const matching=data.figures.find(f=>f.file===figureId+'.png');
  return <section id="explore" className="section explore-section">
    <div className="section-heading"><div><p className="eyebrow">02 / THE EVIDENCE</p><h2>Look closer.<br/><em>The data is yours to explore.</em></h2></div><p>Change the question. Compare the models.<br/>Hover, focus, or tap a mark to inspect its values.</p></div>
    <div className="explorer">
      <div className="mode-tabs" role="tablist" aria-label="Research comparison">{modes.map(([id,label])=><button key={id} id={`tab-${id}`} role="tab" aria-selected={mode===id} aria-controls="comparison-panel" onClick={()=>setMode(id)}>{label}<span>↗</span></button>)}</div>
      <div className="filters">
        {mode!=='llm'&&mode!=='audit'&&<Select label={mode==='detection'?'Dataset':'Training dataset'} value={source} onChange={setSource}><option value="unsw">NF-UNSW-NB15-v2</option><option value="ids2018">NF-CSE-CIC-IDS2018-v2</option></Select>}
        {mode==='detection'&&<><Select label="Task" value={task} onChange={setTask}><option value="binary">Binary detection</option><option value="multiclass">Native multiclass</option></Select><Select label="Metric" value={metric} onChange={setMetric}><option value="macro_f1">Macro-F1</option><option value="false_alarm_rate">False-alarm rate</option></Select></>}
        {mode==='transfer'&&<p className="filter-note">Frozen transfer to <strong>{short(source==='unsw'?'ids2018':'unsw')}</strong><br/>Binary labels only · no target fitting</p>}
        {mode==='xai'&&<><Select label="Evaluation dataset" value={target} onChange={setTarget}><option value="unsw">NF-UNSW-NB15-v2</option><option value="ids2018">NF-CSE-CIC-IDS2018-v2</option></Select><Select label="Explanation metric" value={xmetric} onChange={setXmetric}><option value="jaccard5_mean">Stability · Jaccard@5</option><option value="advantage_mean">Masking advantage</option></Select></>}
        {mode==='llm'&&<Select label="Explanation task" value={kind} onChange={setKind}><option value="detector">Detector-grounded</option><option value="own">Own decision</option></Select>}
        {mode==='audit'&&<Select label="Historical model" value={auditModel} onChange={setAuditModel}>{models.slice(0,3).map(m=><option key={m} value={m}>{names[m]}</option>)}</Select>}
      </div>
      <div className="comparison-panel" id="comparison-panel" role="tabpanel" aria-labelledby={`tab-${mode}`}>
        <div className="plot-top"><div><span className="eyebrow">{mode==='audit'?'HISTORICAL PROTOCOL':'EXPANDED STUDY'}{matching?` / FIGURE ${matching.number}`:''}</span><h3>{title}</h3></div><span className="chart-symbol" aria-hidden="true">⌁</span></div>
        <div className="plot-layout">
          <div className="chart-area" key={figureId}>
            {mode==='audit'?<>
              <svg className="scatter" viewBox="0 0 680 365" role="img" aria-label={`${title}. X axis Jaccard at 5, Y axis ${unit}. Use the case selector or data table for exact values.`}>
                {[0,.25,.5,.75,1].map(v=><g key={v}><line x1={55+v*600} x2={55+v*600} y1="20" y2="310" stroke="#dfe3d9"/><text x={55+v*600} y="333" textAnchor="middle">{v}</text></g>)}
                {[min,(min+max)/2,max].map(v=><g key={v}><line x1="55" x2="655" y1={310-(v-min)/extent*290} y2={310-(v-min)/extent*290} stroke="#dfe3d9"/><text x="46" y={315-(v-min)/extent*290} textAnchor="end">{v.toFixed(2)}</text></g>)}
                <line x1="55" x2="655" y1={310-(0-min)/extent*290} y2={310-(0-min)/extent*290} stroke="#8f9a89"/>
                {rows.map((r,i)=><circle key={i} cx={55+r.x*600} cy={310-(r.value-min)/extent*290} r={active===i?6:3.4} fill={colors[models.indexOf(auditModel)]} opacity={active===i?1:.4} onMouseEnter={()=>focus(i)} onMouseLeave={()=>{if(!pinned)setActive(null)}} onClick={()=>pin(i)}><title>{r.label}: Jaccard {format(r.x)}; advantage {format(r.value)}</title></circle>)}
                <text x="355" y="361" textAnchor="middle">Jaccard@5</text>
              </svg>
              <label className="case-selector">Inspect case {active===null?'—':active+1} / {rows.length}<input aria-label="Historical case" type="range" min="0" max={rows.length-1} value={active??0} onChange={e=>{setPinned(true);setActive(+e.target.value)}}/></label>
            </>:<div className="bar-chart">
              {rows.map((r,i)=><button key={r.model} className={`plot-row ${active===i?'is-active':''}`} onMouseEnter={()=>focus(i)} onMouseLeave={()=>{if(!pinned)setActive(null)}} onFocus={()=>focus(i)} onBlur={()=>{if(!pinned)setActive(null)}} onClick={()=>pin(i)} onKeyDown={e=>{if(e.key==='Escape'){setPinned(false);setActive(null)}}} aria-label={`${r.label}: ${unit} ${format(r.value)}${r.sd!=null?`, sample standard deviation ${format(r.sd)}`:''}`} aria-describedby={active===i?'datum-detail':undefined}>
                <span className="row-label"><i style={{background:colors[i]}}/>{r.label}</span>
                <span className="bar-track"><span className="zero-line" style={{left:zero+'%'}}/><span className="bar" style={{left:Math.min(zero,pos(r.value))+'%',width:Math.abs(pos(r.value)-zero)+'%',background:colors[i],animationDelay:`${i*55}ms`}}/>{r.low!=null&&<span className="error-bar" style={{left:pos(r.low)+'%',width:(pos(r.high)-pos(r.low))+'%'}}/>}</span>
                <span className="row-value">{r.total!=null?`${r.valid}/${r.total}`:format(r.value)}</span>
              </button>)}
              <div className="chart-axis"><span/><div>{[0,.25,.5,.75,1].map(t=><span key={t} style={{left:t*100+'%'}}>{(min+t*extent).toFixed(2)}</span>)}</div><span/></div>
            </div>}
            <p className="axis-label">{unit}{mode==='detection'&&metric==='false_alarm_rate'?' · lower is better':''}</p>
          </div>
          <aside id="datum-detail" className={`datum-detail ${chosen?'has-data':''}`} aria-live="polite" aria-atomic="true">
            <div className="detail-top"><span className="eyebrow">{pinned?'PINNED VALUE':'DATA INSPECTOR'}</span>{pinned&&<button aria-label="Unpin value" onClick={()=>{setPinned(false);setActive(null)}}>×</button>}</div>
            {chosen?<><h4>{chosen.label}</h4><p className="big-value">{format(chosen.value)}</p><p className="detail-unit">{unit}</p><dl>
              {chosen.sd!=null&&<><dt>Sample SD</dt><dd>± {format(chosen.sd)}</dd><dt>Training seeds</dt><dd>3</dd><dt>Test flows / seed</dt><dd>80,000</dd></>}
              {mode==='xai'&&<><dt>Unique-group cases</dt><dd>{chosen.n}</dd><dt>LIME seeds</dt><dd>{chosen.lime_seeds}</dd>{chosen.low!=null&&<><dt>95% conditional CI</dt><dd>[{format(chosen.low)}, {format(chosen.high)}]</dd></>}</>}
              {mode==='llm'&&<><dt>Valid outputs</dt><dd>{chosen.valid}</dd><dt>Requested outputs</dt><dd>{chosen.total}</dd><dt>Coverage</dt><dd>{(chosen.value*100).toFixed(2)}%</dd></>}
              {mode==='audit'&&<><dt>Jaccard@5</dt><dd>{format(chosen.x)}</dd><dt>Original instance</dt><dd>{chosen.instance}</dd><dt>True class</dt><dd>{chosen.true_class}</dd></>}
            </dl><p className="small-hint">{pinned?'Select again or press × to unpin.':'Click to keep this value in view.'}</p></>:<><span className="inspector-glyph" aria-hidden="true">＋</span><h4>Every mark<br/>has a story.</h4><p>Hover or focus a bar to reveal the exact value. Tap to pin it here.</p></>}
          </aside>
        </div>
        <p className="chart-caption">{caption}</p>
        {mode==='llm'&&<p className="finding-note">Classification result: all three models predicted one constant class under the frozen protocol. Macro-F1 = 0.3333 on balanced cohorts. Explanation coverage does not imply successful classification.</p>}
        <div className="chart-actions"><button className="text-button" onClick={()=>setShowTable(!showTable)} aria-expanded={showTable}>{showTable?'Hide':'View'} data table <span>↗</span></button><button className="text-button" onClick={()=>downloadCSV(rows,figureId+'.csv')}>Download CSV <span>↓</span></button><a href={`${REPO}/blob/main/${sourcePath}`} target="_blank" rel="noreferrer">Source evidence ↗</a></div>
        {showTable&&<div className="data-table-wrap"><table><caption>{title} — exact underlying values</caption><thead><tr><th>{mode==='audit'?'Case':'Model'}</th><th>{unit}</th><th>{mode==='audit'?'Jaccard@5':mode==='llm'?'Valid / total':'Uncertainty / scope'}</th></tr></thead><tbody>{rows.map((r,i)=><tr key={i}><th scope="row">{r.label}</th><td>{r.value}</td><td>{mode==='audit'?r.x:r.total!=null?`${r.valid} / ${r.total}`:r.sd!=null?`SD ${r.sd}`:r.low!=null?`95% CI [${r.low}, ${r.high}]`:'20 cases; 3 LIME seeds'}</td></tr>)}</tbody></table></div>}
      </div>
    </div>
  </section>
}
function FigureLibrary({onExplore}){
  const [query,setQuery]=useState('');const [filter,setFilter]=useState('all');const [limit,setLimit]=useState(6);const [selected,setSelected]=useState(null);const dialog=useRef(null);
  const figures=data.figures.filter(f=>(filter==='all'||f.protocol===filter)&&`${f.number} ${f.caption}`.toLowerCase().includes(query.toLowerCase()));
  useEffect(()=>{setLimit(6)},[query,filter]);
  useEffect(()=>{if(selected)dialog.current.showModal();else if(dialog.current.open)dialog.current.close()},[selected]);
  return <section id="figures" className="section library-section"><div className="section-heading"><div><p className="eyebrow">04 / THE FIGURE LIBRARY</p><h2>Nothing left behind.</h2></div><p>18 original figures. 23 new perspectives.<br/>Each preserved, separately captioned, and traceable.</p></div>
    <div className="library-tools"><label className="search-field"><span aria-hidden="true">⌕</span><input aria-label="Search figures" placeholder="Find a figure, model, or research question…" value={query} onChange={e=>setQuery(e.target.value)}/></label><Select label="Collection" value={filter} onChange={setFilter}><option value="all">All 41 figures</option><option value="Expanded study">Expanded study · 23</option><option value="Original study">Original study · 18</option></Select></div>
    <p className="library-count" aria-live="polite">{figures.length} figures{query?` matching “${query}”`:''}</p>
    <div className="figure-grid">{figures.slice(0,limit).map(f=><article className="figure-card" key={f.number}>
      <button className="figure-preview" onClick={()=>setSelected(f)} aria-label={`Enlarge Figure ${f.number}`}><img src={asset(f.path)} alt={f.caption} loading="lazy"/><span className="enlarge" aria-hidden="true">↗</span></button>
      <div className="figure-meta"><span>FIG. {f.number}</span><span>{f.protocol}</span></div><h3>{f.caption.split('. ')[0]}</h3>
      <div className="figure-links">{f.protocol==='Expanded study'?<button onClick={()=>onExplore(f)}>Explore values ↗</button>:<span>Historical protocol</span>}<a href={`${REPO}/blob/main/${f.source.replace('.png','.pdf')}`} target="_blank" rel="noreferrer">Vector PDF ↓</a></div>
    </article>)}</div>
    {!figures.length&&<div className="empty-state">No figures match this search. <button onClick={()=>{setQuery('');setFilter('all')}}>Reset filters</button></div>}
    {limit<figures.length&&<button className="outline-button load-more" onClick={()=>setLimit(limit+9)}>Show more figures <span>+ {Math.min(9,figures.length-limit)}</span></button>}
    <dialog ref={dialog} className="figure-dialog" onCancel={()=>setSelected(null)} onClose={()=>setSelected(null)} onClick={e=>{if(e.target===dialog.current)setSelected(null)}}>{selected&&<><div className="dialog-heading"><span>FIGURE {selected.number} / {selected.protocol}</span><button onClick={()=>setSelected(null)} aria-label="Close figure">×</button></div><img src={asset(selected.path)} alt={selected.caption}/><p>{selected.caption}</p><a href={asset(selected.path)} download>Download separate PNG ↓</a></>}</dialog>
  </section>
}
export default function App(){
  const [sceneOn,setSceneOn]=useState(true);const [preset,setPreset]=useState(null);
  const toFigure=f=>{setPreset({...f});document.getElementById('explore').scrollIntoView({behavior:window.matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'})};
  return <>
    <a className="skip-link" href="#research">Skip to research</a>
    <header className="site-nav"><a className="wordmark" href="#top" aria-label="XAI IDS home"><svg viewBox="0 0 32 36" aria-hidden="true"><path d="M4 26 16 4 28 26M9 17h14M16 4v28"/></svg><span>XAI <b>/</b> IDS</span></a><nav aria-label="Main navigation"><a href="#research">Research</a><a href="#explore">Explore data</a><a href="#figures">Figures</a></nav><a className="nav-paper" href={asset('thesis.pdf')} target="_blank" rel="noreferrer">Read the thesis <Arrow/></a></header>
    <main>
      <section className="hero" id="top" aria-labelledby="hero-title">
        {sceneOn?<Suspense fallback={<div className="scene-fallback">Growing the living world…</div>}><Scene/></Suspense>:<div className="scene-fallback"><span>Living world paused</span></div>}
        <div className="hero-shade"/>
        <div className="hero-content"><p className="hero-eyebrow"><span/> AN EXPLAINABLE AI RESEARCH OBSERVATORY</p><h1 id="hero-title">A prediction isn’t<br/><em>an explanation.</em></h1><p className="hero-description">What makes an intrusion detector trustworthy?<br/>Explore the evidence behind accuracy, explanation<br className="desktop-break"/> stability, and transfer across networks.</p><a href="#explore" className="primary-button">Enter the research <span>↗</span></a></div>
        <div className="hero-footer"><span>MEHEDI HASAN & SAZZADUL ISLAM<br/><small>CSE · International Islamic University Chittagong</small></span><span className="hero-note">A living world. A closer look.<br/><small>Move your pointer through the scene.</small></span><button className="motion-button" onClick={()=>setSceneOn(!sceneOn)} aria-pressed={!sceneOn}>{sceneOn?'Ⅱ Pause scene':'▷ Play scene'}</button></div>
      </section>
      <div className="evidence-strip"><p><strong>02</strong><span>Network datasets</span></p><p><strong>07</strong><span>Detector families</span></p><p><strong>03</strong><span>Local language models</span></p><p><strong>{data.provenance.evaluation_cells}</strong><span>Evaluation cells</span></p><a href={asset('evidence-manifest.json')} target="_blank" rel="noreferrer"><span className="live-dot"/> Traceable evidence <Arrow/></a></div>
      <section id="research" className="section research-section"><div className="section-heading"><div><p className="eyebrow">01 / THE RESEARCH QUESTION</p><h2>Trust is something<br/>we <em>measure.</em></h2></div><div className="research-intro"><p>A highly accurate model can still offer an unreliable explanation. This thesis studies what happens when we ask a detector to explain itself—and then ask again.</p><a className="text-link" href={`${REPO}/blob/main/thesis/study/PROTOCOL.md`} target="_blank" rel="noreferrer">Read the study protocol ↗</a></div></div>
        <div className="rq-grid">{[['01','Stability','Will the same prediction receive the same explanation across repeated runs?','Repeatability ≠ correctness'],['02','Faithfulness','Do the named features change the frozen model’s prediction more than random features?','Masking is a measured proxy'],['03','Transferability','What survives when a model meets a different network dataset?','Two directions. No target fitting.'],['04','Agreement','Do independent explainers identify the same important features?','Original agreement study retained']].map(([n,t,p,tag])=><article key={n}><span className="rq-number">RQ / {n}</span><h3>{t}</h3><p>{p}</p><span className="rq-tag">{tag}</span></article>)}</div>
        <div className="protocol-line"><span>THE EXPANDED WORKFLOW</span><ol><li>Two NetFlow datasets</li><li>Group-disjoint splits</li><li>Frozen model evaluation</li><li>Matched explanation controls</li></ol></div>
      </section>
      <DataExplorer preset={preset}/>
      <section id="findings" className="findings-section"><div className="section findings-inner"><div><p className="eyebrow">03 / WHAT WE LEARNED</p><h2>Reliable once.<br/><em>Not reliable everywhere.</em></h2><p className="findings-intro">The strongest results are not always the most reassuring. These are the findings that deserve a closer look.</p><a className="light-link" href={`${REPO}/blob/main/results/study/RESULTS.md`} target="_blank" rel="noreferrer">Read the full analysis ↗</a></div><div className="findings-list"><article><span>01</span><div><h3>Accuracy does not travel unchanged.</h3><p>All seven detector families lose performance under frozen cross-dataset transfer. Neural models are competitive within datasets, but do not remove this gap.</p></div></article><article><span>02</span><div><h3>A stable explanation can still miss the point.</h3><p>UNSW-trained random forest retains target-domain Jaccard@5 of 0.9222 while its LIME-minus-random masking advantage falls to −0.1338.</p></div></article><article><span>03</span><div><h3>Fluent language is not detection ability.</h3><p>All three small LLMs collapse to a constant predicted class in this protocol. Invalid explanations remain counted. Negative results are evidence too.</p></div></article></div></div></section>
      <FigureLibrary onExplore={toFigure}/>
      <section id="manuscript" className="section manuscript-section"><div className="paper-object" aria-hidden="true"><span>IIUC / DEPARTMENT OF CSE</span><i>Explanation<br/>Reliability in<br/>Intrusion<br/>Detection</i><div className="paper-lines"/><small>THE ORIGINAL STUDY<br/>+ THE EXPANDED EVIDENCE<br/>109 PAGES · 2026</small></div><div><p className="eyebrow">05 / THE COMPLETE THESIS</p><h2>The whole story.<br/><em>Not just the headline.</em></h2><p>The original thesis is preserved: its data, figures, references, and appendices. New neural models, language models, and cross-network evidence extend it without erasing its history.</p><div className="manuscript-stats"><span><b>41</b> figure captions</span><span><b>42</b> references</span><span><b>109</b> pages</span></div><div className="manuscript-actions"><a className="primary-button dark" href={asset('thesis.pdf')} target="_blank" rel="noreferrer">Read the full thesis <Arrow/></a><a className="text-link" href={`${REPO}/blob/main/output/docx/thesis_xai_ids_preserved.docx`} target="_blank" rel="noreferrer">Editable Word ↗</a></div><p className="review-note">Author-review draft. Original reference [28] remains unconfirmed. Historical wording is qualified by the expanded study; see <a href={`${REPO}/issues/11`} target="_blank" rel="noreferrer">the review record</a>.</p></div></section>
      <section className="limitations section"><p className="eyebrow">SCIENCE WITH ITS LIMITS IN VIEW</p><p>Two datasets. Small explanation cohorts. Three small CPU language models. No temporal evaluation, causal ground truth, or analyst study. These results describe the tested protocols—not deployment guarantees.</p></section>
    </main>
    <footer className="site-footer"><a className="wordmark" href="#top">XAI <b>/</b> IDS</a><span>RESEARCH, OPEN TO INSPECTION.<br/><small>Mehedi Hasan · C213061 / Sazzadul Islam · C213066R</small></span><div><a href={REPO} target="_blank" rel="noreferrer">GitHub ↗</a><a href={`${REPO}/wiki`} target="_blank" rel="noreferrer">Wiki ↗</a><a href="https://threeui.com/source-code/sylva-living-world.json" target="_blank" rel="noreferrer">Scene by ThreeUI ↗</a></div></footer>
  </>
}
