import platform, struct, dis
from io import SEEK_END
import types

version = "".join(platform.python_version_tuple()[:2])

for x in dis.opmap:
    globals()[x] = dis.opmap[x]


class _Jump_27(object):
    def __init__(self, ctx, bc):
        self.bc = bc
        self.loc = ctx.stream.tell()
        self.ctx = ctx
        ctx.stream.write(struct.pack("=BH", self.bc, 0xFFFF))
        self.jumpto = 0

    def mark(self):
        self.jumpto = self.ctx.stream.tell()
        self.ctx.stream.seek(self.loc)

        if self.bc == JUMP_ABSOLUTE or self.bc == POP_JUMP_IF_FALSE:
            self.ctx.stream.write(struct.pack("=BH", self.bc, self.jumpto))
        else:
            self.ctx.stream.write(struct.pack("=BH", self.bc, self.jumpto - self.loc))

        self.ctx.stream.seek(0, SEEK_END)

class _Jump_26(object):
    def __init__(self, ctx, bc):
        self.bc = bc
        self.loc = ctx.stream.tell()
        self.ctx = ctx
        ctx.stream.write(struct.pack("=BH", self.bc, 0xFFFF))
        self.jumpto = 0

    def mark(self):
        self.jumpto = self.ctx.stream.tell()
        self.ctx.stream.seek(self.loc)

        if self.bc == JUMP_ABSOLUTE or self.bc == POP_JUMP_IF_FALSE:
            self.ctx.stream.write(struct.pack("=BH", self.bc, self.jumpto))
        else:
            self.ctx.stream.write(struct.pack("=BH", self.bc, self.jumpto - self.loc))

        self.ctx.stream.seek(0, SEEK_END)



def newCode3(co_argcount = 0, co_nlocals = 0, co_stacksize = 0, co_flags = 0x0000,
            co_code = bytes(), co_consts = (), co_names = (), co_varnames = (),
            filename = "<string>", name = "", firstlineno = 0, co_lnotab = bytes(),
            co_freevars = (), co_cellvars = ()):
    """wrapper for CodeType so that we can remember the synatax"""
    return types.CodeType(co_argcount, 0, co_nlocals, co_stacksize,
        co_flags, co_code, co_consts, co_names, co_varnames,
        filename, name, firstlineno, co_lnotab, co_freevars, co_cellvars)

def newCode2(co_argcount = 0, co_nlocals = 0, co_stacksize = 0, co_flags = 0x0000,
             co_code = bytes(), co_consts = (), co_names = (), co_varnames = (),
             filename = "<string>", name = "", firstlineno = 0, co_lnotab = bytes(),
             co_freevars = (), co_cellvars = ()):
    """wrapper for CodeType so that we can remember the synatax"""
    return types.CodeType(co_argcount, co_nlocals, co_stacksize,
        co_flags, co_code, co_consts, co_names, co_varnames,
        filename, name, firstlineno, co_lnotab, co_freevars, co_cellvars)

if version == "26":
    _Jump = _Jump_26
else:
    _Jump = _Jump_27

if int(version) < 30:
    newCode = newCode2
else:
    newCode = newCode3
