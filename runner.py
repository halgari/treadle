#from tests.expression_tests import *
#import unittest

#unittest.main()
from treadle.treadle import *

def foo(a):
  while a != 10:
    a = a + 1
  return a

dis.dis(foo)

accum = Argument("a")
f = Func([accum],
If(NotEqual(accum, Const(10)), Recur(Add(accum, Const(1))), accum))

z = f.toFunc()
dis.dis(z)
import sys
sys.stdout.flush()
sys.stderr.flush()
print z(1)

