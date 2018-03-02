from __future__ import print_function
from .file_finder import FileFinder
from menu import Menu
from ffmpy import FFmpeg
from os import path, remove, rename
import re

class Command:
    def __init__(self, ffmpeg_command, input_file, output_file, is_intermediate):
        self.ffmpeg_command = ffmpeg_command
        self.input_file = input_file
        self.output_file = output_file
        self.is_intermediate = is_intermediate


class Converto:
    menu_options = list()
    files = list()
    config = None
    main_menu = None
    satisfied_menu = None
    chosen_option = None
    user_input = None

    def __init__(self, config, user_input):
        self.config = config
        self.input = user_input

    def choose_ffmpeg_command(self):
        menu_options = self._generate_menu_options()
        self.main_menu = Menu(
            title="Choose which command you would like to run")
        self.main_menu.set_options(menu_options)
        self.main_menu.open()

    def find_files_to_operate_on(self):
        file_finder = FileFinder(
            self.chosen_option, self.user_input)
        while not file_finder.user_satisfied:
            self.files = file_finder.get_user_input()
            self.command_list = self._generate_command_list()
            file_finder._ask_if_user_is_satisfied_with_files(self.command_list)

    def convert(self):
        for command in self.command_list:
            command.ffmpeg_command.run()
            if command.is_intermediate:
                remove(command.input_file)
                new_output_filename = re.sub("-_-_INTERMEDIARY_[0-9]*_-_-","",command.output_file)
                rename(command.output_file, new_output_filename)
            if self.chosen_option.multi_input:
                return

    def _get_file_to_operate_on(self, input_file, i):
        previous_intermediary_file = self._get_output_filename(
            input_file, (i - 1))
        if i > 0:
            return previous_intermediary_file, True
        else:
            return input_file, False

    def _build_ffmpeg_command(self, input_file, command_index):
        command = self.chosen_option.commands[command_index]
        output_filename = self._get_output_filename(input_file, command_index)
        if self.chosen_option.multi_input:
            inputs = {}
            for f in self.files:
                inputs[f] = command.input_options
        else:
            inputs = {input_file: command.input_options}
        outputs = {output_filename: command.output_options}

        ff = FFmpeg(
            inputs=inputs,
            outputs=outputs
        )
        return ff, output_filename

    def _get_output_filename(self, filename, command_index):
        command = self.chosen_option.commands[command_index]
        if self._is_intermediary(command_index):
            output_filename = "{0}-_-_INTERMEDIARY_{1}_-_-.{2}".format(
                filename[:-4], command_index, command.output_extension)
        elif command.output_filename_format:
            fn, ext = path.splitext(filename)
            output_filename = command.output_filename_format.format(
                input_filename=fn, extension=command.output_extension)
        else:
            output_filename = "{0}.{1}".format(
                filename[:-4], command.output_extension)
        return output_filename

    def _is_intermediary(self, index):
        return index != len(self.chosen_option.commands) - 1

    def _generate_menu_options(self):
        menu_options = list()
        for i, opt in enumerate(self.config.options):
            menu_options.append(
                (opt.name, lambda i=i: self._handle_main_menu_choice(i)))
        return menu_options

    def _handle_main_menu_choice(self, option_index):
        self.main_menu.close()
        self.chosen_option = self.config.options[option_index]

    def _generate_command_list(self):
        command_list = list()
        for f in self.files:
            for i, command in enumerate(self.chosen_option.commands):
                input_file, was_intermediate = self._get_file_to_operate_on(
                    f, i)
                ff, output_file = self._build_ffmpeg_command(input_file, i)
                command_list.append(
                    Command(ff, input_file, output_file, was_intermediate))
        return command_list
