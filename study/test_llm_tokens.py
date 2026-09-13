import unittest
import numpy as np,torch
from study.llm_tokens import label_tokens,append_prefix
class LabelTokenTests(unittest.TestCase):
    def test_common_prefix_and_unchanged_single_token(self):
        class Tokenizer:
            def encode(self,label,add_special_tokens=False):return [7,8] if label=='0' else [7,9]
        self.assertEqual(label_tokens(Tokenizer()),([7],[8,9]))
        ids=torch.tensor([[1,2]])
        self.assertIs(append_prefix(ids,[]),ids)
        self.assertTrue(torch.equal(append_prefix(ids,[7]),torch.tensor([[1,2,7]])))
    def test_full_candidate_normalization_cancels_common_prefix(self):
        probabilities=np.array([.4,.6]);full=.17*probabilities
        np.testing.assert_allclose(full/full.sum(),probabilities/probabilities.sum())
    def test_unsupported_nonshared_multiple_tokens_rejected(self):
        class Tokenizer:
            def encode(self,label,add_special_tokens=False):return [1,2] if label=='0' else [3,4]
        with self.assertRaises(ValueError):label_tokens(Tokenizer())
if __name__=='__main__':unittest.main()
