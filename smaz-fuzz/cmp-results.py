#!/usr/bin/env python3

import msgpack
import sys
from collections import namedtuple
from termcolor import colored

sys.path.append('/mnt/third/joel/workspace/opentechlab/16-it9919/lkv373a-tools')
from experiments import *

def print_bin_diff_cols(data1, data2, row_length=16):
  def prepare_data(d):
    return [int(b) for b in d] + (length - len(d)) * [None]

  def hex_byte(b, highlight):
    if b == None: return ' . '
    text = ' {:02x}'.format(b)
    return colored(text, 'red') if highlight else text

  length = ((max(len(data1), len(data2)) + row_length - 1) // row_length) * row_length
  data1 = prepare_data(data1)
  data2 = prepare_data(data2)
  diff = [b[0] != b[1] for b in zip(data1, data2)]

  sym1 = list(zip(data1, diff))
  sym2 = list(zip(data2, diff))

  for row_offset in range(0, length, row_length):
    print(''.join(hex_byte(*b) for b in sym1[row_offset:row_offset+row_length]), ' ',
        ''.join(hex_byte(*b) for b in sym2[row_offset:row_offset+row_length]))

cols = tuple(int(c) for c in sys.argv[1:3])

cases = []
for path in sys.argv[3:]:
  with open(path, 'rb') as f:
    cases.extend(msgpack.Unpacker(f))

cases = tuple(cases[c] for c in cols)

print_bin_diff_cols(*tuple(c[b'smaz'] for c in cases))
print('\n -> \n')
print_bin_diff_cols(*tuple(c[b'decoded'] for c in cases))
