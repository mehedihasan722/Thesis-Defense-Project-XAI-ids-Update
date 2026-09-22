"""Build the revised five-chapter thesis from frozen study evidence (no inference)."""
from pathlib import Path
import csv
import hashlib
import json
import re

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/study/report'
MODELS = ['DecisionTree', 'RandomForest', 'XGBoost', 'SoftVoting', 'ShallowMLP', 'DeepMLP', 'FeatureCNN']
SHORT = {'unsw': 'U', 'ids2018': 'I'}
LLMS = {'Qwen/Qwen2.5-0.5B-Instruct': 'Qwen', 'TinyLlama/TinyLlama-1.1B-Chat-v1.0': 'TinyLlama', 'HuggingFaceTB/SmolLM2-1.7B-Instruct': 'SmolLM2'}


def table(title, headers, rows):
    return title + '\n\n' + '\n'.join('| ' + ' | '.join(map(str, row)) + ' |' for row in [headers, ['---'] * len(headers), *rows])


def main():
    inputs = set()

    def read(path):
        file = ROOT / path
        inputs.add(file)
        return file.read_text(encoding='utf-8-sig')

    def csvrows(path):
        return list(csv.DictReader(read(path).splitlines()))

    data = csvrows('results/study/across_seed_summary.csv')
    assert len(data) == 42 and all(int(r['n_seeds']) == 3 for r in data)
    metrics = csvrows('results/study/completed_metrics.csv')
    assert len(metrics) == 126 and all(int(r['n']) == 80000 for r in metrics)
    lookup = {(r['task'], r['source'], r['target'], r['model']): r for r in data}

    def val(task, src, dst, model, metric='macro_f1'):
        r = lookup[(task, src, dst, model)]
        return f"{float(r[metric + '_mean']):.4f} +/- {float(r[metric + '_sd']):.4f}"

    tokens = {}
    for token, task, dirs, caption in [
        ('WITHIN_TABLE', 'binary', [('unsw', 'unsw'), ('ids2018', 'ids2018')], 'Table 4.1. Within-dataset binary macro-F1, mean +/- sample SD across three seeds.'),
        ('MULTICLASS_TABLE', 'multiclass', [('unsw', 'unsw'), ('ids2018', 'ids2018')], 'Table 4.2. Native multiclass macro-F1, mean +/- sample SD across three seeds.'),
        ('TRANSFER_TABLE', 'binary', [('unsw', 'ids2018'), ('ids2018', 'unsw')], 'Table 4.3. Frozen binary transfer macro-F1, mean +/- sample SD across three seeds.'),
    ]:
        tokens[token] = table(caption, ['Model'] + [SHORT[a] + ' to ' + SHORT[b] for a, b in dirs], [[m] + [val(task, a, b, m) for a, b in dirs] for m in MODELS])
    tokens['TRANSFER_ERRORS'] = table('Table 4.4. Transfer balanced accuracy (BA) and false-alarm rate (FAR), three-seed means.', ['Model', 'U to I BA', 'U to I FAR', 'I to U BA', 'I to U FAR'], [[m] + [f"{float(lookup[('binary', a, b, m)][metric + '_mean']):.4f}" for a, b in [('unsw', 'ids2018'), ('ids2018', 'unsw')] for metric in ['balanced_accuracy', 'false_alarm_rate']] for m in MODELS])

    xai = csvrows('results/study/xai/aggregate.csv')
    assert len(xai) == 28 and all(int(r['n']) == 20 for r in xai)

    def xrow(r, direction=False):
        return ([SHORT[r['source']] + ' to ' + SHORT[r['target']]] if direction else []) + [r['model'], f"{float(r['jaccard5_mean']):.4f}", f"{float(r['advantage_mean']):.4f}", f"[{float(r['ci95_low']):.4f}, {float(r['ci95_high']):.4f}]"]

    for token, src, dst, num in [('XAI_U', 'unsw', 'ids2018', 5), ('XAI_I', 'ids2018', 'unsw', 6)]:
        rows = [next(r for r in xai if (r['source'], r['target'], r['model']) == (src, dst, m)) for m in MODELS]
        tokens[token] = table(f'Table 4.{num}. Explanation transfer, {SHORT[src]} to {SHORT[dst]}: primary median/absolute protocol.', ['Model', 'Jaccard@5', 'Advantage', '95% interval'], [xrow(r) for r in rows])
    tokens['XAI_FULL'] = '\n\n'.join(table(f'Table B.{i + 1}. Explanation results for {SHORT[src]} to {SHORT[dst]}.', ['Model', 'Jaccard@5', 'Advantage', '95% interval'], [xrow(next(r for r in xai if (r['source'], r['target'], r['model']) == (src, dst, m))) for m in MODELS]) for i, (src, dst) in enumerate([('unsw', 'unsw'), ('unsw', 'ids2018'), ('ids2018', 'unsw'), ('ids2018', 'ids2018')]))

    matched = csvrows('results/study/llm/matched_metrics.csv')
    llm_rows = [r for r in matched if r['model'] in LLMS]
    assert len(llm_rows) == 12 and sum(int(r['n']) for r in llm_rows) == 1200
    for r in llm_rows:
        assert abs(float(r['macro_f1']) - 1/3) < 1e-10 and float(r['accuracy']) == 0.5
    tokens['LLM_TABLE'] = table('Table 4.7. LLM classification: identical metrics in each of four balanced 100-case direction cells.', ['Model', 'Predicted class', 'Macro-F1', 'BA', 'FAR'], [[LLMS[m], 'Attack' if 'TinyLlama' in m else 'Benign', '0.3333', '0.5000', '1.0000' if 'TinyLlama' in m else '0.0000'] for m in LLMS])
    matched_lookup = {(r['source'], r['target'], r['model']): r for r in matched if r['model'] in MODELS}
    assert len(matched_lookup) == 28
    tokens['MATCHED_TABLE'] = table('Table 4.8. Detector macro-F1 on the balanced 100-case LLM cohorts (seed 42).', ['Model', 'U to U', 'U to I', 'I to U', 'I to I'], [[m] + [f"{float(matched_lookup[(a, b, m)]['macro_f1']):.4f}" for a, b in [('unsw', 'unsw'), ('unsw', 'ids2018'), ('ids2018', 'unsw'), ('ids2018', 'ids2018')]] for m in MODELS])
    coverage = csvrows('results/study/llm/masking_coverage.csv')
    assert len(coverage) == 24 and sum(int(r['total']) for r in coverage) == 480
    tokens['COVERAGE_TABLE'] = table('Table 4.9. Valid explanation coverage aggregated over all four direction cells.', ['Model', 'Own valid / total', 'Detector valid / total'], [[LLMS[m]] + [f"{sum(int(r['valid']) for r in coverage if r['model'] == m and r['kind'] == k)} / {sum(int(r['total']) for r in coverage if r['model'] == m and r['kind'] == k)}" for k in ['own', 'detector']] for m in LLMS])
    mask = csvrows('results/study/llm/masking_summary.csv')
    tokens['MASK_TABLE'] = table('Table 4.10. Conditional explanation masking: named-minus-random mean advantage on valid outputs only.', ['Model', 'Direction', 'Kind', 'Valid n', 'Advantage'], [[LLMS[r['model']], SHORT[r['source']] + ' to ' + SHORT[r['target']], r['kind'], r['n'], f"{float(r['mean_advantage']):.4f}"] for r in mask])

    manifest = json.loads(read('results/study/data_manifest.json'))
    assert len(manifest['features']) == 39
    tokens['FEATURE_TABLE'] = table('Table A.2. Shared feature inventory in the fixed input order.', ['Index', 'Feature'], [[i + 1, name] for i, name in enumerate(manifest['features'])])
    tokens['PROVENANCE_TABLE'] = table('Table A.1. Reproducibility artifact map (repository-relative locations).', ['Evidence', 'Location'], [
        ['Data hashes, splits and class counts', 'results/study/data_manifest.json'],
        ['Fixed configuration and model revisions', 'study/config.json; study/model_revisions.json'],
        ['126 detector evaluation cells', 'results/study/completed_metrics.csv'],
        ['Three-seed summaries', 'results/study/across_seed_summary.csv'],
        ['Explanation pilots and uncertainty', 'results/study/xai/aggregate.csv'],
        ['Post-hoc masking variants', 'results/study/xai/sensitivity/summary.csv'],
        ['Matched LLM/detector metrics', 'results/study/llm/matched_metrics.csv'],
        ['Explanation coverage and masking', 'results/study/llm/masking_coverage.csv; masking_summary.csv'],
        ['Historical replay', 'results/study/audit/REPLAY.md'],
        ['Report source hashes', 'results/study/report/input_manifest.json'],
    ])
    for path in ['study/build_report.py', 'study/report_figures.py', 'render_thesis_pdf.py', 'study/xai_transfer.py', 'study/config.json', 'study/models.py', 'study/train.py', 'study/model_revisions.json', 'thesis/format_spec.json', 'results/study/audit/ANALYSIS.md', 'results/study/audit/REPLAY.md', 'results/study/xai/sensitivity/ANALYSIS.md', 'results/study/calibration/metrics.csv', 'results/study/imbalance/metrics.csv', 'results/study/shift/ANALYSIS.md', 'results/study/shift/feature_shift.csv', 'results/study/xai/sensitivity/summary.csv', *[f'results/study/audit/{m}_matched.csv' for m in MODELS[:3]]]:
        read(path)
    template = read('thesis/study/report.template.md')
    assert set(re.findall(r'\{\{(\w+)\}\}', template)) == set(tokens)
    for name, value in tokens.items():
        template = template.replace('{{' + name + '}}', value)
    assert '{{' not in template
    for path in re.findall(r'!\[.*?\]\((.*?)\)', template):
        image = (ROOT / 'thesis' / path).resolve()
        assert image.is_file(), image
        inputs.add(image)
    (ROOT / 'thesis/manuscript.md').write_text(template, encoding='utf-8')
    OUT.mkdir(parents=True, exist_ok=True)
    hashes = {str(p.relative_to(ROOT)).replace('\\', '/'): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(inputs)}
    (OUT / 'input_manifest.json').write_text(json.dumps({'inputs': hashes, 'detector_cells': 126, 'three_seed_groups': 42, 'llm_cases': 1200, 'explanations': 480, 'manuscript_sha256': hashlib.sha256((ROOT / 'thesis/manuscript.md').read_bytes()).hexdigest()}, indent=2) + '\n', encoding='utf-8')
    print(f'Built manuscript: {len(template.split())} words; {len(hashes)} hashed inputs.')


if __name__ == '__main__':
    main()
