from .container import Container
from .provider import provider_decorator
from .inject import inject_decorator


c = Container()
provider = provider_decorator(c)
inject = inject_decorator(c)
