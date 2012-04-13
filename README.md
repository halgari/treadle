Treadle
=======

Introduction
------------

Chapman: Trouble at mill.

Cleveland: Oh no - what kind of trouble?

Chapman: One on't cross beams gone owt askew on treadle.

Cleveland: Pardon?

Chapman: One on't cross beams gone owt askew on treadle.

Cleveland: I don't understand what you're saying.

Chapman: [slightly irritatedly and with exaggeratedly clear accent] One of the cross beams has gone out askew on the treadle.

Cleveland: Well what on earth does that mean?

Chapman: *I* don't know - Mr Wentworth just told me to come in here and say that there was trouble at the mill, that's all - I didn't expect a kind of Spanish Inquisition.


-------------

Treadle is a library for easily building compilers and code generators in Python. Using trees of objects, we can easily construct functions. For example:

          import math
 
          a = Local("a")
          b = Local("b")
          expr = Call(Attr(Const(math), "sqrt"), 
                      Add(Mul(a, a), Mul(b, b)))
          expr.toFunc(a, b)