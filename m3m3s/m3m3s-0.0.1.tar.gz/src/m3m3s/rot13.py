#!/usr/bin/env python3


# usage EITHER
# ./rot13.py hello world
# echo hello world | ./rot13.py
# echo hello world | ./rot13.py | ./rot13.py # :D
# (command line "args" take presedence over stdin)

# good ole rot 13 encryption.
# I prefer the `tr "A-Z" "N-ZA-M"` version for the command line
# but wanted to mess with making a python "pipe" that could work with the system

# Also, I should write some "real" code to get my tshirt :D

# I thought about using the argparse thing from the decap script but wanted to try something different
#this means that I can't take any arguments in if I ever wanted to in the future...

import sys

#this is a terrible way to do this....

ENCRYPTDICT={}

normal="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
encrypted="nopqrstuvwxyzabcdefghijklmNOPQRSTUVWXYZABCDEFGHIJKLM"
for i, char in enumerate(normal): ENCRYPTDICT[char]=encrypted[i]

def encrypt(x):
    if x in ENCRYPTDICT: return ENCRYPTDICT[x]
    else: return x

#grab command line args if present, otherwise look for std in
def getInput():

    #the .join isn't the best way to do things
    #(it would ignore things similar to how `echo` does
    # Basically I'll ignore new lines
    if len(sys.argv) != 1: return " ".join(sys.argv[1:])

    #adding .strip() because i keep adding newlines and don't want to figureout why right now
    else: return " ".join(sys.stdin).strip()

def main():

    unencryptedString=getInput()

    encryptedString="".join([encrypt(x) for x in unencryptedString])

    print(encryptedString)

if __name__ == "__main__":
    main()
