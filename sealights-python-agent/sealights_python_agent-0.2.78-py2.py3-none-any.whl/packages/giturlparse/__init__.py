# Imports
from python_agent.packages.giturlparse.parser import parse as _parse
from python_agent.packages.giturlparse.result import GitUrlParsed


def parse(url, check_domain=True):
	return GitUrlParsed(_parse(url, check_domain))

def validate(url, check_domain=True):
    return parse(url, check_domain).valid
