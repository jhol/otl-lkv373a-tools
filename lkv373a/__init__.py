
from . import vserprog

def _find_tty_device():
  import os
  from os import readlink, path
  from os.path import dirname as dn

  tty_class_dir = '/sys/class/tty'

  def tty_usb_interface_dir(tty):
    tty_device_dir = path.join(tty_class_dir, readlink(path.join(tty_class_dir, tty)))
    device = path.abspath(path.join(tty_device_dir, readlink(path.join(tty_device_dir, 'device'))))
    if path.basename(device).startswith('tty'):
      return dn(device)
    return device

  def tty_usb_bus(tty):
    try:
      with open(path.join(dn(tty_usb_interface_dir(tty)), 'busnum'), 'r') as f:
        return f.read()
    except FileNotFoundError:
      return None

  def usb_device_id(device_dir):
    with open(path.join(device_dir, 'idVendor'), 'r') as vid_f:
      with open(path.join(device_dir, 'idProduct'), 'r') as pid_f:
        return (vid_f.read().strip(), pid_f.read().strip())

  try:
    vserprog_device = next(iter(vserprog.devices.values()))
  except StopIteration:
    return None

  tty_devices = os.listdir(tty_class_dir)
  tty_usb_busses = {tty: tty_usb_bus(tty) for tty in tty_devices}
  rig_bus_num = tty_usb_busses[vserprog_device]
  sibling_ttys = {tty for tty in tty_devices if tty_usb_busses[tty] == rig_bus_num}
  sibling_tty_ids = [(tty, usb_device_id(dn(tty_usb_interface_dir(tty)))) for tty in sibling_ttys]

  return [tty for tty in sibling_tty_ids if tty[1] == ('067b', '2303')][0][0]

tty_device = _find_tty_device()

def reset():
  with open('/dev/{}'.format(vserprog.devices['u2']), 'wb') as f:
    f.write(b'\x16')
