import math

if __name__ == "__main__":
    from colorUtils import ColorUtils
else:
    from .colorUtils import ColorUtils

class OutputUtils:
    def __init__(self):
        self.colors = ColorUtils()


    '''
    Prints a colorized error message.

    @param msg: the message to print
    '''
    def error(self, msg):
        print("{0}ERROR:{1} {2}".format(self.colors.RED, self.colors.RETURN_TO_NORMAL, msg))


    '''
    Prints a colorized warning message.

    @param msg: the message to print
    '''
    def warning(self, msg):
        print("{0}WARNING:{1} {2}".format(self.colors.MAGENTA, self.colors.RETURN_TO_NORMAL, msg))


    '''
    Prints a colorized informational message.

    @param msg: the message to print
    '''
    def info(self, msg):
        print("{0}INFO:{1} {2}".format(self.colors.WHITE, self.colors.RETURN_TO_NORMAL, msg))


    '''
    Prints a stylalized banner containing a header and body.

    @param header: the header to print (must be less than 80 characters)
    @param msg: the message to print
    @raise ValueError: the given header is greater than 80 characters
    '''
    def banner(self, header, msg):
        if len(header) > 80:
            raise ValueError("Header is greater than 80 characters.")

        columns = 80
        stars_left = "*"*int(((columns - len(header)) / 2) - 1) # - 1 accounts for the space before header
        stars_right = "*"*(columns - len(stars_left) - len(header) - 2) # - 2 accounts for spaces before and after header

        print("{0}{1} {2} {3}".format(self.colors.WHITE, stars_left, header, stars_right))

        msg_line_len = (columns - 4) # - 4 accounts for a star and space at beginning and end.
        num_lines = math.ceil(len(msg) / msg_line_len) 

        # TODO: Handle cases where the line breaks in the middle of a word.
        for i in range(0, num_lines):
            start_location = i * msg_line_len
            line = msg[start_location:(start_location + msg_line_len)]

            # Pad the last line with spaces if needed.
            if i == (num_lines - 1):
                if len(line) < msg_line_len:
                    spaces = msg_line_len - len(line)
                    line = "{0}{1}".format(line, " "*spaces)

            print("* {0} *".format(line))

        print("{0}{1}".format("*"*80, self.colors.RETURN_TO_NORMAL))


if __name__ == "__main__":
    ou = OutputUtils()

    ou.error("This is an error.")
    ou.warning("This is a warning.")
    ou.info("This is info.")
    ou.banner("This header is longer but less than 80 characters.", "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque sit amet efficitur sapien. Nunc a posuere magna, nec lacinia quam. In lobortis varius lectus non volutpat. Morbi scelerisque purus quis ultricies elementum. Orci varius natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Curabitur semper eu dui vel ullamcorper. Ut pharetra nibh purus, ut tristique erat cursus ut. Vestibulum vel ex scelerisque, congue neque ac, rutrum dolor. Suspendisse interdum consectetur odio quis dictum. Nam lacinia cursus dapibus. Cras efficitur interdum nisi et auctor. Vivamus a nulla sollicitudin, efficitur massa vitae, dictum mauris. Nulla mauris purus, elementum eget tempor ut, tristique at nisl. Maecenas scelerisque nunc urna, eu viverra nunc ullamcorper eu. Ut tristique ornare sem vitae euismod.")
