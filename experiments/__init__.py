#!/usr/bin/env python3

import time

start_time = time.time()


def print_bin(data, row_length=16):
  print('\n'.join(' '.join('{:02x}'.format(b) for b in data[o:o+row_length]) for o in range(0, len(data), row_length)))


def print_status(status):
  print('[{: 8.1f}] {}'.format(time.time() - start_time, status))
