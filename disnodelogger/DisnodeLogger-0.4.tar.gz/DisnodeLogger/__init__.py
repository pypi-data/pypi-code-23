import os
from colorama import init, Fore
from datetime import datetime
init(autoreset=True)

def Write(message):
    time = str(datetime.now().month) + "-" + \
        str(datetime.now().day) + "-" + str(datetime.now().year)
    dir = os.path.realpath(os.path.join(os.getcwd(), 'logs'))
    if not os.path.exists(dir):
        os.makedirs(dir)
    file = open(os.path.join(dir, time + '-LOG.txt'), 'a+')
    file.write(message + " \n")
    file.close()

def Info(title='', event='', message=''):
    time = str(datetime.now().month) + "/" + str(datetime.now().day) + "/" + str(datetime.now().year) + \
        ' ' + str(datetime.now().hour) + ":" + \
        str(datetime.now().minute) + ":" + str(datetime.now().second)

    print(Fore.WHITE + "[" + Fore.CYAN + " INFO  " + Fore.WHITE + "] " + Fore.MAGENTA + time + Fore.WHITE +
          " [" + str(title) + " " + Fore.CYAN + "(" + str(event) + ")" + Fore.WHITE + "]" + " " + str(message))

    Write(("[ INFO  ] " + time + " [" + str(title) +
           " (" + str(event) + ")] " + str(message)))


def Success(title='', event='', message=''):
    time = str(datetime.now().month) + "/" + str(datetime.now().day) + "/" + str(datetime.now().year) + \
        ' ' + str(datetime.now().hour) + ":" + \
        str(datetime.now().minute) + ":" + str(datetime.now().second)

    print(Fore.WHITE + "[" + Fore.GREEN + "SUCCESS" + Fore.WHITE + "] " + Fore.MAGENTA + time + Fore.WHITE +
          " [" + str(title) + " " + Fore.CYAN + "(" + str(event) + ")" + Fore.WHITE + "]" + " " + Fore.GREEN + str(message))

    Write(("[SUCCESS] " + time + " [" + str(title) +
           " (" + str(event) + ")] " + str(message)))


def Warning(title='', event='', message=''):
    time = str(datetime.now().month) + "/" + str(datetime.now().day) + "/" + str(datetime.now().year) + \
        ' ' + str(datetime.now().hour) + ":" + \
        str(datetime.now().minute) + ":" + str(datetime.now().second)

    print(Fore.WHITE + "[" + Fore.YELLOW + "WARNING" + Fore.WHITE + "] " + Fore.MAGENTA + time + Fore.WHITE +
          " [" + str(title) + " " + Fore.CYAN + "(" + str(event) + ")" + Fore.WHITE + "]" + " " + Fore.YELLOW + str(message))

    Write(("[WARNING] " + time + " [" + str(title) +
           " (" + str(event) + ")] " + str(message)))


def Error(title='', event='', message=''):
    time = str(datetime.now().month) + "/" + str(datetime.now().day) + "/" + str(datetime.now().year) + \
        ' ' + str(datetime.now().hour) + ":" + \
        str(datetime.now().minute) + ":" + str(datetime.now().second)

    print(Fore.WHITE + "[" + Fore.RED + " ERROR " + Fore.WHITE + "] " + Fore.MAGENTA + time + Fore.WHITE +
          " [" + str(title) + " " + Fore.CYAN + "(" + str(event) + ")" + Fore.WHITE + "]" + " " + Fore.RED + str(message))

    Write(("[ ERROR ] " + time + " [" + str(title) +
           " (" + str(event) + ")] " + str(message)))
