#!/usr/bin/env python3

import hashlib
import lkv373a
from lkv373a import vserprog
import serial
import subprocess
import sys
import time
import re

base=0x831C9
length=1

timeout=3
lines=32
u2_firmware_path='/home/joel/opentechlab/16-it9919/20181226-lkv-373a-backups/u2.bin'

vserprog_devices = vserprog.devices.values()
if len(vserprog_devices) != 2:
  sys.stderr.write('{} vserprogs found: {}'.format(len(vserprog.devices), vserprog.devices))

print('Tristate {}'.format(', '.join(vserprog_devices)))
vserprog.trisate_vserprogs(vserprog_devices)

print('Begin...')
start_time = time.time()
with open(sys.argv[1], 'w') as log:
  log.write('#,Lines,Hash,Redacted Hash\n')
  for i in range(base, base + length):
    sys.stdout.write('[{: 5.1f}] 0x{:03x} '.format(time.time() - start_time, i))
    sys.stdout.flush()

    with open('mod-firmware.bin', 'wb') as f:
      mod_firmware = bytearray(open(u2_firmware_path, 'rb').read())
      mod_firmware[i] = 0xFF ^ mod_firmware[i]
      f.write(mod_firmware)

    while True:
      try:
        vserprog.write(vserprog.devices['u2'], 'mod-firmware.bin')
        break
      except RuntimeError as e:
        sys.stderr.write('flashrom failed!\n')
        sys.stderr.write(str(e))

    lkv373a.reset()

    with serial.Serial('/dev/{}'.format(lkv373a.tty_device), 115200, timeout=timeout) as ser:
      capture_lines = ser.read(1024*1024).split(b'\n')[:lines]
      capture = b'\n'.join(capture_lines)
      capture_hash = hashlib.md5(capture).hexdigest()
      with open('{}.asc'.format(capture_hash), 'wb') as f:
        f.write(capture)

      capture_redacted = re.sub('[x ][a-f0-9]+', ' ----', capture.decode('ascii', 'ignore')).encode('ascii')
      capture_redacted_hash = hashlib.md5(capture_redacted).hexdigest()
      with open('{}.asc'.format(capture_redacted_hash), 'wb') as f:
        f.write(capture_redacted)

      sys.stdout.write('{}-lines, {}, redacted={}\n'.format(len(capture_lines), capture_hash, capture_redacted_hash))
      log.write('{},{},{},{}\n'.format(i, len(capture_lines), capture_hash, capture_redacted_hash))
      log.flush()
