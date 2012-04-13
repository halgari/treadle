import dis
import types
import struct

from .treadle_exceptions import *
from .compat import version, newCode, SEEK_END, CondJump, AbsoluteJump

from io import BytesIO



for x in dis.opmap:
    globals()[x] = dis.opmap[x]



class AExpression(object):
    """defines a abstract expression subclass this to create new expressions"""
    def __init__(self):
        pass

    def toCode(self):

        expr = self

        if not isinstance(self, Return):
            expr = Return(self)

        size, max_seen = expr.size(0, 0)

        ctx = Context()


        expr.emit(ctx)

        code = ctx.stream.getvalue()
        if size != 0:
            raise UnbalancedStackException("Unbalanced stack")

        consts = [None] * (len(ctx.consts) + 1)
        for k, v in list(ctx.consts.items()):
            consts[v + 1] = k.getConst()
        consts = tuple(consts)
        print(repr(code))
        c = newCode(co_code = code, co_stacksize = size, co_consts = consts)
        import dis
        dis.dis(c)
        return c

    def toFunc(self):
        c = self.toCode()
        return types.FunctionType(c, {})


class IAssignable(object):
    """defines an expression that can be on the left side of an assign expression"""
    pass

class Return(AExpression):
    """defines an explicit 'return' in the code """
    def __init__(self, expr):
        if not isinstance(expr, AExpression):
            raise ExpressionRequiredException()

        self.expr = expr

    def emit(self, ctx):
        self.expr.emit(ctx)

        data = struct.pack("=B", RETURN_VALUE)
        ctx.stream.write(data)

    def size(self, current, max_seen):
        current, max_seen = self.expr.size(current, max_seen)
        return current - 1, max_seen

class Const(AExpression):
    """defines a constant that will generate a LOAD_CONST bytecode. Note: Const objects
       do no intern their constants, that is left to the language implementors"""
    def __init__(self, const):
        if isinstance(const, AExpression):
            raise ExpressionNotAllowedException()

        self.value = const

    def emit(self, ctx):
        # find a location for the const
        if self not in ctx.consts:
            ctx.consts[self] = len(ctx.consts)
        idx = len(ctx.consts)

        data = struct.pack("=BH", LOAD_CONST, idx)
        ctx.stream.write(data)

    def getConst(self):
        return self.value

    def size(self, current, max_seen):
        current += 1
        return current, max(current, max_seen)

class If(AExpression):
    def __init__(self, condition, thenexpr, elseexpr = None):
        if elseexpr == None:
            elseexpr = Const(None)

        self.exprs = [condition, thenexpr, elseexpr]

        for x in self.exprs:
            if not isinstance(x, AExpression):
                raise ExpressionRequiredException()

        self.condition = condition
        self.thenexpr = thenexpr
        self.elseexpr = elseexpr

    def size(self, current, max_seen):
        for x in self.exprs:
            _ , new_max = x.size(current, max_seen)
            max_seen = max(max_seen, new_max)

        return current + 1, max_seen

    def emit(self, ctx):
        self.condition.emit(ctx)

        elsejump = CondJump(ctx)



        self.thenexpr.emit(ctx)

        endofif = AbsoluteJump(ctx)

        elsejump.mark()

        self.elseexpr.emit(ctx)

        endofif.mark()


class ABinaryOp(AExpression):
    def __init__(self, a, b, op):
        self.a = a
        self.b = b
        self.op = op

    def size(self, current, max_seen):
        current, max_seen = self.a.size(current, max_seen)
        current, max_seen = self.b.size(current, max_seen)

        return current - 1, max_seen

    def emit(self, ctx):
        self.a.emit(ctx)
        self.b.emit(ctx)
        ctx.stream.write(struct.pack("=B", self.op))

class Add(ABinaryOp):
    def __init__(self, a, b):
        ABinaryOp.__init__(self, a, b, BINARY_ADD)

class Subtract(ABinaryOp):
    def __init__(self, a, b):
        ABinaryOp.__init__(self, a, b, BINARY_SUBTRACT)




class Context(object):
    """defines a compilation context this keeps track of locals, output streams, etc"""
    def __init__(self):
        self.stream = BytesIO()
        self.consts = {}






### Taken from byteplay.py

# Flags from code.h
CO_OPTIMIZED              = 0x0001      # use LOAD/STORE_FAST instead of _NAME
CO_NEWLOCALS              = 0x0002      # only cleared for module/exec code
CO_VARARGS                = 0x0004
CO_VARKEYWORDS            = 0x0008
CO_NESTED                 = 0x0010      # ???
CO_GENERATOR              = 0x0020
CO_NOFREE                 = 0x0040      # set if no free or cell vars
CO_GENERATOR_ALLOWED      = 0x1000      # unused
# The future flags are only used on code generation, so we can ignore them.
# (It does cause some warnings, though.)
CO_FUTURE_DIVISION        = 0x2000
CO_FUTURE_ABSOLUTE_IMPORT = 0x4000
CO_FUTURE_WITH_STATEMENT  = 0x8000


ConstTrue = Const(True)
ConstFalse = Const(False)