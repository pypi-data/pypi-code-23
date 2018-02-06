import hashlib
import json
import os

import redis

# This Client provides a connection to the Redis server.
# Usage ex: RedisClient.redis_client(), RedisClient.requests_handler(...)

REDIS_HOST = os.getenv('REDIS_HOST') or 'localhost'
REDIS_PORT = os.getenv('REDIS_PORT') or 6379


class RedisClient:
    __redis_instance = None
    __ttl_key = "ttl_sec"

    @staticmethod
    def __generate_md5_redis_key(event, context):
        event_str = str(event)
        lambda_arn = context.invoked_function_arn
        str_for_md5 = event_str + lambda_arn
        return hashlib.md5(str_for_md5.encode('utf-8')).hexdigest()

    @staticmethod
    def __generic_generate_md5_redis_key(function_name, payload):
        function_str = str(function_name)
        payload_str = str(payload)
        print("Generating md5_redis_key for " + function_str)
        str_for_md5 = function_str + payload_str
        return hashlib.md5(str_for_md5.encode('utf-8')).hexdigest()

    # AWS Lambda Requests handler can be used to interface with any Lambda handlers.
    # This internally invokes RedisClient.fetch_data that has the workflow to cache
    # if needed.
    # Cache key is the md5 result of context.arn + event params
    # parameters:
    #   1. event = aws lambda event
    #   2. context = aws lambda context
    #   3. callback_method = actual aws lambda handler to invoke if there is a cache miss
    #   4. cache_params = (dict) (optional) a hash defining the cache properties where ttl_key is mandatory if present
    @staticmethod
    def aws_lambda_request_handler(event, context, callback_method, cache_params=None):
        _self = RedisClient

        if not callable(callback_method):
            raise TypeError("callback_method should a callable function")
        redis_key_md5 = _self.__generate_md5_redis_key(event, context)

        _params = cache_params or _self.redis_params()
        if _params is not None and (not isinstance(_params, dict) or _self.__ttl_key not in _params):
            raise TypeError("Params must be a dictionary and must provide a TTL value")
        method_params = {'event': event, 'context': context}
        _params.update({'method_params': method_params})

        return _self.fetch_data(redis_key_md5, callback_method, _params)

    # Generic Request Handler can be used to interface with generic web requests
    # This internally invokes RedisClient.fetch_data that has the workflow to cache
    # if needed.
    # Cache key is the md5 result of function_name and payload
    # parameters:
    #   1. function_name = function requesting cache services
    #   2. payload = what needs to be looked up, body of lookup
    #   3. callback_method = actual lookup method in case there is a cache miss
    #   4. cache_params = (dict) (optional) a hash defining the cache properties where ttl_key is mandatory if present

    @staticmethod
    def generic_request_handler(function_name, payload, callback_method, cache_params=None):
        _self = RedisClient

        if not callable(callback_method):
            raise TypeError("Your generic callback_method should be callable. ")

        redis_key_md5 = _self.__generic_generate_md5_redis_key(function_name, payload)

        _params = cache_params or _self.redis_params()
        print("Cache params set to " + str(_params))
        if _params is not None and (not isinstance(_params, dict) or _self.__ttl_key not in _params):
            raise TypeError("Params must be a dictionary and must provide a TTL value")

        method_params = {'payload': payload}
        _params.update({'method_params': method_params})
        print("Passing " + str(_params) + "into fetch_data")
        return _self.fetch_data(redis_key_md5, callback_method, _params)

    # Redis client instance. Only create if one doesn't exist.
    @staticmethod
    def redis_client():
        if RedisClient.__redis_instance is not None:
            return RedisClient.__redis_instance
        else:
            RedisClient.__redis_instance = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, charset="utf-8",
                                                       decode_responses=True)
            return RedisClient.__redis_instance

    # Default redis params that has TTL for now.
    @staticmethod
    def redis_params(ttl=300):
        return {RedisClient.__ttl_key: ttl}

    # Fetch data method to fetch data from Redis server. If the corresponding key doesn't exist (cache miss) then
    # the cache is populated with the obtained result.
    # Note: Passing params (ttl as dict) is optional. It can be used to override the default 60 sec TTL.
    @staticmethod
    def fetch_data(key, query_method, params=None):
        _self = RedisClient
        _method_attrs = None
        try:
            if key is None or not isinstance(key, str):
                raise TypeError("Key must be a string and cannot be null")

            _params = params or _self.redis_params()
            if _params is not None and (not isinstance(_params, dict) or _self.__ttl_key not in _params):
                raise TypeError("Params must be a dictionary and must provide a TTL value")
            if 'method_params' in _params:
                _method_attrs = list(_params.get('method_params').values())

            _redis_client = _self.redis_client()
            redis_get_result = _redis_client.get(key)

            if redis_get_result is not None:
                print("Requested key " + key + " found in Redis server. Total key count: " + str(_redis_client.dbsize()))
                return json.loads(redis_get_result)
            else:
                # cache miss

                invoker_method_result = query_method(*_method_attrs[0:2]) if _method_attrs is not None else query_method()
                _redis_client.set(key, json.dumps(invoker_method_result), int(_params.get(_self.__ttl_key)))
                print(
                    "Requested key " + key + " is missing in Redis server. Adding it to cache. Total key count: " + str(
                        _redis_client.dbsize()))
                return invoker_method_result

        except redis.ConnectionError as e:
            print("Redis connection error. Skipping cache layer and making network request" + str(e))
            return query_method(*_method_attrs[0:2]) if _method_attrs is not None else query_method()

