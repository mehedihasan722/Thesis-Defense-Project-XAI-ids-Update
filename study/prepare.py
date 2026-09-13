"""Streaming, globally group-disjoint and bounded two-dataset preparation."""
from pathlib import Path
import json,hashlib,sys
from collections import Counter
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from config import IDENTIFIER_COLUMNS
CFG=json.loads((ROOT/'study/config.json').read_text(encoding='utf-8-sig'))
OUT=ROOT/'data/study';OUT.mkdir(parents=True,exist_ok=True)

def mix64(x):
    x=np.asarray(x,dtype=np.uint64).copy()
    with np.errstate(over='ignore'):
        x=(x^(x>>30))*np.uint64(0xbf58476d1ce4e5b9)
        x=(x^(x>>27))*np.uint64(0x94d049bb133111eb)
    return x^(x>>31)

def partition(groups,seed):
    h=mix64(np.asarray(groups,dtype=np.uint64)^np.uint64(seed))
    u=(h>>11).astype(np.float64)/(2**53)
    return np.where(u<.70,0,np.where(u<.85,1,2))

def reservoir(previous,frame,cap):
    if previous is not None: frame=pd.concat([previous,frame],ignore_index=True)
    return frame.nsmallest(min(cap,len(frame)),'_priority').copy()

def main():
    files={key:next((ROOT/'data/raw'/key).glob('*.parquet')) for key in ['unsw','ids2018']}
    schemas={key:{name.lower():name for name in pq.ParquetFile(path).schema.names} for key,path in files.items()}
    common=sorted(set.intersection(*(set(s) for s in schemas.values()))-IDENTIFIER_COLUMNS-{'label','attack'})
    assert len(common)==39,(len(common),common)
    spec={'features':common,'seeds':CFG['seeds'],'caps':CFG['caps'],'split':'seeded common-feature hashes, 70/15/15 group assignment','sampling':'uniform row-priority reservoir after group assignment','datasets':{}}
    split_names=['train','validation','test']
    for key,path in files.items():
        destination=OUT/key
        if (destination/'complete.json').exists():
            spec['datasets'][key]=json.loads((destination/'complete.json').read_text());continue
        reservoirs={(s,p):None for s in CFG['seeds'] for p in split_names}
        counts=Counter();total=0;invalid=0
        partitions={(s,p):Counter() for s in CFG['seeds'] for p in split_names}
        schema=schemas[key];columns=[schema[n] for n in common+['label','attack']]
        for batch in pq.ParquetFile(path).iter_batches(batch_size=100000,columns=columns):
            d=batch.to_pandas();d.columns=[c.lower() for c in d.columns]
            values=d[common].to_numpy(dtype=np.float64)
            invalid+=int((~np.isfinite(values)).sum());values[~np.isfinite(values)]=0
            x=pd.DataFrame(values,columns=common)
            group=pd.util.hash_pandas_object(x,index=False).to_numpy(dtype=np.uint64)
            x['label']=d.label.astype(np.int8).values;x['attack']=d.attack.astype(str).values
            assert set(x.label.unique())<={0,1}
            assert ((x.attack.str.lower()=='benign')==(x.label==0)).all(),'Conflicting binary/family labels'
            x['_group']=group;x['_row']=np.arange(total,total+len(x),dtype=np.int64)
            counts.update(x.attack);total+=len(x)
            for seed in CFG['seeds']:
                split=partition(group,seed)
                x['_priority']=mix64(x['_row'].to_numpy(dtype=np.uint64)^np.uint64(seed+100003))
                for i,name in enumerate(split_names):
                    part=x.loc[split==i]
                    partitions[(seed,name)].update(part.attack)
                    reservoirs[(seed,name)]=reservoir(reservoirs[(seed,name)],part,CFG['caps'][name])
            print(key,total,'rows processed',flush=True)
        info={'raw_file':str(path.relative_to(ROOT)),'raw_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rows':total,'class_counts':dict(counts),'nonfinite_feature_values_replaced':invalid,'samples':{}}
        for seed in CFG['seeds']:
            folder=destination/f'seed{seed}';folder.mkdir(parents=True,exist_ok=True)
            groups=[]
            for name in split_names:
                d=reservoirs[(seed,name)].drop(columns='_priority').sort_values('_row').reset_index(drop=True)
                groups.append(set(d._group));d.to_parquet(folder/f'{name}.parquet',index=False)
                info['samples'][f'{seed}/{name}']={'rows':len(d),'feature_groups':d._group.nunique(),'class_counts':d.attack.value_counts().to_dict(),'partition_class_counts':dict(partitions[(seed,name)])}
            assert not groups[0]&groups[1] and not groups[0]&groups[2] and not groups[1]&groups[2]
        (destination/'complete.json').write_text(json.dumps(info,indent=2));spec['datasets'][key]=info
    # Global hash assignment provides the same guarantee across dataset names.
    for seed in CFG['seeds']:
        a=pd.read_parquet(OUT/'unsw'/f'seed{seed}/train.parquet',columns=['_group'])
        b=pd.read_parquet(OUT/'ids2018'/f'seed{seed}/test.parquet',columns=['_group'])
        assert not set(a._group)&set(b._group)
        a=pd.read_parquet(OUT/'ids2018'/f'seed{seed}/train.parquet',columns=['_group'])
        b=pd.read_parquet(OUT/'unsw'/f'seed{seed}/test.parquet',columns=['_group'])
        assert not set(a._group)&set(b._group)
    (OUT/'manifest.json').write_text(json.dumps(spec,indent=2));print('Prepared and verified both datasets',flush=True)

if __name__=='__main__':main()
