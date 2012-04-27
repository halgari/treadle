#from tests.expression_tests import *
#import unittest

#unittest.main()
from treadle.treadle import *


class T(object):
    def foo(self):
        return 42

z = Call(Attr(Const(T()), "foo")).toFunc()
dis.dis(z)
import sys
sys.stdout.flush()
sys.stderr.flush()
print(z())

