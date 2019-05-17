#!/usr/bin/env python3

import io


def pretty_bin(data, row_length=16):
  return '\n'.join(' '.join('{:02x}'.format(b) for b in data[o:o+row_length])
      for o in range(0, len(data), row_length))


class Decoder:
  def read_back_ref(self, length, t2=None):
    if t2: self.prev_back_ref = t2
    else: t2 = self.prev_back_ref
    assert(t2)

    def back_ref_iter(t2, length):
      o = base_offset = len(self.data) - (t2 >> 1) - 1
      for i in range(length):
        yield self.data[o]
        o = o + 1 if o < len(self.data) - 1 else base_offset

    print('back_ref t2 = {:02x}'.format(t2))
    #assert(t2 & ~0x7E == 0)

    # What is t2[0] ?
    return [x for x in back_ref_iter(t2, length)]

  def decode(self, smaz):
    self.smaz = io.BytesIO(smaz)
    self.data = bytearray()

    prev_back_ref_t2 = None

    while True:
      off = self.smaz.tell()
      t = int(self.smaz.read(1)[0])

      try:
        description = chunk_descriptions[t]
      except KeyError:
        raise RuntimeError('Unknown chunk type 0x{:02x}\n\nPreceding bytes:\n{}'.format(
            t, pretty_bin(self.data)))

      decoded = sum((verb.decode(self) for verb in description), [])
      print('{: 4x}: {:02x} -> {}'.format(off, t, pretty_bin(decoded)))
      self.data.extend(decoded)

    return self.data


class T:
  def __init__(self, repeat=1):
    self.repeat = repeat

  @property
  def src_len(self): return 0

  def decode(self, decoder):
    return [decoder.data[-1]] * self.repeat


class L:
  def __init__(self, repeat=1):
    self.repeat = repeat

  @property
  def src_len(self): return 1

  def decode(self, decoder):
    return [decoder.smaz.read(1)[0]] * self.repeat


class B:
  def __init__(self, length):
    self.length = length

  @property
  def src_len(self): return 1

  def decode(self, decoder):
    return decoder.read_back_ref(self.length, decoder.smaz.read(1)[0])


class R:
  def __init__(self, length):
    self.length = length

  @property
  def src_len(self): return 0

  def decode(self, decoder):
    return decoder.read_back_ref(self.length)


class V:
  def __init__(self, length):
    self.length = length

  @property
  def src_len(self): return 1

  def decode(self, decoder):
    return decoder.read_back_ref(decoder.smaz.read(1) >> 1)


chunk_descriptions = {
  0x07: [T(15), L()],
  0x0b: [T(6), B(3)],
  0x0c: [T(6), L(4)],
  0x0d: [T(6), L()],
  # 0x20 - lots of repetition
  # 0x21 - lots of repetition
  0x23: [R(6), L()], # Or T(6) after fe? 
  # 0x24 - lots of repetition
  # 0x25 - lots of repetition
  0x27: [R(7), L()], # Or T(7) after fe?
  0x2b: [R(4), L(), L()],
  0x2f: [R(5), L(), L()],
  #0x31:
    # Extended back reference - what controls the length?
    #  B(10) L() L()
  # 0x33 - lots of repetition
  #0x33:
    # Extended back-ref 2-bytes?
    #B(2) L() L()
  0x37: [R(2), L(), L(), L()],
  #0x39:
    # Extended back reference - what controls the length?
    #B(11) L() L()
  #0x3b:
    # Extended back-ref 2-bytes?
    #B(3) L() L()
  0x3f: [R(3), L(), L(), L()],
  0x47: [T(6), L(), L()],
  0x4f: [T(6), L(), L()],
  0x57: [T(4), L(), L(), L()],
  0x5f: [T(5), L(), L(), L()],
  #0x60: [  # Back reference from first byte of length defined by second byte! + two literals!
  0x61: [B(8)],
  #0x62: [  # Back reference from first byte of length defined by second byte! + two literals!
  0x63: [B(9)],
  0x66: [T(2), B(2)], # after not ff
  0x67: [B(6), L(), L()], # after not ff. Previously: [T(2), B(3)
  # 0x68: [lots of repetition
  # 0x6a: [lots of repetition
  0x69: [B(10)], # Confirmed
  0x6b: [B(11)], # Confirmed
  0x6f: [B(7), L(), L()], # Previously: [T(2), L(), L(), L(), L()
  #0x71: [# Back reference from first byte of length defined by second byte! - CHECK THIS ONE with 71 05 03
  # 71 09 07 05 03
  0x76: [T(3), B(2)], # after not ff
  0x77: [B(4), L(), L(), L()], # after not ff, previously T(3), B(3)
  #0x79: [# Back reference from first byte of length defined by second byte! - CHECK THIS ONE with 71 05 03
  #  79 09 07 05 03
  0x7f: [B(5), L(), L(), L()], # previously T(3), L(), L(), L(), L()
  #0x90:
    #L()
    # Long back reference defined by... what? 90 05 03
    #assert(False)
    #L(), B(3), L(), L()
  0x91: [L(), R(6)], # Confirmed
  0x92: [L(), V(52)],
  0x93: [L(), R(7)], # Confirmed
  0x94: [L(7)],
  0x95: [L(), R(4), L()],
  0x96: [L(8)],
  0x97: [L(), R(5), L()],
  0x9a: [L(3), L()],
  0x9b: [L(), R(2), L(), L()],
  0x9e: [L(4), L()],
  0x9f: [L(), R(3), L(), L()],
  #0xb0: [ # is this right? - NO!
  #  L(), B(4)],
  0xb3: [L(), B(6), L()],
  0xb7: [L(), B(7), L()],
  0xbb: [L(), B(4), L(), L()],
  0xbf: [L(), B(5), L(), L()],
  0xc6: [ # after not ff
    B(4)],
  0xc7: [ # after not ff
    B(5)],
  0xc8: [ # big long repetition spotted
    L(), L(7)],
  0xc9: [ # big long repetition spotted
    L(), L(8)],
  0xca: [ # formerly observed as L(5) ??
    L(), L(), R(4)],
  0xcb: [L(), L(), R(5)],
  0xcc: [L(), L(3)],
  #0xcd:
    # formerly
    #B(2), B(2), L()],
    # also found: [L(), L(), R(2), L()
  0xce: [L(), L(4)],
  0xcf: [B(2), B(3), L()],
  0xd6: [B(2), B(1), B(2)],
  0xd7: [B(2), B(1), B(3)],
  0xd8: [L(), L(), B(0), V(36)],
  # 0xda
    # L()
    # L()
    # Extended back-ref?
    # L()
  #0xdb: [ # is this right?
  #  L(), L(), B(2), L(), L()],
  0xdd: [L(), L(), B(4), L()],
  0xdf: [B(2), L(), L(), L(), L(), L()], # Confirmed
    # Was going to comment this out... when I found above:
    # df 09 07 05 03: [L(), L(), B(5), L()
  0xe4: [L(), L(), L(), V(20)],
  0xe6: [L(), L(), L(), R(2)], # after not ff #formerly B(5)
  0xe7: [B(6)], # after not ff
  0xed: [B(3), B(2), L()], # confirmed
  0xee: [L(), L(), L(), B(4)],
  #0xef:
    #formerly B(3), B(3), L()
  #  L(), L(), L(), B(5)
  0xf6: [B(3), L(), B(2)],
  0xf7: [B(3), L(), B(3)],
  0xf9: [L(), L(), L(), L(), L(5)],
  # 0xfb - 6 literals, back reference
  0xfe: [L(), L(), L(), L(), L(), L(), L()],
  0xff: [L(), L(), L(), L(), L(), L(), L(), L()]
}

def decode(smaz):
  return Decoder().decode(smaz)
