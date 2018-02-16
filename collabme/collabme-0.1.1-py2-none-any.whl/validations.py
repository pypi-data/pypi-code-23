import re
import bson


def ip(data):
    match = re.search('^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9])$',data)
    if match:
	return True
    else:
	return False


def alph(data):
    if str(data).isalpha():
        return True
    else:
        return False


def aplhnum(data):
    if str(data).isalnum():
	return True
    else:
	return False


def api(data):
    if type(data) == str:
	if data.count('-') ==4:
	    if aplhnum(data.split('-')[0]) and aplhnum(data.split('-')[1]) and aplhnum(data.split('-')[2]) and aplhnum(data.split('-')[3]):
		return True
	    else:
		return False
        else:
	    return False
    else:
	return False


def version(data):
    if type(data) == float or type(data) ==int :
	return True
    else:
	return False

