import unittest,tempfile
from pathlib import Path
import numpy as np,pandas as pd,torch,joblib
from sklearn.preprocessing import StandardScaler
from study.prepare import partition,reservoir
from study.models import neural_model,Predictor,log_values
from study.train import metrics
class StudyTests(unittest.TestCase):
    def test_extreme_finite_values_and_rounding_groups(self):
        raw=np.array([[1e300,-1e300,0],[1e300*(1+1e-9),-1e300,0]])
        encoded=log_values(raw)
        self.assertTrue(np.isfinite(encoded.astype(np.float32)).all())
        groups=pd.util.hash_pandas_object(pd.DataFrame(encoded),index=False).values
        self.assertEqual(groups[0],groups[1])
    def test_global_group_partition_independent_of_dataset_and_order(self):
        a=np.array([17,42,17,999],dtype=np.uint64)
        for seed in [42,7,1337]:
            p=partition(a,seed);self.assertEqual(p[0],p[2]);np.testing.assert_array_equal(partition(a[::-1],seed),p[::-1])
    def test_reservoir_equals_global_lowest_priority(self):
        d=pd.DataFrame({'_priority':np.array([2**64-1,0,15,2,77],dtype=np.uint64),'x':range(5)})
        r=reservoir(reservoir(None,d.iloc[:2],3),d.iloc[2:],3)
        self.assertEqual(r.x.tolist(),[1,3,2])
    def test_neural_probabilities_and_serialization(self):
        torch.set_num_threads(2);x=np.random.RandomState(42).normal(size=(20,39))
        scaler=StandardScaler().fit(log_values(x));before=scaler.mean_.copy()
        for name in ['ShallowMLP','DeepMLP','FeatureCNN']:
            model=neural_model(name,39,3);predictor=Predictor(model,3,scaler=scaler)
            p=predictor.predict_proba(x);self.assertEqual(p.shape,(20,3));np.testing.assert_allclose(p.sum(1),1,atol=1e-6)
            with tempfile.TemporaryDirectory() as folder:
                path=Path(folder)/'m.joblib';joblib.dump(predictor,path);np.testing.assert_allclose(joblib.load(path).predict_proba(x),p)
            predictor.predict_proba(x*100);np.testing.assert_array_equal(scaler.mean_,before)
    def test_metrics_count_false_alarms(self):
        y=np.array([0,0,1,1]);p=np.array([[.9,.1],[.2,.8],[.1,.9],[.7,.3]])
        values,_,cm=metrics(y,p,['Benign','Attack']);self.assertEqual(values['false_alarm_rate'],.5);self.assertEqual(values['macro_f1'],.5);np.testing.assert_array_equal(cm,[[1,1],[1,1]])
if __name__=='__main__':unittest.main()
