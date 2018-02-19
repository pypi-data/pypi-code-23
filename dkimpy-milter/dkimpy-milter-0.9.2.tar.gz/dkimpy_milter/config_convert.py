def read_config(list):
  "Return new config object."
  for fn in list:
    if os.access(fn,os.R_OK):
      logging.config.fileConfig(fn)
      break
  cp = MilterConfigParser()
  cp.read(list)
  if cp.has_option('milter','datadir'):
        os.chdir(cp.get('milter','datadir'))
  conf = Config()
  conf.log = logging.getLogger('dkim-milter')
  conf.log.info('logging started')
  conf.socketname = cp.getdefault('milter','socketname', '/tmp/dkimmiltersock')
  conf.miltername = cp.getdefault('milter','name','pydkimfilter')
  conf.internal_connect = cp.getlist('milter','internal_connect')
  # DKIM section
  if cp.has_option('dkim','privkey'):
    conf.keyfile = cp.getdefault('dkim','privkey')
    conf.selector = cp.getdefault('dkim','selector','default')
    conf.domain = cp.getdefault('dkim','domain')
    conf.reject = cp.getdefault('dkim','reject')
    if conf.keyfile and conf.domain:
      try:
        with open(conf.keyfile,'r') as kf:
          conf.key = kf.read()
      except:
        conf.log.error('Unable to read: %s',conf.keyfile)
  return conf
