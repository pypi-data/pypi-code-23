# Copyright (C) 2018 Yuval Langer
#
# This file is part of Meditate.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


"""Meditate.

Usage:
  meditate [options]
           [--session-sound=PATH]
           [--interval-sound=PATH]
           [--session-time=TIME]
           [--interval-time=TIME]
  meditate [options]

Options:
  -h --help                This hopefully helpful help message.

  --usage                  A shorter version of the above.

  -v --verbose             Print all the logging messages!

  --debug                  Same as the above.

  --interval-sound=PATH    Path to a wave file signifying the passage of
                              time, reminding you to come back from
                              mind wandering.

  --start-stop-sound=PATH  Path to a wave file denoting the start and stop of
                             a session.

  --session-time=TIME      Total meditation session time in
                             seconds. [default: 1200]

  --interval-time=TIME     Length of each interval in seconds. [default: 300]
"""

import itertools
import json
import logging
import os
import pathlib

import attr


import docopt

import pkg_resources

import simpleaudio

import trio

command_line_arguments = docopt.docopt(__doc__)

if (
    command_line_arguments.get("--verbose")
    or command_line_arguments.get("--debug")
):
    logging.basicConfig(level="DEBUG")

logger = logging.getLogger(__name__)


def validate_path_exists(instance, attribute, value) -> None:
    """Make sure that the provided path's file actually exists."""
    value.resolve(strict=True)
    logger.debug("Path %s resolved", value)


@attr.s
class Configuration:
    """Configuration."""

    start_stop_sound_path: pathlib.Path = attr.ib(
        validator=validate_path_exists,
    )
    interval_sound_path: pathlib.Path = attr.ib(
        validator=validate_path_exists,
    )
    interval_time: float = attr.ib()
    session_time: float = attr.ib()


def make_default_config() -> Configuration:
    """Generate configuration."""
    bell_resource_filename = pkg_resources.resource_filename(
        __name__,
        "sound/140128__jetrye__bell-meditation-cleaned.wav",
    )
    bell_file_path = pathlib.Path(bell_resource_filename)

    return Configuration(
        start_stop_sound_path=bell_file_path,
        interval_sound_path=bell_file_path,
        interval_time=1200,
        session_time=3600,
    )


@attr.s
class Session:
    """Meditation session."""

    configuration: Configuration = attr.ib()

    def __attrs_post_init__(self) -> None:
        """Load files into memory."""
        self.interval_wave_object = simpleaudio.WaveObject.from_wave_file(
            self.configuration.interval_sound_path.as_posix(),
        )
        self.start_stop_wave_object = simpleaudio.WaveObject.from_wave_file(
            self.configuration.start_stop_sound_path.as_posix(),
        )

    async def meditate(self) -> None:
        """Start meditation session."""
        print("Start meditation.")
        self.start_stop_wave_object.play()

        with trio.move_on_after(self.configuration.session_time):
            for i in itertools.count(1):
                print(f"Interval {i} starts.")
                await trio.sleep(self.configuration.interval_time)
                print(f"Interval {i} ends.")
                self.interval_wave_object.play()

        self.start_stop_wave_object.play()
        print("End meditation.")


def load_user_configuration_file() -> Configuration:
    """Load user configuration file."""
    _home = pathlib.Path('~').expanduser()
    xdg_config_home = pathlib.Path(
        os.environ.get('XDG_CONFIG_HOME')
        or (_home / '.config'),
    )
    config_filepath = xdg_config_home.joinpath('meditate.json')
    with open(config_filepath, 'r') as f:
        configuration = Configuration(**json.load(f))

    return configuration


def load_config(
        command_line_arguments: dict,
) -> Configuration:
    """Load configuration.

    Use command line arguments,
      or user configuration (TODO),
      or default configuration.
    """
    default_configuration = make_default_config()

    interval_time = float(
        command_line_arguments["--interval-time"] or
        default_configuration.interval_time,
    )

    session_time = float(
            command_line_arguments["--session-time"] or
            default_configuration.session_time,
    )

    interval_sound_path = pathlib.Path(
        command_line_arguments["--interval-sound"] or
        default_configuration.interval_sound_path,
    ).expanduser().absolute()

    start_stop_sound_path = pathlib.Path(
        command_line_arguments["--start-stop-sound"] or
        default_configuration.start_stop_sound_path,
    ).expanduser().absolute()

    configuration = Configuration(
        start_stop_sound_path=start_stop_sound_path,
        interval_sound_path=interval_sound_path,
        interval_time=interval_time,
        session_time=session_time,
    )

    logger.debug("Configuration: %s", configuration)

    return configuration


def main() -> None:
    """Run program."""
    configuration = load_config(command_line_arguments)

    session = Session(configuration=configuration)

    trio.run(session.meditate)


if __name__ == '__main__':
    main()
