
JMP=0x00
CALL=0x01
J_=0x03
JG=0x04
NOP=0x05
LH=0x06
RET=0x11
LW=0x21
MOV=0x27
LA=0x2A
CMP=0x2F
SW=0x35

class Instruction:
  word = None

  def encode(self, pc):
    return self.word

  def __init__(self, opcode, *k):
    if len(k) == 1:
      offset = k[0]
      self.word = ((opcode & 0x3F) << 26) | (offset & 0x03FFFFFF)
    elif len(k) == 3:
      dest, src, offset = tuple(k)
      self.word = ((opcode & 0x3F) << 26) | ((dest & 0x1F) << 21) | \
          ((src & 0x1F) << 16) | (offset & 0xFFFF)
    elif len(k) == 4:
      dest, src, base, offset = tuple(k)
      self.word = ((opcode & 0x3F) << 26) | ((dest & 0x1F) << 21) | \
          ((src & 0x1F) << 16) | ((base & 0x1F) << 11) | (offset & 0x7FF)
    else:
      assert(False)
