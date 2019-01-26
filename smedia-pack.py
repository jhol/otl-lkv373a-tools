#!/usr/bin/env python3

import sys
from struct import *


unpacked_unit_length = 0x80000
padding = 4  # Any length above this value appears to be valid


def usage():
  print('{} SMEDIA_HEADER SMAZ_UNPACKED_LENGTH SMAZ_UNITS... OUT'.format(sys.argv[0]))


if len(sys.argv) < 4:
  usage()
  sys.exit(1)

smedia_header = open(sys.argv[1], 'rb').read()
smaz_unpacked_length = int(sys.argv[2])
smaz_units = [open(f, 'rb').read() for f in sys.argv[3:-1]]

with open(sys.argv[-1], 'wb') as out:
  out.write(b'SMEDIA02')
  out.write(b'\x00\x00\x00\x70')
  out.write(pack('>I', len(smedia_header) + 20))

  smaz_length = sum(len(unit) + 4 * 2 for unit in smaz_units) + 4 * 2

  out.write(pack('>I', smaz_length + padding))

  out.write(smedia_header)

  out.write(b'SMAZ')
  out.write(pack('>I', unpacked_unit_length))

  for unit in smaz_units:
    out.write(pack('>I', min(unpacked_unit_length, smaz_unpacked_length)))
    smaz_unpacked_length -= unpacked_unit_length

    out.write(pack('>I', len(unit)))
    out.write(unit)

  out.write(b'\x00' * padding)

  # Expand to match size of flash chip
  out.write(b'\xFF' * (4194304 - out.tell()))
