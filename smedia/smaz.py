#!/usr/bin/env python3

import io


def pretty_bin(data, row_length=16):
  return '\n'.join(' '.join('{:02x}'.format(b) for b in data[o:o+row_length])
      for o in range(0, len(data), row_length))


class A:
  def __init__(self, length):
    self.length = length

  def decode(self, decoder):
    decoder.write([x for x in decoder.back_ref_iter(decoder.prev_back_ref_offset, self.length)])

class T:
  def __init__(self, repeat=1):
    self.repeat = repeat

  @property
  def src_len(self): return 0

  def decode(self, decoder):
    decoder.write([decoder.data[-1]] * self.repeat)


class L:
  def __init__(self, repeat=1):
    self.repeat = repeat

  @property
  def src_len(self): return 1

  def decode(self, decoder):
    decoder.write([decoder.smaz.read(1)[0]] * self.repeat)


class B:
  def __init__(self, length):
    self.length = length

  @property
  def src_len(self): return 1

  def decode(self, decoder):
    decoder.read_back_ref(self.length)


# Is this what Bs were all along?
class C:
  def __init__(self, *verbs):
    self.verbs = verbs

  def decode(self, decoder):
    t2 = decoder.smaz.read(1)[0]
    decoder.prev_back_ref_offset = (t2 >> 1) + 1
    for verb in self.verbs[t2 & 0x01]:
      verb.decode(decoder)

class E:
  def __init__(self, t):
    self.type = t
    pass

  def decode(self, decoder):
    if self.type == 'A':
      decoder.read_ext_a_back_ref()
    elif self.type == 'B':
      decoder.read_ext_b_back_ref()


class R:
  def __init__(self, offset, length):
    self.offset = offset
    self.length = length

  @property
  def src_len(self): return 0

  def decode(self, decoder):
    decoder.write([x for x in decoder.back_ref_iter(self.offset, self.length)])


class V:
  def __init__(self, length):
    self.length = length

  @property
  def src_len(self): return 1

  def decode(self, decoder):
    decoder.read_back_ref(decoder.smaz.read(1)[0] >> 1)


chunk_descriptions = {
  #0x07: [T(15), L()],
  #0x0b: [T(6), B(3)],
  #0x0c: [T(6), L(4)],
  #0x0d: [T(6), L()],
  # 0x20 - lots of repetition
  # 0x21 - lots of repetition
  0x23: [R(4, 6), L()],
  # 0x24 - lots of repetition
  # 0x25 - lots of repetition
  0x27: [R(4, 7), L()],
  0x2b: [R(4, 4), L(), L()],
  0x2f: [R(4, 5), L(), L()],
  #0x31:
    # Extended back reference - what controls the length?
    #  B(10) L() L()
  # 0x33 - lots of repetition
  #0x33:
    # Extended back-ref 2-bytes?
    #B(2) L() L()
  0x37: [R(4, 2), L(), L(), L()],
  #0x39:
    # Extended back reference - what controls the length?
    #B(11) L() L()
  #0x3b:
    # Extended back-ref 2-bytes?
    #B(3) L() L()
  0x3f: [R(4, 3), L(), L(), L()],
  0x41: [T(8)],
  0x43: [T(9)],
  0x47: [T(6), L(), L()],
  0x49: [T(10)],
  0x4b: [T(11)],
  0x4f: [T(7), L(), L()],
  #0x4f: [T(6), L(), L()],
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
  0x6f: [T(2), L(), L(), L(), L()], #0x6f: [B(7), L(), L()], # Previously: [T(2), L(), L(), L(), L()
  #0x71: [# Back reference from first byte of length defined by second byte! - CHECK THIS ONE with 71 05 03
  # 71 09 07 05 03
  0x76: [T(3), B(2)], # after not ff
  0x77: [B(4), L(), L(), L()], # after not ff, previously T(3), B(3)
  #0x79: [# Back reference from first byte of length defined by second byte! - CHECK THIS ONE with 71 05 03
  #  79 09 07 05 03
  #0x7f: [B(5), L(), L(), L()], # previously T(3), L(), L(), L(), L()
  0x7f: [L(), L(), L(), L(), L(), L(), L()],
  #0x7f: [T(3), L(), L(), L()], # Check this one... 766 - what happes if a literal does not precede this?
  #0x90:
    #L()
    # Long back reference defined by... what? 90 05 03
    #assert(False)
    #L(), B(3), L(), L()
  0x91: [L(), R(4, 6)], # Confirmed
  0x92: [L(), V(52)],
  0x93: [L(), R(4, 7)], # Confirmed
  0x94: [L(7)],
  0x95: [L(), R(4, 4), L()],
  0x96: [L(8)],
  0x97: [L(), R(4, 5), L()],
  0x9a: [L(3), L()],
  0x9b: [L(), R(4, 2), L(), L()],
  0x9e: [L(4), L()],
  0x9f: [L(), R(4, 3), L(), L()],
  0xb0: [L(), E('A')],
  0xb3: [L(), B(6), L()],
  0xb7: [L(), B(7), L()],
  0xbb: [L(), B(4), L(), L()],
  0xbf: [L(), B(5), L(), L()],
  0xc6: [ # after not ff
    B(4)],
  0xc7: [B(5)],
  0xc8: [ # big long repetition spotted
    L(), L(7)],
  0xc9: [ # big long repetition spotted
    L(), L(8)],
  0xca: [ # formerly observed as L(5) ??
    L(), L(), R(4, 4)],
  0xcb: [L(), L(), R(4, 5)],
  0xcc: [L(), L(3)],
  0xcd: [L(), L(), R(4, 2), L()],
      # also found: [B(2), B(2), L()],
  0xce: [L(), L(4)],
  0xcf: [L(), L(), R(4, 3), L()],
      # also found: [B(2), B(3), L()],
  0xd6: [B(2), L(), B(2)], #0xd6: [B(2), B(1), B(2)],
  0xd7: [B(2), L(), B(3)], #[B(2), B(1), B(3)],

  0xd8: [L(), L(), E('B')],
  0xd9: [L(), L(), B(6)],
      # also found: [B(2), L(), L()],
  # 0xda
    # L()
    # L()
    # Extended back-ref?
    # L()
  0xdb: [L(), L(), C([A(2), L(), L()], [A(7)])],
  0xdd: [L(), L(), B(4), L()],
  0xdf: [B(2), L(), L(), L(), L(), L()], # Confirmed
    #[L(), L(), B(5), L()],
    # Was going to comment this out... when I found above:
    # df 09 07 05 03: [L(), L(), B(5), L()
  0xe4: [L(), L(), L(), V(20)],
  0xe6: [L(), L(), L(), A(2)],
    # previously: [B(5)],
  0xe7: [L(), L(), L(), A(3)],
    # previously: [B(6)],
  0xed: [L(), L(), L(), C([A(2), L()], [])],
    #0xed: [B(3), B(2), L()],
  0xee: [L(), L(), L(), B(4)],
  0xef: [B(3), B(3), L()],
  #0xef:
    #formerly B(3), B(3), L()
  #  L(), L(), L(), B(5)
 #0xf2: [L(), L(), L(), L()],
  0xf6: [L(), L(), L(), L(), B(2)],
    #previously: [B(3), L(), B(2)],
  0xf7: [L(), L(), L(), L(), B(3)],
    #previously: [B(3), L(), B(3)],
  0xf9: [L(), L(), L(), L(), L(5)],
  0xfb: [L(), L(), L(), L(), L(), B(2)],
  0xfc: [L(), L(), L(), L(), L(), L()],
  0xfe: [L(), L(), L(), L(), L(), L(), L()],
  0xff: [L(), L(), L(), L(), L(), L(), L(), L()]
}

class Decoder:
  prev_back_ref_offset = 1

  def write(self, data):
    self.data.extend(data)

  def back_ref_iter(self, offset, length):
    o = base_offset = len(self.data) - offset
    for i in range(length):
      yield self.data[o]
      o = o + 1 if o < len(self.data) - 1 else base_offset

  def read_back_ref(self, length, t2=None):
    t2 = self.smaz.read(1)[0]
    if t2 & 1 == 1:
      print('Unexpected B.t2 bits set!: {:02x}'.format(t2))
    self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, length)])

  def read_ext_a_back_ref(self):
    t2, t3 = self.smaz.read(2)

    print('E.t2 = {:02x}, E.t3 = {:02x}'.format(t2, t3))

    lut = {0x03: 36, 0x07: 37, 0x13: 38, 0x17: 39, 0x43: 40, 0x47: 41, 0x53: 42, 0x57: 43,
        0x95: 12, 0x97: 13}
    if t3 in lut.keys():
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, lut[t3])])
      self.write(self.smaz.read(1))
      return

    lut = {0x26: 14, 0x27: 15, 0x66: 15, 0x67: 16, 0x91: 14, 0x93: 15}
    if t3 in lut.keys():
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, lut[t3])])

    lut = {0x2e: 4, 0x2f: 5}
    if t3 in lut.keys():
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, 12)])
      t4 = self.smaz.read(1)[0]
      if t4 & 1 == 0:
        self.write([x for x in self.back_ref_iter((t4 >> 1) + 1, 3)])
        self.write(self.smaz.read(1))
      else:
        self.write([x for x in self.back_ref_iter((t4 >> 1) + 1, lut[t3])])
      return

    '''
    lut = {0x2f: 4}
    if t3 in lut.keys():
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, 12)])
      self.write(self.smaz.read(1))
      return
    '''

    lut = {0x6e: 4, 0x6f: 5}
    if t3 in lut.keys():
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, 13)])
      t4 = self.smaz.read(1)[0]
      self.write([x for x in self.back_ref_iter((t4 >> 1) + 1, lut[t3])])
      return

    lut = {0xca: 13, 0xcb: 14}
    if t3 in lut:
      sequence = [x for x in self.back_ref_iter((t2 >> 1) + 1, lut[t3])]
      sequence[8] = self.smaz.read(1)[0]
      self.write(sequence)
      return


  def read_ext_b_back_ref(self):
    t2, t3 = self.smaz.read(2)

    print('E.t2 = {:02x}, E.t3 = {:02x}'.format(t2, t3))

    if t2 & 1 == 0:
      raise RuntimeError(
          'Unexpected E.t2 bits unset!: {:02x}'.format(t2))

    def e_back_ref(arg, length):
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, length1)])
      if arg & 0x01 == 0:
        print("arg is even: {:02x}")

    lut = {0x4a: 12, 0x4b: 13, 0xca: 13, 0xcb: 14}
    if t3 in lut.keys():
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, lut[t3])])
      return

    # 0x00, 0x02, 0x08, 0x0a, 0x20, 0x22, 0x28, 0x2a, 0x80, 0x82, 0x88, 0x8a, 0x00, 0x02, 0x08, 0x0a
    if (t3 & 0x55) == 0x00:
      length1 = 132 + (((t3 & 0x80) >> 4) + ((t3 & 0x20) >> 3) +
          ((t3 & 0x08) >> 2) + ((t3 & 0x02) >> 1)) * 4
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, length1)])

      # Someth odd  here - is this a cmd?
      t4 = self.smaz.read(1)[0]
      print('t4 = {:02x}'.format(t4))
      self.write(self.smaz.read(1))

      self.write([x for x in self.back_ref_iter((self.smaz.read(1)[0] >> 1) + 1, 3)])

      t7 = self.smaz.read(1)[0]
      self.write(self.smaz.read(1))

      self.write([x for x in self.back_ref_iter((t7 >> 1) + 1, 3)])
      self.write(self.smaz.read(1))
      
      return

    # 0x01, 0x03, 0x09, 0x0b, 0x21, 0x23, 0x29, 0x2b, 0x81, 0x83, 0x89, 0x8b, 0x01, 0x03, 0x09, 0x0b
    if (t3 & 0x55) == 0x01:
      length1 = 36 + (((t3 & 0x80) >> 4) + ((t3 & 0x20) >> 3) +
          ((t3 & 0x08) >> 2) + ((t3 & 0x02) >> 1))
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, length1)])
      return

    # 0x07, 0x0f, 0x27, 0x2f, 0x87, 0x8f, 0xa7, 0xaf
    if (t3 & 0x57) == 0x07:
      length1 = 20 + (((t3 & 0x80) >> 5) + ((t3 & 0x20) >> 4) + ((t3 & 0x08) >> 3))
      print('length1 = {}, t2 = {:02x}'.format(length1, t2))
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, length1)])
      self.write(self.smaz.read(2))
      return

    # 0x1f, 0x3f, 0x9f, 0xbf
    if (t3 & 0x5f) == 0x1f:
      length1 = 12 + (((t3 & 0x80) >> 6) + ((t3 & 0x20) >> 5))
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, length1)])
      self.write(self.smaz.read(4))
      return

    lut = {0x2d: 12}
    if t3 in lut:
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, lut[t3])])
      t4 = self.smaz.read(1)[0]
      self.write([x for x in self.back_ref_iter((t4 >> 1) + 1, 2)])
      self.write(self.smaz.read(1))
      return

    lut = {0x13: 16, 0x33: 17, 0x93: 18, 0xb3: 19}
    if t3 in lut:
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, lut[t3])])
      t4 = self.smaz.read(1)[0] # !!! this is dodgy - 7-length t3 = 0x13
      print('t4 = {:02x}'.format(t4))
      self.write(self.smaz.read(2))
      return

    lut = {0x4d: 10, 0x4f: 11, 0xcd: 11, 0xcf: 12}
    if t3 in lut:
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, lut[t3])])
      self.write(self.smaz.read(1))
      return

    lut = {0x59: 6, 0x5b: 7}
    if t3 in lut:
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, 8)])
      t4 = self.smaz.read(1)[0]
      print("t4 = {:02x}".format(t4))
      self.write([x for x in self.back_ref_iter((t4 >> 1) + 1, lut[t3])])
      return

    lut = {0x5d: 4, 0x5f: 5}
    if t3 in lut:
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, 8)])
      t4 = self.smaz.read(1)[0]
      self.write([x for x in self.back_ref_iter((t4 >> 1) + 1, lut[t3])])
      self.write(self.smaz.read(1))
      return

    lut = {0x66: 11, 0x67: 12}
    if t3 in lut:
      sequence = [x for x in self.back_ref_iter((t2 >> 1) + 1, lut[t3])]
      sequence[8] = self.smaz.read(1)[0]
      self.write(sequence)
      return

    lut = {0x6d: 2, 0x6f: 3}
    if t3 in lut:
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, 8)])
      self.write(self.smaz.read(1))
      t4 = self.smaz.read(1)[0]
      self.write([x for x in self.back_ref_iter((t4 >> 1) + 1, lut[t3])])
      self.write(self.smaz.read(1))
      return

    lut = {0x76: 8, 0xf6: 9}
    if t3 in lut:
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, lut[t3])])
      self.write(self.smaz.read(2))
      t4 = self.smaz.read(1)[0]
      self.write([x for x in self.back_ref_iter((t4 >> 1) + 1, 2)])
      return

    lut = {0x77: 8, 0xf7: 9}
    if t3 in lut:
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, lut[t3])])
      self.write(self.smaz.read(2))
      t4 = self.smaz.read(1)[0]
      self.write([x for x in self.back_ref_iter((t4 >> 1) + 1, 3)])
      return

    lut = {0x79: 8, 0xf9: 9}
    if t3 in lut:
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, lut[t3])])
      self.write(self.smaz.read(3))
      t4 = self.smaz.read(1)[0]
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, 6)])
      self.write(self.smaz.read(1))
      return

    lut = {0xd9: 6, 0xdb: 7}
    if t3 in lut:
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, 9)])
      t4 = self.smaz.read(1)[0]
      self.write([x for x in self.back_ref_iter((t4 >> 1) + 1, lut[t3])])
      return

    lut = {0xdd: 4, 0xdf: 5}
    if t3 in lut:
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, 9)])
      t4 = self.smaz.read(1)[0]
      self.write([x for x in self.back_ref_iter((t4 >> 1) + 1, lut[t3])])
      self.write(self.smaz.read(1))
      return

    lut = {0xe6: 12, 0xe7: 13}
    if t3 in lut:
      sequence = [x for x in self.back_ref_iter((t2 >> 1) + 1, lut[t3])]
      sequence[9] = self.smaz.read(1)[0]
      self.write(sequence)
      return

    lut = {0xed: 2, 0xef: 3}
    if t3 in lut:
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, 9)])
      self.write(self.smaz.read(1))
      t4 = self.smaz.read(1)[0]
      self.write([x for x in self.back_ref_iter((t4 >> 1) + 1, lut[t3])])
      self.write(self.smaz.read(1))
      return

    elif t3 in {0x7f, 0xff}:
      length1 = {0x7f: 8, 0xff: 9}[t3]
      self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, length1)])

      self.write(self.smaz.read(6))
      return

    print("Unknown E cmd")
    assert(False)

    '''
    # mutate-t2-bit-set-extended-ref-b1-0.msgpack
    elif t3 in {0xcb}:
      length1 = 14
    elif t3 in {0x9b}:
      length1 = 10
    elif t3 in {0x9f}:
      length1 = 11
    elif t3 in {0x2d, 0x2f, 0xca}:
      length1 = 12 
    elif t3 in {0x6d, 0x6f}:
      length1 = 13

    # test-d8-3rd-byte.msgpack
    elif t3 in {0x7f}:
      length1 = 4
    elif t3 in {0xff}:
      length1 = 9
    else:
      print('Unknown length1 from E.t3: {:02x}'.format(t3))
      length1 = 12

    self.write([x for x in self.back_ref_iter((t2 >> 1) + 1, length1)])

    if t3 in {0xca, 0xcb}:
      self.write(self.smaz.read(1))
    elif t3 in {0x9b, 0x9f}:
      self.write(self.smaz.read(2))
    elif t3 in {0x00, 0x02, 0x08, 0x0a, 0x20, 0x22, 0x28, 0x2a}:
      # test-d8-3rd-byte
      t4 = self.smaz.read(1)[0]

      self.write(self.smaz.read(1))
      weird_length = self.smaz.read(1)[0] >> 1
      self.write([x for x in self.back_ref_iter((t4 >> 1) + 1, weird_length)])
      
    else:
      t4 = self.smaz.read(1)[0]
      print('E.t4 = {:02x}'.format(t4))

      if t4 & 1 == 0:
        # mutate-t2-bit-set-extended-ref-b2-0.msgpack 
        if t3 in {0x2d, 0x6d}:
          weird_length = 2
        elif t3 in {0x2f, 0x6f}:
          weird_length = 3
        else:
          weird_length = 3
          print('Unknown weird_length from E.t3: {:02x}'.format(t3))

        self.write([x for x in self.back_ref_iter((t4 >> 1) + 1, weird_length)])
        self.write(self.smaz.read(1))
      else:
        # extended-back-ref-0.msgpack
        weird_length = 5
        self.write([x for x in self.back_ref_iter((t4 >> 1) + 1, weird_length)])
    '''

  def decode(self, smaz):
    self.smaz = io.BytesIO(smaz)
    self.data = bytearray()

    while self.decode_chunk(chunk_descriptions):
      pass

    return self.data

  def decode_chunk(self, descriptions):
    off = self.smaz.tell()
    t = self.smaz.read(1)
    if t == None or len(t) != 1:
      return False
    t = int(t[0])

    try:
      description = descriptions[t]
    except KeyError:
      raise RuntimeError('Unknown chunk type 0x{:02x}\n\nPreceding bytes:\n{}'.format(
          t, pretty_bin(self.data)))

    for verb in description:
      verb.decode(self)

    return True


def decode(smaz):
  return Decoder().decode(smaz)
