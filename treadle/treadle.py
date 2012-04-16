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

        locals = {}
        argcount = 0

        if isinstance(self, Func):
            expr = self.expr

            for x in self.args:
                locals[x] = len(locals)

            argcount = len(self.args)


        if not isinstance(expr, Return):
            expr = Return(expr)



        size, max_seen = expr.size(0, 0)

        ctx = Context(locals)


        expr.emit(ctx)

        code = ctx.stream.getvalue()
        if size != 0:
            raise UnbalancedStackException("Unbalanced stack")

        consts = [None] * (len(ctx.consts) + 1)
        for k, v in list(ctx.consts.items()):
            consts[v + 1] = k.getConst()
        consts = tuple(consts)

        varnames = [None] * (len(ctx.varnames))
        for k, v in list(ctx.varnames.items()):
            varnames[v] = k.name
        varnames = tuple(varnames)

        print(repr(code))
        c = newCode(co_code = code, co_stacksize = size, co_consts = consts, co_varnames = varnames,
                    co_argcount = argcount)
        import dis
        dis.dis(c)
        return c

    def toFunc(self):
        c = self.toCode()
        return types.FunctionType(c, {})


class IAssignable(object):
    """defines an expression that can be on the left side of an assign expression"""


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

class StoreLocal(AExpression):
    def __init__(self, local, expr):
        self.local = local
        self.expr = expr
    def size(self, current, max_seen):
        current, max_seen = self.expr.size(current, max_seen)

        return current, max(max_seen, current + 1)

    def emit(self, ctx):
        if self.local not in ctx.varnames:
            ctx.varnames[self.local] = len(ctx.varnames)

        idx = ctx.varnames[self.local]

        self.expr.emit(ctx)

        ctx.stream.write(struct.pack("=BBH", DUP_TOP, STORE_FAST, idx))


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

class Do(AExpression):
    def __init__(self, *exprs):
        if not exprs:
            exprs = [Const(None)]

        for x in exprs:
            if not isinstance(x, AExpression):
                raise ExpressionRequiredException()
        self.exprs = exprs

    def size(self, current, max_seen):
        last = self.exprs[-1]
        for x in self.exprs:
            current, max_seen = x.size(current, max_seen)
            if last is not x:
                current -= 1

        return current, max_seen

    def emit(self, ctx):
        last = self.exprs[-1]
        for x in self.exprs:
            x.emit(ctx)
            if last is not x:
                ctx.stream.write(struct.pack("=B", POP_TOP))

class Local(AExpression, IAssignable):
    def __init__(self, name):
        self.name = name

    def size(self, current, max_count):
        current += 1
        return current, max(current, max_count)

    def emit(self, ctx):
        if self not in ctx.varnames:
            ctx.varnames[self] = len(self.varnames)

        idx = ctx.varnames[self]

        ctx.stream.write(struct.pack("=BH", LOAD_FAST, idx))

class Func(AExpression):
    def __init__(self, args, expr):
        for x in args:
            if not isinstance(x, Argument):
                raise ArgumentExpressionRequiredException()
        self.args = args
        self.expr = expr
        self.value = None

    def size(self, current, max_seen):
        current += 1
        return current, max(max_seen, current)

    def emit(self, ctx):
        if self.value is None:
            self.value = self.toFunc()

        if self not in ctx.consts:
            ctx.consts[self] = len(ctx.consts)

        idx = ctx.consts[self]

        ctx.stream.write(struct.pack("=BH", LOAD_CONST, idx))



class Argument(Local):
    def __init__(self, name):
        Local.__init__(self, name)




class Context(object):
    """defines a compilation context this keeps track of locals, output streams, etc"""
    def __init__(self, varnames = {}):
        self.stream = BytesIO()
        self.consts = {}
        self.varnames = varnames






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