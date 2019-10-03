#!/usr/bin/env python3

import sys
from elftools.elf.elffile import ELFFile

out_file_name, base_file_name, elf_overlay_file_name = sys.argv[1:4]

result = bytearray(open(base_file_name, 'rb').read())

with open(elf_overlay_file_name, 'rb') as elf_overlay_file:
  elf_file = ELFFile(elf_overlay_file)
  for section in elf_file.iter_sections():
    if section.header['sh_flags'] == 6:
      d = section.data()
      addr = section.header['sh_addr']
      result[addr:addr+len(d)] = d

open(out_file_name, 'wb').write(result)

