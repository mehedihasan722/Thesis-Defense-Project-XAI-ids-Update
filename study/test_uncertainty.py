import unittest
from study.summarize_xai import stratified_bootstrap
class UncertaintyTests(unittest.TestCase):
    def test_preserves_class_mix(self):
        self.assertEqual(stratified_bootstrap([1,1,3,3],[0,0,1,1],100),[2.,2.])
    def test_reproducible_and_retains_negative_effect(self):
        a=stratified_bootstrap([-1,-2,-3,-4],[0,0,1,1],100)
        self.assertEqual(a,stratified_bootstrap([-1,-2,-3,-4],[0,0,1,1],100))
        self.assertLess(a[1],0)
if __name__=='__main__':unittest.main()
