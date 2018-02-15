from sys import argv
from .core import Resizer


class ResizerConsole(Resizer):

    def show_progress(self, src, percent, count, total_count):
        print('{}/{} ({}%) : {}'.format(count, total_count, percent, src))

    def run(self):
        print('INPUT DIR  : {}'.format(self.input_dir))
        print('OUTPUT DIR : {}'.format(self.output_dir))
        print('IMAGE SIZE : {}'.format(self.size))
        if input('Continue(y/n)? >> ') == 'y':
            execution_time = super().run()
            print('TIME: {} seconds'.format(execution_time))


def main():
    input_dir = None
    output_dir = None
    size = None
    quality = None
    for option in argv[1:]:
        key, val = option.split('=')
        if key == '-in':
            input_dir = val
        elif key == '-out':
            output_dir = val
        elif key == '-size':
            size = tuple([int(v) for v in val.split('x')])
        elif key == '-quality':
            quality = int(val)

    if input_dir and size and quality:
        if not output_dir:
            output_dir = input_dir + '_CONVERTED'
        c = ResizerConsole(input_dir, output_dir, size, quality)
        c.run()
    else:
        print('Usage: batch-image-resize -in=<dir> [-out=<dir>] -size=<0x0> -quality=<1..95>')


if __name__ == '__main__':
    main()