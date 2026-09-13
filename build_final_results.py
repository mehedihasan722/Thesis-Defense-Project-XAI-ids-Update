"""Build publication tables and figures from an explicit completed-run selection."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
import numpy as np
import pandas as pd
from scipy.stats import spearmanr, wilcoxon
from experiment import bootstrap_mean_ci
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

OUT = ROOT / 'results/final'
FIG = OUT / 'figures'
MODELS = ['DecisionTree', 'XGBoost', 'RandomForest', 'SoftVotingEnsemble']
SHORT = {'DecisionTree': 'DT', 'RandomForest': 'RF', 'XGBoost': 'XGB',
         'SoftVotingEnsemble': 'Voting', 'LogisticRegression': 'LR',
         'GaussianNB': 'GNB', 'MLP': 'MLP'}


def clustered_ci(values, groups, seed=42, repeats=2000):
    """Resample whole feature-vector groups; keep all sampled rows per group."""
    frame = pd.DataFrame({'value': values, 'group': groups})
    stats = frame.groupby('group')['value'].agg(['sum', 'size']).to_numpy()
    rng = np.random.default_rng(seed)
    samples = []
    for _ in range(repeats):
        draw = stats[rng.integers(0, len(stats), len(stats))]
        samples.append(draw[:, 0].sum() / draw[:, 1].sum())
    return np.quantile(samples, [0.025, 0.975])


def savefig(name):
    plt.savefig(FIG / f'{name}.png', dpi=220, bbox_inches='tight')
    plt.savefig(FIG / f'{name}.pdf', bbox_inches='tight')
    plt.close()


def main():
    FIG.mkdir(exist_ok=True)
    status = json.loads((OUT / 'suite_status.json').read_text())
    expected = {'prepare', 'rq1_SoftVotingEnsemble', 'baselines_seed7', 'baselines_seed1337'}
    expected |= {f'rq2_{m}_{mask}' for m in MODELS for mask in ['mean', 'median']}
    expected |= {f'rq4_{m}' for m in MODELS}
    if not all(status.get(k, {}).get('status') == 'complete' for k in expected):
        raise SystemExit('Final suite is incomplete; refusing to mix partial results.')
    for seed in [42, 7, 1337]:
        assert (OUT / 'grouped' / f'seed{seed}' / 'complete.json').exists()
    runs = {}
    for key in sorted(expected):
        folders = status[key].get('run_dirs', [])
        if not folders:
            continue
        # Other independent smoke checks may create run folders while a job
        # executes. Select by recorded protocol, model and full perturbation size.
        folders = [p for p in folders if (ROOT / p / 'manifest.json').exists()]
        matches = []
        for p in folders:
            m = json.loads((ROOT / p / 'manifest.json').read_text())
            if (key.startswith(f'{m["experiment"]}_{m["model"]}') and
                m['parameters'].get('num_samples') == 5000 and
                (m['experiment'] != 'rq2' or key.endswith('_' + m['parameters']['masking']))):
                matches.append(p)
        assert len(matches) == 1, (key, matches)
        folder = ROOT / matches[0]
        manifest = json.loads((folder / 'manifest.json').read_text())
        assert manifest['status'] == 'complete'
        assert manifest['parameters']['num_samples'] == 5000
        runs[key] = folder
    selected = {'runs': {k: str(v.relative_to(ROOT)) for k, v in runs.items()},
                'legacy_rq1': [], 'input_sha256': {}}
    meta = json.loads((ROOT / 'results/models/split_multiclass_seed42.json').read_text())
    X = pd.read_parquet(ROOT / 'data/processed/unsw_clean.parquet', columns=meta['feature_names'])
    hashes = pd.util.hash_pandas_object(X, index=False)
    stability, faithfulness, comparisons, mask_effects, associations = [], [], [], [], []
    rq1_frames, rq2_frames = {}, {}
    for model in ['DecisionTree', 'RandomForest', 'XGBoost', 'LogisticRegression', 'GaussianNB', 'MLP', 'SoftVotingEnsemble']:
        if model == 'SoftVotingEnsemble':
            path = runs['rq1_SoftVotingEnsemble'] / f'rq1_stability_{model}_multiclass.csv'
            origin = 'revised run'
        else:
            path = ROOT / f'results/tables/rq1_stability_{model}_multiclass.csv'
            selected['legacy_rq1'].append(str(path.relative_to(ROOT)))
            origin = 'retained historical instance results'
        d = pd.read_csv(path)
        assert len(d) == 933 and d.instance.is_unique
        rq1_frames[model] = d
        low, high = clustered_ci(d.jaccard_at_5, hashes.loc[d.instance].values)
        stability.append(dict(model=model, n=len(d), feature_groups=hashes.loc[d.instance].nunique(),
                              jaccard5=d.jaccard_at_5.mean(), jaccard10=d.jaccard_at_10.mean(),
                              kendall=d.kendall_tau.mean(), ci_low=low, ci_high=high, origin=origin))
    for model in MODELS:
        for mask in ['mean', 'median']:
            folder = runs[f'rq2_{model}_{mask}']
            d = pd.read_csv(folder / f'rq2_faithfulness_{model}_multiclass.csv')
            assert d.instance.nunique() == 483 and set(d.lime_seed) == {101, 202, 303}
            assert not d.duplicated(['instance', 'explainer', 'lime_seed']).any()
            avg = d.groupby(['instance', 'true_class', 'explainer'], as_index=False).mean(numeric_only=True)
            rq2_frames[(model, mask)] = avg
            for method, group in avg.groupby('explainer'):
                lo, hi = clustered_ci(group.comprehensiveness_auc, hashes.loc[group.instance].values)
                faithfulness.append(dict(model=model, masking=mask, explainer=method, n=len(group),
                    comp=group.comprehensiveness_auc.mean(), comp_ci_low=lo, comp_ci_high=hi,
                    retained=group.sufficiency_auc.mean()))
            pivot = avg.pivot(index='instance', columns='explainer', values='comprehensiveness_auc')
            for method in pivot.columns.drop('Random'):
                delta = pivot[method] - pivot.Random
                groups = hashes.loc[delta.index].values
                lo, hi = clustered_ci(delta.values, groups)
                cluster_delta = pd.Series(delta.values).groupby(groups).mean()
                p = 1.0 if (cluster_delta == 0).all() else wilcoxon(cluster_delta, alternative='greater').pvalue
                comparisons.append(dict(model=model, masking=mask, explainer=method,
                    n_instances=len(delta), n_groups=len(cluster_delta), mean_difference=delta.mean(),
                    ci_low=lo, ci_high=hi, p_value=p))
            class_table = avg.groupby(['true_class', 'explainer']).agg(
                n=('instance', 'size'), comp=('comprehensiveness_auc', 'mean'),
                retained=('sufficiency_auc', 'mean')).reset_index()
            class_table.to_csv(OUT / f'rq2_classes_{model}_{mask}.csv', index=False)
            # Across-seed variation is descriptive, not three independent instances.
            d[d.explainer == 'LIME'].groupby('instance').comprehensiveness_auc.agg(['mean', 'std', 'min', 'max']).to_csv(
                OUT / f'rq2_seed_variation_{model}_{mask}.csv')
            joint = rq1_frames[model].merge(avg[avg.explainer == 'LIME'], on='instance', suffixes=('_stability', '_faithfulness'))
            rho = spearmanr(joint.jaccard_at_5, joint.comprehensiveness_auc).statistic
            associations.append(dict(model=model, masking=mask, n=len(joint), spearman=rho,
                                      interpretation='descriptive matched-instance association; no causal tradeoff claim'))
        a = rq2_frames[(model, 'mean')]
        b = rq2_frames[(model, 'median')]
        paired = a.merge(b, on=['instance', 'explainer'], suffixes=('_mean', '_median'))
        for method, d in paired.groupby('explainer'):
            delta = d.comprehensiveness_auc_median - d.comprehensiveness_auc_mean
            lo, hi = clustered_ci(delta, hashes.loc[d.instance].values)
            mask_effects.append(dict(model=model, explainer=method, median_minus_mean=delta.mean(),
                                    ci_low=lo, ci_high=hi, n=len(d)))
    comparisons = pd.DataFrame(comparisons)
    # Bonferroni across every model/masking/method comparison in this final family.
    comparisons['p_bonferroni_global'] = np.minimum(1, comparisons.p_value * len(comparisons))
    stability = pd.DataFrame(stability)
    faithfulness = pd.DataFrame(faithfulness)
    stability.to_csv(OUT / 'rq1_summary.csv', index=False)
    faithfulness.to_csv(OUT / 'rq2_summary.csv', index=False)
    comparisons.to_csv(OUT / 'rq2_paired_effects.csv', index=False)
    pd.DataFrame(mask_effects).to_csv(OUT / 'masking_sensitivity.csv', index=False)
    pd.DataFrame(associations).to_csv(OUT / 'matched_stability_faithfulness.csv', index=False)
    baseline = pd.read_csv(OUT / 'baselines_seed42.csv').assign(seed=42)
    baseline = pd.concat([baseline, *[pd.read_csv(ROOT / f'results/tables/baselines_multiclass_seed{s}.csv').assign(seed=s)
                                     for s in [7, 1337]]], ignore_index=True)
    baseline.to_csv(OUT / 'random_split_metrics.csv', index=False)
    grouped = pd.read_csv(OUT / 'grouped/metrics.csv')
    split_stats = pd.concat([baseline.assign(protocol='Random flow split'), grouped.assign(protocol='Feature-group split')])
    split_summary = split_stats.groupby(['protocol', 'model']).agg(
        n_seeds=('seed', 'size'), macro_f1_mean=('macro_f1', 'mean'), macro_f1_std=('macro_f1', 'std'),
        far_mean=('false_alarm_rate', 'mean'), ap_mean=('pr_auc', 'mean')).reset_index()
    split_summary.to_csv(OUT / 'split_comparison.csv', index=False)
    plt.rcParams.update({'font.size': 12, 'axes.spines.top': False, 'axes.spines.right': False})
    plt.figure(figsize=(7.2, 4))
    for i, protocol in enumerate(['Random flow split', 'Feature-group split']):
        d = split_summary[split_summary.protocol == protocol].set_index('model').loc[MODELS]
        plt.bar(np.arange(4) + (i - .5) * .36, d.macro_f1_mean, width=.36,
                yerr=d.macro_f1_std, capsize=3, label=protocol)
    plt.xticks(range(4), [SHORT[m] for m in MODELS]); plt.ylabel('Macro F1'); plt.ylim(0, 1)
    plt.legend(); plt.title('Detection performance across three seeds'); savefig('01_detection_splits')
    d = stability.sort_values('jaccard5')
    plt.figure(figsize=(7.2, 4))
    plt.errorbar(d.jaccard5, [SHORT[m] for m in d.model],
                 xerr=np.array([d.jaccard5-d.ci_low, d.ci_high-d.jaccard5]), fmt='o', capsize=3)
    plt.xlim(0, 1); plt.xlabel('Mean Jaccard at 5\n95% feature-group bootstrap interval')
    plt.title('LIME repeatability on frozen models'); savefig('02_stability')
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 4.6), sharey=True)
    for ax, mask in zip(axes, ['mean', 'median']):
        for j, method in enumerate(['LIME', 'TreeSHAP']):
            d = comparisons[(comparisons.masking == mask) & (comparisons.explainer == method)]
            xpos = np.array([MODELS.index(m) for m in d.model]) + (j - .5) * .14
            ax.errorbar(xpos, d.mean_difference, yerr=np.array([d.mean_difference-d.ci_low, d.ci_high-d.mean_difference]),
                        fmt='o', capsize=3, label=method)
        ax.axhline(0, color='gray', ls='--'); ax.set_xticks(range(4), [SHORT[m] for m in MODELS]); ax.set_title(mask.title()+' masking')
    axes[0].set_ylabel('Comprehensiveness advantage over random'); axes[1].legend()
    fig.suptitle('Paired effects with feature-group bootstrap intervals'); fig.tight_layout(); savefig('03_faithfulness')
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 7))
    agreement_rows = []
    for ax, model in zip(axes.flat, MODELS):
        folder = runs[f'rq4_{model}']
        matrix = pd.read_csv(folder / f'rq4_agreement_{model}_multiclass.csv', index_col=0)
        ax.imshow(matrix, vmin=-1, vmax=1, cmap='RdBu_r')
        labels = [n.replace('ProbabilityPermutation', 'Prob perm').replace('TreeSHAP', 'SHAP') for n in matrix.columns]
        ax.set_xticks(range(len(matrix)), labels, rotation=35, ha='right'); ax.set_yticks(range(len(matrix)), labels)
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                value = matrix.iloc[i,j]
                ax.text(j,i,f'{value:.2f}',ha='center',va='center', color='white' if abs(value)>.65 else 'black')
                if i < j:
                    agreement_rows.append(dict(model=model, method_a=matrix.index[i], method_b=matrix.columns[j], spearman=value))
        ax.set_title(SHORT[model])
    fig.suptitle('RQ4 agreement on matched instances\nand original predicted classes')
    fig.tight_layout(); savefig('04_agreement')
    pd.DataFrame(agreement_rows).to_csv(OUT / 'rq4_agreement.csv', index=False)
    effects = pd.DataFrame(mask_effects)
    d = effects[effects.explainer == 'LIME'].set_index('model').loc[MODELS]
    plt.figure(figsize=(7.2,4)); plt.errorbar(range(4), d.median_minus_mean,
        yerr=np.array([d.median_minus_mean-d.ci_low, d.ci_high-d.median_minus_mean]), fmt='o', capsize=4)
    plt.axhline(0, color='gray', ls='--'); plt.xticks(range(4),[SHORT[m] for m in MODELS])
    plt.ylabel('Median minus mean masking comprehensiveness'); plt.title('LIME masking sensitivity'); savefig('05_masking')
    inputs = list(runs.values())
    for folder in inputs:
        for p in folder.glob('*.csv'):
            selected['input_sha256'][str(p.relative_to(ROOT))] = hashlib.sha256(p.read_bytes()).hexdigest()
    for relative in selected['legacy_rq1']:
        selected['input_sha256'][relative] = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
    (OUT / 'selected_runs.json').write_text(json.dumps(selected, indent=2))
    print('Built final tables and five figures from completed runs.', flush=True)


if __name__ == '__main__':
    main()
