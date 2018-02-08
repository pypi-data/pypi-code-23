#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __coconut_hash__ = 0xff2d6ec8

# Compiled with Coconut version 1.3.1-post_dev17 [Dead Parrot]

# Coconut Header: -------------------------------------------------------------

import sys as _coconut_sys, os.path as _coconut_os_path
_coconut_file_path = _coconut_os_path.dirname(_coconut_os_path.abspath(__file__))
_coconut_sys.path.insert(0, _coconut_file_path)
from __coconut__ import _coconut, _coconut_NamedTuple, _coconut_MatchError, _coconut_tail_call, _coconut_tco, _coconut_igetitem, _coconut_base_compose, _coconut_forward_compose, _coconut_back_compose, _coconut_forward_star_compose, _coconut_back_star_compose, _coconut_pipe, _coconut_star_pipe, _coconut_back_pipe, _coconut_back_star_pipe, _coconut_bool_and, _coconut_bool_or, _coconut_none_coalesce, _coconut_minus, _coconut_map, _coconut_partial
from __coconut__ import *
_coconut_sys.path.remove(_coconut_file_path)

# Compiled Coconut: -----------------------------------------------------------

sys = _coconut_sys  # line 1

MARKER = r"/###/"  # type: str  # line 3


def usage(appname, version: 'str', short: 'bool'=False):  # line 6
    print("{marker} {appname}{version}".format(marker=MARKER, appname=appname, version="" if not short else " (PyPI: %s)" % version))  # line 7
    if not short:  # line 8
        print("""

Usage: {cmd} <command> [<argument>] [<option1>, ...]        When operating in offline mode, or command is one of "help", "offline", "version"
       {cmd} --sos <sos command and arguments>              When operating in offline mode, forced passthrough to SOS
       {cmd} --vcs <underlying vcs command and arguments>   When operating in offline mode, forced passthrough to traditional VCS
       {cmd} <underlying vcs command and arguments>         When operating in online mode, automatic passthrough to traditional VCS

  Repository handling:
    offline [<name>]                                      Start working offline, creating a branch (named <name>), default name depending on VCS
      --compress                                            Compress versioned files (same as `sos config set compress on && sos offline`)
      --track                                               Setup SVN-style mode: users add/remove tracking patterns per branch
      --picky                                               Setup Git-style mode: users pick files for each operation
      --strict                                              Always compare entire file contents
    online                                                Finish working offline
    dump [<path>/]<name[.sos.zip]>                        Dump entire repository into an archive file

  Working with branches:
    branch [<name>]                                       Create a new branch from current file tree and switch to it
      --last                                                Use last revision, not current file tree, but keep file tree unchanged
      --stay                                                Don't switch to new branch, continue on current one
    destroy [<branch>]                                    Remove (current or specified) branch entirely
    switch [<branch>][/<revision>]                        Continue work on another branch
      --meta                                                Only switch file tracking patterns for current branch, don't update any files
    update [<branch>][/<revision>]                        Integrate work from another branch
      --add | --rm | --ask                                  Only add new files / only remove vanished files / Ask what to do. Default: add and remove
      --add-lines | --rm-lines | --ask-lines                Only add inserted lines / only remove deleted lines / Ask what to do. Default: add and remove
      --add-chars | --rm-chars | --ask-chars                Only add new characters / only remove vanished characters / Ask what to do. Default: add and remove
      --eol                                                 Use EOL style from the integrated file instead. Default: EOL style of current file

  Working with files:
    changes [<branch>][/<revision>]                       List changed paths vs. last or specified revision
    commit [<message>]                                    Create a new revision from current state file tree, with an optional commit message
      --tag                                               Memorizes commit message as a tag that can be used instead of numeric revisions
    diff [<branch>][/<revision>]                          List changes in file tree (or `--from` specified revision) vs. last (or specified) revision
      --to=branch/revision                                Take "to" revision as target to compare against (instead of current file tree state)
    ls [<folder path>] [--patterns|--tags]                List file tree and mark changes and tracking status

  Defining file patterns:
    add <file pattern>                                    Add a tracking pattern to current branch (file pattern)
    rm <file pattern>                                     Remove a tracking pattern. Only useful after "offline --track" or "offline --picky"
    mv <oldpattern> <newPattern>                          Rename, move, or move and rename tracked files according to tracked file patterns
      --soft                                                Don't move or rename files, only the tracking pattern

  More commands:
    help, --help                                          Show this usage information
    log                                                   List commits of current branch
      --changes                                             Also list file differences
      --diff                                                Also show textual version differences
    status [-v]                                           List branches and display repository status
    version                                               Display version and package information

  User configuration:
    config [set/unset/show/add/rm] [<param> [<value>]]    Configure user-global defaults.
                                                          Flags (1/0, on/off, true/false, yes/no):
                                                            strict, track, picky, compress
                                                          Lists (semicolon-separated when set; single values for add/rm):
                                                            texttype, bintype, ignores, ignoreDirs, ignoresWhitelist, ignoreDirsWhitelist
                                                          Supported texts:
                                                            defaultbranch (has a dynamic default value, depending on VCS discovered)
    config show|list flags|lists|texts                    Enumerates all configurable settings for specified type
    config show <key>                                     Displays only single value

  Arguments:
    [<branch>][/<revision>]      Revision string. Branch is optional (defaulting to current branch) and may be a label or number >= 0
                                 Revision is an optional integer and may be negative to reference from the latest commits (-1 is most recent revision), or a tag name

  Common options:
    --force                      Executes potentially harmful operations. SOS will tell you when it needs you to confirm an operation with "--force"
                                   for offline: ignore being already offline, start from scratch (same as 'sos online --force && sos offline')
                                   for online: ignore uncommitted branches, just go online and remove existing offline repository
                                   for commit, switch, update, add: ignore uncommitted changes before executing command
    --strict                     Always perform full content comparison, don't rely only on file size and timestamp
                                   for offline command: memorize strict mode setting in repository
                                   for changes, diff, commit, switch, update, delete: perform operation in strict mode, regardless of repository setting
    --progress                   Display file names during file tree traversal, and show compression advantage, if enabled
    --only   <tracked pattern>   Restrict operation to specified pattern(s). Available for "changes", "commit", "diff", "switch", and "update"
    --except <tracked pattern>   Avoid operation for specified pattern(s). Available for "changes", "commit", "diff", "switch", and "update"
    --{cmd}                      When executing {CMD} not being offline, pass arguments to {CMD} instead (e.g. {cmd} --{cmd} config set key value.)
    --log                        Enable logging details
    --verbose                    Enable verbose output, including show compression ratios""".format(appname=appname, cmd="sos", CMD="SOS"))  # line 87
    sys.exit(0)  # line 88
