import platform, struct, dis
from io import SEEK_END

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


if version == "26":
    _Jump = _Jump_26
else:
    _Jump = _Jump_27

