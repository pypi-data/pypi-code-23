#!/usr/bin/env python3

import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("text")
    args = parser.parse_args()

    text = args.text.upper().split()
    out = " ".join([c for s in text for c in s]) + '\n'
    for i in range(1,max([len(s) for s in text])):
        for s in text:
            try:
                out += s[i]
            except:
                out += ' '
            try:
                out += ' '*(len(s)-1)*2
            except:
                pass
            out += ' '
        else:
            out = out[0:-1] + '\n'
    else:
        out = out[0:-1]
    print(out)

if __name__ == "__main__":
    main()
