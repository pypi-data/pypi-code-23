commands=\
{
'_order': ['maincommands', 'subcommands for maincommand "config"', 'subcommands for maincommand "db"', 'subcommands for maincommand "build"'],
'maincommands': {
'_order': ['help COMMAND', 'config SUBCOMMAND', 'lock FILE', 'unlock FILE', 'db SUBCOMMAND', 'build SUBCOMMAND'],
"": """
maincommands
++++++++++++
""",
'help COMMAND': """
help COMMAND
::::::::::::

This command prints help for the given command. It can be invoked as:

  help
  help MAINCOMMAND
  help SUBCOMMAND
  help MAINCOMMAND SUBCOMMAND

You get a list of all known MAINCOMMANDS with:

  help maincommand
""",
'config SUBCOMMAND': """
config SUBCOMMAND
:::::::::::::::::

Show the configuration or create or modify a configuration file. These
are known subcommands here:

- list       - list loaded configuration files
- show       - show configuration data
- make       - create configuration file
- standalone - create configuration for "standalone" builds
- local      - create configuration for "local" builds

You get help on each subcommand with:

  help SUBCOMMAND
""",
'lock FILE': """
lock FILE
:::::::::

Lock a FILE, then exit sumo. This is useful if you want to read or
write a database file without sumo interfering. Don't forget to remove
the lock later with the "unlock" command.

This command must be followed by a *filename*.
""",
'unlock FILE': """
unlock FILE
:::::::::::

Unlock a FILE, then exit sumo. If you locked a database with "lock"
before you should always unlock it later, otherwise sumo can't access
the file.

This command must be followed by a *filename*.
""",
'db SUBCOMMAND': """
db SUBCOMMAND
:::::::::::::

This is the maincommand for all operations that work with the
dependency database or DEPS.DB file.

For all of the db subcommands you have to specify the dependency
database directory with option --dbdir or a configuration file.

These are the known subcommands here:

convert
  convert a scanfile created by sumo-scan to a DB file

convert-old
  convert DB file from old to new format

appconvert
  convert a scanfile to a MODULES file for an application

modconvert
  convert a scanfile to DB file format for a list of supports

edit
  edit the dependency file with an editor

format
  reformat the dependency file

weight
  set the weight factor for modules

alias-add
  add an alias for a dependency in a module

dependency-add
  add a dependency to a module

dependency-delete
  delete a dependency of a module

make-recipes
  define special make-recipes for a module

list
  list modules or versions of modules

show
  show details of moduleversions

find
  search for modules with a regexp

check
  consistency check of the DB file

merge
  merge two DB files

cloneversion
  create a new DB entry by copying an old one

releasefilename
  define an alternative filename for the RELEASE file

replaceversion
  replace a DB entry with a new one

clonemodule
  add a module under a new name in the DB file

You get help on each subcommand with:

  help SUBCOMMAND
""",
'build SUBCOMMAND': """
build SUBCOMMAND
::::::::::::::::

This is the maincommand for all operations that work with builds and
the build database (BUILDS.DB).

For all of the build subcommands you have to specify the dependency
database directory and the build directory with --dbdir and --builddir
or a configuration file.

These are the known subcommands:

try
  check the module specification for completeness and consistency

new
  create a new build

remake
  do "make clean" and "make all" with a build

find
  look for builds that match a module specification

use
  use all modules or your module specification in your application

list
  list names of all builds

show
  show details of a build

state
  show or change the state of a build

delete
  delete a build

You get help on each subcommand with:

  help SUBCOMMAND
""",
},
'subcommands for maincommand "config"': {
'_order': ['config list', 'config show [OPTIONNAMES]', 'config make FILENAME [OPTIONNAMES]', 'config standalone DIRECTORY', 'config local DIRECTORY'],
"": """
subcommands for maincommand "config"
++++++++++++++++++++++++++++++++++++
""",
'config list': """
config list
:::::::::::

List all configuration files that were loaded.
""",
'config show [OPTIONNAMES]': """
config show [OPTIONNAMES]
:::::::::::::::::::::::::

Show the configuration in JSON format.  OPTIONNAMES is an optional
list of long option names. If OPTIONNAMES are specified, only options
from this list are saved in the configuration file.
""",
'config make FILENAME [OPTIONNAMES]': """
config make FILENAME [OPTIONNAMES]
::::::::::::::::::::::::::::::::::

Create a new configuration file from the options read from
configuration files and options from the command line. If FILENAME is
'-' dump to the console. OPTIONNAMES is an optional list of long
option names. If OPTIONNAMES are specified, only options from this
list are saved in the configuration file.
""",
'config standalone DIRECTORY': """
config standalone DIRECTORY
:::::::::::::::::::::::::::

This command is used to create a new sumo directory with an
independent build directory and an independent copy of the dependency
database.

It creates a new configuration for "standalone" builds. DIRECTORY is
created if it does not yet exist. This command takes all settings and
command line options but sets dbrepomode to "pull" and dbdir to
DIRECTORY/database. It also sets builddir to DIRECTORY/build. Option
dbrepo must be set, this is used to create a local copy of the
dependency database in DIRECTORY/database. If there is a file
"sumo.config" in the current working directory it is copied to
"sumo.config.bak". A new file "sumo.config" is then created in the
current working directory.
""",
'config local DIRECTORY': """
config local DIRECTORY
::::::::::::::::::::::

This command is used to create a new sumo directory with a new build
directory but using existing builds from your current build directory.
It also creates an independent copy of the dependency database.

DIRECTORY is created if it does not yet exist. This command takes all
settings and command line options but sets dbrepomode to "pull" and
dbdir to DIRECTORY/database. It also sets localbuilddir to
DIRECTORY/build. Option dbrepo must be set, this is used to create a
local copy of the dependency database in DIRECTORY/database. If there
is a file "sumo.config" in the current working directory it is copied
to "sumo.config.bak". A new file "sumo.config" is then created in the
current working directory.
""",
},
'subcommands for maincommand "db"': {
'_order': ['db convert SCANFILE', 'db convert-old OLDDB', 'db appconvert SCANFILE', 'db modconvert SCANFILE MODULES', 'db edit', 'db format', 'db weight WEIGHT MODULES', 'db list MODULES', 'db show MODULES', 'db find REGEXP', 'db check', 'db merge DB', 'db cloneversion MODULE OLD-VERSION NEW-VERSION [SOURCESPEC]', 'db releasefilename MODULE RELEASEFILENAME', 'db replaceversion MODULE OLD-VERSION NEW-VERSION', 'db clonemodule OLD-MODULE NEW-MODULE [VERSIONS]', 'db dependency-delete MODULE DEPENDENCY', 'db dependency-add MODULE DEPENDENCY', 'db alias-add MODULE DEPENDENCY ALIAS', 'db make-recipes MODULE TARGET LINES'],
"": """
subcommands for maincommand "db"
++++++++++++++++++++++++++++++++
""",
'db convert SCANFILE': """
db convert SCANFILE
:::::::::::::::::::

Convert a scanfile that was created by by "sumo-scan all" to a new
dependency database.  If SCANFILE is a dash "-", the program expects
the scanfile on stdin.  Note that options --dbdir and --scandb are
mandatory here. With --dbdir you specify the drectory where the new
created dependency database file is stored, with --scandb you specify
the name of the scan database file. The scan database file contains
information on what moduleversion can be used with what dependency
version.
""",
'db convert-old OLDDB': """
db convert-old OLDDB
::::::::::::::::::::

Convert a dependency database file OLDDB from old to new format. The
old format had architecture data ("arch") for each moduleversion. In
the new format this data is removed.  Note that this command IGNORES
option --dbrepo" it directly operates on the dependency database file
in the directory given with option --dbdir.
""",
'db appconvert SCANFILE': """
db appconvert SCANFILE
::::::::::::::::::::::

Convert a scanfile that was created by applying "sumo-scan all" to an
application to a list of aliases and modulespecs in JSON
<http://www.json.org> format. If SCANFILE is a dash "-" the program
expects the scanfile on stdin. The result is printed to the console.
""",
'db modconvert SCANFILE MODULES': """
db modconvert SCANFILE MODULES
::::::::::::::::::::::::::::::

Convert a scanfile that was created by applying "sumo-scan all" to the
dependency database format for all the selected modules. If SCANFILE
is a dash "-" the program expects the scanfile on stdin.  The result
is printed to the console. This data can be added to the dependency
database using the command "db edit".

""",
'db edit': """
db edit
:::::::

Start the editor specified by option --editor or the environment
variables "VISUAL" or "EDITOR" to edit the dependency database file.
This command first aquires a file-lock on the file, that prevents
other users from acessing the file at the same time.  When the editor
program is terminated, sumo checks if the file is still a valid JSON
<http://www.json.org> file. If not, you can start the editor again or
abort the program. If the file is valid JSON <http://www.json.org>,
sumo commits the changes if option --dbrepo was specified.  If option
--logmsg was given, this is used as commit log message, otherwise an
editor is started where you can enter a log message. Finally the file
lock is released. If you want to edit the dependency database file you
should always do it with this command.
""",
'db format': """
db format
:::::::::

Just load and save the dependency database. This ensures that the file
is formatted in the standard sumo format. This is useful when the file
was edited and you want to ensure that key sort order and indentation
are restored. If you specified a repository with --dbrepo, the command
will commit the changes. If you want a log message different from "db
format" use option --logmsg

""",
'db weight WEIGHT MODULES': """
db weight WEIGHT MODULES
::::::::::::::::::::::::

Set the weight factor for modules. A weight determines where a module
is placed in the generated RELEASE file. Modules there are sorted
first by weight, then by dependency. Parameter MODULES is a list of
modulespecs. Use modulename:{+-}versionname to select more versions of
a module.

Note that this command *does not* use the --modules command line
option.

Parameter WEIGHT must be an integer.
""",
'db list MODULES': """
db list MODULES
:::::::::::::::

If called with no argument, list the names of all modules. If called
with '.', the wildcard symbol, list all versions of all modules. If
called with argument MODULES, a list of modulespecs MODULE:{+-}VERSION
that specifies modules and versions, list all the matching versions of
all specified modules.
""",
'db show MODULES': """
db show MODULES
:::::::::::::::

This command prints only the parts of the dependency database that
contain the given modules.

Parameter MODULES is a list of modulespecs MODULE:{+-}VERSION that
specifies the modules and versions to operate on.
""",
'db find REGEXP': """
db find REGEXP
::::::::::::::

This command shows all modules whose names or sources match a regexp.
Parameter REGEXP is a perl compatible regular expression.
""",
'db check': """
db check
::::::::

Do some consistency checks on the dependency database file in the
directory specifed by --dbdir.
""",
'db merge DB': """
db merge DB
:::::::::::

Merge the given dependency database file with the dependency database
in the directory specifed by --dbdir.
""",
'db cloneversion MODULE OLD-VERSION NEW-VERSION [SOURCESPEC]': """
db cloneversion MODULE OLD-VERSION NEW-VERSION [SOURCESPEC]
:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

This command adds a new version of a module to the dependency database
by copying the old version. MODULE here is just the name of the module
since the version follows as a separate argument.

If SOURCESPEC is not given, the command copies the source
specification from OLD-VERSION but sets the tag to NEW-VERSION. Note
that this is not allowed for "path" and "tar" sources (see below).

If SOURCESPEC is given, the source specification from OLD-VERSION is
copied an the all values from SOURCESPEC are added.

A sourcespec has the form:
  NAME=VALUE[,VALUE...] [NAME=VALUE[,VALUE..] ...]

In general, NAME must start with a letter or underscore character and
must be
following by a sequence of letters, underscrores or digits.

A VALUE must be a JSON simple value (no map or list). If VALUE is a
string, it must be enclosed in double quotes '"' if it contains any of
the characters '"', ',' or ' '.

These are possible names:

type
  The source type. Currently known are "path", "tar", "cvs", "svn",
  "darcs", "hg" and "git".

url
  This is the URL. For the types "path" and "tar" it may also be a
  filename.

tag
  This defines the revision tag.

rev
  This defines the revision hash key.

patches
  This defines names or URLs for patch files. This is the only name,
  where several values may be provided as a comma separated list.

Note that you can define an empty value (on the bash shell) like in
this example:

  tag='""'

This means that the "tag" is removed from the source specification.

The command always asks for a confirmation of the action unless option
"-y" is used.
""",
'db releasefilename MODULE RELEASEFILENAME': """
db releasefilename MODULE RELEASEFILENAME
:::::::::::::::::::::::::::::::::::::::::

This command defines an alternative filename for the RELEASE file of
the module. Usually the RELEASE file is generated as
"configure/RELEASE". You can specify a different filename for the
given module with this command. This may be useful for support modules
that have no regular EPICS makefile system or for some special
configurations of the EPICS base. If you set the RELEASEFILENAME to an
empty string or "configure/RELEASE", the special entry for the
filename is removed for this module in the dependency database.
""",
'db replaceversion MODULE OLD-VERSION NEW-VERSION': """
db replaceversion MODULE OLD-VERSION NEW-VERSION
::::::::::::::::::::::::::::::::::::::::::::::::

This command replaces a version of a module with a new version. MODULE
here is just the name of the module since the version follows as a
separate argument. All the data of the module is copied. If sourcespec
is given, the command changes the source part according to this
parameter. A sourcespec has the form "path PATH", "tar TARFILE",
"REPOTYPE URL" or "REPOTYPE URL TAG".  REPOTYPE may be "darcs", "hg"
or "git". Both, URL or TAG may be ".", in this case the original URL
or TAG remains unchanged.
""",
'db clonemodule OLD-MODULE NEW-MODULE [VERSIONS]': """
db clonemodule OLD-MODULE NEW-MODULE [VERSIONS]
:::::::::::::::::::::::::::::::::::::::::::::::

Copy all versions of the existing old module and add this with the
name of thew new module to the dependency database. OLD-MODULE and
NEW-MODULE here are just the module names since the versions may
follow as a separate argument. If there are no versions specified, the
command copies all existing versions. Note that this DOES NOT add the
new module as dependency to any other modules.
""",
'db dependency-delete MODULE DEPENDENCY': """
db dependency-delete MODULE DEPENDENCY
::::::::::::::::::::::::::::::::::::::

Delete a dependency of a module. MODULE here is a modulespec of the
form MODULE:VERSION that specifies a single version of a module.
""",
'db dependency-add MODULE DEPENDENCY': """
db dependency-add MODULE DEPENDENCY
:::::::::::::::::::::::::::::::::::

Add a dependency to a module. MODULE here is a modulespec of the form
MODULE:VERSION that specifies a single version of a module.
""",
'db alias-add MODULE DEPENDENCY ALIAS': """
db alias-add MODULE DEPENDENCY ALIAS
::::::::::::::::::::::::::::::::::::

Define a new alias for a dependency of a module. MODULE here is a
modulespec of the form MODULE:VERSION that specifies a single version
of a module.

""",
'db make-recipes MODULE TARGET LINES': """
db make-recipes MODULE TARGET LINES
:::::::::::::::::::::::::::::::::::

Define special make recipes for a module. See also "make-recipes" in
the chapter "The dependency database".

MODULE here is a modulespec of the form MODULE:VERSION that specifies
a single version of a module. TARGET must be "all", "clean", "config"
or "distclean" and specifies the make target for which a recipe is
defined. LINES is a list of space separated strings. It is recommended
to enclose the line strings in single or double quotes.

Special variables and characters when you use double quotes:

- \$DIR: (bash, sumo) The directory of the MODULE.
- \n: (bash) Separates the lines in the LINES argument, which is a
  single string.
- \": (bash) A literal double quote character.
- \$: (bash) A literal dollar character.
""",
},
'subcommands for maincommand "build"': {
'_order': ['build try MODULES', 'build new MODULES', 'build remake BUILDTAG', 'build find MODULES', 'build use MODULES', 'build list', 'build show BUILDTAG', 'build state BUILDTAG [NEW-STATE]', 'build delete BUILDTAGS'],
"": """
subcommands for maincommand "build"
+++++++++++++++++++++++++++++++++++
""",
'build try MODULES': """
build try MODULES
:::::::::::::::::

This command is intended to help you create module specifications for
the "new" command.

Each MODULE here is a modulespec of the form MODULE or
MODULE:{+-}VERSION that specifies just a module name, a module and
some versions or a single version. You can specify an incomplete list
of modules.

The detail of the output is determined by option --detail which is an
integer between 0 and 3. 0, the default, gives the shortest, 3 gives
the longest report. The program then shows which modules you have to

In any case the command shows which modules are missing since they
depend on other modules of your specification and which ones are
missing an exact version.

If you converted an existing support directory to sumo you have a scan
database file which you can specify with option --scandb to this
command.

For a detailed example see try example.

""",
'build new MODULES': """
build new MODULES
:::::::::::::::::

This command creates a new build. Each module given in MODULES here is
a modulespec of the form MODULE:VERSION that specifies a single
version of a module. If the buildtag is not given as an option, the
program generates a buildtag in the form "AUTO-nnn". A new build is
created according to the modulespecs. Your modulespecifications must
be *complete* and *exact* meaning that all dependencies are included
and all modules are specified with exactly a single version. Use
command "try" in order to create module specifications that can be
used with command "new".  This command calls "make" and, after
successful completion, sets the state of the build to "testing". If
you want to skip this step, use option --no-make. In order to provide
arbitrary options to make use option --makeflags.
""",
'build remake BUILDTAG': """
build remake BUILDTAG
:::::::::::::::::::::

This command recreates a build by first calling "make clean" and then
"make all" with the build's makefile. If you develop a support module
(see also "config standalone" and "config local") you want to
recompile the build after changes in the sources. In order to provide
arbitrary options to make use option --makeflags.
""",
'build find MODULES': """
build find MODULES
::::::::::::::::::

This command is used to find matching builds for a given list of
modulespecs. Each module in MODULES here is a modulespec of the form
MODULE or MODULE:{+-}VERSION that specifies just a module name, a
module and some versions or a single version. The command prints a
list of buildtags of matching builds on the console. If option --brief
is given, the program just shows the buildtags.

""",
'build use MODULES': """
build use MODULES
:::::::::::::::::

This command creates a configure/RELEASE file for an application. Each
module given in MODULES here is a modulespec of the form
MODULE:VERSION that specifies a single version of a module. If option
--buildtag is given, it checks if this is compatible with the given
modules.  Otherwise it looks for all builds that have the modules in
the required versions. If more than one matching build found it takes
the one with the alphabetically first buildtag. The RELEASE file
created includes only the modules that are specified. Output to
another file or the console can be specified with option '-o'.
""",
'build list': """
build list
::::::::::

This command lists the names of all builds.
""",
'build show BUILDTAG': """
build show BUILDTAG
:::::::::::::::::::

This command shows the data of a build. The buildtag must be given as
an argument.
""",
'build state BUILDTAG [NEW-STATE]': """
build state BUILDTAG [NEW-STATE]
::::::::::::::::::::::::::::::::

This command is used to show or change the state of a build. The
buildtag must be given as an argument. If there is no new state given,
it just shows the current state of the build. Otherwise the state of
the build is changed to the given value. If a build is set to state
'disabled', all dependend builds are also set to this state. In this
case, unless option '-y' or '--recursive' are given, sumo asks for
your confirmation.
""",
'build delete BUILDTAGS': """
build delete BUILDTAGS
::::::::::::::::::::::

The directories of the builds are removed and their entries in the
build database are deleted. If other builds depend on the builds to be
deleted, the command fails unless option '--recursive' is given. In
this case all dependent builds are deleted, too.  The buildtags must
be given as an argument.
""",
},
}
completion=\
{
'_order': ['Command completion'],
'Command completion': """
Command completion
------------------

Command completion means that you can press <TAB> on any incomplete
sumo command and you get a list of possibilities how to complete that
command. By pressing <TAB> several times you can try each possible
completion.

Prerequisites
+++++++++++++

Command completion works with `bash` or `zsh` (Z-Shell), you need to
have one of these installed. Your environment variable `SHELL` must be
set to the binary file of the shell, e.g. `/usr/bin/bash` or
`/usr/bin/zsh`.

In any case the package `bash-completion` must be installed.

If you use the Z-Shell, the following commands must be executed at
start up. Add them for example to the file `$HOME/.zshenv`:

  autoload -U +X compinit && compinit
  autoload -U +X bashcompinit && bashcompinit

There are two ways to activate command completion, described in the
following chapters.

Activate command completion on the fly
++++++++++++++++++++++++++++++++++++++

Enter this command:
  eval `sumo help completion-line`

Activate command completion permanently
+++++++++++++++++++++++++++++++++++++++

Enter this command:
  sumo help completion-script > $HOME/_sumo

Then add the line:
  source $HOME/_sumo

to your $HOME/.bashrc or $HOME/.zshrc

Completion cache files
++++++++++++++++++++++

Sumo will create cache files in your home directory to speed up
command completion. These are the files ".dbcache.sumo" and
".buildcache.sumo". If you don't want this set the environment
variable "SUMOHELP" in a way that it contains the string "nocache"
like in:

  export SUMOHELP="nocache"

If there are other help options defined in SUMOHELP, you should
seperate them with commas ",".
""",
}
pager=\
{
'_order': ['The help pager'],
'The help pager': """
The help pager
--------------

The build in pager allows you to navigate in long help texts that sumo
displays when you use command "help" or option "-h". There are three
modes:

pager:off
  The pager is off, all help is printed directly to the console.

pager:on
  The pager is used only for long help texts (more than 24 lines).

pager:always
  The pager is always used, even for short help texts.

Mode "pager:on" is the default.

You define the pager mode by adding one of the three strings to the
environment variable "SUMOHELP" like in:

    export SUMOHELP="pager:off"

If there are other help options defined in SUMOHELP, you should
seperate them with commas ",".
""",
}
options=\
{
'_order': ['Options'],
'Options': {
'_order': ['``--version``', '``-h [OPTIONS], --help [OPTIONS]``', '``--summary``', '``--test``', '``-c FILE, --config FILE``', '``-C, --no-default-config``', '``--disable-loading``', '``-A, --append OPTIONNAME``', '``--#preload FILES``', '``--#opt-preload FILES``', '``--#postload FILES``', '``--#opt-postload FILES``', '``--dbdir DBDIR``', '``--dbrepomode MODE``', '``--dbrepo REPOSITORY``', '``--scandb SCANDB``', '``--dumpdb``', '``--logmsg LOGMESSAGE``', '``-t BUILDTAG, --buildtag BUILDTAG``', '``--buildtag-stem STEM``', '``--builddir BUILDDIR``', '``--localbuilddir BUILDDIR``', '``-o OUTPUTFILE, --output OUTPUTFILE``', '``-x EXTRALINE, --extra EXTRALLINE``', '``-a ALIAS, --alias ALIAS``', '``-m MODULE, --module MODULE``', '``-X REGEXP, --exclude-states REGEXP``', '``-b, --brief``', '``--recursive``', '``--detail NO``', '``-D EXPRESSION, --dir-patch EXPRESSION``', '``-U EXPRESSION, --url-patch EXPRESSION``', '``--noignorecase``', '``--no-checkout``', '``--no-make``', '``--makeflags MAKEFLAGS``', '``--readonly``', '``--nolock``', '``--no-multiprocessing``', '``-p, --progress``', '``--trace``', '``--tracemore``', '``--dump-modules``', '``--list``', '``-y, --yes``', '``--editor EDITOR``', '``--exceptions``', '``-v, --verbose``', '``--version``', '``-n, --dry-run``'],
"": """
Options
-------


Here is a short overview on command line options:
""",
'``--version``': """
--version
+++++++++

    Show the program version and exit.
""",
'``-h [OPTIONS], --help [OPTIONS]``': """
-h [OPTIONS], --help [OPTIONS]
++++++++++++++++++++++++++++++

    If other OPTIONS are given, show help for these options. If
    OPTIONS is 'all', show help for all options. If OPTIONS is
    missing, show a short generic help message for the program.
""",
'``--summary``': """
--summary
+++++++++
    Print a summary of the function of the program.

""",
'``--test``': """
--test
++++++
    Perform some self tests.

""",
'``-c FILE, --config FILE``': """
-c FILE, --config FILE
++++++++++++++++++++++

    Load options from the given configuration file. You can specify
    more than one of these.  Unless --no-default-config is given, the
    program always loads configuration files from several standard
    directories first before it loads your configuration file. The
    contents of all configuration files are merged.
""",
'``-C, --no-default-config``': """
-C, --no-default-config
+++++++++++++++++++++++

    If this option is not given and --no-default-config is not given,
    the program tries to load the default configuration file sumo-
    scan.config from several standard locations (see documentation on
    configuration files).
""",
'``--disable-loading``': """
--disable-loading
+++++++++++++++++

    If given, disable execution of load commands like '#preload' in
    configuration files. In this case these keys are treated like
    ordinary keys.
""",
'``-A, --append OPTIONNAME``': """
-A, --append OPTIONNAME
+++++++++++++++++++++++

    If an option with name OPTIONNAME is given here and it is a list
    option, the list from the command line is *appended* to the list
    from the configuration file. The default is that options from the
    command line *override* option values from the configuration file.
""",
'``--#preload FILES``': """
--#preload FILES
++++++++++++++++

    Specify a an '#preload' directive in the configuration file. This
    option has only a meaning if a configuration file is created with
    the 'makeconfig' command. '#preload' means that the following
    file(s) are loaded before the rest of the configuration file.
""",
'``--#opt-preload FILES``': """
--#opt-preload FILES
++++++++++++++++++++

    This option does the same as --#preload but the file loading is
    optional. If they do not exist the program continues without an
    error.
""",
'``--#postload FILES``': """
--#postload FILES
+++++++++++++++++

    Specify a an '#postload' directive in the configuration file. This
    option has only a meaning if a configuration file is created with
    the 'makeconfig' command. '#postload' means that the following
    file(s) are loaded after the rest of the configuration file.
""",
'``--#opt-postload FILES``': """
--#opt-postload FILES
+++++++++++++++++++++

    This option does the same as --#postload but the file loading is
    optional. If they do not exist the program continues without an
    error.
""",
'``--dbdir DBDIR``': """
--dbdir DBDIR
+++++++++++++

    Define the directory where the dependency database file 'DEPS.DB'
    is found. A default for this option can be put in a configuration
    file.
""",
'``--dbrepomode MODE``': """
--dbrepomode MODE
+++++++++++++++++

    Specify how sumo should use the dependency database repository.
    There are three possible values: 'get', 'pull' and 'push'. Mode
    'get' is the default. The meaning depends on the used version
    control system (VCS), if it is distributed (git,mercurial,darcs)
    or centralized (subversion,cvs). There are three possible
    operations on the dependency database:

      * init : create the dependency database if it doesn't exist *
      read : read the dependency database * write: write (change) the
      dependency database

    Here is what happens during these operations depending on the
    mode:

    +------+----------+--------------------------------------------+
    |mode  |operation |action                                      |
    +======+==========+============================================+
    |get   |init      |create the repository if it doesn't exist   |
    |      +----------+--------------------------------------------+
    |      |read      |none                                        |
    |      +----------+--------------------------------------------+
    |      |write     |distr. VCS: commit changes                  |
    |      |          +--------------------------------------------+
    |      |          |centr. VCS: none                            |
    +------+----------+--------------------------------------------+
    |pull  |init      |create the repository if it doesn't exist   |
    |      +----------+--------------------------------------------+
    |      |read      |distr. VCS: pull                            |
    |      |          +--------------------------------------------+
    |      |          |centr. VCS: update                          |
    |      +----------+--------------------------------------------+
    |      |write     |distr. VCS: commit changes                  |
    |      |          +--------------------------------------------+
    |      |          |centr. VCS: none                            |
    +------+----------+--------------------------------------------+
    |push  |init      |create the repository if it doesn't exist   |
    |      +----------+--------------------------------------------+
    |      |read      |distr. VCS: pull                            |
    |      |          +--------------------------------------------+
    |      |          |centr. VCS: update                          |
    |      +----------+--------------------------------------------+
    |      |write     |distr. VCS: pull, commit changes, push      |
    |      |          +--------------------------------------------+
    |      |          |centr. VCS: update, commit changes          |
    +------+----------+--------------------------------------------+

""",
'``--dbrepo REPOSITORY``': """
--dbrepo REPOSITORY
+++++++++++++++++++

    Define a REPOSITORY for the db file. REPOSITORY must have the form
    'REPOTYPE URL' or 'type=REPOTYPE url=URL". REPOTYPE may be
    'darcs', 'hg' or 'git'. Option --dbdir must specify a directory
    that will contain the repository for the db file.  Before reading
    the db file a 'pull' command will be executed. When the file is
    changed, a 'commit' and a 'push' command will be executed. If the
    repository doesn't exist the program tries to check out a working
    copy from the given URL. A default for this option can be put in a
    configuration file.
""",
'``--scandb SCANDB``': """
--scandb SCANDB
+++++++++++++++

    Specify the (optional) SCANDB file. The scan database file
    contains information on what moduleversion can be used with what
    dependency version.
""",
'``--dumpdb``': """
--dumpdb
++++++++

    Dump the modified db on the console, currently only for the
    commands "weight", "merge", "cloneversion" and "replaceversion".
""",
'``--logmsg LOGMESSAGE``': """
--logmsg LOGMESSAGE
+++++++++++++++++++

    Specify a logmessage for automatic commits when --dbrepo is used.
""",
'``-t BUILDTAG, --buildtag BUILDTAG``': """
-t BUILDTAG, --buildtag BUILDTAG
++++++++++++++++++++++++++++++++

    Specify a buildtag.
""",
'``--buildtag-stem STEM``': """
--buildtag-stem STEM
++++++++++++++++++++

    Specify the stem of a buildtag. This option has only an effect on
    the commands 'new' and 'try' if a buildtag is not specified. The
    program generates a new tag in the form 'stem-nnn' where 'nnn' is
    the smallest possible number that ensures that the buildtag is
    unique.
""",
'``--builddir BUILDDIR``': """
--builddir BUILDDIR
+++++++++++++++++++

    Specify the support directory. If this option is not given take
    the current working directory as support directory. A default for
    this option can be put in a configuration file.
""",
'``--localbuilddir BUILDDIR``': """
--localbuilddir BUILDDIR
++++++++++++++++++++++++

    Specify a *local* support directory. Modules from the directory
    specifed by --builddir are used but this directory is not modfied.
    All new builds are created in the local build directory and only
    the build database file there is modified.
""",
'``-o OUTPUTFILE, --output OUTPUTFILE``': """
-o OUTPUTFILE, --output OUTPUTFILE
++++++++++++++++++++++++++++++++++

    Define the output for command 'use'. If this option is not given,
    'use' writes to 'configure/RELEASE'. If this option is '-', the
    command writes to standard-out.",
""",
'``-x EXTRALINE, --extra EXTRALLINE``': """
-x EXTRALINE, --extra EXTRALLINE
++++++++++++++++++++++++++++++++

    Specify an extra line that is added to the generated RELEASE file.
    A default for this option can be put in a configuration file.
""",
'``-a ALIAS, --alias ALIAS``': """
-a ALIAS, --alias ALIAS
+++++++++++++++++++++++

    Define an alias for the command 'use'. An alias must have the form
    FROM:TO. The path of module named 'FROM' is put in the generated
    RELEASE file as a variable named 'TO'. You can specify more than
    one of these by repeating this option or by joining values in a
    single string separated by spaces. A default for this option can
    be put in a configuration file.
""",
'``-m MODULE, --module MODULE``': """
-m MODULE, --module MODULE
++++++++++++++++++++++++++

    Define a modulespec. If you specify modules with this option you
    don't have to put modulespecs after some of the commands. You can
    specify more than one of these by repeating this option or by
    joining values in a single string separated by spaces. A default
    for this option can be put in a configuration file.
""",
'``-X REGEXP, --exclude-states REGEXP``': """
-X REGEXP, --exclude-states REGEXP
++++++++++++++++++++++++++++++++++

    For command 'try' exclude all 'dependents' whose state does match
    one of the regular expressions (REGEXP).
""",
'``-b, --brief``': """
-b, --brief
+++++++++++

    Create a more brief output for some commands.
""",
'``--recursive``': """
--recursive
+++++++++++

    For command 'build delete', delete all dependend builds, too. For
    command 'build state' with state 'disabled', disable all dependend
    builds, too.
""",
'``--detail NO``': """
--detail NO
+++++++++++

    Control the output of command 'try'. The value must be an integer
    between 0 (very short) and 3 (very long)."
""",
'``-D EXPRESSION, --dir-patch EXPRESSION``': """
-D EXPRESSION, --dir-patch EXPRESSION
+++++++++++++++++++++++++++++++++++++

    Specify a directory patchexpression. Such an expression consists
    of a tuple of 2 python strings. The first is the match expression,
    the second one is the replacement string. The regular expression
    is applied to every source path generated. You can specify more
    than one patchexpression. A default for this option can be put in
    a configuration file.
""",
'``-U EXPRESSION, --url-patch EXPRESSION``': """
-U EXPRESSION, --url-patch EXPRESSION
+++++++++++++++++++++++++++++++++++++

    Specify a repository url patchexpression. Such an expression
    consists of a tuple of 2 python strings. The first is the match
    expression, the second one is the replacement string. The regular
    expression is applied to every source url generated. You can
    specify more than one patchexpression. A default for this option
    can be put in a configuration file.
""",
'``--noignorecase``': """
--noignorecase
++++++++++++++

    For command 'find', do NOT ignore case.
""",
'``--no-checkout``': """
--no-checkout
+++++++++++++

    With this option, "new" does not check out sources of support
    modules. This option is only here for test purposes.
""",
'``--no-make``': """
--no-make
+++++++++

    With this option, "new" does not call "make".j
""",
'``--makeflags MAKEFLAGS``': """
--makeflags MAKEFLAGS
+++++++++++++++++++++

    Specify extra option strings for make You can specify more than
    one of these by repeating this option or by joining values in a
    single string separated by spaces. A default for this option can
    be put in a configuration file.
""",
'``--readonly``': """
--readonly
++++++++++

    Do not allow modifying the database files or the support
    directory. A default for this option can be put in a configuration
    file.
""",
'``--nolock``': """
--nolock
++++++++

    Do not use file locking.
""",
'``--no-multiprocessing``': """
--no-multiprocessing
++++++++++++++++++++

    Do not use multiprocessing in the program. This is mainly here to
    help debugging the program. Currently multiprocessing is used when
    the sources for modules of a build are created by checking out
    from version control systems.
""",
'``-p, --progress``': """
-p, --progress
++++++++++++++

    Show progress of some commands on stderr. A default for this
    option can be put in a configuration file.
""",
'``--trace``': """
--trace
+++++++

    Switch on some trace messages.
""",
'``--tracemore``': """
--tracemore
+++++++++++

    Switch on even more trace messages.
""",
'``--dump-modules``': """
--dump-modules
++++++++++++++

    Dump module specs, then stop the program.
""",
'``--list``': """
--list
++++++

    Show information for automatic command completion.
""",
'``-y, --yes``': """
-y, --yes
+++++++++

    All questions the program may ask are treated as if the user
    replied 'yes'.
""",
'``--editor EDITOR``': """
--editor EDITOR
+++++++++++++++

    Specify the preferred editor. If this is not given, sumo takes the
    name of the editor from environment variables "VISUAL" or EDITOR".
""",
'``--exceptions``': """
--exceptions
++++++++++++

    On fatal errors that raise python exceptions, don't catch these.
    This will show a python stacktrace instead of an error message and
    may be useful for debugging the program."
""",
'``-v, --verbose``': """
-v, --verbose
+++++++++++++

    Show command calls. A default for this option can be put in a
    configuration file.
""",
'``--version``': """
--version
+++++++++

    Show the program version and exit.
""",
'``-n, --dry-run``': """
-n, --dry-run
+++++++++++++

    Just show what the program would do.""",
},
}
