#!/usr/bin/env python3

import msgpack
import sys

row_length = 16

test_cases = []
for path in sys.argv[2:]:
  with open(path, 'rb') as f:
    test_cases.extend(msgpack.Unpacker(f))

test_case = test_cases[int(sys.argv[1])][b'smaz']
for row in range(0, len(test_case), row_length):
  print("    b'{}'".format(''.join('\\x{:02x}'.format(b) for b in test_case[row:row + row_length])))
