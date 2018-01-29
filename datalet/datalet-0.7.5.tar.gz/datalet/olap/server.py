#!/usr/bin/env python
# -*- coding: utf-8  -*-


from gateway_lanucher import GatewayLanucher

if __name__ == "__main__":
	lanucher = GatewayLanucher()
	try:
		lanucher.start()
	except Exception as err:
		print(err)
	#finally:
	#	lanucher.stop()
