"""
Command line utility for my personal needs.


Commands:
    fixjpg - Recreate .jpg files
    cleanxcodeswifttemplates - Remove redunant boilerplate text from .swift templates
    pypiupload - Build, upload to PyPI, clean temporary directories (build, dist, *.egginfo)
    gitinit - Initialize and set up git repo
    cleanappdelegate - Replace AppDelegate.swift with my template
    svg2pdf - Convert <path> from SVG to PDF
"""
import pathlib
import re
import subprocess

import click

from PIL import Image


def recreate_image(path: str):
    """
    Read PIL-supported image and save it at same path.
    :param path: Path to image
    """
    img = Image.open(path)
    img.save(path)


GITIGNORE = {
    'xcode': [
        "*.xcodeproj",
    ],
    'py': [
        ".idea/",
        "__pycache__/",
        "build/",
        "dist/",
        "*.egg-info/",
    ],
}


APP_DELEGATE = """\
import UIKit


@UIApplicationMain
class AppDelegate: UIResponder, UIApplicationDelegate {

    // MARK: :UIApplicationDelegate

    var window: UIWindow?

    func application(_ application: UIApplication, 
                     didFinishLaunchingWithOptions launchOptions: [UIApplicationLaunchOptionsKey: Any]?) -> Bool {
        return true
    }

}
"""


@click.group()
def gin():
    """
    Command line utility for my personal needs.
    """
    pass


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True))
def fixjpg(paths):
    """
    Fix .jpg files by simply recreating image.

    If <paths> not specified, recreate .jpg files found in current working directory.
    For every file path in <paths> recreate image without checking extension.
    For every directory path in <paths> recreate .jpg files found in it.
    """
    # Sort out what files to recreate / Understand command input
    paths = [pathlib.Path(i) for i in paths]
    if not paths:
        paths = [pathlib.Path.cwd()]
    files = []  # what to recreate exactly
    for value in paths:
        if value.is_dir():
            files.extend([i for i in value.iterdir() if i.suffix == '.jpg'])
        else:
            files.append(value)

    if not files:
        click.echo("Nothing to recreate / .jpg files are not found")
        return
    for i in files:
        click.echo(f"Recreating {i}")
        recreate_image(i)


@click.command()
@click.argument("path", default="/Applications/Xcode.app", type=click.Path(exists=True))
def cleanxcodeswifttemplates(path):
    """
    Remove fileheader from Xcode swift templates. sudo required

    Remove '//___FILEHEADER___\n\n' from any file that fits all rules:
    - it is inside <path> ('/Application/Xcode.app' by default) and its subdirectories
        - it is inside 'Templates' directory and its subdirectories
    - it matches pattern "^//___FILEHEADER___\n\n"
    """
    path = pathlib.Path(path) / "Contents" / "Developer"
    pattern = "^//___FILEHEADER___\n\n"
    glob = "**/Templates/**/*.swift"

    click.echo("Starting to clean Xcode swift templates")
    for i in path.glob(glob):
        with open(i) as file:
            content = file.read()
        # edit all files vs containing pattern only?
        if re.match(pattern, content):
            new = re.sub(pattern, "", content, count=1)
            click.echo(f"Clearing: {i}")
            with open(i, mode='w') as file:
                file.write(new)


@click.command()
def pypiupload():
    """
    Build, upload to PyPI, clean temporary directories (build, dist, *.egginfo).

    Just execute following bash commands:
    > python3 setup.py sdist
    > python3 setup.py bdist_wheel
    > twine upload dist/*
    > rm -rf build
    > rm -rf dist
    > rm -rf *.egg-info
    """
    click.echo('Building...')

    click.echo('Running: python3 setup.py sdist')
    subprocess.run(("python3", "setup.py", "sdist",), check=True)

    click.echo('Running: python3 setup.py bdist_wheel')
    subprocess.run(("python3", "setup.py", "bdist_wheel",), check=True)

    click.echo('Uploading...')
    click.echo('Running: twine upload dist/*')
    subprocess.run(("twine", "upload", "dist/*",), check=True)

    click.echo('Cleaning...')

    click.echo('Running: rm -rf build')
    subprocess.run(("rm", "-rf", "build",))

    click.echo('Running: rm -rf dist')
    subprocess.run(("rm", "-rf", "dist",))

    click.echo('Running: rm -rf *.egg-info')
    # '*.egg-info' doesn't work like i want
    path = list(pathlib.Path().glob("*.egg-info"))[0]
    subprocess.run(("rm", "-rf", f"{path}",))


@click.command()
@click.option("--xcode", is_flag=True, help="Initialize git for new Xcode project")
@click.option("--py", is_flag=True, help="Initialize git for Python project")
def gitinit(xcode, py):
    """
    Initialize and set up git repo.

    `--xcode` and `--py` options are mutually exclusive.

    Basic behaviour:
        1. git init
        2. create .gitignore file specific for project type
        3. git status
        4. promt for commit
        5. git commit -m "init"

    Xcode:
        1. git init
        2. create .gitignore
        3. git add *.xcodeproj/project.pbxproj
        4. git status
        5. promt for commit
        6. git commit -m "init"
    """
    # Validation
    if xcode and py:
        click.echo("<xcode> and <py> options should never be used in the same time", err=True)
        return
    if not (xcode or py):
        click.echo("<xcode> or <py> option should be specified", err=True)
        return
    if pathlib.Path('.git').exists():
        click.echo("Git repository already exists", err=True)
        return

    click.echo("Initializing git repository...")
    subprocess.run(("git", "init",))

    click.echo("Creating .gitignore file...")
    ignore_entries = None
    if xcode:
        ignore_entries = GITIGNORE['xcode']
    elif py:
        ignore_entries = GITIGNORE['py']
    assert ignore_entries is not None
    with open(".gitignore", mode='w') as file:
        file.writelines(ignore_entries)
        file.write('\n')

    # Xcode only - git add -f .pbxproj
    if xcode:
        click.echo("Adding .pbxproj file...")
        paths = list(pathlib.Path().rglob("project.pbxproj"))
        if len(paths) != 1:
            click.echo(f"There should be only one .pbxproj file, {len(paths)} found")
            return
        # relative to current working directory
        path = paths[0].relative_to(pathlib.Path())
        subprocess.run(("git", "add", "-f", f"{path}",))

    click.echo("Adding all...")
    subprocess.run(("git", "add", ".",))

    click.echo("Showing status...")
    subprocess.run(("git", "status",))

    if click.confirm("Do you want to commit?"):
        click.echo("Making initial commit...")
        subprocess.run(("git", "commit", "-m", "init"))


@click.command()
def cleanappdelegate():
    """
    Replace AppDelegate.swift with my template
    """
    paths = list(pathlib.Path().rglob("AppDelegate.swift"))
    if len(paths) != 1:
        click.echo("There should be only one AppDelegate.swift file, {len(paths)} found", err=True)
        return

    click.echo("Clearing...")
    with open(paths[0], mode='w') as file:
        file.write(APP_DELEGATE)
    click.echo("Done")


@click.command()
@click.argument("path", type=click.Path(exists=True))
def svg2pdf(path):
    """
    Convert <path> from SVG to PDF.

    `svg2pdf` command-line tool required (from `svglib` python library)
    """
    subprocess.run(("svg2pdf", path,), check=True)


gin.add_command(fixjpg)
gin.add_command(cleanxcodeswifttemplates)
gin.add_command(pypiupload)
gin.add_command(gitinit)
gin.add_command(cleanappdelegate)
gin.add_command(svg2pdf)


if __name__ == '__main__':
    gin()
