from .resolvable import Resolvable
from sys import stdout, exit
import sys
from .input_grabbers import *


class UserMultiChoice(Resolvable):
    '''
    lets a user select may options from a list

    On resolution this will return a list of options

    'new' may be assigned to a function that will be called
    if the user selects new. This can allow subwizards that create new
    choices. Multiple calls to new() are allowed and all results will
    be returned
    '''

    def __init__(self, name, options,
                 new=None,
                 fineControlOnly=False,
                 display=lambda x: x):
        super(UserMultiChoice, self).__init__()
        self.name = name
        self.opts = [el for el in options]
        self.fineOnly = fineControlOnly
        self.new = new
        self.display = display

    def _resolve(self, useDefaults, fineControl):
        if ((len(self.opts) == 1 and not self.new) or
            useDefaults or
            (self.fineOnly and not fineControl)):
            return [self.opts[0]]
        elif len(self.opts) == 0 and not self.new:
            sys.stdout.write('No options for {} found.\n'.format(self.name))
            sys.exit(1)

        choices = []
        select_more_refs = True
        while select_more_refs:
            msg = '\tPlease select an option for {}:\n'
            stdout.write(msg.format(self.name))
            for i, opt in enumerate(self.opts):
                sys.stdout.write('\t\t[{}] {}\n'.format(i, self.display(opt)))
            if self.new:
                stdout.write('\t\t[{}] Pick new\n'.format(len(self.opts)))
            choice = out_input('\tPlease enter the index of your choice [0]: ')
            try:
                choice = int(choice)
            except ValueError:
                choice = 0
            if choice == len(self.opts):
                choices.append(self.new())
            else:
                choices.append(self.opts[choice])
            more = err_input('Select another reference? (y/[n]): ')
            if 'y' not in more.lower():
                select_more_refs = False

        chosenStr = ' '.join([str(choice) for choice in choices])
        stdout.write('Chose: {}\n'.format(chosenStr))
        return choices
