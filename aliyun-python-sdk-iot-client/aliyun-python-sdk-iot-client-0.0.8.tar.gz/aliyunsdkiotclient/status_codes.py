# -*- coding: utf-8 -*-

from .structures import LookupDict

_codes = {
	1: ('Unacceptable protocol version',),
	2: ('Identifier rejected',),
	3: ('Server unavailable',),
	4: ('Bad username or password',),
	5: ('Not authorized',),
}

codes = LookupDict(name='status_codes')


def _init():
	for code, titles in _codes.items():
		for title in titles:
			setattr(codes, title, code)
			if not title.startswith(('\\', '/')):
				setattr(codes, title.upper(), code)

	def doc(code):
		names = ', '.join('``%s``' % n for n in _codes[code])
		return '* %d: %s' % (code, names)

	global __doc__
	__doc__ = (__doc__ + '\n' +
			   '\n'.join(doc(code) for code in sorted(_codes)))


_init()
