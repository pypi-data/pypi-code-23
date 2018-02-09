import configparser
import os.path


class _AbsolutePath:

    def __call__(self, track):
        return track.filename


class _RelativePath:

    def __init__(self, base_path):
        self.base_path = base_path

    def __call__(self, track):
        return os.path.relpath(track.filename, self.base_path)


def write(file, groups, music_dir, settings):
    """Write playlist to file according to settings."""
    paths = settings['playlist']['paths']
    if paths == 'absolute':
        filename_func = _AbsolutePath()
    elif paths == 'relative':
        filename_func = _RelativePath(music_dir)
    else:
        assert False

    format = settings['playlist']['format']
    if format == 'm3u8':
        _write_m3u8(file, filename_func, groups)
    elif format == 'pls':
        _write_pls(file, filename_func, groups)
    else:
        assert False


def _write_m3u8(file, filename_func, groups):
    for _, tracks in groups:
        for track in tracks:
            print(filename_func(track), file=file)


def _write_pls(file, filename_func, groups):
    cp = configparser.ConfigParser()
    cp.optionxform = str
    cp.add_section('playlist')

    file_number = 0
    for _, tracks in groups:
        for track in tracks:
            file_number += 1
            cp.set('playlist', f'File{file_number}', filename_func(track))

    cp.set('playlist', 'NumberOfEntries', str(file_number))
    cp.set('playlist', 'Version', '2')
    cp.write(file, False)
