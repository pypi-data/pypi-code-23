import aiohttp


async def get(url, *args, return_type='text', **kwargs):
    """"""
    async with aiohttp.ClientSession() as session:
        async with session.get(url, *args, **kwargs) as result:
            if return_type == 'json':
                return await result.json()
            elif return_type == 'text':
                return await result.text()


async def post(url, *args, return_type='text', **kwargs):
    """"""
    async with aiohttp.ClientSession() as session:
        async with session.post(url, *args, **kwargs) as result:
            if return_type == 'json':
                return await result.json()
            elif return_type == 'text':
                return await result.text()
