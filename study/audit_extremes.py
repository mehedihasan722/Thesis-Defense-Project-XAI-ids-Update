"""Locate extreme finite raw rate values and their representation in study splits."""
from pathlib import Path
import json
import numpy as np,pandas as pd,pyarrow.parquet as pq
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/study/shift'
def main():
    names=['SRC_TO_DST_SECOND_BYTES','DST_TO_SRC_SECOND_BYTES'];rows=[];counts={n:0 for n in names};extreme_rows=set();offset=0;maximum={n:0. for n in names}
    raw=next((ROOT/'data/raw/ids2018').glob('*.parquet'))
    for batch in pq.ParquetFile(raw).iter_batches(batch_size=100000,columns=names):
        d=batch.to_pandas()
        for n in names:
            values=d[n].to_numpy();mask=abs(values)>np.finfo(np.float32).max;counts[n]+=int(mask.sum());maximum[n]=max(maximum[n],float(np.abs(values).max()));extreme_rows.update((np.flatnonzero(mask)+offset).tolist())
        offset+=len(d)
    for seed in [42,7,1337]:
        for split in ['train','validation','test']:
            d=pd.read_parquet(ROOT/f'data/study/ids2018/seed{seed}/{split}.parquet',columns=['_row'])
            rows.append(dict(seed=seed,split=split,sampled_rows=len(d),rows_with_extreme_raw_rates=int(d._row.isin(extreme_rows).sum())))
    OUT.mkdir(exist_ok=True);pd.DataFrame(rows).to_csv(OUT/'extreme_rate_split_counts.csv',index=False)
    summary=dict(raw_rows=offset,unique_rows_with_extreme_rates=len(extreme_rows),feature_value_counts=counts,maximum_absolute_raw_values=maximum)
    (OUT/'extreme_rate_audit.json').write_text(json.dumps(summary,indent=2))
    text=['# Extreme raw rate-value audit','',f'In the cleaned IDS2018 release, {sum(counts.values())} finite rate values on {len(extreme_rows)} rows exceed float32 range out of {offset} rows. Counts are streamed from both SECOND_BYTES fields. The audit does not determine the exporter or cleaning cause.','', 'The study applies the predeclared signed-log encoding to all models and hashes that float32-equivalent representation before splitting. This prevents numerical overflow but does not establish physical validity of the original values. No post-test replacement or clipping is introduced. A separate predeclared data-cleaning sensitivity study would be needed to quantify their impact.','', '| Seed | Split | Sampled rows | Rows with extreme raw rates |','| --- | --- | --- | --- |']
    for r in rows:text.append(f"| {r['seed']} | {r['split']} | {r['sampled_rows']} | {r['rows_with_extreme_raw_rates']} |")
    (OUT/'EXTREME_VALUES.md').write_text('\n'.join(text)+'\n',encoding='utf-8');print(json.dumps(summary))
if __name__=='__main__':main()
