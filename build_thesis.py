"""Insert verified final tables into the editable thesis manuscript."""
import json
from pathlib import Path
import re
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results/final'


def table(headers, rows):
    lines = ['| ' + ' | '.join(headers) + ' |', '| ' + ' | '.join(['---'] * len(headers)) + ' |']
    lines += ['| ' + ' | '.join(str(c) for c in row) + ' |' for row in rows]
    return '\n'.join(lines)


def main():
    selected = json.loads((OUT / 'selected_runs.json').read_text())
    stability = pd.read_csv(OUT / 'rq1_summary.csv')
    split = pd.read_csv(OUT / 'split_comparison.csv')
    effects = pd.read_csv(OUT / 'rq2_paired_effects.csv')
    masks = pd.read_csv(OUT / 'masking_sensitivity.csv')
    assoc = pd.read_csv(OUT / 'matched_stability_faithfulness.csv')
    agreement = pd.read_csv(OUT / 'rq4_agreement.csv')
    audit = json.loads((OUT / 'data_audit.json').read_text())
    short = {'DecisionTree': 'DT', 'RandomForest': 'RF', 'XGBoost': 'XGB',
             'SoftVotingEnsemble': 'Voting', 'LogisticRegression': 'Logistic regression',
             'GaussianNB': 'Gaussian NB', 'MLP': 'MLP'}
    replacements = {}
    def metric(protocol, model):
        return float(split[(split.protocol == protocol) & (split.model == model)].macro_f1_mean.iloc[0])
    replacements['ensemble_jaccard'] = f"{stability[stability.model == 'SoftVotingEnsemble'].jaccard5.iloc[0]:.4f}"
    replacements['xgb_random'] = f"{metric('Random flow split', 'XGBoost'):.4f}"
    replacements['xgb_grouped'] = f"{metric('Feature-group split', 'XGBoost'):.4f}"
    replacements['ensemble_random'] = f"{metric('Random flow split', 'SoftVotingEnsemble'):.4f}"
    replacements['ensemble_grouped'] = f"{metric('Feature-group split', 'SoftVotingEnsemble'):.4f}"
    lime_mean = effects[(effects.explainer == 'LIME') & (effects.masking == 'mean')]
    replacements['mean_effect_range'] = f'{lime_mean.mean_difference.min():.3f} to {lime_mean.mean_difference.max():.3f}'
    replacements['class_table'] = 'Table 1 Dataset class distribution\n\n' + table(
        ['Class', 'Flows', 'Percent'], [[k, f'{v:,}', f'{100*v/audit["rows"]:.3f}'] for k,v in audit['class_counts'].items()])
    replacements['split_table'] = 'Table 2 Detection performance across three seeds\n\n' + table(
        ['Split', 'Model', 'Macro F1 mean', 'SD', 'Mean FAR'],
        [[r.protocol.replace('Random flow split','Random').replace('Feature-group split','Grouped'), short[r.model],
          f'{r.macro_f1_mean:.4f}', f'{r.macro_f1_std:.4f}', f'{100*r.far_mean:.3f}%'] for r in split.itertuples()])
    replacements['stability_table'] = 'Table 3 LIME repeatability on 933 instances per model\n\n' + table(
        ['Model', 'Jaccard 5', 'Jaccard 10', 'Kendall', 'Groups'],
        [[short[r.model],f'{r.jaccard5:.4f}',f'{r.jaccard10:.4f}',f'{r.kendall:.4f}',r.feature_groups] for r in stability.itertuples()])
    replacements['faithfulness_table'] = 'Table 4 Paired comprehensiveness differences from random\n\n' + table(
        ['Model', 'Mask', 'Method', 'Difference', '95% interval'],
        [[short[r.model],r.masking,r.explainer,f'{r.mean_difference:.3f}',f'[{r.ci_low:.3f}, {r.ci_high:.3f}]'] for r in effects.itertuples()])
    significant = effects[(effects.ci_low > 0) & (effects.p_bonferroni_global < .05)]
    replacements['faithfulness_interpretation'] = (
        f'Of {len(effects)} model-baseline-method comparisons, {len(significant)} have both a positive lower bootstrap bound '
        'and a globally adjusted one-sided p-value below 0.05. These are conditional effects on the selected '
        'benchmark representations. Statistical significance does not establish that the intervention is physically '
        'realistic or that the explanation would improve an analyst decision. The complete adjusted p-values and '
        'numbers of independent feature groups are preserved in rq2_paired_effects.csv.')
    replacements['masking_table'] = 'Table 5 LIME median minus mean masking effects\n\n' + table(
        ['Model', 'Difference', '95% interval'],
        [[short[r.model],f'{r.median_minus_mean:.3f}',f'[{r.ci_low:.3f}, {r.ci_high:.3f}]'] for r in masks[masks.explainer=='LIME'].itertuples()])
    replacements['association_table'] = 'Table 6 Matched instance Spearman associations\n\n' + table(
        ['Model','Mask','Matched instances','Spearman'],
        [[short[r.model],r.masking,r.n,f'{r.spearman:.3f}'] for r in assoc.itertuples()])
    focused = agreement[(agreement.method_a != 'TOPSIS') & (agreement.method_b != 'TOPSIS')]
    replacements['agreement_table'] = 'Table 7 Full ranking agreement between model based methods\n\n' + table(
        ['Model','Method pair','Spearman'],
        [[short[r.model], f'{r.method_a} / {r.method_b}'.replace('ProbabilityPermutation','Prob permutation'),f'{r.spearman:.3f}'] for r in focused.itertuples()])
    replacements['inventory_table'] = table(['Evidence','Location'],[
        ['Selected revised runs','results/final/selected_runs.json'],
        ['Run commands and completion','results/final/suite_status.json'],
        ['Original split audit','results/final/data_audit.json'],
        ['Three seed detection comparison','results/final/split_comparison.csv'],
        ['Repeatability summary','results/final/rq1_summary.csv'],
        ['Paired masking effects','results/final/rq2_paired_effects.csv'],
        ['Grouped split metadata','results/final/grouped/seed*/split.json'],
        ['Original RQ1 provenance','legacy_rq1 in selected_runs.json']])
    per_class = pd.read_csv(OUT / 'per_class_SoftVotingEnsemble.csv')
    replacements['inventory_table'] += '\n\n## B.2 Per Class Voting Performance on the Original Split\n\nTable B.1 Three model ensemble class performance\n\n' + table(
        ['Class', 'Precision', 'Recall', 'F1', 'Support'],
        [[r[0], f'{r[2]:.3f}', f'{r[1]:.3f}', f'{r[3]:.3f}', int(r[4])] for r in per_class.itertuples(index=False, name=None)])
    text = (ROOT / 'thesis/manuscript.template.md').read_text(encoding='utf-8')
    for key, value in replacements.items():
        text = text.replace('{{'+key+'}}', value)
    # Follow the supplied IIUC five-chapter format without copying its old results.
    chapter_map = {
        '1 Introduction': 'CHAPTER I\nINTRODUCTION',
        '2 Background and Related Work': 'CHAPTER II\nLITERATURE REVIEW',
        '3 Data and Methodology': 'CHAPTER III\nMETHODOLOGY',
        '4 Detection Results and Split Audit': 'CHAPTER IV\nRESULTS AND DISCUSSION\n\n## 4.1 Detection Results and Split Audit',
        '10 Conclusions and Future Work': 'CHAPTER V\nCONCLUSION AND FUTURE WORKS',
    }
    section_map = {'5': '4.2', '6': '4.3', '7': '4.4', '8': '4.5', '9': '4.6'}
    converted = []
    for line in text.splitlines():
        if line.startswith('# ') and line[2:] in chapter_map:
            title = chapter_map[line[2:]]
            parts = title.split('\n', 1)
            line = '# ' + parts[0] + '\n' + parts[1]
        elif re.match(r'^# [5-9] ', line):
            match = re.match(r'^# ([5-9]) (.*)', line)
            line = '## ' + section_map[match[1]] + ' ' + match[2]
        elif re.match(r'^## [4-9]\.\d+', line):
            match = re.match(r'^## ([4-9])\.(\d+) (.*)', line)
            prefix = '4.1' if match[1] == '4' else section_map[match[1]]
            line = '### ' + prefix + '.' + match[2] + ' ' + match[3]
        converted.append(line)
    text = '\n'.join(converted)
    text = text.replace('# Appendix B Evidence Inventory', '# Appendix B Supplementary Result Tables\n\n## B.1 Evidence Inventory')
    text = text.replace('# Appendix C Interpretation Guide', '## B.3 Interpretation Guide')
    text = text.replace('CONCLUSION AND FUTURE WORKS\n\nThe thesis evaluates', 'CONCLUSION AND FUTURE WORKS\n\n## 5.1 Conclusions\n\nThe thesis evaluates')
    text = text.replace('\nFuture work should prioritize', '\n## 5.2 Future Works\n\nFuture work should prioritize')
    text = text.replace('Chapter 4 presents detection and split-audit results. Chapters 5 through 7 present repeatability, faithfulness and agreement. Chapter 8 discusses their joint interpretation, Chapter 9 states validity limits, and Chapter 10 gives conclusions and future work.',
        'Chapter 4 presents detection, split-audit, repeatability, faithfulness and agreement results, followed by discussion and validity limits. Chapter 5 gives conclusions and future work.')
    text = re.sub(r'\bFigure ([1-5])\b', lambda m: 'Figure 4.' + m[1], text)
    text = re.sub(r'\bTable ([1-7])\b', lambda m: 'Table 3.1' if m[1]=='1' else 'Table 4.'+str(int(m[1])-1), text)
    unresolved = re.findall(r'\{\{.*?\}\}',text)
    assert not unresolved, unresolved
    (ROOT / 'thesis/manuscript.md').write_text(text, encoding='utf-8')
    summary = {'manuscript_words': len(text.split()), 'selected_revised_runs': len(selected['runs']),
               'rq2_comparisons': len(effects), 'positive_adjusted_comparisons': len(significant),
               'xgb_random_macro_f1': metric('Random flow split','XGBoost'),
               'xgb_grouped_macro_f1': metric('Feature-group split','XGBoost')}
    (OUT / 'thesis_summary.json').write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
