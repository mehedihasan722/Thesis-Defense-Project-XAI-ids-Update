import unittest
from study.summarize_llm import parse_features
class LLMOutputTests(unittest.TestCase):
    def test_valid_and_invalid_outputs_are_distinguished(self):
        self.assertEqual(parse_features('{"features":["bytes"],"explanation":"Observed value"}',['bytes']),(['bytes'],True))
        for text in ['not json','{"features":["invented"],"explanation":"x"}','{"features":[],"explanation":"x"}','{"features":["bytes","bytes"],"explanation":"x"}']:
            self.assertEqual(parse_features(text,['bytes']),([],False))
if __name__=='__main__':unittest.main()
