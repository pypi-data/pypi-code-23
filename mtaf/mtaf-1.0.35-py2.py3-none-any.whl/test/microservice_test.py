from lib.microservices import Microservices
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("login", type=str, help="<phone number>@<domain>")
parser.add_argument('password', help='password',
                    default='vqda')
args = parser.parse_args()

print "login = %s" % args.login
print "password = %s" % args.password
ms = Microservices(args.login, args.password)
for cat in 'new', 'saved', 'deleted':
    print "%s %s" % (cat, ms.get_vm_count(cat))
