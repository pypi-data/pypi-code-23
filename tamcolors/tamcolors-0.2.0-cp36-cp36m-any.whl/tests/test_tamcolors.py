from tamcolors import*
from random import choice


numList = list(range(1,16,1))

def test():
    title = textBuffer(' ', (-1, -1), 110, 28)

    for y in range(28):
        for x in range(10):
            title.place(x*len('tamcolors'), y, 'tamcolors', background = choice(numList))

            
    title.printt()
    inputc(">>> ", (choice(numList), choice(numList)))

if __name__ == "__main__":
    test()
