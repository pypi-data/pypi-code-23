from aiohttp import ClientSession

async def get(*args, **kargs):
    async with ClientSession() as session:
        async with session.get(*args, **kargs) as response:
            mimetype = response.content_type
            if mimetype.endswith('json'):
                return response.status, response.headers, await response.json()
            elif mimetype.startswith('text') or mimetype.endswith('javascript') or mimetype.endswith('svg') or mimetype.endswith('xml'):
                return response.status, response.headers, await response.text()
            else:
                return response.status, response.headers, await response.read()
