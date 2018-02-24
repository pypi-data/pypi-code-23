from __future__ import print_function
from huntsgambit.huntsgambit.utils import *
import argparse
import os

__version__ = '0.2.3'


def hunts_gambit():
    """
    Has your pass been compromised? Let's find out!
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('-f', '--forget_pass', action='store_true',
                        help="If this option is enabled, clear the last console line from .bash_history")
    parser.add_argument('password', help="Enter the password you want to check for pwnage")
    parser.add_argument('-h', '--help', action='help',
                        help="""This module queries Troy Hunt's excellent PwnedPasswords repository
                        to see if your password has ever been 1337 h4x0red before.
                        
                        HOW IT WORKS: Using the k-anonimity functionality of PwnedPasswords, hunts_gambit
                        sends the first five characters of your password's hash to PP and retrieves all possible
                        password hashes that begin with those characters. It then processes whether any of these is 
                        _your_ password, and tells you the result in a friendly output message.
                        
                        NOTE: Your full password (neither in plaintext nor hashed) is _never_ sent out to the interwebs.
                        All processing is done locally on your machine""")
    args = parser.parse_args()
    # get plaintext pass
    try:
        plaintext_pass = args.password
    except TypeError:
        print("Gonna need a password to check against there, bud. Run pwnage_checker -h for help")
        return
    # process it against PP
    gambit = Pwnification(plaintext_pass)
    if gambit.is_pass_compromised:
        pwd_list = gambit.pass_list
        freq = pwd_list[pwd_list.password == gambit.hashed_pass].frequency.iloc[0]
        print_stats(freq)
    else:
        print("Yeah you're fine... for now.")
    # clear last line of terminal output
    if args.forget_pass:
        os.system('let "line_num=$HISTCMD-1"; history -d $line_num')


if __name__ == '__main__':
    hunts_gambit()
