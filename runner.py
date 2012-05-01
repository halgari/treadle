#from tests.expression_tests import *
#import unittest

#unittest.main()
from treadle.treadle import *
import sys


r = None
def Foo():
    r = 2
    return r

fb = Finally(Const(1), Call(Const(Foo))).toFunc()
import dis
#dis.dis(fb)
sys.stdout.flush()
print fb()