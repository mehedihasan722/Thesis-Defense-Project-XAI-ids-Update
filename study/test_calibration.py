import unittest
import numpy as np
from study.calibration import scaled,scores
class CalibrationTests(unittest.TestCase):
    def test_identity_and_confidence_softening(self):
        p=np.array([[.9,.1],[.2,.8]])
        np.testing.assert_allclose(scaled(p,1),p)
        self.assertTrue(np.all(np.abs(scaled(p,2)[:,1]-.5)<np.abs(p[:,1]-.5)))
    def test_perfect_scores_and_edges(self):
        p=np.array([[1.,0.],[0.,1.]])
        self.assertEqual(scores(np.array([0,1]),p),(0.,0.))
        self.assertEqual(scores(np.array([1,0]),p),(1.,1.))
if __name__=='__main__':unittest.main()
