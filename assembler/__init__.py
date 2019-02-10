import struct
import assembler.instructions

def patch(fw, base, instruction):
  for pc, inst in zip(range(base, base + len(instruction) * 4, 4), instruction):
    struct.pack_into('>I', fw, pc, (instructions.Instruction(*inst) if isinstance(inst, tuple) else inst).encode(pc))

def patch_raw(fw, base, data):
  fw[base:base+len(data)] = data
