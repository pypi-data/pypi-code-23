# encoding=utf8
# author=spenly
# mail=i@spenly.com

from redis import StrictRedis

_DEFAULT_MODEL_VER = 1


class AutoDiscovery(object):

    def __init__(self, **kwargs):
        self._redis = StrictRedis(**kwargs)

    def _build_key(self, model_name, version):
        return "%s@%d" % (model_name, version)

    def register(self, model_name, hostport, version=_DEFAULT_MODEL_VER, timeout=10):
        """
        register a TF serving info
        :param model_name: model name
        :param version: model version
        :param timeout: expire time
        :return:
        """
        key = self._build_key(model_name, version)
        self._redis.set(key, value=hostport, ex=timeout)

    def get_host_port(self, model_name, version=_DEFAULT_MODEL_VER):
        """
        get a TF serving host info
        :param model_name:
        :param version:
        :return:
        """
        key = self._build_key(model_name, version)
        val = self._redis.get(key)
        # if default version has no value, try to get the latest version value.
        if version == _DEFAULT_MODEL_VER and not val:
            start_index = len(model_name) + 1
            latest_ver = _DEFAULT_MODEL_VER
            # find the latest version
            for item in self._redis.keys("%s*" % model_name):
                item = isinstance(item, bytes) and item.decode("utf8") or item
                cur_ver = item[start_index:]
                cur_ver = cur_ver and int(cur_ver) or _DEFAULT_MODEL_VER
                latest_ver = cur_ver > latest_ver and cur_ver or latest_ver
            key = self._build_key(model_name, latest_ver)
            val = self._redis.get(key)
        if isinstance(val, bytes):
            val = val.decode("utf8")
        if not val:
            val = ""
        return val


if __name__ == "__main__":
    ad = AutoDiscovery(host="sol")
    print("\nregister: test=hostport_for_test")
    ad.register("test", "hostport_for_test")

    print("\nget hostport for model test [latest]")
    print("value => " + ad.get_host_port("test"))

    print("\nget host port for model test [1]")
    print("value => " + ad.get_host_port("test", version=1))

    print("\nget host port for model test [2]")
    print("value => " + ad.get_host_port("test", version=2))

    print("\nregister: abc[2]=hostport_for_abc")
    ad.register("abc", "hostport_for_abc", version=2)

    print("\nget hostport for model abc [latest]")
    print("value => " + ad.get_host_port("abc"))
