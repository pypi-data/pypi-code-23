import sys
import os

sys.path.append(os.path.abspath(os.path.join('..', 'buildlib')))

from typing import Union
from buildlib import yaml, semver, build, git
from cmdi import CmdResult, print_summary

CFG_FILE = 'Project'
CFG = yaml.load(
    file=CFG_FILE,
    keep_order=True
)

__version__ = CFG.get('version')


def get_version_from_user() -> str:
    """
    Get new Version number from user or use the one from CONFIG.yaml.
    """
    return semver.prompt.semver_num_by_choice(
        cur_version=CFG.get('version')
    )


def build_wheel(
) -> Union[CmdResult, None]:
    """"""
    return build.cmd.build_python_wheel(
        clean_dir=True
    )


def push_registry(
) -> Union[CmdResult, None]:
    """"""
    return build.cmd.push_python_wheel_to_pypi(
        clean_dir=True
    )


def bump_version(
    new_version: str = None,
) -> Union[CmdResult, None]:
    """
    Bump (update) version number in CONFIG.yaml.
    """
    if not new_version:
        new_version: str = get_version_from_user()

    return build.cmd.update_version_num_in_cfg(
        config_file=CFG_FILE,
        semver_num=new_version,
    )


def bump_git() -> None:
    """"""
    results = []

    should_bump_version = build.prompt.should_update_version(
        default='y'
    )

    if should_bump_version:
        version = get_version_from_user()
    else:
        version = CFG.get('version')

    seq_settings = git.seq.get_settings_from_user(
        should_tag_default=version != CFG.get('version'),
        should_bump_any=True,
        version=version,
    )

    if should_bump_version:
        results.append(bump_version(
            new_version=version,
        ))

    results.extend(git.seq.bump_sequence(seq_settings))

    print_summary(results)


def bump_all() -> None:
    """"""
    results = []

    should_bump_version: bool = build.prompt.should_update_version(
        default='y'
    )

    if should_bump_version:
        version = get_version_from_user()
    else:
        version = CFG.get('version')

    should_build_wheel: bool = build.prompt.should_build_wheel(
        default='y'
    )

    should_push_registry: bool = build.prompt.should_push_pypi(
        default='y' if should_bump_version else 'n'
    )

    if should_bump_version:
        results.append(bump_version(
            new_version=version,
        ))

    git_settings = git.seq.get_settings_from_user(
        should_tag_default=version != CFG.get('version'),
        version=version,
    )

    if should_build_wheel:
        results.append(build.cmd.build_python_wheel(
            clean_dir=True,
        ))

    if git_settings.should_bump_any:
        results.extend(git.seq.bump_sequence(git_settings))

    if should_push_registry:
        results.append(build.cmd.push_python_wheel_to_pypi(
            clean_dir=True
        ))

    print_summary(results)
