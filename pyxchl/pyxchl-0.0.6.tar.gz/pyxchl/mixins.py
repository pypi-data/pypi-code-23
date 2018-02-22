import io
import sys

import logging
import logging.handlers

from yamlsettings.yamldict import YAMLDict, load

from . import BaseObject
from .utils import Utils


# region Mixins
class CLHMixin(BaseObject):
    DEFAULT_CONF = None

    _conf = None
    _cconf = None

    @property
    def rconf(self):
        """Root config
        """
        return self._conf

    @property
    def gconf(self):
        return self._conf['global'] if self._conf and 'global' in self._conf \
            else self._conf['g'] if self._conf and 'g' in self._conf else None

    @property
    def conf(self):
        return self._cconf

    @property
    def logger(self):
        return self._logger

    def __init__(self, conf=None, logger=None, *args, **kwargs):
        self._conf = conf

        def_conf = YAMLDict()

        if isinstance(self.DEFAULT_CONF, unicode):
            def_conf = load(io.StringIO(self.DEFAULT_CONF))
        elif isinstance(self.DEFAULT_CONF, dict):
            def_conf.update(self.DEFAULT_CONF)

        def iter_over_bases(cls):
            for t in cls.__bases__:
                if t is CLHMixin:
                    return

                yield t.__name__

                for b in iter_over_bases(t):
                    yield b

        if conf is not None:
            # Try to predict config
            for class_name in reversed(list([self.__class__.__name__]) + list(iter_over_bases(self.__class__))):
                names = Utils.camel2underscore(class_name)

                possible_conf_keys = list([names])

                for x in range(1, len(names)):
                    possible_conf_keys.append(names[:-x])

                for pc in possible_conf_keys:
                    if ''.join(pc) in self._conf:
                        def_conf.update(self._conf[''.join(pc)])
                        break

                    if '_'.join(pc) in self._conf:
                        def_conf.update(self._conf['_'.join(pc)])
                        break

        self._cconf = def_conf

        if logger is None:
            try:
                level = self.gconf.logging.level
            except (AttributeError, TypeError):
                level = 'INFO'

            try:
                fmt = self.gconf.logging.format
            except (AttributeError, TypeError):
                fmt = '%(asctime)s %(module)s: %(message)s'

            logger = logging.getLogger('{module}.{class_name}'.format(module=self.__class__.__module__,
                                                                      class_name=self.__class__.__name__))

            if logger.level == logging.NOTSET:
                logger.setLevel(level)

                formatter = logging.Formatter(fmt,
                                              datefmt='%b %d %H:%M:%S')

                try:
                    for h in self.gconf.logging.handlers:
                        if h == 'stdout':
                            handler = logging.StreamHandler(sys.stdout)
                        elif h == 'stderr':
                            handler = logging.StreamHandler(sys.stderr)
                        elif h == 'syslog':
                            handler = logging.handlers.SysLogHandler(address='/dev/log',
                                                                     facility=logging.handlers.SysLogHandler.LOG_DAEMON)

                        logger.addHandler(handler)
                        handler.setFormatter(formatter)

                except (AttributeError, TypeError):
                    handler = logging.StreamHandler(sys.stdout)

                    logger.addHandler(handler)
                    handler.setFormatter(formatter)

        self._logger = logger

        super(CLHMixin, self).__init__(*args, **kwargs)
# endregion


__all__ = ['CLHMixin']
