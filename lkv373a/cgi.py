
import aiohttp
import async_timeout

async def upgrade_encoder(host, file):
  async with aiohttp.ClientSession() as session:
    async with async_timeout.timeout(60):
      async with session.post('http://{}/dev/encinfo.cgi'.format(host),
          data={'filename' : open(file, 'rb')}) as r:
        r.raise_for_status()
