import unittest
from treadle.treadle import Const, Return, AExpression, If, Add, Subtract, Do, Func, Argument, StoreLocal, Local
from treadle.treadle_exceptions import *
from treadle.macros import And

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

class AddExpression(unittest.TestCase):
    def test_Add(self):
        self.assertEqual(Add(Const(1), Const(2)).toFunc()(), 3)

class SubExpression(unittest.TestCase):
    def test_Sub(self):
        self.assertEqual(Subtract(Const(3), Const(2)).toFunc()(), 1)

class AndExpression(unittest.TestCase):
    def test_And(self):
        self.assertFalse(And(Const(0), Const(0), Const(0)).toFunc()())
        self.assertFalse(And(Const(1), Const(0), Const(0)).toFunc()())
        self.assertFalse(And(Const(0), Const(1), Const(0)).toFunc()())
        self.assertFalse(And(Const(0), Const(0), Const(1)).toFunc()())
        self.assertFalse(And(Const(0), Const(1), Const(1)).toFunc()())
        self.assertTrue(And(Const(1), Const(1), Const(1)).toFunc()())

class DoExpresion(unittest.TestCase):
    def test_Do(self):
        self.assertEqual(Do(Const(0), Const(1), Const(2)).toFunc()(), 2)
        self.assertEqual(Do(Const(0), Const(1)).toFunc()(), 1)
        self.assertEqual(Do(Const(0)).toFunc()(), 0)
        self.assertEqual(Do().toFunc()(), None)

    def test_Args(self):
        self.assertRaises(ExpressionRequiredException, Do, Const(False), 1)

class FuncTests(unittest.TestCase):
    def test_Func(self):
        self.assertEqual(Func([], Const(1)).toFunc()(), 1)

class ArgTests(unittest.TestCase):
    def test_Argument(self):
        a = Argument("a")
        self.assertEqual(Func([a], a).toFunc()(42), 42)

class StoreLocalTests(unittest.TestCase):
    def test_StoreLocal(self):
        a = Local("a")
        self.assertEqual(StoreLocal(a, Const(42)).toFunc()(), 42)



