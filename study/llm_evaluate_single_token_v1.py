"""Local frozen LLM classification and explanation evidence; no external API."""
from pathlib import Path
import argparse,json,hashlib,time
import numpy as np,pandas as pd,torch,joblib
from transformers import AutoTokenizer,AutoModelForCausalLM
from study.xai_transfer import cohort
from study.representation import log_values
ROOT=Path(__file__).resolve().parents[1]

def vector(z):return ','.join(format(float(v),'.3g') for v in z)

def main(model,limit):
    torch.set_num_threads(2)
    downloads=json.loads((ROOT/'results/study/llm_downloads.json').read_text())
    info=downloads[model];tokenizer=AutoTokenizer.from_pretrained(info['path'],local_files_only=True,trust_remote_code=False)
    llm=AutoModelForCausalLM.from_pretrained(info['path'],local_files_only=True,trust_remote_code=False,torch_dtype=torch.float32).eval()
    label_ids=[tokenizer.encode(s,add_special_tokens=False) for s in ['0','1']]
    assert all(len(t)==1 for t in label_ids),'Label scoring requires single-token candidates'
    label_ids=[t[0] for t in label_ids]
    max_context=min(int(getattr(llm.config,'max_position_embeddings',2048)),8192)
    features=json.loads((ROOT/'data/study/manifest.json').read_text())['features']
    out=ROOT/'results/study/llm'/model.replace('/','--')/('full' if limit==100 else f'pilot{limit}')
    out.mkdir(parents=True,exist_ok=True)
    signature=hashlib.sha256((Path(__file__).read_text()+info['revision']+(ROOT/'data/study/manifest.json').read_text()+str(limit)).encode()).hexdigest()
    manifest=out/'manifest.json'
    if manifest.exists():assert json.loads(manifest.read_text())['signature']==signature,'Changed LLM protocol'
    meta=dict(model=model,revision=info['revision'],signature=signature,dtype='float32',quantization=None,cases_per_target=limit,classification='normalized conditional scores for single-token 0/1; not calibrated probability',status='running')
    manifest.write_text(json.dumps(meta,indent=2))
    path=out/'cases.jsonl';records=[json.loads(l) for l in path.read_text().splitlines()] if path.exists() else []
    seen={(r['source'],r['target'],r['row']) for r in records}
    def tokens(prompt,reserve=0):
        ids=tokenizer.apply_chat_template([{'role':'user','content':prompt}],add_generation_prompt=True,return_tensors='pt')
        assert ids.shape[1]+reserve<=max_context,f'Context overflow {ids.shape[1]} + {reserve} > {max_context}'
        return ids
    def classify(prompt):
        ids=tokens(prompt)
        with torch.inference_mode():scores=llm(input_ids=ids).logits[0,-1,label_ids].softmax(dim=0).numpy()
        return scores,ids.shape[1]
    def explain(prompt):
        ids=tokens(prompt,192)
        with torch.inference_mode():generated=llm.generate(input_ids=ids,attention_mask=torch.ones_like(ids),max_new_tokens=192,do_sample=False,pad_token_id=tokenizer.eos_token_id)
        return tokenizer.decode(generated[0,ids.shape[1]:],skip_special_tokens=True)
    for source in ['unsw','ids2018']:
        training=pd.read_parquet(ROOT/f'data/study/{source}/seed42/train.parquet')
        examples=cohort(training,4)
        prefix='Classify a network flow: 0=Benign, 1=Attack. Values are signed log1p transformed and rounded to 3 significant digits, in the listed feature order. Use the four labeled training examples. Return only 0 or 1.\nFeatures: '+','.join(features)+'\n'
        for _,example in examples.iterrows():prefix+='Flow: '+vector(log_values(example[features].to_numpy(dtype=float)))+' Label: '+str(int(example.label))+'\n'
        detector_folder=ROOT/f'results/study/{source}/binary/seed42/XGBoost'
        detector=joblib.load(detector_folder/'predictor.joblib')
        detector_baseline=np.median(log_values(training.sample(10000,random_state=42)[features].to_numpy()),axis=0)
        for target in ['unsw','ids2018']:
            frame=pd.read_parquet(ROOT/f'data/study/{target}/seed42/test.parquet')
            cases=cohort(frame,100)
            if limit!=100:cases=cohort(frame,limit)
            explanation_rows=set(cohort(frame,20)._row)
            for _,case in cases.iterrows():
                row=int(case['_row'])
                if (source,target,row) in seen:continue
                start=time.perf_counter();z=log_values(case[features].to_numpy(dtype=float));query=prefix+'Flow: '+vector(z)+' Label:'
                scores,count=classify(query)
                record=dict(source=source,target=target,row=row,group=str(int(case['_group'])),true_label=int(case.label),scores=scores.tolist(),predicted_label=int(scores.argmax()),prompt=query,prompt_tokens=count)
                if row in explanation_rows or limit!=100:
                    own=query+'\nThe selected label is '+str(record['predicted_label'])+'. Explain it briefly. Return JSON with keys features (up to three exact feature names) and explanation. Do not invent unobserved traffic history.'
                    record['own_explanation_prompt']=own;record['own_explanation']=explain(own)
                    probability=detector.predict_encoded(z[None])[0];label=int(probability.argmax());masked=np.tile(z,(len(features),1));np.fill_diagonal(masked,detector_baseline)
                    drops=probability[label]-detector.predict_encoded(masked)[:,label]
                    top=np.argsort(-drops)[:3]
                    evidence={features[i]:float(drops[i]) for i in top}
                    grounded=query+'\nA frozen XGBoost detector predicts '+str(label)+'. Its class-score drops when each feature is replaced by its source-training median: '+json.dumps(evidence)+'. Explain this detector result using only this measured evidence. Negative drop means opposing evidence. These are model sensitivities, not causal claims. Return JSON with keys features and explanation.'
                    record['detector_label']=label;record['detector_evidence']=evidence;record['detector_explanation_prompt']=grounded;record['detector_explanation']=explain(grounded)
                record['seconds']=time.perf_counter()-start;records.append(record)
                temporary=out/'cases.tmp.jsonl';temporary.write_text(''.join(json.dumps(r)+'\n' for r in records));temporary.replace(path)
                print(model,source,target,row,'saved',flush=True)
    meta['status']='complete';manifest.write_text(json.dumps(meta,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--model',required=True);ap.add_argument('--limit',type=int,choices=[2,100],default=100);main(**vars(ap.parse_args()))
