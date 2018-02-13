#!/usr/bin/env python
# coding: utf-8

from __future__ import unicode_literals

import click as c

from . import core


@c.group(context_settings={'help_option_names': ['-h', '--help']})
def main():
    pass


class CommaSeparatedList(c.ParamType):

    name = 'CommaSeparatedList'

    def convert(self, value, param, ctx):
        if isinstance(value, list):
            return value

        return [s.lower().strip() for s in value.split(',')]


pic_exts_opt = c.option(
    '--pic-exts', '-p',
    default='jpg,jpeg',
    show_default=True,
    help='Comma separated and case insensitive list of picture file extensions',
    type=CommaSeparatedList(),
)

dir_opt = c.option(
    '--dir', '-d',
    default='.',
    show_default=True,
    help='Target directory to search for orphans',
    type=c.Path(exists=True, file_okay=False),
)

batch_opt = c.option('--batch', '-b', is_flag=True, help='Delete raw files without confirmation')


@main.command('remove-orphan-raws', help='Removes raw files that do not match any picture')
@dir_opt
@pic_exts_opt
@c.option('--raw-exts', '-r', default='nef,cn2', show_default=True,
          help='Comma separated and case insensitive list of raw file extensions to be removed',
          type=CommaSeparatedList())
@batch_opt
def remove_orphans(dir, pic_exts, raw_exts, batch):
    core.remove_raw_orphans(**locals())


@main.command('rename-to-timestamp', help='Renames files to their timestamp')
@dir_opt
@pic_exts_opt
@batch_opt
def rename_to_ts(dir, pic_exts, batch):
    core.rename_to_ts(**locals())


if __name__ == '__main__':
    main()
