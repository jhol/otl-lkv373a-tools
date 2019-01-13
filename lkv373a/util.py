import os


tty_class_dir = '/sys/class/tty'
vserprog_ids = {'234218677285525154FF6E06': 'mu1', '164023677572545554FF6B06': 'u2'}

def list_vserprogs():
  from os import path, readlink
  from os.path import dirname as dn

  tty_devices = os.listdir(tty_class_dir)
  vserprog_devices = [
    (d, open(path.join(tty_class_dir, dn(dn(dn(readlink(path.join(tty_class_dir, d))))), 'serial'), 'r').read().strip())
    for d in tty_devices if d.startswith('ttyACM')]

  return {vserprog_ids[kv[1]]: kv[0] for kv in vserprog_devices}
