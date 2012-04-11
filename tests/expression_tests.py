import unittest
from treadle.treadle import Const

class ExpressionTests(unittest.TestCase):
    def setUp(self):
        pass
    def test_Const(self):
        self.assertEqual(Const(42).toFunc()(), 42)
        self.assertEqual(Const("foo").toFunc()(), "foo")






