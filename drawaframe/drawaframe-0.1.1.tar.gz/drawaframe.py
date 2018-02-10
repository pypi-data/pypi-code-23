import math


class Draw:

    @staticmethod
    def draw_char(char, quantity):
        print(char * int(quantity))

    @staticmethod
    def ndraw(space, n, content, border):
        space = int(math.ceil(space / 2))
        for i in range(n):
            print(border, " " * space, "{}".format(content), " " * space, border)
