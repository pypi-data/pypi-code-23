from json import JSONDecodeError
from .exceptions import APIInvalidJSONError, APIContentTypeError


async def cors_signal(request, response):
    """Add some CORS headers"""
    response.headers["Access-Control-Allow-Origin"] = '*'
    response.headers["Access-Control-Allow-Headers"] = 'Content-Type, Authorization'
    response.headers["Access-Control-Allow-Methods"] = 'POST, OPTIONS, GET, PUT, DELETE'