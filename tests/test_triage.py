import unittest
from triage import Model, tokens
from evaluate import evaluate
class Tests(unittest.TestCase):
    def test_smoke_holdout(self):
        r=evaluate(); self.assertEqual(r['passed'],r['total'],r)
    def test_normalization(self):
        self.assertEqual(tokens('إِضَاءَة'), tokens('اضاءه'))
    def test_invalid(self):
        for x in ['', ' '*3, 'connectivity'*1001, None]:
            with self.subTest(x=x):
                with self.assertRaises(ValueError): Model().predict(x)
    def test_abstention(self):
        self.assertEqual(Model().predict('xyz qqq')['category'],'human_review')
    def test_human_always_required(self):
        self.assertTrue(Model().predict('التسجيل متوقف التسجيلات القرص')['review_required'])
    def test_learning_not_keyword_switch(self):
        model=Model({'connectivity':['alpha beta'], 'recording':['gamma delta']})
        self.assertEqual(model.predict('alpha beta')['category'],'connectivity')
        other=Model({'recording':['alpha beta'], 'connectivity':['gamma delta']})
        self.assertEqual(other.predict('alpha beta')['category'],'recording')
if __name__=='__main__': unittest.main()
