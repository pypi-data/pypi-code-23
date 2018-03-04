from __future__ import print_function
from menu import Menu
from .configuration import format_command
from .utils import list_to_comma_newline_separated_string
from .executor import execute


class MainMenu:
    commands_to_execute = None

    def __init__(self, configuration):
        self.configuration = configuration

        self.main_menu_message = "Choose a command to execute."
        self.main_menu_choices = self.generate_main_menu_choices()
        self.confirmation_choices = [
            ("Execute", self.execute_commands),
            ("Cancel", self.cancel)
        ]

        self.main_menu = Menu(
            title="Comrade",
            message=self.main_menu_message,
            options=self.main_menu_choices,
            refresh=self.refresh_menu
        )

    def show(self):
        self.main_menu.open()

    def execute_commands(self):
        self.main_menu.close()
        execute(self.commands_to_execute)

    def cancel(self):
        self.commands_to_execute = None

    def generate_main_menu_choices(self):
        menu_choices = []
        for i, choice in enumerate(self.configuration.choices):
            menu_choices.append(
                (choice.name, lambda i=i: self.handle_main_menu_choice(i)))
        menu_choices.append(("Exit", lambda: exit(0)))
        return menu_choices

    def handle_main_menu_choice(self, i):
        self.commands_to_execute = list()
        for command in self.configuration.choices[i].commands:
            self.commands_to_execute.append(format_command(command))

    def refresh_menu(self):
        if self.commands_to_execute:
            self.main_menu.set_options(self.confirmation_choices)
            self.main_menu.set_message("Commands to execute:\n\n{0}".format(
                list_to_comma_newline_separated_string(self.commands_to_execute)))
        else:
            self.main_menu.set_options(self.main_menu_choices)
            self.main_menu.set_message(self.main_menu_message)
