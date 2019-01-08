#!/usr/bin/env python3

import os

from os import path, readlink
from os.path import dirname as dn

tty_class_dir = '/sys/class/tty'
tty_devices = os.listdir(tty_class_dir)

blue_pill_devices = {
  open(path.join(tty_class_dir, dn(dn(dn(readlink(path.join(tty_class_dir, d))))), 'serial'), 'r').read().strip() :
  d for d in tty_devices if d.startswith('ttyACM')}

serprogs = {kv[0] : blue_pill_devices.get(kv[1], None) for kv in [
  ('mu1', '234218677285525154FF6E06'), ('u2', '164023677572545554FF6B06')]}

for serprog in serprogs.items():
  print('%04s: %s' % (serprog[0].upper(), serprog[1] or '-'))
