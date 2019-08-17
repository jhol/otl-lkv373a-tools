#!/usr/bin/env python3

import argparse
import msgpack
import sys
import traceback
from collections import namedtuple
from termcolor import colored

sys.path.append('/mnt/third/joel/workspace/opentechlab/16-it9919/lkv373a-tools')
from experiments import *
from smedia import smaz

subscripts = '₀₁₂₃₄₅₆₇₈₉'

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--show-unsynced', action='store_true')
parser.add_argument('-p', '--show-passed', action='store_true')
parser.add_argument('-v', '--require-verb', action='append', type=lambda x: int(x, 0))
parser.add_argument('FILE', nargs='+')
args = parser.parse_args()

def print_annotated_smaz(data, cmd_offsets, row_length=16):
  def hex_byte(o):
    try: return colored('{}{:02x}'.format(subscripts[cmd_offsets.index(o) % 10], data[o]), 'blue')
    except: return ' {:02x}'.format(data[o])

  print('\n'.join(''.join(hex_byte(o) for o in range(row_base, min(row_base + row_length, len(data))))
    for row_base in range(0, len(data), row_length)))


def print_bin_diff_cols(data1, data2, chunk_offsets, row_length=16):
  def prepare_data(d):
    return [int(b) for b in d] + (length - len(d)) * [None]

  def hex_byte(b, label, highlight):
    if b == None: return ' . '
    text = '{}{:02x}'.format(' ' if label == None else subscripts[label % 10], b)
    return colored(text, 'red') if highlight else text

  def find_label(offset):
    try: return chunk_offsets.index(offset)
    except: return None

  length = ((max(len(data1), len(data2)) + row_length - 1) // row_length) * row_length
  data1 = prepare_data(data1)
  data2 = prepare_data(data2)
  diff = [b[0] != b[1] for b in zip(data1, data2)]
  labels = [find_label(o) for o in range(length)]

  sym1 = list(zip(data1, labels, diff))
  sym2 = list(zip(data2, labels, diff))

  for row_offset in range(0, length, row_length):
    print(''.join(hex_byte(*b) for b in sym1[row_offset:row_offset+row_length]), ' ',
        ''.join(hex_byte(*b) for b in sym2[row_offset:row_offset+row_length]))


def test_decode_chunk(self, descriptions):
  cmd_offset = self.smaz.tell()
  try: self.present_verbs.add(self.smaz.read(1)[0])
  except: pass
  self.smaz.seek(cmd_offset)
  self.cmd_offsets.append(cmd_offset)
  self.decode_offsets.append(len(decoder.data))
  return orig_decode_chunk(self, descriptions)

orig_decode_chunk = smaz.Decoder.decode_chunk
smaz.Decoder.decode_chunk = test_decode_chunk


test_cases = []
for path in args.FILE:
  with open(path, 'rb') as f:
    test_cases.extend(msgpack.Unpacker(f))

passed = failed = 0
total_verbs = set()

sync = b'\x00\x01\x02\x03\x04\x05\x06\x07' 
for no, case in enumerate(test_cases):
  if sync in case[b'decoded'] or args.show_unsynced:
    expected = case[b'decoded']
    decoder = smaz.Decoder()
    decoder.cmd_offsets = []
    decoder.decode_offsets = []
    decoder.present_verbs = set()

    exception = None
    try:
      decoder.decode(case[b'smaz'])
    except Exception as e:
      exception = e
    decoded = decoder.data

    if sync in decoded and not exception:
      decoded = decoded[0:decoded.rfind(sync) + len(sync)]
      expected = expected[0:expected.rfind(sync) + len(sync)]

    if args.require_verb == None or any(v in decoder.present_verbs for v in args.require_verb):
      case_passed = decoded == expected and not exception

      if case_passed:
        print(f'{no}. PASSED')
        passed += 1
      else:
        print(f'{no}. FAILED')
        failed += 1
        if exception:
          print(exception)

      if not case_passed or args.show_passed:
        print()
        print_annotated_smaz(case[b'smaz'], decoder.cmd_offsets)
        print(' -> ')
        print_bin_diff_cols(expected or [], decoded or [], decoder.decode_offsets)
        print()

    total_verbs = total_verbs.union(decoder.present_verbs)


print('\n{} / {} PASSED'.format(passed, passed + failed))

unused_verbs = sorted(list(set(smaz.chunk_descriptions.keys()) - total_verbs))
print('Unused verbs: {}'.format(', '.join('0x{:02x}'.format(v) for v in unused_verbs)))
