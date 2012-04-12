import unittest
from treadle.treadle import Const, Return, AExpression, If
from treadle.treadle_exceptions import *

class ConstTests(unittest.TestCase):
    def setUp(self):
        pass
    def test_Const(self):
        self.assertEqual(Const(42).toFunc()(), 42)
        self.assertEqual(Const("foo").toFunc()(), "foo")
    def test_Arg(self):
        self.assertRaises(ExpressionNotAllowedException, Const, Const(3))


class ReturnTests(unittest.TestCase):
    def test_Arg(self):
        self.assertRaises(ExpressionRequiredException, Return, 42)

class IfTests(unittest.TestCase):
    def test_If(self):
        self.assertEqual(If(Const(True), Const(1), Const(0)).toFunc()(), 1)
        self.assertEqual(If(Const(False), Const(1), Const(0)).toFunc()(), 0)
        self.assertEqual(If(Const(False), Const(1)).toFunc()(), None)

    def test_Args(self):
        self.assertRaises(ExpressionRequiredException, If, Const(False), 1)


class AbstractExpression(unittest.TestCase):
    def test_Init(self):
        AExpression()
    def test_UnbalanedStack(self):
        class UnbalancedStackExpression(AExpression):
            def __init__(self):
                pass
            def size(self, current, max_seen):
                return 2, 2
            def emit(self, ctx):
                pass

        self.assertRaises(UnbalancedStackException, UnbalancedStackExpression().toCode)




