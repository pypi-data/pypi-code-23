# Application version
ver = '0.2.4'

# Default paths to Mercurial and Git
hg_cmd = 'hg'
git_cmd = 'git'

ignores = [
    "make",
    "make.exe",
    "Makefile",
    "build",
    ".cproject",
    ".gdbinit",
    ".openocd_cfg",
    ".project",
    "aos",
    ".aos",
]

# reference to local (unpublished) repo - dir#rev
regex_local_ref = r'^([\w.+-][\w./+-]*?)/?(?:#(.*))?$'
# reference to repo - url#rev
regex_url_ref = r'^(.*/([\w.+-]+)(?:\.\w+)?)/?(?:#(.*?)?)?$'

# git url (no #rev)
regex_git_url = r'^(git\://|ssh\://|https?\://|)(([^/:@]+)(\:([^/:@]+))?@)?([^/:]+)[:/](.+?)(\.git|\/?)$'
# hg url (no #rev)
regex_hg_url = r'^(file|ssh|https?)://([^/:]+)/([^/]+)/?([^/]+?)?$'

# aos url is subset of hg. aos doesn't support ssh transport
regex_aos_url = r'^(https?)://([\w\-\.]*aos\.(co\.uk|org|com))/(users|teams)/([\w\-]{1,32})/(repos|code)/([\w\-]+)/?$'
# aos sdk builds url
regex_build_url = r'^(https?://([\w\-\.]*aos\.(co\.uk|org|com))/(users|teams)/([\w\-]{1,32})/(repos|code)/([\w\-]+))/builds/?([\w\-]{6,40}|tip)?/?$'

# default aos url
aos_os_url = 'https://github.com/alibaba/AliOS-Things.git'
# default aos component url
aos_lib_url = 'https://aos.org/users/aos_official/code/aos/builds/'
# aos SDK tools needed for programs based on aos SDK component
aos_sdk_tools_url = 'https://aos.org/users/aos_official/code/aos-sdk-tools'
# open_ocd_zip
open_ocd_url = 'https://files.alicdn.com/tpsservice/27ba2d597a43abfca94de351dae65dff.zip'

# verbose logging
verbose = False
very_verbose = False
install_requirements = True
cache_repositories = True

# stores current working directory for recursive operations
cwd_root = ""

eclispe_project_dir = 'aos/makefiles/eclipse_project'

APP_PATH = 'app_path'
PROGRAM_PATH = 'program_path'
AOS_SDK_PATH = 'AOS_SDK_PATH'
OS_PATH = 'os_path'
OS_NAME = 'AliOS-Things'
PATH_TYPE = 'path_type'
AOS_COMPONENT_BASE_URL = 'https://github.com/AliOS-Things'
CUBE_MAKEFILE = 'cube.mk'
CUBE_MODIFY = 'cube_modify'
REMOTE_PATH = 'remote'
