"""Separate extension figures, using the original thesis model colours."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/study/preserved_report/figures'
MODELS = ['DecisionTree', 'RandomForest', 'XGBoost', 'SoftVoting', 'ShallowMLP', 'DeepMLP', 'FeatureCNN']
LABELS = ['Decision tree', 'Random forest', 'XGBoost', 'Soft voting', 'Shallow MLP', 'Deep MLP', 'Feature CNN']
COLORS = ['#c1440e', '#3d4f8f', '#4a8c5f', '#777777', '#2b7a9e', '#7851a9', '#bd5995']

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.size':10, 'axes.titlesize':11, 'axes.titleweight':'bold', 'axes.spines.top':False, 'axes.spines.right':False, 'axes.grid':True, 'grid.alpha':.25, 'legend.frameon':False, 'svg.hashsalt':'preserved-thesis'})
    catalog=[]
    def save(fig, name, caption, section):
        fig.tight_layout()
        for ext in ['png','svg','pdf']:
            target = OUT / f'{name}.{ext}'
            fig.savefig(target, dpi=300, bbox_inches='tight')
            if ext == 'svg':
                target.write_text('\n'.join(line.rstrip() for line in target.read_text(encoding='utf-8').splitlines())+'\n', encoding='utf-8')
        plt.close(fig)
        catalog.append({'file':name+'.png','caption':caption,'section':section})
    d=pd.read_csv(ROOT/'results/study/across_seed_summary.csv')
    for task in ['binary','multiclass']:
        for src in ['unsw','ids2018']:
            g=d[(d.task==task)&(d.source==src)&(d.target==src)].set_index('model').loc[MODELS]
            for metric,label in [('macro_f1','Macro-F1'),('false_alarm_rate','False-alarm rate')]:
                fig,ax=plt.subplots(figsize=(6.5,3.9))
                ax.barh(LABELS,g[metric+'_mean'],xerr=g[metric+'_sd'],color=COLORS,capsize=3)
                ax.invert_yaxis(); ax.set_xlim(0,max(1.05,float((g[metric+'_mean']+g[metric+'_sd']).max())+.02)); ax.set_xlabel(label+' (mean +/- sample SD)')
                ax.set_title(f'{src.upper()} {task} detection')
                save(fig,f'{task}_{src}_{metric}',f'{src.upper()} {task} {label.lower()} across seven detector families. Error bars show sample SD across seeds 7, 42 and 1337; 80,000 test flows per evaluation. These group-disjoint results are separate from the historical protocol in Figure 4.2.', 'detection')
    for src,dst in [('unsw','ids2018'),('ids2018','unsw')]:
        g=d[(d.task=='binary')&(d.source==src)&(d.target==dst)].set_index('model').loc[MODELS]
        fig,ax=plt.subplots(figsize=(6.5,3.9)); ax.barh(LABELS,g.macro_f1_mean,xerr=g.macro_f1_sd,color=COLORS,capsize=3)
        ax.invert_yaxis();ax.set_xlim(0,1);ax.set_xlabel('Macro-F1 (mean +/- sample SD)');ax.set_title(f'Frozen transfer: {src.upper()} to {dst.upper()}')
        save(fig,f'transfer_{src}_{dst}',f'Binary detection transfer from {src.upper()} to {dst.upper()}. All seven models are fitted on the source only; error bars represent three training seeds.', 'transfer')
    x=pd.read_csv(ROOT/'results/study/xai/aggregate.csv')
    for src,dst in [('unsw','unsw'),('unsw','ids2018'),('ids2018','unsw'),('ids2018','ids2018')]:
        g=x[(x.source==src)&(x.target==dst)].set_index('model').loc[MODELS]
        for metric,label in [('jaccard5_mean','Jaccard@5'),('advantage_mean','LIME minus random probability drop')]:
            fig,ax=plt.subplots(figsize=(6.5,3.9))
            err=None if metric=='jaccard5_mean' else np.array([g.advantage_mean-g.ci95_low,g.ci95_high-g.advantage_mean])
            ax.barh(LABELS,g[metric],xerr=err,color=COLORS,capsize=3);ax.invert_yaxis();ax.axvline(0,color='gray',lw=.8)
            if metric=='jaccard5_mean':ax.set_xlim(0,1)
            ax.set_xlabel(label);ax.set_title(f'LIME: {src.upper()} to {dst.upper()}')
            detail='Mean pairwise set overlap across three explanation seeds.' if err is None else 'Intervals are 95% stratified bootstrap intervals over 20 cases, conditional on one fitted model; they are not training-seed uncertainty.'
            save(fig,f'xai_{src}_{dst}_{metric}',f'{label} for {src.upper()} to {dst.upper()}: seed-42 detectors, 20 balanced unique-group cases, three LIME seeds, source-median masking and absolute attribution rankings. {detail}', 'xai')
    for model in MODELS[:3]:
        g=pd.read_csv(ROOT/f'results/study/audit/{model}_matched.csv')
        fig,ax=plt.subplots(figsize=(6.5,3.9));ax.scatter(g.jaccard_at_5,g.advantage,s=12,alpha=.35,color=COLORS[MODELS.index(model)])
        ax.set(xlabel='Jaccard@5',ylabel='LIME minus random probability drop',title=f'{model}: matched historical cases');ax.axhline(0,color='gray',lw=.8)
        rho=g.jaccard_at_5.corr(g.advantage,method='spearman')
        save(fig,f'audit_{model}',f'{model}: historical within-model stability versus random-controlled masking effect on {len(g)} matched cases. Descriptive Spearman rho = {rho:.4f}; this addresses a different question from the cross-model means in Figure 4.9.', 'audit')
    names=['Qwen/Qwen2.5-0.5B-Instruct','TinyLlama/TinyLlama-1.1B-Chat-v1.0','HuggingFaceTB/SmolLM2-1.7B-Instruct']
    g=pd.read_csv(ROOT/'results/study/llm/masking_coverage.csv')
    for kind in ['own','detector']:
        v=g[g.kind==kind].groupby('model')[['valid','total']].sum().loc[names]
        fig,ax=plt.subplots(figsize=(6.5,3.9));bars=ax.bar(['Qwen','TinyLlama','SmolLM2'],v.valid/v.total,color=['#3d4f8f','#c1440e','#4a8c5f'])
        ax.bar_label(bars,labels=[f'{a}/{b}' for a,b in zip(v.valid,v.total)],padding=4);ax.set_ylim(0,1);ax.set_ylabel('Valid explanation fraction');ax.set_title('Own-decision explanations' if kind=='own' else 'Detector-grounded explanations')
        save(fig,f'llm_{kind}',f'Valid {kind} explanations out of all 80 requested outputs per model. Coverage must accompany any masking score calculated only on valid explanations.', 'llm')
    (OUT.parent/'figure_catalog.json').write_text(json.dumps(catalog,indent=2),encoding='utf-8')
    print(f'Created {len(catalog)} independent figures in PNG, SVG and PDF')

if __name__=='__main__':main()
