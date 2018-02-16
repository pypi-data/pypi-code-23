class ColorUtils:
    RETURN_TO_NORMAL = "\033[0m"
    BOLD = "\033[1m"
    GRAY = "\033[1;30m"
    RED = "\033[1;31m"
    GREEN = "\033[1;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[1;34m"
    MAGENTA = "\033[1;35m"
    CYAN = "\033[1;36m"
    WHITE = "\033[1;37m"
    RED_HIGHLIGHTED = "\033[1;41m"
    GREEN_HIGHLIGHTED = "\033[1;42m"
    YELLOW_HIGHLIGHTED = "\033[1;43m"
    BLUE_HIGHLIGHTED = "\033[1;44m"
    MAGENTA_HIGHLIGHTED = "\033[1;45m"
    CYAN_HIGHLIGHTED = "\033[1;46m"
    GRAY_HIGHLIGHTED = "\033[1;47m"


if __name__ == "__main__":
    cu = ColorUtils()

    all_colors = [a for a in dir(cu) if not a.startswith('__') and not callable(getattr(cu,a))]
    for color in all_colors:
        print("{0}This is {1}{2}".format(getattr(cu, color), str(color), cu.RETURN_TO_NORMAL))
