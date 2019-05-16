#!/usr/bin/env python3

def decode(smaz):
  d = []
  off = 0
  prev_back_ref_t2 = None

  def put_back_ref(length, t2):
    def back_ref_iter(t2, length):
      o = base_offset = len(d) - (t2 >> 1) - 1
      for i in range(length):
        yield d[o]
        o = o + 1 if o < len(d) - 1 else base_offset

    print('back_ref t2 = {:02x}'.format(t2))
    #assert(t2 & ~0x7E == 0)

    # What is t2[0] ?
    d.extend([x for x in back_ref_iter(t2, length)])

  def T(repeat=1):
    d.extend([d[-1]] * repeat)

  def L(repeat=1):
    nonlocal off
    d.extend([smaz[off]] * repeat)
    off += 1

  def B(length):
    nonlocal off
    nonlocal prev_back_ref_t2
    prev_back_ref_t2 = smaz[off]
    off += 1
    put_back_ref(length, prev_back_ref_t2)

  def R(length):
    nonlocal prev_back_ref_t2
    put_back_ref(length, prev_back_ref_t2)

  def V(length):
    nonlocal off
    nonlocal prev_back_ref_t2
    length += (smaz[off] >> 1)
    off += 1
    put_back_ref(length, prev_back_ref_t2)

  def back_ref2(length, t2):
    t2, t3, t4 = smaz[off:off+3]
    off += 3

    def back_ref_iter(t2, length):
      o = base_offset = len(d) - (t2 >> 1) - 1
      for i in range(length):
        yield d[o]
        o = o + 1 if o < len(d) - 1 else base_offset

    print('back_ref t2 = {:02x}'.format(t2))
    assert(t2 & ~0x7E == 0)
    assert(t4 & 0x01)

    # What is t2[0] ?
    d.extend([x for x in back_ref_iter(t2, length)])

  while off < len(smaz):
    t = int(smaz[off])
    print('{: 4x}: {:02x}'.format(off, t))
    off += 1
    if t == 0x07:
      T(15)
      L()
    elif t == 0x0b:
      T(6)
      B(3)
    elif t == 0x0c:
      T(6)
      L(4)
    elif t == 0x0d:
      T(6)
      L()
    # 0x20 - lots of repetition
    # 0x21 - lots of repetition
    elif t == 0x23:
      R(6) # Or T(6) after fe?
      L()
    # 0x24 - lots of repetition
    # 0x25 - lots of repetition
    elif t == 0x27:
      R(7) # Or T(7) after fe?
      L()
    elif t == 0x2b:
      R(4)
      L()
      L()
    elif t == 0x2f:
      R(5)
      L()
      L()
    elif t == 0x31:
      # Extended back reference - what controls the length?
      B(10)
      L()
      L()
      assert(False)
    # 0x33 - lots of repetition
    elif t == 0x33:
      B(2)
      # Extended back-ref 2-bytes?
      L()
      L()
      assert(False)
    elif t == 0x37:
      R(2)
      L()
      L()
      L()
    elif t == 0x39:
      # Extended back reference - what controls the length?
      B(11)
      L()
      L()
      assert(False)
    elif t == 0x3b:
      B(3)
      # Extended back-ref 2-bytes?
      L()
      L()
    elif t == 0x3f:
      R(3)
      L()
      L()
      L()
    elif t == 0x47:
      T(6)
      L()
      L()
    elif t == 0x4f:
      T(6)
      L()
      L()
    elif t == 0x57:
      T(4)
      L()
      L()
      L()
    elif t == 0x5f:
      T(5)
      L()
      L()
      L()
    #elif t == 0x60:   # Back reference from first byte of length defined by second byte! + two literals!
    elif t == 0x61:
      B(8)
    #elif t == 0x62:   # Back reference from first byte of length defined by second byte! + two literals!
    elif t == 0x63:
      B(9)
    elif t == 0x66:  # after not ff
      T(2)
      B(2)
    elif t == 0x67:  # after not ff
      B(6)
      L()
      L()
      # Previously: T(2) B(3)
    # 0x68: lots of repetition
    # 0x6a: lots of repetition
    elif t == 0x69:  # Confirmed
      B(10)
    elif t == 0x6b:  # Confirmed
      B(11)
    elif t == 0x6f:
      B(7)
      L()
      L()
      # Previously: T(2) L() L() L() L()
    #elif t == 0x71: # Back reference from first byte of length defined by second byte! - CHECK THIS ONE with 71 05 03
    # 71 09 07 05 03
    elif t == 0x76:  # after not ff
      T(3)
      B(2)
    elif t == 0x77:  # after not ff
      B(4)
      L()
      L()
      L()
      # previously T(3) B(3)
    #elif t == 0x79: # Back reference from first byte of length defined by second byte! - CHECK THIS ONE with 71 05 03
    #  79 09 07 05 03
    elif t == 0x7f:
      B(5)
      L()
      L()
      L()
      # previously T(3) L() L() L() L()
    elif t == 0x90:
      #L()
      # Long back reference defined by... what? 90 05 03
      #assert(False)
      L()
      B(3)
      L()
      L()
    elif t == 0x91:  # Confirmed
      L()
      R(6)
    elif t == 0x92:
      L()
      V(52)
    elif t == 0x93:  # Confirmed
      L()
      R(7)
    elif t == 0x94:
      L(7)
    elif t == 0x95:
      L()
      R(4)
      L()
    elif t == 0x96:
      L(8)
    elif t == 0x97:
      L()
      R(5)
      L()
    elif t == 0x9a:
      L(3)
      L()
    elif t == 0x9b:
      L()
      R(2)
      L()
      L()
    elif t == 0x9e:
      L(4)
      L()
    elif t == 0x9f:
      L()
      R(3)
      L()
      L()
    elif t == 0xb0:  # is this right? - NO!
      L()
      B(4)
    elif t == 0xb3:
      L()
      B(6)
      L()
    elif t == 0xb7:
      L()
      B(7)
      L()
    elif t == 0xbb:
      L()
      B(4)
      L()
      L()
    elif t == 0xbf:
      L()
      B(5)
      L()
      L()
    elif t == 0xc6:  # after not ff
      B(4)
    elif t == 0xc7:  # after not ff
      B(5)
    elif t == 0xc8:  # big long repetition spotted
      L()
      L(7)
    elif t == 0xc9:  # big long repetition spotted
      L()
      L(8)
    elif t == 0xca:  # formerly observed as L(5) ??
      L()
      L()
      R(4)
    elif t == 0xcb:
      L()
      L()
      R(5)
    elif t == 0xcc:
      L()
      L(3)
    elif t == 0xcd:
      # formerly
      B(2)
      B(2)
      L()
      # also found: L() L() R(2) L()
    elif t == 0xce:
      L()
      L(4)
    elif t == 0xcf:
      B(2)
      B(3)
      L()
    elif t == 0xd6:
      B(2)
      B(1)
      B(2)
    elif t == 0xd7:
      B(2)
      B(1)
      B(3)
    elif t == 0xd8:
      L()
      L()
      B(0)
      V(36)
    # 0xda
      # L()
      # L()
      # Extended back-ref?
      # L()
    elif t == 0xdb:  # is this right?
      L()
      L()
      B(2)
      L()
      L()
    elif t == 0xdd:
      L()
      L()
      B(4)
      L()
    elif t == 0xdf:  # Confirmed
      B(2)
      L()
      L()
      L()
      L()
      L()
      # Was going to comment this out... when I found above:
      # df 09 07 05 03: L() L() B(5) L()
    elif t == 0xe4:
      L()
      L()
      L()
      V(20)
    elif t == 0xe6:  # after not ff
      L()
      L()
      L()
      R(2)
      #formerly B(5)
    elif t == 0xe7:  # after not ff
      B(6)
    elif t == 0xed:  # confirmed
      B(3)
      B(2)
      L()
    elif t == 0xee:
      L()
      L()
      L()
      B(4)
    elif t == 0xef:
      #formerly B(3) B(3) L()
      L()
      L()
      L()
      B(5)
    elif t == 0xf6:
      B(3)
      L()
      B(2)
    elif t == 0xf7:
      B(3)
      L()
      B(3)
    elif t == 0xf9:
      L()
      L()
      L()
      L()
      L(5)
    # 0xfb - 6 literals, back reference
    elif t == 0xfe:
      L()
      L()
      L()
      L()
      L()
      L()
      L()
    elif t == 0xff:
      L()
      L()
      L()
      L()
      L()
      L()
      L()
      L()
    else:
      print('----')
      print('\n'.join([' '.join(['{:02x}'.format(b) for b in d[i*16:i*16+16]]) for i in range(int((len(d) + 15) / 16))]))
      assert(False)

  return d
