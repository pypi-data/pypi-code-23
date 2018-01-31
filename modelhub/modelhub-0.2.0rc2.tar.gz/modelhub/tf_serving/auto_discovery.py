# encoding=utf8
# author=spenly
# mail=i@spenly.com

from redis import StrictRedis


class AutoDiscovery(object):

    def __init__(self, **kwargs):
        self._redis = StrictRedis(**kwargs)

    def _build_key(self, model_name, version):
        return "%s@%d" % (model_name, version)

    def register(self, model_name, hostport, version, timeout=10):
        """
        register a TF serving info
        :param model_name: model name
        :param version: model version
        :param timeout: expire time
        :return:
        """
        version = int(version)
        key = self._build_key(model_name, version)
        self._redis.set(key, value=hostport, ex=timeout)

    def get_host_port(self, model_name, version=None):
        """
        get a TF serving host info
        :param model_name:
        :param version: int or str
        :return:
        """
        if not version:
            start_index = len(model_name) + 1
            latest_ver = -1
            # find the latest version
            for item in self._redis.keys("%s*" % model_name):
                # model_name@ver, e.g.: language_detection@1
                item = isinstance(item, bytes) and item.decode("utf8") or item
                cur_ver = int(item[start_index:])
                latest_ver = cur_ver > latest_ver and cur_ver or latest_ver
            # version validation
            if latest_ver < 0:
                raise Exception("No available serving versions for model %s" % model_name)
            else:
                version = latest_ver
        version = int(version)
        key = self._build_key(model_name, version)
        val = self._redis.get(key)
        if isinstance(val, bytes):
            val = val.decode("utf8")
        # value validation, empty value will raise a exception
        if not val:
            raise Exception("Serving host for %s@%s not exists" % (model_name, version))
        return val


if __name__ == "__main__":
    ad = AutoDiscovery(host="sol")
    print("\nregister: test@1=hostport_for_test")
    ad.register("test", "hostport_for_test", "1")

    print("\nget hostport for model test@latest")
    print("value => " + ad.get_host_port("test", None))

    print("\nget host port for model test@1")
    print("value => " + ad.get_host_port("test", version=1))

    print("\nregister: abc@2=hostport_for_abc")
    ad.register("abc", "hostport_for_abc", version=2)

    print("\nget hostport for model abc@latest")
    print("value => " + ad.get_host_port("abc"))

    print("\nget host port for model test@2")
    # this will cause a exception
    print("value => " + ad.get_host_port("test", version=2))