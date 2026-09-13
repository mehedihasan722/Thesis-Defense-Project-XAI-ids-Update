"""Train-only numerical transforms and CPU neural/classical predictors."""
import numpy as np
import torch
from torch import nn
from sklearn.preprocessing import StandardScaler
from study.representation import log_values

class FeatureCNN(nn.Module):
    def __init__(self,n_features,n_classes):
        super().__init__()
        self.net=nn.Sequential(nn.Conv1d(1,16,3,padding=1),nn.ReLU(),nn.Conv1d(16,32,3,padding=1),nn.ReLU(),nn.Flatten(),nn.Linear(32*n_features,64),nn.ReLU(),nn.Dropout(.1),nn.Linear(64,n_classes))
    def forward(self,x):return self.net(x.unsqueeze(1))

def neural_model(name,n_features,n_classes):
    if name=='ShallowMLP':return nn.Sequential(nn.Linear(n_features,64),nn.ReLU(),nn.Linear(64,n_classes))
    if name=='DeepMLP':return nn.Sequential(nn.Linear(n_features,256),nn.ReLU(),nn.Dropout(.1),nn.Linear(256,128),nn.ReLU(),nn.Dropout(.1),nn.Linear(128,64),nn.ReLU(),nn.Linear(64,n_classes))
    if name=='FeatureCNN':return FeatureCNN(n_features,n_classes)
    raise ValueError(name)

class Predictor:
    def __init__(self,model,n_classes,scaler=None,class_indices=None,members=None):
        self.model=model;self.n_classes=n_classes;self.scaler=scaler;self.members=members
        self.class_indices=class_indices;self.classes_=np.arange(n_classes)
    def predict_proba(self,x):
        return self.predict_encoded(log_values(x))
    def predict_encoded(self,z):
        z=np.asarray(z,dtype=np.float64)
        if self.members:return np.mean([m.predict_encoded(z) for m in self.members],axis=0)
        if self.scaler is not None:
            z=self.scaler.transform(z).astype(np.float32)
            self.model.eval();values=[]
            with torch.inference_mode():
                for start in range(0,len(z),4096):values.append(torch.softmax(self.model(torch.from_numpy(z[start:start+4096])),dim=1).numpy())
            return np.concatenate(values)
        raw=self.model.predict_proba(z)
        result=np.zeros((len(z),self.n_classes))
        result[:,self.class_indices]=raw
        return result
    def predict(self,x):return self.predict_proba(x).argmax(axis=1)
