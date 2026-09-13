"""Fresh fixed-protocol training, checkpointed by model and seed."""
from pathlib import Path
import argparse,json,time,hashlib,copy,os
import numpy as np
import pandas as pd
import joblib
import torch
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import f1_score,classification_report,confusion_matrix,average_precision_score,balanced_accuracy_score
from xgboost import XGBClassifier
from study.models import Predictor,neural_model,log_values
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/'study/config.json').read_text(encoding='utf-8-sig'))
MODELS=['DecisionTree','RandomForest','XGBoost','SoftVoting','ShallowMLP','DeepMLP','FeatureCNN']

def metrics(y,p,classes):
    pred=p.argmax(axis=1);labels=list(range(len(classes)))
    report=classification_report(y,pred,labels=labels,target_names=classes,output_dict=True,zero_division=0)
    benign=classes.index('Benign') if 'Benign' in classes else 0
    present=np.unique(y)
    ap=[average_precision_score(y==c,p[:,c]) for c in present if 0<int((y==c).sum())<len(y)]
    result={'n':len(y),'macro_f1':f1_score(y,pred,labels=labels,average='macro',zero_division=0),'balanced_accuracy':balanced_accuracy_score(y,pred),'accuracy':float((pred==y).mean()),'macro_average_precision':float(np.mean(ap)) if ap else None,'false_alarm_rate':float((pred[y==benign]!=benign).mean()) if np.any(y==benign) else None,'absent_test_classes':[classes[c] for c in labels if c not in present]}
    return result,report,confusion_matrix(y,pred,labels=labels)

def train_neural(name,x,y,xv,yv,n_classes,seed,folder):
    torch.manual_seed(seed);np.random.seed(seed)
    scaler=StandardScaler().fit(log_values(x))
    tx=torch.from_numpy(scaler.transform(log_values(x)).astype(np.float32));ty=torch.from_numpy(y.astype(np.int64))
    vx=torch.from_numpy(scaler.transform(log_values(xv)).astype(np.float32));vy=torch.from_numpy(yv.astype(np.int64))
    model=neural_model(name,x.shape[1],n_classes)
    counts=np.bincount(y,minlength=n_classes);weights=np.zeros(n_classes,dtype=np.float32)
    nonzero=counts>0;weights[nonzero]=len(y)/(nonzero.sum()*counts[nonzero])
    criterion=torch.nn.CrossEntropyLoss(weight=torch.tensor(weights))
    optimizer=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001)
    history=[];best=float('inf');best_state=copy.deepcopy(model.state_dict());bad=0;first=0
    checkpoint=folder/'training.pt'
    if checkpoint.exists():
        state=torch.load(checkpoint,map_location='cpu',weights_only=False)
        model.load_state_dict(state['model']);optimizer.load_state_dict(state['optimizer']);torch.set_rng_state(state['rng'])
        history=state['history'];best=state['best'];best_state=state['best_state'];bad=state['bad'];first=state['epoch']+1
    for epoch in range(first,CFG['epochs']):
        if bad>=CFG['patience']:break
        model.train();order=torch.randperm(len(tx));loss_sum=0
        for indices in order.split(CFG['batch_size']):
            optimizer.zero_grad();loss=criterion(model(tx[indices]),ty[indices]);loss.backward();optimizer.step();loss_sum+=float(loss.detach())*len(indices)
        model.eval();val_sum=0
        with torch.inference_mode():
            for start in range(0,len(vx),4096):
                logits=model(vx[start:start+4096]);val_sum+=float(torch.nn.functional.cross_entropy(logits,vy[start:start+4096],reduction='sum'))
        val_loss=val_sum/len(vx);history.append({'epoch':epoch+1,'train_weighted_loss':loss_sum/len(tx),'validation_unweighted_loss':val_loss})
        if val_loss<best-1e-5:best=val_loss;best_state=copy.deepcopy(model.state_dict());bad=0
        else:bad+=1
        temporary=folder/'training.tmp.pt';torch.save({'model':model.state_dict(),'optimizer':optimizer.state_dict(),'rng':torch.get_rng_state(),'history':history,'best':best,'best_state':best_state,'bad':bad,'epoch':epoch},temporary);temporary.replace(checkpoint)
        print(name,'epoch',epoch+1,'validation loss',round(val_loss,5),flush=True)
    model.load_state_dict(best_state);pd.DataFrame(history).to_csv(folder/'learning_curve.csv',index=False)
    return Predictor(model,n_classes,scaler=scaler)

def main(dataset,task,seed):
    torch.set_num_threads(4)
    meta=json.loads((ROOT/'data/study/manifest.json').read_text());features=meta['features']
    assert meta.get('split_representation')=='signed_log1p_float32','Finish current preparation before training'
    frames={s:pd.read_parquet(ROOT/f'data/study/{dataset}/seed{seed}/{s}.parquet') for s in ['train','validation','test']}
    classes=['Benign','Attack'] if task=='binary' else sorted(meta['datasets'][dataset]['class_counts'])
    def label(d):return d.label.to_numpy(dtype=int) if task=='binary' else pd.Categorical(d.attack,categories=classes).codes.astype(int)
    x=frames['train'][features].to_numpy();y=label(frames['train']);xv=frames['validation'][features].to_numpy();yv=label(frames['validation'])
    assert len(np.unique(y))>1
    base=ROOT/f'results/study/{dataset}/{task}/seed{seed}';base.mkdir(parents=True,exist_ok=True)
    signature=hashlib.sha256(((ROOT/'data/study/manifest.json').read_text()+json.dumps(CFG)+Path(__file__).read_text()+(ROOT/'study/models.py').read_text()+(ROOT/'study/representation.py').read_text()).encode()).hexdigest()
    predictors={}
    for name in MODELS:
        folder=base/name;folder.mkdir(exist_ok=True)
        done=folder/'complete.json'
        if done.exists():
            assert json.loads(done.read_text())['signature']==signature,'Changed protocol; use a fresh results directory'
            predictors[name]=joblib.load(folder/'predictor.joblib');print('REUSE',dataset,task,seed,name,flush=True);continue
        manifest={'dataset':dataset,'task':task,'seed':seed,'model':name,'classes':classes,'features':features,'signature':signature,'status':'running'}
        if (folder/'training.pt').exists():
            assert json.loads((folder/'manifest.json').read_text())['signature']==signature,'Checkpoint protocol changed'
        (folder/'manifest.json').write_text(json.dumps(manifest,indent=2));t=time.perf_counter()
        if name=='SoftVoting':model=Predictor(None,len(classes),members=[predictors[n] for n in MODELS[:3]])
        elif name in MODELS[:3]:
            if name=='DecisionTree':est=DecisionTreeClassifier(max_depth=30,min_samples_leaf=5,class_weight='balanced',random_state=seed)
            elif name=='RandomForest':est=RandomForestClassifier(n_estimators=100,max_depth=30,min_samples_leaf=5,class_weight='balanced',random_state=seed,n_jobs=4)
            else:est=XGBClassifier(n_estimators=200,max_depth=8,learning_rate=.1,subsample=.8,colsample_bytree=.8,tree_method='hist',random_state=seed,n_jobs=4)
            indices,local_y=np.unique(y,return_inverse=True);est.fit(log_values(x),local_y);model=Predictor(est,len(classes),class_indices=indices)
        else:model=train_neural(name,x,y,xv,yv,len(classes),seed,folder)
        fit_seconds=time.perf_counter()-t
        if name=='SoftVoting':
            manifest['aggregation_seconds']=fit_seconds
            fit_seconds=sum(json.loads((base/n/'complete.json').read_text())['train_seconds'] for n in MODELS[:3])
        joblib.dump(model,folder/'predictor.joblib',compress=3);predictors[name]=model
        targets=[dataset] if task!='binary' else [dataset,'ids2018' if dataset=='unsw' else 'unsw']
        for target in targets:
            d=frames['test'] if target==dataset else pd.read_parquet(ROOT/f'data/study/{target}/seed{seed}/test.parquet')
            xt=d[features].to_numpy();yt=label(d);start=time.perf_counter();prob=model.predict_proba(xt);infer=time.perf_counter()-start
            values,report,cm=metrics(yt,prob,classes);values.update(source=dataset,target=target,task=task,seed=seed,model=name,train_seconds=fit_seconds,inference_seconds=infer)
            (folder/f'metrics_{target}.json').write_text(json.dumps(values,indent=2));pd.DataFrame(report).T.to_csv(folder/f'classes_{target}.csv');pd.DataFrame(cm,index=classes,columns=classes).to_csv(folder/f'confusion_{target}.csv')
            prediction=pd.DataFrame(prob,columns=[f'p_{i}' for i in range(len(classes))]);prediction['_row']=d._row.values;prediction['true']=yt;prediction.to_parquet(folder/f'predictions_{target}.parquet',index=False)
            print(dataset,task,seed,name,'->',target,'macro F1',values['macro_f1'],flush=True)
        manifest.update(status='complete',train_seconds=fit_seconds);done.write_text(json.dumps(manifest,indent=2));(folder/'manifest.json').write_text(json.dumps(manifest,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--dataset',choices=['unsw','ids2018'],required=True);ap.add_argument('--task',choices=['binary','multiclass'],required=True);ap.add_argument('--seed',type=int,default=42);main(**vars(ap.parse_args()))
