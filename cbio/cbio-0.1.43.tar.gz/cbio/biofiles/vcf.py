import tailer as tl


class VCF():
    def __init__(self, filepath):
        self.filepath = filepath

        self.get_header()

    def get_header(self):

        self.header = ""

        for line in open(self.filepath, 'r'):
            if line.startswith('#CHROM'):
                self.header = line.strip('\n').split('\n')

        if self.header == "":
            self.header = ['CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO', 'FORMAT', 'SAMPLE']


    def head(self, lines, pretty=False):
        print('==> HEAD OF VCF FILE <==')
        c = 0
        fhand = open(self.filepath, 'r')
        for line in fhand:
            if line.startswith('##'):
                continue
            elif line.startswith('#'):
                print(line.strip('\n'))
                continue

            line = line.strip('\n').split('\t')

            if pretty:
                line[7] = line[7][0:4] + '[...]' + line[7][-7:]
            print('\t'.join(line))
            c += 1

            if c == lines:
                print()
                fhand.close()
                break

        return ()

    def tail(self, lines, pretty=False):
        c = 0
        print('==> TAIL OF VCF FILE <==')
        print('#' + "\t".join(self.header))

        fhand = open(self.filepath)
        lastLines = tl.tail(fhand, lines)
        fhand.close()

        for line in lastLines:
            if line.startswith('##'):
                continue
            elif line.startswith('#'):
                print(line.strip('\n'))
                continue

            line = line.strip('\n').split('\t')

            if pretty:
                line[7] = line[7][0:4] + '[...]' + line[7][-7:]
            print('\t'.join(line))
            c += 1

            if c == lines:
                print()
                break

        return ()
