#!/usr/bin/env python3

import sys
from collections import namedtuple
from string import printable

Result = namedtuple('Result', ['byte', 'line_count', 'hash', 'redacted_hash'])

col_count = 16
u2_firmware_path='/home/joel/opentechlab/16-it9919/20181226-lkv-373a-backups/u2.bin'

firmware = open(u2_firmware_path, 'rb').read()
lines = [l.strip().split(',') for l in open(sys.argv[1], 'r').readlines()][1:]

hashes = {l[2] for l in lines}
line_counts = {h: len(open('{}.asc'.format(h), 'rb').readlines()) for h in hashes}

results = {int(l[0]) : Result(firmware[int(l[0])], line_counts[l[2]], l[2], l[3]) for l in lines}

print('''<html>
<head>
<style>
body {
  font-family: monospace;
}

table {
  border-collapse: collapse;
}

table, th, td {
  border: 1px solid #ccc;
}

td {
  width: 3em;
  height: 3em;
  text-align: center;
}

td.addr {
  text-align: right;
  width: 6em;
}

a {
  text-decoration: none;
  color: black;
}

.char {
  font-size: 150%;
}

.byte {
  font-size: 100%;
}
</style>
</head>
<body><table>''')

start_byte = min(results.keys())
end_byte = max(results.keys())

for r in range(int(start_byte / col_count), int((end_byte + col_count - 1) / col_count)):
  print('<tr><td class="addr">{:04X}</td>'.format(r * col_count))
  for c in range(col_count):
    try:
      result = results[r * col_count + c] 
      char = chr(result.byte)
      line_count = line_counts[result.hash]
      print('<td style="{style}"><a href="{hash}.asc">'
        '<span class="char">{char}</span><br/><span class="byte">{byte:02X}</span>'
        '</a></td>'.format(
          style='background-color: #{};'.format(result.redacted_hash[-6:]) if line_count else '',
          hash=result.hash,
          char=char if char in printable else ' ',
          byte=result.byte))
    except KeyError:
      print('</td>')
  print('<tr/>')

print('</table></body></html>')

