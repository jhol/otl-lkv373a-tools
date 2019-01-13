import os
import subprocess
import tempfile

empty_file = tempfile.NamedTemporaryFile()

vserprog_ids = {'234218677285525154FF6E06': 'mu1', '164023677572545554FF6B06': 'u2'}

def _list_vserprogs():
  from os import path, readlink
  from os.path import dirname as dn

  tty_class_dir = '/sys/class/tty'
  tty_devices = os.listdir(tty_class_dir)
  vserprog_devices = [
    (d, open(path.join(tty_class_dir, dn(dn(dn(readlink(path.join(tty_class_dir, d))))), 'serial'), 'r').read().strip())
    for d in tty_devices if d.startswith('ttyACM')]

  return {vserprog_ids[kv[1]]: kv[0] for kv in vserprog_devices}

devices = _list_vserprogs()

def spawn_tristate_vserprog(device):
  return subprocess.Popen(['flashrom', '-p', 'serprog:dev=/dev/{}:40000000'.format(device), '-v', empty_file.name],
      stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

def trisate_vserprogs(devices):
  for p in [spawn_tristate_vserprog(device) for device in devices]:
    p.wait()
