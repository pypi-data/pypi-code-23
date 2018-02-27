import ctypes

from config import *
from util import *
from repo import *


# Program class, acts code base root
class Program(object):
    path = None
    name = None
    is_cwd = False
    is_repo = False
    is_classic = False
    build_dir = "BUILD"

    def __init__(self, path=None, print_warning=False):
        path = os.path.abspath(path or os.getcwd())
        self.path = path
        self.is_cwd = True

        while cd(path):
            tpath = path
            if os.path.isfile(os.path.join(path, Cfg.file)):
                self.path = path
                self.is_cwd = False
                break

            path = os.path.split(path)[0]
            if tpath == path:       # Reached root.
                break

        self.name = os.path.basename(self.path)
        self.is_classic = os.path.isfile(os.path.join(self.path, 'aos.bld'))

        # is_cwd flag indicates that current dir is assumed to be root, not root repo
        if self.is_cwd and print_warning:
            warning(
                "Could not find aos program in current path \"%s\".\n"
                "You can fix this by calling \"aos new .\" in the root of your program." % self.path)

    def get_cfg(self, *args, **kwargs):
        return Cfg(self.path).get(*args, **kwargs) or Global().get_cfg(*args, **kwargs)

    def set_cfg(self, *args, **kwargs):
        return Cfg(self.path).set(*args, **kwargs)

    def list_cfg(self, *args, **kwargs):
        return Cfg(self.path).list(*args, **kwargs)

    def set_root(self):
        return self.set_cfg('ROOT', '.')

    def unset_root(self, path=None):
        fl = os.path.join(path or self.path, Cfg.file)
        if os.path.isfile(fl):
            os.remove(fl)

    # Gets aos dir (unified)
    def get_os_dir(self):
        if os.path.isdir(os.path.join(self.path, 'aos')):
            return os.path.join(self.path, 'aos')
        elif self.name == 'aos':
            return self.path
        else:
            return None

    def get_aoslib_dir(self):
        if os.path.isdir(os.path.join(self.path, 'aos')):
            return os.path.join(self.path, 'aos')
        else:
            return None

    # Gets aos tools dir (unified)
    def get_tools_dir(self):
        paths = []
        # aos dir identified and tools is a sub dir
        aos_os_path = self.get_os_dir()
        if aos_os_path:
            paths.append([aos_os_path, 'tools'])
            paths.append([aos_os_path, 'core', 'tools'])
        # aos not identified but tools found under cwd/tools
        paths.append([self.path, 'tools'])
        paths.append([self.path, 'core', 'tools'])
        # aos Classic deployed tools
        paths.append([self.path, '.temp', 'tools'])

        return self._find_file_paths(paths, 'make.py')

    def get_requirements(self):
        paths = []
        aos_os_path = self.get_os_dir()
        if aos_os_path:
            paths.append([aos_os_path, 'tools'])
            paths.append([aos_os_path])
        # aos not identified but tools found under cwd/tools
        paths.append([self.path, 'tools'])
        # aos Classic deployed tools
        paths.append([self.path, '.temp', 'tools'])
        # current dir
        paths.append([self.path])

        return self._find_file_paths(paths, 'requirements.txt')

    def _find_file_paths(self, paths, fl):
        for p in paths:
            path = os.path.join(*p)
            if os.path.isdir(path) and os.path.isfile(os.path.join(path, fl)):
                return os.path.join(path)
        return None

    def check_requirements(self, show_warning=False):
        req_path = self.get_requirements() or self.path
        req_file = 'requirements.txt'
        missing = []
        try:
            with open(os.path.join(req_path, req_file), 'r') as f:
                import pip
                installed_packages = [re.sub(r'-', '_', package.project_name.lower()) for package in pip.get_installed_distributions(local_only=True)]
                for line in f.read().splitlines():
                    pkg = re.sub(r'-', '_', re.sub(r'^([\w-]+).*$', r'\1', line).lower())
                    if not pkg in installed_packages:
                        missing.append(pkg)

                if missing and install_requirements:
                    try:
                        action("Auto-installing missing Python modules...")
                        pquery(['pip', 'install', '-q', '-r', os.path.join(req_path, req_file)])
                        missing = []
                    except ProcessException:
                        warning("Unable to auto-install required Python modules.")

        except (IOError, ImportError, OSError):
            pass

        if missing:
            err = (
                "-----------------------------------------------------------------\n"
                "The aos OS tools in this program require the following Python modules: %s\n"
                "You can install all missing modules by running \"pip install -r %s\" in \"%s\"" % (', '.join(missing), req_file, req_path))
            if os.name == 'posix':
                err += "\nOn Posix systems (Linux, Mac, etc) you might have to switch to superuser account or use \"sudo\""

            if show_warning:
                warning(err)
            else:
                error(err, 1)


    # Routines after cloning aos
    def post_action(self):
        aos_tools_path = self.get_tools_dir()

        if not aos_tools_path and (self.is_classic or os.path.exists(os.path.join(self.path, Cfg.file))):
            self.add_tools(os.path.join(self.path, '.temp'))
            aos_tools_path = self.get_tools_dir()

        if not aos_tools_path:
            warning("Cannot find the aos tools directory in \"%s\"" % self.path)
            return False

        if (not os.path.isfile(os.path.join(self.path, 'aos_settings.py')) and
                os.path.isfile(os.path.join(aos_tools_path, 'default_settings.py'))):
            shutil.copy(os.path.join(aos_tools_path, 'default_settings.py'), os.path.join(self.path, 'aos_settings.py'))

        self.check_requirements(True)

    def add_tools(self, path):
        if not os.path.exists(path):
            os.mkdir(path)
        with cd(path):
            tools_dir = 'tools'
            if not os.path.exists(tools_dir):
                try:
                    action("Couldn't find build tools in your program. Downloading the aos 2.0 SDK tools...")
                    repo = Repo.fromurl(aos_sdk_tools_url)
                    repo.clone(aos_sdk_tools_url, tools_dir)
                except Exception:
                    if os.path.exists(tools_dir):
                        rmtree_readonly(tools_dir)
                    error("An error occurred while cloning the aos SDK tools from \"%s\"" % aos_sdk_tools_url)

    def update_tools(self, path):
        tools_dir = 'tools'
        if os.path.exists(os.path.join(path, tools_dir)):
            with cd(os.path.join(path, tools_dir)):
                try:
                    action("Updating the aos 2.0 SDK tools...")
                    repo = Repo.fromrepo()
                    repo.update()
                except Exception:
                    error("An error occurred while update the aos SDK tools from \"%s\"" % aos_sdk_tools_url)

    def get_tools(self):
        aos_tools_path = self.get_tools_dir()
        if not aos_tools_path:
            error('The aos tools were not found in "%s". \nRun `aos deploy` to install dependencies and tools. ' % self.path, -1)
        return aos_tools_path

    def get_env(self):
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.abspath(self.path)
        compilers = ['ARM', 'GCC_ARM', 'IAR']
        for c in compilers:
            if self.get_cfg(c+'_PATH'):
                env['aos_'+c+'_PATH'] = self.get_cfg(c+'_PATH')

        return env

    def get_target(self, target=None):
        target_cfg = self.get_cfg('TARGET')
        target = target if target else target_cfg

        if target and (target.lower() == 'detect' or target.lower() == 'auto'):
            targets = self.get_detected_targets()
            if targets == False:
                error("The target detection requires that the 'aos-ls' python module is installed.\nYou can install aos-ls by running 'pip install aos-ls'.")
            elif len(targets) > 1:
                error("Multiple targets were detected.\nOnly 1 target board should be connected to your system when you use the '-m auto' switch.")
            elif len(targets) == 0:
                error("No targets were detected.\nPlease make sure a target board is connected to this system.")
            else:
                action("Detected \"%s\" connected to \"%s\" and using com port \"%s\"" % (targets[0]['name'], targets[0]['mount'], targets[0]['serial']))
                target = targets[0]['name']

        if target is None:
            error("Please specify target using the -m switch or set default target using command 'aos target'", 1)
        return target

    def get_toolchain(self, toolchain=None):
        toolchain_cfg = self.get_cfg('TOOLCHAIN')
        tchain = toolchain if toolchain else toolchain_cfg
        if tchain is None:
            error("Please specify toolchain using the -t switch or set default toolchain using command 'aos toolchain'", 1)
        return tchain

    def set_defaults(self, target=None, toolchain=None):
        if target and not self.get_cfg('TARGET'):
            self.set_cfg('TARGET', target)
        if toolchain and not self.get_cfg('TOOLCHAIN'):
            self.set_cfg('TOOLCHAIN', toolchain)

    def get_macros(self):
        macros = []
        if os.path.isfile('MACROS.txt'):
            with open('MACROS.txt') as f:
                macros = f.read().splitlines()
        return macros


    def ignore_build_dir(self):
        build_path = os.path.join(self.path, self.build_dir)
        if not os.path.exists(build_path):
            os.mkdir(build_path)
        if not os.path.exists(os.path.join(build_path, '.aosignore')):
            try:
                with open(os.path.join(build_path, '.aosignore'), 'w') as f:
                    f.write('*\n')
            except IOError:
                error("Unable to write build ignore file in \"%s\"" % os.path.join(build_path, '.aosignore'), 1)

    def get_detected_targets(self):
        targets = []
        try:
            import aos_lstools
            oldError = None
            if os.name == 'nt':
                oldError = ctypes.windll.kernel32.SetErrorMode(1) # Disable Windows error box temporarily. note that SEM_FAILCRITICALERRORS = 1
            aoss = aos_lstools.create()
            detect_muts_list = aoss.list_aoss()
            if os.name == 'nt':
                ctypes.windll.kernel32.SetErrorMode(oldError)

            for mut in detect_muts_list:
                targets.append({
                    'id': mut['target_id'], 'name': mut['platform_name'],
                    'mount': mut['mount_point'], 'serial': mut['serial_port']
                })
        except (IOError, ImportError, OSError):
            return False

        return targets
