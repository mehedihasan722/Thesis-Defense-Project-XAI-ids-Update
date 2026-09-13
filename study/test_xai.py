import unittest
import numpy as np,pandas as pd
from study.xai_transfer import effects,cohort
class XAITests(unittest.TestCase):
    def test_masking_fixes_class_and_ignores_unused_feature(self):
        def predict(x):return np.column_stack([1-x[:,0],x[:,0]])
        z=np.array([.9,5.]);baseline=np.array([.1,0.])
        drop,gap=effects(predict,z,[0,1],baseline,1,ks=(1,2))
        np.testing.assert_allclose(drop,[.8,.8]);np.testing.assert_allclose(gap,[0,0])
        drop,_=effects(predict,z,[1,0],baseline,1,ks=(1,2))
        np.testing.assert_allclose(drop,[0,.8])
    def test_balanced_cohort_deduplicates_groups(self):
        frame=pd.DataFrame({'_group':np.repeat(np.arange(40),2),'label':np.repeat([0,1],40),'_row':np.arange(80)})
        a=cohort(frame);self.assertEqual(len(a),20);self.assertEqual(a._group.nunique(),20)
        self.assertEqual(a.label.value_counts().to_dict(),{0:10,1:10})
        pd.testing.assert_frame_equal(a,cohort(frame))
if __name__=='__main__':unittest.main()
