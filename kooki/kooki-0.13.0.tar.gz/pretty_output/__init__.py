from termcolor import colored
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler()
formatter = logging.Formatter('%(message)s')
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)
logger.addHandler(stream_handler)

_color_policy = True
_output_policy = True
_debug_policy = False
_message = ''


def output_control(func):
    def wrapper(*args, **kwargs):
        if _output_policy:
            func(*args, **kwargs)
    return wrapper


def set_color_policy(color_policy):
    global _color_policy
    _color_policy = color_policy


def set_output_policy(output_policy):
    global _output_policy
    _output_policy = output_policy


def set_debug_policy(debug):
    global _debug_policy
    _debug_policy = debug


@output_control
def color(full_text):
    results = full_text.split('[')
    for result in results:
        if result and result != '':
            second_results = result.split(']')
            color, text = second_results[0], second_results[1]
            _print_colored(text, color, end='')


@output_control
def title_1(name=None):
    if name:
        _step(name, 'white', '=', '[', ']')
    else:
        _step('', 'white', '=', no_space=True)


@output_control
def title_2(name=None):
    if name:
        _step(name, 'white', '-', '[', ']')
    else:
        _step('', 'white', '-', no_space=True)


@output_control
def title_3(name=None):
    if name:
        _step(name, 'yellow', '-')
    else:
        _step('', 'yellow', '-', no_space=True)


@output_control
def start_step(name):
    _step(name, 'yellow', '-')


@output_control
def error_step(name):
    _step(name, 'red', '-')


@output_control
def category(message):
    _print_colored('[' + message + ']', 'magenta')


@output_control
def error(message):
    _print_colored(message, 'red')


@output_control
def warning(message):
    _print_colored(message, 'orange')


@output_control
def info(message):
    _print_colored(message, 'cyan')


def _step(name, text_color, character, before='', after='', no_space=False, fixed_width=80):

    str_size = len(name)

    if (str_size % 2) == 0:
        number_of_dash_left = int((fixed_width - str_size) / 2)
        number_of_dash_right = number_of_dash_left

    else:
        number_of_dash_left = int((fixed_width - str_size) / 2)
        number_of_dash_right = number_of_dash_left + 1

    number_of_dash_left -= len(before)
    number_of_dash_right -= len(after)

    space = ' '
    if no_space:
        space = ''
        number_of_dash_left += 1
        number_of_dash_right += 1

    dash_left = ''
    for i in range(0, number_of_dash_left):
        dash_left += character
    dash_left += before

    dash_right = after
    for i in range(0, number_of_dash_right):
        dash_right += character

    _print_colored('{0}{3}{1}{3}{2}'.format(dash_left, name, dash_right, space), text_color)


@output_control
def push(message):
    pass


@output_control
def infos(infos, attrs):
    text = ''
    spaces = {}
    shift = 2

    for info in infos:
        for attr in attrs:
            name = attr[0]
            if name in spaces:
                if len(info[name]) + shift > spaces[name]:
                    spaces[name] = len(info[name]) + shift
            else:
                spaces[name] = len(info[name]) + shift

    for info in infos:
        for attr in attrs:
            name = attr[0]
            color = attr[1]
            text = ''
            if len(attr) > 2:
                text = attr[2]

            if isinstance(info[name], tuple):
                full_text = text + info[name][0]
                color = info[name][1]
            else:
                full_text = text + info[name]

            _print_colored(full_text, color, end='')
            _print_colored(' ' * (spaces[name] - len(info[name])), end='')
        _print_colored()


@output_control
def clear():
    pass


def _print_colored(text='', color='blue', end='\n'):
    global _message
    global _color_policy

    if _color_policy:
        if color:
            _message += colored(text, color)
        else:
            _message += colored(text)
    else:
        _message += text

    if end == '\n':
        logger.info(_message)
        _message = ''
