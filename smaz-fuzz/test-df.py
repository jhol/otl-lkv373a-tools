#!/usr/bin/env python3

import asyncio
import serial_asyncio
import async_timeout
import msgpack
import os
import sys

sys.path.append('/mnt/third/joel/workspace/opentechlab/16-it9919/lkv373a-tools')
from experiments import *
import experiments.dpu.smaz
import smedia
import lkv373a

date_str = time.strftime('%Y%m%d-%H%M%S', time.localtime())
run_name = os.path.splitext(__file__)[0]


async def run_tests():
  serial_reader, _ = await serial_asyncio.open_serial_connection(loop=None, url='/dev/{}'.format(lkv373a.tty_device),
      baudrate=115200)

  j = k = 0

  blob = bytearray(b'\xdb\xe0\x62\x05' b'\xdf\x31\x20\x15\x1c')
  #blob = bytearray(b'\xdf\x04\x02\x9c\x20\x00\x11')

  blob = bytearray(
      b''.join(bytes([0xff] + [0x80 + x + y * 8 for x in range(8)]) for y in range(16)) +
      blob +
      b'\xff\x00\x01\x02\x03\x04\x05\x06\x07\xff\x08'
      b'\x09\x0a\x0b\x0c\x0d\x0e\x0f\xff\x10\x11\x12\x13\x14\x15\x16\x17'
      b'\xff\x18\x19\x1a\x1b\x1c\x1d\x1e\x1f\xff\x20\x21\x22\x23\x24\x25'
      b'\x26\x27\xff\x28\x29\x2a\x2b\x2c\x2d\x2e\x2f\xff\x30\x31\x32\x33'
      b'\x34\x35\x36\x37\xff\x38\x39\x3a\x3b\x3c\x3d\x3e\x3f'
    )
  results = await experiments.dpu.smaz.do_test_run(serial_reader, {k * 256 + j: blob})

  for test_result in results:
    print('---- {:08x}'.format(test_result.label))
    print_bin(test_result.smaz)
    print(' --> ')
    print_bin(test_result.decoded)
    print()

    test_log = '{}-{}.msgpack'.format(run_name, date_str)
    with open(test_log, 'ab') as f:
      msgpack.pack({
          'smaz': test_result.smaz,
          'decoded': test_result.decoded,
          'tail_length': k,
          'sub_cmd': j
          }, f)

asyncio.run(run_tests())
