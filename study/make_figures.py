"""Reproducible scientific figures from completed evidence only (PNG and SVG)."""
from pathlib import Path
import json
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
ROOT=Path(__file__).resolve().parents[1];BASE=ROOT/'results/study';OUT=BASE/'figures'
MODELS=['DecisionTree','RandomForest','XGBoost','SoftVoting','ShallowMLP','DeepMLP','FeatureCNN']
LABELS=['Decision tree','Random forest','XGBoost','Soft voting','Shallow MLP','Deep MLP','Feature CNN']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})
CAPTIONS=[]
def save(fig,name,caption):
    fig.savefig(OUT/f'{name}.png',dpi=220,bbox_inches='tight');fig.savefig(OUT/f'{name}.svg',bbox_inches='tight');plt.close(fig)
    CAPTIONS.append((name,caption))
def heatmap(values,title,color,label,vmin=None,vmax=None):
    fig,ax=plt.subplots(figsize=(11,4));im=ax.imshow(values,cmap=color,aspect='auto',vmin=vmin,vmax=vmax)
    ax.set_xticks(range(7),LABELS,rotation=25,ha='right');ax.set_yticks(range(4),['UNSW → UNSW','UNSW → IDS2018','IDS2018 → IDS2018','IDS2018 → UNSW']);ax.set_title(title,pad=14)
    for (i,j),v in np.ndenumerate(values):
        if np.isfinite(v):ax.text(j,i,f'{v:.3f}',ha='center',va='center',color='black',bbox=dict(facecolor='white',alpha=.72,edgecolor='none',pad=1.5))
    fig.colorbar(im,ax=ax,label=label,shrink=.85);return fig

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    d=pd.read_csv(BASE/'completed_metrics.csv');directions=[('unsw','unsw'),('unsw','ids2018'),('ids2018','ids2018'),('ids2018','unsw')]
    binary=d[(d.task=='binary')&(d.seed==42)]
    values=np.full((4,7),np.nan)
    for i,(s,t) in enumerate(directions):
        for j,m in enumerate(MODELS):
            cell=binary[(binary.source==s)&(binary.target==t)&(binary.model==m)]
            if len(cell)==1:values[i,j]=cell.iloc[0].macro_f1
    save(heatmap(values,'Binary classification: frozen-model transfer (seed 42)','YlGnBu','Macro-F1 · higher is better',0,1),'01_detection_transfer','Completed seed-42 binary detectors, 80000 test rows per target. Models are frozen across datasets. Single-seed evidence; not a final three-seed estimate. Blank cells indicate unavailable completed results.')
    fig,axes=plt.subplots(1,3,figsize=(12,3.7),sharey=True)
    for ax,m in zip(axes,MODELS[:3]):
        frame=pd.read_csv(BASE/f'audit/{m}_matched.csv');ax.scatter(frame.jaccard_at_5,frame.advantage,s=10,alpha=.3,color='#2166ac',edgecolors='none');rho=frame.jaccard_at_5.corr(frame.advantage,method='spearman');ax.axhline(0,color='#777777',lw=.8);ax.set_title(f'{m}\nSpearman ρ = {rho:.3f}; n = {len(frame)}');ax.set_xlabel('Jaccard@5 · higher is more repeatable')
    axes[0].set_ylabel('LIME minus random removal drop');fig.suptitle('Historical audit: within-model association',y=1.06)
    save(fig,'02_historical_stability_faithfulness','483 matched historical cases/model. Positive within-model random-adjusted associations do not imply the same ordering across model averages. Points may share feature groups; these plots do not establish significance or causation.')
    fig,axes=plt.subplots(1,2,figsize=(12,4.4),sharex=True,sharey=True)
    for ax,source in zip(axes,['unsw','ids2018']):
        count=0
        for j,m in enumerate(MODELS):
            path=BASE/f'xai/{source}/{m}/summary.csv'
            if not path.exists():continue
            data=pd.read_csv(path).set_index('target');target='ids2018' if source=='unsw' else 'unsw'
            a,b=data.loc[source],data.loc[target];color=plt.cm.tab10(j)
            ax.annotate('',xy=(b.jaccard5,b.paired_random_advantage),xytext=(a.jaccard5,a.paired_random_advantage),arrowprops=dict(arrowstyle='->',color=color,lw=1.6))
            ax.scatter(a.jaccard5,a.paired_random_advantage,c=[color],marker='o',s=45,label=LABELS[j]);ax.scatter(b.jaccard5,b.paired_random_advantage,c=[color],marker='s',s=40);count+=1
        ax.axhline(0,color='#777777',lw=.8);ax.set_title(f'Trained on {source.upper()} · {count}/7 models');ax.set_xlabel('Jaccard@5 across LIME seeds');ax.legend(fontsize=7,loc='best',framealpha=.7)
    axes[0].set_ylabel('LIME minus random removal drop');fig.suptitle('RQ3: circles = source domain; arrows point to target squares',y=1.02)
    save(fig,'03_explanation_transfer','Completed RQ3 pilots only: 20 balanced unique feature groups per domain, three LIME seeds, one training seed. Arrows connect cohort means, not paired instances. Higher repeatability does not guarantee larger random-adjusted masking effects.')
    calibration=pd.read_csv(BASE/'calibration/metrics.csv');delta=np.full((4,7),np.nan)
    for i,(s,t) in enumerate(directions):
        for j,m in enumerate(MODELS):
            group=calibration[(calibration.source==s)&(calibration.target==t)&(calibration.model==m)].set_index('variant');delta[i,j]=group.loc['source_calibrated','brier']-group.loc['raw','brier']
    limit=max(float(np.abs(delta).max()),1e-6)
    save(heatmap(delta,'Calibration effect: source-validation temperature scaling','RdBu_r','Calibrated minus raw Brier · negative is improvement',-limit,limit),'04_calibration','Temperature is fitted only on source validation. Negative cells indicate improved Brier score; positive cells indicate deterioration. Test labels are evaluation-only. Seed 42; 80000 cases per target.')
    imbalance=pd.read_csv(BASE/'imbalance/metrics.csv');fig,axes=plt.subplots(2,2,figsize=(10,6),sharey=True)
    variants=['balanced_weights','unweighted','random_undersampling']
    for ax,(s,t) in zip(axes.flat,directions):
        group=imbalance[(imbalance.source==s)&(imbalance.target==t)].set_index('variant');heights=group.loc[variants,'macro_f1'];bars=ax.bar(['Weighted','Unweighted','Undersampled'],heights,color=['#2166ac','#67a9cf','#ef8a62']);ax.bar_label(bars,fmt='%.3f',padding=3);ax.set_title(f'{s.upper()} → {t.upper()}');ax.set_ylim(0,1.08);ax.set_ylabel('Macro-F1')
    fig.suptitle('Random forest: training-only imbalance strategies');fig.tight_layout()
    save(fig,'05_imbalance','Same seed-42 split and random-forest hyperparameters; only class weighting or training-row undersampling changes. Test prevalence remains untouched. This is a single-seed ablation.')
    complete_models=len(list(BASE.glob('*/*/seed*/*/complete.json')))
    complete_xai=sum(json.loads(p.read_text()).get('status')=='complete' for p in (BASE/'xai').glob('*/*/manifest.json'))
    complete_llm=sum(json.loads(p.read_text()).get('status')=='complete' for p in (BASE/'llm').glob('*/full/manifest.json'))
    fig,axes=plt.subplots(1,3,figsize=(10,3.5))
    for ax,title,n,total in zip(axes,['Detector fits','RQ3 model pilots','Full LLM runs'],[complete_models,complete_xai,complete_llm],[84,14,3]):
        ax.pie([n,total-n],colors=['#218c74','#e5e7eb'],startangle=90,wedgeprops=dict(width=.3,edgecolor='white'));ax.text(0,0,f'{n}/{total}',ha='center',va='center',fontsize=21);ax.set_title(title)
    fig.suptitle('Completion snapshot · green = complete; gray = unfinished')
    save(fig,'06_completion','Counts are read from completion markers when regenerated. Unfinished includes pending or interrupted/running jobs; this chart does not independently verify live processes. LLM smoke tests do not count as full runs.')
    fig,ax=plt.subplots(figsize=(12,6));ax.set_xlim(0,12);ax.set_ylim(0,6);ax.axis('off')
    boxes=[(0.3,4.3,3.2,1,'Two public NetFlow releases\n39 shared predictive features'),(4.3,4.3,3.3,1,'Global encoded-feature groups\nTrain / validation / test'),(8.4,4.3,3.2,1,'Frozen classical + neural models\n3 training seeds'),(0.3,2.4,3.2,1,'Local LLMs\nClassification + explanations'),(4.3,2.4,3.3,1,'Cross-dataset evaluation\nDetection + RQ3 explanation transfer'),(8.4,2.4,3.2,1,'Controls and extensions\nRandom masking\nCalibration / imbalance'),(4.3,.4,3.3,1,'Auditable evidence\nMarkdown + tables + figures + Git')]
    for x,y,w,h,text in boxes:ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.08',facecolor='#eaf2f8',edgecolor='#2166ac'));ax.text(x+w/2,y+h/2,text,ha='center',va='center',fontsize=9)
    for a,b in [((3.6,4.8),(4.15,4.8)),((7.7,4.8),(8.25,4.8)),((5.95,4.2),(5.95,3.5)),((10,4.2),(10,3.5)),((8.3,4.35),(7.1,3.5)),((4.2,4.5),(1.9,3.5)),((3.6,2.9),(4.15,2.9)),((8.25,2.9),(7.7,2.9)),((5.95,2.3),(5.95,1.5))]:ax.add_patch(FancyArrowPatch(a,b,arrowstyle='->',mutation_scale=15,color='#444444',lw=1.5))
    ax.set_title('Study workflow · report revision deferred until evidence is complete',fontsize=14)
    save(fig,'07_workflow','Workflow diagram distinguishes model fitting, held-out evaluation and stored evidence. Source training provides LLM examples and explanation baselines; calibration fits source validation only. No target-test tuning.')
    lines=['# Figures and diagrams','','Regenerate with `.venv-study/Scripts/python.exe -m study.summarize` followed by `.venv-study/Scripts/python.exe -m study.make_figures`. PNG files are for viewing; SVG files are scalable publication assets. These figures do not modify the thesis report.','']
    for name,caption in CAPTIONS:lines.extend([f'## {name}', '',f'![{name}]({name}.png)','',caption,'',f'[Scalable SVG]({name}.svg)',''])
    (OUT/'FIGURES.md').write_text('\n'.join(lines),encoding='utf-8')
    report=BASE/'RESULTS.md'
    existing=report.read_text(encoding='utf-8').split('<!-- generated-figures -->')[0].rstrip()
    embedded=['','<!-- generated-figures -->','## Figures and diagrams','']
    for name,caption in CAPTIONS:
        embedded.extend([f'![{name}](figures/{name}.png)','',caption,'',f'[Scalable SVG](figures/{name}.svg)',''])
    report.write_text(existing+'\n'+'\n'.join(embedded),encoding='utf-8')
    print(f'Saved and embedded {len(CAPTIONS)} figures in PNG and SVG')
if __name__=='__main__':main()

