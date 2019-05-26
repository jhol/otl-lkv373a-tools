
import aiohttp

async def upgrade_encoder(host, file):
  async with aiohttp.ClientSession() as session:
    async with session.post('http://{}/dev/encinfo.cgi'.format(host),
        data={'filename' : open(file, 'rb')}) as r:
      r.raise_for_status()
