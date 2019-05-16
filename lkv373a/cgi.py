import requests

def upgrade_encoder(host, file):
  r = requests.post('http://{}/dev/encinfo.cgi'.format(host),
      files={'filename' : open(file, 'rb')})
  if r.status_code != 200:
    raise RuntimeError('Upgrade failed: {}'.format(r.status_code))
