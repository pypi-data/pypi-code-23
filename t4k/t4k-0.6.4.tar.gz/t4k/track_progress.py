def pc(fraction, decimals=2):
    formatter = '%%.%df %%%%' % decimals
    return formatter % (fraction*100)

def progress(i, total, period=1000, prefix='', decimals=1):
	'''
	Prints a string representing the % completion when starting the
	`i`th step out of `total` steps, but only prints every `period` steps.
	'''
        formatter = '%s%2.' + str(decimals) + 'f %%'
	if i % period == 0:
		print formatter % (prefix, i/float(total) * 100)
