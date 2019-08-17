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

with open('LKV373A_TX_V3.0c_d_20161116_bin.smedia02', 'rb') as f:
  smedia_header = smedia.read_smedia_header(f)
  f.seek(smedia_header.smaz_offset)
  smaz_chunks = [c for c in smedia.read_smaz(f, smedia_header)]

async def run_tests():
  serial_reader, _ = await serial_asyncio.open_serial_connection(loop=None, url='/dev/{}'.format(lkv373a.tty_device),
      baudrate=115200)

  for chunk in range(1, len(smaz_chunks)):
    for j in range(256):
      terminator = b''.join(b'\xff' + bytes(b % 256 for b in range(i * 8, (i + 1) * 8)) for i in range(8))
      blob = smaz_chunks[chunk].data[0:j] + terminator
      results = await experiments.dpu.smaz.do_test_run(serial_reader, {j: blob})
      for test_result in results:
        print('---- {:08x}'.format(test_result.label))
        print_bin(test_result.smaz)
        print(' --> ')
        print_bin(test_result.decoded)
        print()

        test_log = '{}-chun1-{}-cases-{}.msgpack'.format(run_name, chunk, date_str)
        with open(test_log, 'ab') as f:
          msgpack.pack({
              'smaz': test_result.smaz,
              'decoded': test_result.decoded,
              'print_length': experiments.dpu.smaz.print_length,
              'unpacked_length': experiments.dpu.smaz.unpacked_length
              }, f)

asyncio.run(run_tests())
