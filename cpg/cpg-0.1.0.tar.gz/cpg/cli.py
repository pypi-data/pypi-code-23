import sys

import click
import toml

from . import groups, playlist, settings, version


@click.command()
@click.option('-a', '--absolute', 'paths',
              flag_value='absolute',
              help='Output playlist with absolute paths.')
@click.option('-c', '--config',
              type=click.File(),
              help='Configuration file path.')
@click.option('-f', '--format',
              type=click.Choice(('m3u8', 'pls')),
              help='Playlist format.')
@click.option('-r', '--relative', 'paths',
              flag_value='relative',
              help='Output playlist with relative paths.')
@click.version_option(version, '-v', '--version')
@click.argument('audio_dir', type=click.Path(exists=True))
@click.argument('playlist_file', type=click.File(mode='w'))
def cli(audio_dir, config, format, paths, playlist_file):
    """CPG (stands for configurable playlist generator) recursively scans AUDIO_DIR
    for audio files and outputs PLAYLIST_FILE with the encountered files.

    The playlist's format and the type of its paths (absolute or relative) can
    be specified in OPTIONS or via a configuration file.  More complex playlist
    generation requirements can only be specified through a configuration file.

    Supported advanced playlist generation features include categorizing tracks
    into groups, sorting tracks within groups or omitting certain tracks from
    the playlist.  The resulting groups of tracks are shuffled (preserving the
    specified order of tracks within each group) before writing the playlist.

    For detailed usage instructions, including how to use CPG's advanced
    features, please refer to https://cpg.readthedocs.io/.
    """
    setts = settings.default()

    if config:
        try:
            loaded_setts = toml.load(config)
        except (toml.TomlDecodeError, ValueError) as e:
            s = f'Error reading configuration file "{config.name}": {e}'
            click.echo(s, err=True)
            sys.exit(1)

        try:
            settings.merge(loaded_setts, setts)
        except settings.InvalidSetting:
            s = f'Malformed setting in configuration file "{config.name}".'
            click.echo(s, err=True)
            sys.exit(1)

    if format:
        settings.set_format(format, setts)
    if paths:
        settings.set_paths(paths, setts)

    gs = groups.create(audio_dir, setts)
    playlist.write(playlist_file, gs, audio_dir, setts)


def main():
    cli(prog_name='cpg', help_option_names=('-h', '--help'))
