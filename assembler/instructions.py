
JMP=0x00
CALL=0x01
JNC=0x03
JC=0x04
NOP=0x05
LH=0x06
RET=0x11
LW=0x21
LB=0x23
MOV=0x27
ADDI=0x27
ANDI=0x29
ORI=0x2A
XORI=0x2B
MULTI=0x2C
CMP=0x2F
SW=0x35

class EXT38:
  ADD=0x0
  OR=0x1
  SUB=0x2
  AND=0x3
  XOR=0x5
  MUL=0x6
  MOV=0x7
  SHL=0x8
  DIV=0x9
  MOV2=0xb
  MOVH=0xc

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

class JInstruction:
  opcode = None

  def __init__(self, opcode, address):
    self.opcode = opcode
    self.address = address

  def encode(self, pc):
    return ((self.opcode & 0x3F) << 26) | (int((self.address - pc) / 4) & 0x03FFFFFF)
