"""Print-sized thesis figures from existing evidence; never reruns experiments."""
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'results/study'
OUT = BASE / 'report/figures'
MODELS = ['DecisionTree', 'RandomForest', 'XGBoost', 'SoftVoting', 'ShallowMLP', 'DeepMLP', 'FeatureCNN']
LABELS = ['Decision tree', 'Random forest', 'XGBoost', 'Soft voting', 'Shallow MLP', 'Deep MLP', 'Feature CNN']
DIRECTIONS = [('unsw', 'unsw'), ('unsw', 'ids2018'), ('ids2018', 'unsw'), ('ids2018', 'ids2018')]


def save(fig, name):
    fig.savefig(OUT / (name + '.png'), dpi=250, bbox_inches='tight')
    fig.savefig(OUT / (name + '.svg'), bbox_inches='tight', metadata={'Date': None})
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10, 'axes.spines.top': False, 'axes.spines.right': False, 'svg.hashsalt': 'thesis-report-v2'})
    fig, ax = plt.subplots(figsize=(5.7, 3.9))
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis('off')
    steps = ['Two cleaned NetFlow releases\n39 shared numeric features', 'Common encoded-feature groups\n70 / 15 / 15 train / validation / test', 'Source-only fitting and prompts\n7 detector families; 3 local LLMs', 'Frozen within-domain and transfer tests\nDetection; LIME; generated explanations', 'Controls and validation\nRandom masks; calibration; imbalance', 'Preserved evidence and revised thesis\nTables, figures, raw outputs and hashes']
    ys = np.linspace(.89, .09, len(steps))
    for y, label in zip(ys, steps):
        ax.add_patch(FancyBboxPatch((.04, y-.052), .92, .105, boxstyle='round,pad=.01', facecolor='#edf4fa', edgecolor='#2166ac'))
        ax.text(.5, y, label, ha='center', va='center', fontsize=10)
    for a, b in zip(ys[:-1], ys[1:]):
        ax.annotate('', xy=(.5, b+.063), xytext=(.5, a-.063), arrowprops={'arrowstyle': '->', 'color': '#444444'})
    save(fig, '07_workflow')

    d = pd.read_csv(BASE / 'across_seed_summary.csv')
    fig, axes = plt.subplots(2, 1, figsize=(5.7, 5.8), sharex=True)
    y = np.arange(7)
    for ax, task in zip(axes, ['binary', 'multiclass']):
        for shift, src, color, label in [(-.13, 'unsw', '#2166ac', 'UNSW'), (.13, 'ids2018', '#d95f02', 'IDS2018')]:
            g = d[(d.task == task) & (d.source == src) & (d.target == src)].set_index('model').loc[MODELS]
            ax.errorbar(g.macro_f1_mean, y+shift, xerr=g.macro_f1_sd, fmt='o', capsize=2, color=color, label=label)
        ax.set_yticks(y, LABELS); ax.invert_yaxis(); ax.set_title(task.capitalize()); ax.set_xlim(.2, 1.04); ax.grid(axis='x', alpha=.15)
    axes[0].legend(loc='lower left', fontsize=9); axes[-1].set_xlabel('Macro-F1: mean +/- sample SD (3 seeds)')
    fig.tight_layout(); save(fig, '10_across_seed_variation')

    shift = pd.read_csv(BASE / 'shift/feature_shift.csv').head(8).iloc[::-1]
    fig, ax = plt.subplots(figsize=(5.7, 3.6))
    ax.barh(shift.feature.str.replace('_', ' '), shift.ks_distance, color='#2166ac')
    ax.set_xlim(0, 1); ax.set_xlabel('Marginal KS distance'); ax.tick_params(axis='y', labelsize=9)
    fig.tight_layout(); save(fig, '09_feature_shift')

    fig, axes = plt.subplots(3, 1, figsize=(5.7, 6.0), sharex=True, sharey=True)
    for ax, model, label in zip(axes, MODELS[:3], LABELS[:3]):
        g = pd.read_csv(BASE / f'audit/{model}_matched.csv')
        ax.scatter(g.jaccard_at_5, g.advantage, s=7, alpha=.3, color='#2166ac')
        ax.axhline(0, color='gray', lw=.7)
        ax.text(.02, .93, f'{label}; n = {len(g)}; Spearman rho = {g.jaccard_at_5.corr(g.advantage, method="spearman"):.3f}', transform=ax.transAxes, va='top', fontsize=9, bbox={'facecolor': 'white', 'edgecolor': 'none', 'alpha': .9})
    axes[1].set_ylabel('LIME minus random drop'); axes[-1].set_xlabel('Jaccard@5')
    fig.tight_layout(); save(fig, '02_historical_stability_faithfulness')

    g = pd.read_csv(BASE / 'xai/aggregate.csv')
    fig, axes = plt.subplots(2, 1, figsize=(5.7, 6.1), sharex=True)
    for ax, src in zip(axes, ['unsw', 'ids2018']):
        dst = 'ids2018' if src == 'unsw' else 'unsw'
        for delta, target, color, label in [(-.13, src, '#2166ac', 'Source domain'), (.13, dst, '#d95f02', 'Target domain')]:
            v = g[(g.source == src) & (g.target == target)].set_index('model').loc[MODELS]
            ax.errorbar(v.advantage_mean, y+delta, xerr=np.array([v.advantage_mean-v.ci95_low, v.ci95_high-v.advantage_mean]), fmt='o', capsize=2, color=color, label=label)
        ax.set_yticks(y, LABELS); ax.invert_yaxis(); ax.axvline(0, color='gray', lw=.7); ax.set_title('Trained on ' + src.upper())
    axes[0].legend(loc='lower right', fontsize=8); axes[-1].set_xlabel('LIME minus random drop: mean and 95% interval')
    fig.tight_layout(); save(fig, '08_rq3_uncertainty')

    g = pd.read_csv(BASE / 'xai/sensitivity/summary.csv')
    combos = [('median', 'absolute'), ('mean', 'absolute'), ('median', 'signed_descending'), ('mean', 'signed_descending')]
    values = []; labels = []
    for src, dst, direction in [('unsw', 'ids2018', 'U-I'), ('ids2018', 'unsw', 'I-U')]:
        for model, label in zip(MODELS, LABELS):
            v = g[(g.source == src) & (g.target == dst) & (g.model == model)].set_index(['baseline', 'ranking'])
            values.append([v.loc[c, 'advantage'] for c in combos]); labels.append(direction + ' ' + label)
    values = np.array(values); lim = abs(values).max()
    fig, ax = plt.subplots(figsize=(5.7, 5.6)); im = ax.imshow(values, aspect='auto', cmap='RdBu_r', vmin=-lim, vmax=lim)
    ax.set_yticks(range(14), labels, fontsize=9); ax.set_xticks(range(4), ['Median\nabsolute', 'Mean\nabsolute', 'Median\nsigned', 'Mean\nsigned'], fontsize=9)
    for (i, j), v in np.ndenumerate(values):
        ax.text(j, i, f'{v:.3f}', ha='center', va='center', fontsize=8, color='white' if abs(v) > lim*.55 else 'black')
    fig.colorbar(im, ax=ax, shrink=.7, label='Masking advantage'); fig.tight_layout(); save(fig, '13_masking_sensitivity')

    g = pd.read_csv(BASE / 'llm/masking_coverage.csv')
    names = ['Qwen/Qwen2.5-0.5B-Instruct', 'TinyLlama/TinyLlama-1.1B-Chat-v1.0', 'HuggingFaceTB/SmolLM2-1.7B-Instruct']
    fig, ax = plt.subplots(figsize=(5.7, 3.5))
    for offset, kind, color in [(-.18, 'own', '#2166ac'), (.18, 'detector', '#d95f02')]:
        counts = g[g.kind == kind].groupby('model')[['valid', 'total']].sum().loc[names]
        bars = ax.bar(np.arange(3)+offset, counts.valid/counts.total, width=.34, color=color, label=kind.capitalize())
        ax.bar_label(bars, labels=[f'{v}/{n}' for v, n in zip(counts.valid, counts.total)], padding=3, fontsize=9)
    ax.set_xticks(range(3), ['Qwen', 'TinyLlama', 'SmolLM2']); ax.set_ylim(0, 1); ax.set_ylabel('Valid explanations / all outputs'); ax.legend()
    fig.tight_layout(); save(fig, '12_llm_explanation_checks')

    g = pd.read_csv(BASE / 'calibration/metrics.csv')
    vals = []
    for model in MODELS:
        row = []
        for src, dst in DIRECTIONS:
            v = g[(g.source == src) & (g.target == dst) & (g.model == model)].set_index('variant')
            row.append(v.loc['source_calibrated', 'brier'] - v.loc['raw', 'brier'])
        vals.append(row)
    vals = np.array(vals); lim = abs(vals).max()
    fig, ax = plt.subplots(figsize=(5.7, 4)); im = ax.imshow(vals, aspect='auto', cmap='RdBu_r', vmin=-lim, vmax=lim)
    ax.set_xticks(range(4), ['U to U', 'U to I', 'I to U', 'I to I']); ax.set_yticks(range(7), LABELS)
    for (i, j), v in np.ndenumerate(vals):
        ax.text(j, i, f'{v:.3f}', ha='center', va='center', fontsize=9, color='white' if abs(v) > lim*.55 else 'black')
    fig.colorbar(im, ax=ax, label='Calibrated minus raw Brier'); fig.tight_layout(); save(fig, '04_calibration')

    g = pd.read_csv(BASE / 'imbalance/metrics.csv')
    fig, axes = plt.subplots(2, 2, figsize=(5.7, 5), sharey=True)
    variants = ['balanced_weights', 'unweighted', 'random_undersampling']
    for ax, (src, dst), label in zip(axes.flat, DIRECTIONS, ['U to U', 'U to I', 'I to U', 'I to I']):
        v = g[(g.source == src) & (g.target == dst)].set_index('variant').loc[variants]
        bars = ax.bar(range(3), v.macro_f1, color=['#2166ac', '#67a9cf', '#d95f02'])
        ax.bar_label(bars, fmt='%.3f', fontsize=8, padding=2); ax.set_xticks(range(3), ['Weight', 'None', 'Under'], fontsize=9)
        ax.set_ylim(0, 1.13); ax.set_title(label); ax.set_ylabel('Macro-F1')
    fig.tight_layout(); save(fig, '05_imbalance')
    print('Saved 9 print-sized PNG/SVG figures from existing evidence.')


if __name__ == '__main__':
    main()
