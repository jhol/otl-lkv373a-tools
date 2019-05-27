#!/usr/bin/env python3

import aiohttp.client_exceptions
import asyncio
import async_timeout
from collections import namedtuple
import itertools
import msgpack
import os
import sys
import struct
import serial
import time

import assembler
from assembler.instructions import *
import lkv373a
import lkv373a.cgi
import smedia.smaz

from experiments import *

line_length = 16
print_length = 65536
unpacked_length = 65535

func_puts = 0x9b960
func_printf = 0x9b86c

Test = namedtuple('Test', ['label', 'smaz'])
TestResult = namedtuple('TestResult', ['label', 'smaz', 'decoded'])

test_fields = ['label', 'src_addr', 'dest_addr', 'packed_length', 'unpacked_length', 'print_length']
TestTableEntry = namedtuple('TestTableEntry', test_fields)


def write_fw(f, tests):
  fw = bytearray(open('LKV373A_TX_V3.0c_d_20161116_bin.bin', 'rb').read())

  patch_code_base = 0x1000
  dst_addr = 0x120000
  test_data_base = 0x00180000

  # Patch in strings
  data2_base = 0x2000

  sync_str = b'----\0'
  sync_str_base = data2_base
  heading_str = b'>%08x:\0'
  heading_str_base = sync_str_base + len(sync_str)
  byte_str = b'%08x\0'
  byte_str_base = heading_str_base + len(heading_str)
  term_str_base = sync_str_base + 4

  assembler.patch_raw(fw, data2_base, sync_str + heading_str + byte_str)

  # Patch in the source data
  test_data = b''.join(t.smaz for t in tests)
  test_data += b' ' * ((((len(test_data) + 3) // 4) * 4) - len(test_data))
  assembler.patch_raw(fw, test_data_base, test_data)

  # Patch in the test table
  test_table_base = test_data_base + len(test_data)

  test_table = []
  off = test_data_base
  for test in tests:
    test_table.append(TestTableEntry(test.label, off, dst_addr, len(test.smaz), unpacked_length, print_length))
    off += len(test.smaz)

  assembler.patch_raw(fw, test_table_base,
      b''.join(struct.pack('>{}I'.format(len(test_fields)), *test) for test in test_table))

  run_test_addr = patch_code_base
  dst_addr_reg = 20
  table_entry_ptr_reg = 21
  print_length_reg = 22
  run_test_save_regs = [3, 4, dst_addr_reg, table_entry_ptr_reg, print_length_reg, 9]
  run_test = [
    # Save the registers
    (ADDI, 1, 1, -len(run_test_save_regs)*4)
    ] + [(SW, 0, 1, run_test_save_regs[i], 4*i) for i in range(len(run_test_save_regs))] + [

    # Allocate stack space
    (ADDI, 1, 1, -1*4),

    # Load the table
    (ORI, table_entry_ptr_reg, 3, 0),

    # Clear the destination buffer
    (LH, 4, 0, 0x5555),
    (ORI, 4, 4, 0x5555),
    (LW, 3, table_entry_ptr_reg, 0, 2 * 4),  # Load dst_addr
    (LW, 5, table_entry_ptr_reg, 0, 5 * 4),  # Load print_length

    (SW, 0, 3, 4, 0x0),
    (ADDI, 3, 3, 4),
    (ADDI, 5, 5, -4),
    (CMPI, CMP_COND.NE, 5, 0),
    (JC, -4),
    (NOP, 8, 0, 0),

    # Configure the DPU
    (LH, 3, 0, 0xd090),
    (ORI, 3, 3, 0x300),

    # SRC_ADDR
    (LW, 4, table_entry_ptr_reg, 0, 1 * 4),
    (SW, 0, 3, 4, 0x8),

    # DST_ADDR
    (LW, 4, table_entry_ptr_reg, 0, 2 * 4),
    (SW, 0, 3, 4, 0xc),

    # SRC_LEN
    (LW, 4, table_entry_ptr_reg, 0, 3 * 4),
    (SW, 0, 3, 4, 0x10),

    # DST_LEN
    (LW, 4, table_entry_ptr_reg, 0, 4 * 4),
    (SW, 0, 3, 4, 0x14),

    # CTRL - Start decoding!
    (ADDI, 4, 0, 0x22),
    (SW, 0, 3, 4, 0x0),

    # Print heading
    (LW, 3, table_entry_ptr_reg, 0, 0),  # Load the label from the table
    (SW, 0, 1, 3, 0x0),
    (LH, 3, 0, heading_str_base >> 16),
    (ORI, 3, 3, heading_str_base & 0xFFFF),
    JInstruction(CALL, func_printf),
    (NOP, 8, 0, 0),

    # Search backwards to find end of decoded data
    (LW, dst_addr_reg, table_entry_ptr_reg, 0, 2 * 4),  # Load dst_addr
    (LW, print_length_reg, table_entry_ptr_reg, 0, 5 * 4),

    #(LB, 3, dst_addr_reg, print_length_reg, -1),
    #(CMPI, CMP_COND.NE, 3, 0x55),
    #(JC, 4),
    #(NOP, 8, 0, 0),

    #(ADDI, print_length_reg, print_length_reg, -1),
    #(CMPI, CMP_COND.NE, print_length_reg, 0),
    #(JC, -6),
    #(NOP, 8, 0, 0),

    # Print the result
    (LW, 3, dst_addr_reg, 0, 0),

    (LH, 4, 0, 0x5555),
    (ORI, 4, 4, 0x5555),
    (CMP, CMP_COND.EQ, 3, 4, 0),
    (JC, 12),
    (NOP, 8, 0, 0),

    (SW, 0, 1, 3, 0x0),

    (LH, 3, 0, byte_str_base >> 16),
    (ORI, 3, 3, byte_str_base & 0xFFFF),
    JInstruction(CALL, func_printf),
    (NOP, 8, 0, 0),

    (ADDI, dst_addr_reg, dst_addr_reg, 4),
    (ADDI, print_length_reg, print_length_reg, -4),

    (CMPI, CMP_COND.NE, print_length_reg, 0),
    (JC, -14),
    (NOP, 8, 0, 0),

    # Print a new line
    (LH, 3, 0, term_str_base >> 16),
    (ORI, 3, 3, term_str_base & 0xFFFF),
    JInstruction(CALL, 0x9b960),
    (NOP, 8, 0, 0),

    # Free stack space
    (ADDI, 1, 1, 1*4),

    # Retore the registers
    ] + [(LW, run_test_save_regs[i], 1, 0, 4*i) for i in range(len(run_test_save_regs))] + [
    (ADDI, 1, 1, len(run_test_save_regs)*4),

    # Return
    (JMP, 0, 0, 9, 0),
    (NOP, 8, 0, 0)
    ]

  run_tests_addr = run_test_addr + len(run_test) * 4
  run_tests = [
    # Print sync line
    (LH, 3, 0, sync_str_base >> 16),
    (ORI, 3, 3, sync_str_base & 0xFFFF),
    JInstruction(CALL, func_puts),
    (NOP, 8, 0, 0),

    # Iterate through test table
    (LH, 3, 0, test_table_base >> 16),
    (ORI, 3, 3, test_table_base & 0xFFFF),
    (ORI, 4, 0, len(tests)),

    JInstruction(CALL, run_test_addr),
    (NOP, 8, 0, 0),
    (ADDI, 3, 3, len(test_fields) * 4),
    (ADDI, 4, 4, -1),
    (CMPI, CMP_COND.EQ, 4, 0),
    (JNC, -5),
    (NOP, 8, 0, 0),

    # Print the done line
    (LH, 3, 0, sync_str_base >> 16),
    (ORI, 3, 3, sync_str_base & 0xFFFF),
    JInstruction(CALL, func_puts),
    (NOP, 8, 0, 0),

    # Infinite loop
    (JMPI, 0),
    (NOP, 8, 0, 0)
    ]

  assembler.patch(fw, patch_code_base,
      run_test + run_tests)

  assembler.patch(fw, 0x7d6f0, [
    (NOP, 8, 0, 0),
    JInstruction(JMPI, run_tests_addr),
    (NOP, 8, 0, 0)
    ])

  f.write(fw[0:0x00200000])


async def await_serial_line(serial_reader, string):
  while True:
    line = (await serial_reader.readline()).decode('ascii', 'ignore')
    #sys.stdout.write(line)
    if line.startswith(string):
      return True


async def do_test_run(serial_reader, test_dict):
  with open('test.bin', 'wb') as f:
    write_fw(f, [Test(k, v) for k, v in test_dict.items()])

  started_up = False
  while not started_up:
    print_status('Starting up...')
    lkv373a.reset()

    await await_serial_line(serial_reader, 'First Out Video Timestamp:')

    print_status('Load software...')
    upload_begin_time = time.time()
    while not started_up and (time.time() - upload_begin_time) < 60.0:
      upload_task = asyncio.create_task(lkv373a.cgi.upgrade_encoder('192.168.1.141', 'test.bin'))
      await_sync_task = asyncio.create_task(await_serial_line(serial_reader, '----'))

      done, pending = await asyncio.wait([upload_task, await_sync_task],
          timeout=45, return_when=asyncio.FIRST_COMPLETED)

      for t in pending:
        t.cancel()
      await asyncio.wait(pending)

      try:
        upload_task.result()
      except aiohttp.client_exceptions.ClientConnectionError:
        pass
      except asyncio.CancelledError:
        pass

      try:
        if await_sync_task.result():
          started_up = True
      except asyncio.CancelledError:
        pass

  print_status('Results begin...')
  #log.write('\n\n{:02x}\n'.format(*args))

  results = []
  while True:
    line = (await serial_reader.readline()).decode('ascii', 'ignore')
    #sys.stdout.write(line)
    if not line.startswith('>'):
      break
    label = int(line[1:9], 16)
    results.append(TestResult(label, test_dict[label], bytearray.fromhex(line[10:].strip())))

  return results

