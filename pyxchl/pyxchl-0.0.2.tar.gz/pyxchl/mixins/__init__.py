import logging
import logging.handlers

from pyxchl import BaseObject
from pyxchl import Utils


# region Mixins
class CLHMixin(BaseObject):
    _conf = None
    _cconf = None

    @property
    def rconf(self):
        """Root config
        """
        return self._conf

    @property
    def gconf(self):
        return self._conf['global'] if 'global' in self._conf else self._conf['g'] if 'g' in self._conf else None

    @property
    def conf(self):
        return self._cconf

    @property
    def logger(self):
        return self._logger

    @property
    def stats(self):
        return self._stats

    def __init__(self, conf=None, logger=None, stats=None, *args, **kwargs):
        self._conf = conf

        if conf is not None:
            # Try to predict config
            names = Utils.camel2underscore(self.__class__.__name__)

            possible_conf_keys = list([names])

            for x in range(len(names)):
                possible_conf_keys.append(names[:-x])

            for pc in possible_conf_keys:
                if ''.join(pc) in self._conf:
                    self._cconf = self._conf[''.join(pc)]
                    break

                if '_'.join(pc) in self._conf:
                    self._cconf = self._conf['_'.join(pc)]
                    break

        self._stats = stats

        if logger is None and conf is not None:
            logger = logging.getLogger(__name__)
            logger.setLevel(self.gconf.logging.level)

            formatter = logging.Formatter(self.gconf.logging.format
                                          if self.gconf.logging.format else
                                          '%(asctime)s %(processName)s %(threadName)s %(module)s: %(message)s',
                                          datefmt='%b %d %H:%M:%S')

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

        self._logger = logger

        super(CLHMixin, self).__init__(*args, **kwargs)
# endregion
