
import os
import glob

import shutil
import pathspec

import click


@click.command()
@click.argument('src',
                metavar='<source>',
                type=click.Path(exists=True,
                                dir_okay=True,
                                readable=True),
                required=True,
                nargs=1)
@click.argument('dst',
                metavar='<destination>',
                type=click.Path(exists=False),
                required=True,
                nargs=1)
@click.option('--overwrite',
              '-ow',
              help='Overwrite dst folder if exists',
              is_flag=True)
@click.option('--git',
              '-g',
              help='Copy .git folder if exists',
              is_flag=True)
def main(src, dst, overwrite, git):
    """This script copies folder <source> which must be a git repo
    (i.e. containing a .gitignore file) to folder <destination>.
    Only those files not mentionned in .gitignore are copied.

    If <overwrite> is set the <destination> folder contents
    are overwritten.

    If <git> is set the .git folder in <source> if any is copied to 
    <destination>.
    """
    click.echo('source = {}'.format(os.path.abspath(src)))
    click.echo('destination = {}'.format(os.path.abspath(dst)))
    click.echo('src is a git repo ? {}'.format(is_git_repo(src)))

    if os.path.exists(dst):
        click.echo('destination folder exists')
        if not overwrite or (overwrite and not click.confirm('overwrite ?')):
            click.echo('abort')
            return
        else:
            delete_folder(dst)
    else:
        click.echo('destination folder will be created')

    click.echo('make copy')

    ig_func = build_ignore_function(src, incl_git=git)

    make_copy(src, dst, ignore_func=ig_func)
    click.echo('done')


def is_git_repo(src):
    """
    """
    path = os.path.join(src, '.git')
    return os.path.exists(path)


def remove_empty_folders(path):
    """
    remove empty directories
    as shutil.copytree cannot do it
    """
    for (_path, _dirs, _files) in os.walk(path, topdown=False):
        # skip remove
        if _files:
            continue
        if '.git' in _path:
            continue
        
        try:
            delete_folder(_path)
            print(_path)
        except OSError as e:
            print('error :', e)


def make_copy(src, dst, ignore_func=None):
    """
    shutil copytree call
    """
    shutil.copytree(src, dst, ignore=ignore_func)
    remove_empty_folders(dst)


def delete_folder(drc):
    """
    shutil rmtree
    """
    shutil.rmtree(drc)


def build_ignore_function(src, incl_git=False):

    path = os.path.join(src, '.gitignore')
    with open(path, 'r') as f:
        # .gitignore lines
        spec_src = [e.rstrip() for e in f.readlines()]
        
        # .git folder
        if not incl_git:
            spec_src.append('.git/*')

        spec = pathspec.PathSpec.from_lines('gitwildmatch', spec_src)

    # data to recompose path relative to source
    abs_src = os.path.abspath(src)
    len_abs_src = len(abs_src) + 1

    def ig_f(curr_dir, files):
        """
        ignore function to be used in shutil.copytree
        """
        def path_rel_src(f):
            """
            build path relative to source
            necessary to use pathspec
            """
            abs_f = os.path.abspath(os.path.join(curr_dir, f))
            path = abs_f[len_abs_src:]
            return path

        ignored_files = [f for f in files
                         if spec.match_file(path_rel_src(f))]

        return ignored_files

    return ig_f
