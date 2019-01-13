
from . import vserprog

def reset():
  with open('/dev/{}'.format(vserprog.devices['u2']), 'wb') as f:
    f.write(b'\x16')
