
from collections import namedtuple
import struct as s
import os


smedia02_sync = b'SMEDIA02'
smaz_sync = b'SMAZ'

SmediaHeader = namedtuple('SmediaHeader', ['setup_microcode_offset', 'smaz_offset', 'smaz_length'])
SmazHeader = namedtuple('SmazHeader', ['checksum', 'total_unpacked_length', 'unpacked_chunk_length'])
SmazSegment = namedtuple('SmazSegment', ['unpacked_length', 'packed_length', 'data'])


def read_smedia_header(f):
  sync_word = f.read(8)
  if sync_word != smedia02_sync:
    raise ValueError('Expected {}, got {}'.format(smedia02_sync, sync_word))
  return SmediaHeader(*s.unpack('>3I', f.read(12)))


def read_smaz_header(f):
  f.seek(-8, os.SEEK_CUR)
  checksum, length = s.unpack('>2I', f.read(8))

  sync_word = f.read(4)
  if sync_word != smaz_sync:
    raise ValueError('Expected {}, got {}'.format(smaz_sync, sync_word))

  return SmazHeader(checksum, length, *s.unpack('>I', f.read(4)))


def read_smaz(f, smedia_header):
  data_length = smedia_header.smaz_length
  header = read_smaz_header(f)

  data_length -= 8
  while data_length > 8:
    unpacked_length, packed_length = s.unpack('>2I', f.read(8))
    yield SmazSegment(unpacked_length, packed_length, f.read(packed_length))
    data_length -= packed_length + 8


def pack(smedia_header_path, smaz_unpacked_length, smaz_chunk_paths, out_path):
  unpacked_chunk_length = 0x80000
  padding = 4  # Any length above this value appears to be valid

  smedia_header = open(smedia_header_path, 'rb').read()
  smaz_chunks = [open(f, 'rb').read() for f in smaz_chunk_paths]

  with open(out_path, 'wb') as out:
    out.write(smedia02_sync)
    out.write(b'\x00\x00\x00\x70')
    out.write(s.pack('>I', len(smedia_header) + 20))

    smaz_length = sum(len(chunk) + 4 * 2 for chunk in smaz_chunks) + 4 * 2

    out.write(s.pack('>I', smaz_length + padding))

    out.write(smedia_header)

    out.write(smaz_sync)
    out.write(s.pack('>I', unpacked_chunk_length))

    for chunk in smaz_chunks:
      out.write(s.pack('>I', min(unpacked_chunk_length, smaz_unpacked_length)))
      smaz_unpacked_length -= unpacked_chunk_length

      out.write(s.pack('>I', len(chunk)))
      out.write(chunk)

    out.write(b'\x00' * padding)

    # Expand to match size of flash chip
    out.write(b'\xFF' * (4194304 - out.tell()))

