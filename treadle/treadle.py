import dis
import types
import struct

from io import StringIO



for x in dis.opmap:
    globals()[x] = dis.opmap[x]



class AExpression(object):
    """defines a abstract expression subclass this to create new expressions"""
    def __init__(self):
        pass

    def toCode(self):
        size, max_seen = self.size(0, 0)
        if size != 1:
            raise Exception("Unbalanced stack")

        ctx = Context()
        self.emit(ctx)

        code = ctx.stream.getvalue()

        consts = None * len(ctx.consts)
        for k, v in ctx.consts.items():
            consts[v] = k.getConst()
        
        return NewCode(0, 0, size, 0, code, consts, [], [], "<string>", "foo", 0, {}, {}, {})

    def toFunc(self):
        c = self.toCode()
        return types.FunctionType(c, {})


class IAssignable(object):
    """defines an expression that can be on the left side of an assign expression"""
    pass



class Const(AExpression):
    """defines a constant that will generate a LOAD_CONST bytecode. Note: Const objects
       do no intern their constants, that is left to the language implementors"""
    def __init__(self, const):
        if isinstance(const, AExpression):
            raise Exception("Const cannot take an expression as an argument")

        self.value = const

    def emit(self, ctx):
        # find a location for the const
        if self not in ctx.consts:
            ctx.consts[self] = len(ctx.consts)
        idx = len(ctx.consts)

        data = struct.pack("BH", LOAD_CONST, idx)
        ctx.stream.write(data)

    def getConst(self):
        return self.value

    def size(self, current, max_seen):
        current += 1
        return current, max(current, max_seen)


class Context(object):
    """defines a compilation context this keeps track of locals, output streams, etc"""
    def __init__(self):
        self.stream = StringIO()
        self.consts = {}

    def writeByte(self):
        self.stream.write




def NewCode(co_argcount, co_nlocals, co_stacksize, co_flags,
            co_code, co_consts, co_names, co_varnames,
            filename, name, firstlineno, co_lnotab,
            co_freevars, co_cellvars):
    """wrapper for CodeType so that we can remember the synatax"""
    return types.CodeType(co_argcount, co_nlocals, co_stacksize,
                          co_flags, co_code, co_consts, co_names, co_varnames,
                          filename, name, firstlineno, co_lnotab,
                          co_freevars, co_cellvars)


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