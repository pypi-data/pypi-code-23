import sys
from PIL import Image, ImageDraw, ImageFont

class Spiral:
    """Spiral

    Generates spiral that looks like:
        4 3
        1 2

    Than you can make all what you want with it.
    """
    def __init__(self):
        self.map = [[4, 3], [1, 2]]
        self.i = 4
        self.font = ImageFont.truetype("FreeSansBold.ttf")
    
    def __len__(self):
        """Last number in spiral(also the biggest one)
        """
        return self.i

    def __pow__(self, n):
        """Runs to len in n
        """
        self.run(pow(len(self), n))

    def comp(self, a):
        """Default comparator, always returns True
        """
        return True

    def cout(self, comp = None):
        """Writing spiral in console (bad when you have a big amount of numbers because console will cut and it won't be a table)
        """
        if comp == None:
            comp = self.comp
        ln = len(str(self.map[0][0]))
        for i in range(len(self.map)):
            for j in range(len(self.map[i])):
                if comp(self.map[i][j]) == True:
                    for k in range(abs(len(str(self.map[i][j])) - ln)):
                        sys.stdout.write(" ")
                    sys.stdout.write(str(self.map[i][j]) + " ")
                else:
                    sys.stdout.write((ln + 1) * " ")
            sys.stdout.write("\n")
    
    def img_out(self, filename = "output", comp = None):
        """Making image with spiral.

        Attributes:
            filename - the output file. It contains spiral. By default output.
            comp - comparator wich will check every number. Need to be only with 1 param. By default it's standart comparator that returns always true.
        """
        if comp == None:
            comp = self.comp
        out = []
        ln = len(str(self.map[0][0]))
        for i in range(len(self.map)):
            string = ""
            for j in range(len(self.map[i])):
                if comp(self.map[i][j]) == True:
                    for k in range(abs(len(str(self.map[i][j])) - ln)):
                        string += " "
                    string += str(self.map[i][j]) + " "
                else:
                    string += (ln + 1) * " "
            out.append(string)
        text_size = self.font.getsize(out[0])
        img = Image.new('RGB', (text_size[0], text_size[0]), "black")
        tmp_size = (text_size[0], text_size[1] + 1)
        for i in range(len(out)):
            tmp = Image.new('RGB', tmp_size, "black")
            tmp_draw = ImageDraw.Draw(tmp)
            tmp_draw.text((0, 0), out[i], font = self.font)
            img.paste(tmp, (0, 0 + text_size[0] / len(self.map) * i))
        img.save(filename + ".png")

    def move(self):
        """Makes new circle around the numbers. Need in function run.
        """
        self.map.append([])
        self.map.append([])
        for i in range(len(self.map) - 2):
            self.map[i].append(0)
            self.map[i].append(0)
        for i in range(2):
            for j in range(len(self.map)):
                self.map[len(self.map) - i - 1].append(0)
        for i in range(len(self.map) - 2, 0, -1):
            for j in range(len(self.map) - 2, 0, -1):
                self.map[i - 1][j - 1], self.map[i][j] = self.map[i][j], self.map[i - 1][j - 1]
            
    def run(self, n):
        """Generates spiral to n. May contains more the n because circle building full not to current
        """
        while(self.i < n):
            self.move()
            for j in range(len(self.map)):
                self.map[j][0] = self.i
                self.i += 1
            self.i -= 1
            for j in range(len(self.map)):
                self.map[len(self.map) - 1][j] = self.i
                self.i += 1
            self.i -= 1
            for j in range(len(self.map)):
                self.map[len(self.map) - 1 - j][len(self.map) - 1] = self.i
                self.i += 1
            self.i -= 1
            for j in range(len(self.map)):
                self.map[0][len(self.map) - 1 - j] = self.i
                self.i += 1
            self.i -= 1

    def previos(self):
        """Deletes last circle.
        """
        for i in range(1, len(self.map) - 1):
            for j in range(1, len(self.map[i]) - 1):
                self.map[i][j], self.map[i - 1][j - 1] = self.map[i - 1][j - 1], self.map[i][j]
        self.map.pop()
        self.map.pop()
        for i in range(len(self.map)):
            for j in range(2):
                self.map[i].pop()
        self.i = self.map[0][0]
