import unittest
from .helper import create_env, create_manifest, mock_lint, patch

import sys
sys.stderr = sys.stdout
import os

from tempfile import mkdtemp
import shutil
import argparse
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
from catkin_lint.main import prepare_arguments, run_linter
import catkin_lint.environment

class AllChecksTest(unittest.TestCase):

    @patch("os.path.isfile", lambda x: x == os.path.normpath("/mock-path/src/source.cpp"))
    def test_project(self):
        """Test minimal catkin project for compliance"""
        env = create_env(catkin_pkgs=[ "catkin", "foo", "foo_msgs" ])
        pkg = create_manifest("mock", description="Cool Worf", build_depends=[ "foo", "foo_msgs" ], run_depends=[ "foo_msgs" ])
        result = mock_lint(env, pkg,
            """\
            project(mock)
            find_package(catkin REQUIRED COMPONENTS foo foo_msgs)
            catkin_package(CATKIN_DEPENDS foo_msgs)
            include_directories(${catkin_INCLUDE_DIRS})
            add_executable(${PROJECT_NAME}_node src/source.cpp)
            target_link_libraries(${PROJECT_NAME}_node ${catkin_LIBRARIES})
            install(TARGETS ${PROJECT_NAME}_node RUNTIME DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION})
            """)
        self.assertEqual([], result)


class DummyDist(object):
    def get_release_package_xml(self, name):
        if name == "roscpp":
            raise KeyError("Mock error")
        if name == "rospy":
            return '''<package format="2">
                <name>rospy</name>
                <version>0.0.0</version>
                <description>Mock package</description>
                <maintainer email="mock@example.com">Mister Mock</maintainer>
                <license>none</license>
            </package>'''
        return None

def get_dummy_index_url():
    return "http://127.0.0.1:9"

def get_dummy_index(url):
    return None

def get_dummy_cached_distribution(index, dist_name, cache=None, allow_lazy_load=False):
    return DummyDist()

class CatkinInvokationTest(unittest.TestCase):
    
    def fake_package(self, name, depends, wsdir):
        pkgdir = os.path.join(wsdir, "src", name)
        os.makedirs(pkgdir)
        with open(os.path.join(pkgdir, "package.xml"), "w") as f:
            f.write(
                '<package format="2"><name>%s</name><version>0.0.0</version>'
                '<description>Mock package</description>'
                '<maintainer email="mock@example.com">Mister Mock</maintainer>'
                '<license>none</license>' % name
            )
            if name != "catkin":
                f.write('<buildtool_depend>catkin</buildtool_depend>')
            f.write(''.join(['<depend>%s</depend>' % dep for dep in depends]))
            f.write('</package>\n')
        with open(os.path.join(pkgdir, "CMakeLists.txt"), "w") as f:
            f.write(
                'project(%s)\n' % name +
                'find_package(catkin REQUIRED ' +
                (('COMPONENTS ' + ' '.join(dep for dep in depends)) if depends else '') + ')\n'
                'catkin_package()'
            )
        os.makedirs(os.path.join(pkgdir, ".git"))
        with open(os.path.join(pkgdir, ".git", "script"), "w") as f:
            f.write("Random executable file")
        os.chmod(os.path.join(pkgdir, ".git", "script"), 0o755)

    def raise_io_error(self, *args):
        raise IOError("mock exception")

    @patch("rosdistro.get_index_url", get_dummy_index_url)
    @patch("rosdistro.get_index", get_dummy_index)
    @patch("rosdistro.get_cached_distribution", get_dummy_cached_distribution)
    def run_catkin_lint(self, *argv):
        catkin_lint.environment._cache = None  # force cache reloads
        parser = prepare_arguments(argparse.ArgumentParser())
        args = parser.parse_args(argv)
        stdout = StringIO()
        with patch("sys.stdout", stdout):
            with patch("sys.stderr", stdout):
                returncode =  run_linter(args)
        return returncode, stdout.getvalue()
     
    def setUp(self):
        self.old_environ = os.environ
        self.upstream_ws = mkdtemp()
        self.upstream_ws_srcdir = os.path.join(self.upstream_ws, "src")
        self.fake_package("gamma", ["missing"], wsdir=self.upstream_ws)
        self.fake_package("invalid_dep", ["boost"], wsdir=self.upstream_ws)
        self.fake_package("delta", ["std_msgs"], wsdir=self.upstream_ws)
        self.fake_package("std_msgs", [], wsdir=self.upstream_ws)
        self.homedir = mkdtemp()
        self.wsdir = mkdtemp()
        self.ws_srcdir = os.path.join(self.wsdir, "src")
        os.makedirs(os.path.join(self.wsdir, "src", "no_packages_here"))
        self.fake_package("alpha", ["beta", "rospy", "roscpp"], wsdir=self.wsdir)
        self.fake_package("beta", [], wsdir=self.wsdir)
        self.fake_package("gamma", ["delta"], wsdir=self.wsdir)
        self.fake_package("broken", ["missing"], wsdir=self.wsdir)
        with open(os.path.join(self.wsdir, "src", "broken", "CATKIN_IGNORE"), "w"):
            pass
        self.fake_package(".dotdir_with_broken_package", ["missing"], wsdir=self.wsdir)
        catkin_lint.environment._cache_dir = os.path.join(self.homedir, ".ros", "catkin_lint")
        os.makedirs(catkin_lint.environment._cache_dir)
        os.environ = {
            "PATH": "/usr/bin:/bin",
            "ROS_DISTRO": "kinetic",
            "HOME": self.homedir,
            "ROS_PACKAGE_PATH": self.upstream_ws_srcdir,
        }
        shutil.copytree(os.path.join(os.path.dirname(__file__), "sources.cache"), os.path.join(self.homedir, ".ros", "rosdep", "sources.cache"))
    
    def tearDown(self):
        shutil.rmtree(self.homedir, ignore_errors=True)
        shutil.rmtree(self.wsdir, ignore_errors=True)
        shutil.rmtree(self.upstream_ws, ignore_errors=True)
        os.environ = self.old_environ

    def runTest(self):
        """Test catkin_lint invocation on a ROS workspace"""
        pwd = os.getcwd()
        os.chdir(os.path.join(self.ws_srcdir, "beta"))
        exitcode, stdout = self.run_catkin_lint()
        self.assertEqual(exitcode, 0)
        self.assertIn("checked 1 packages and found 0 problems", stdout)
        with patch("catkin_lint.linter.CMakeLinter._read_file", self.raise_io_error):
            exitcode, stdout = self.run_catkin_lint()
        self.assertEqual(exitcode, 1)
        self.assertIn("OS error: mock exception", stdout)
        os.chdir(pwd)

        exitcode, stdout = self.run_catkin_lint(self.ws_srcdir, "--explain")
        self.assertEqual(exitcode, 0)
        self.assertIn("checked 3 packages and found 0 problems", stdout)

        exitcode, stdout = self.run_catkin_lint(self.ws_srcdir, "--disable-cache", "--xml")
        self.assertEqual(exitcode, 0)
        self.assertIn("</catkin_lint>", stdout)
        self.assertIn("checked 3 packages and found 0 problems", stdout)

        exitcode, stdout = self.run_catkin_lint("--pkg", "gamma", "-c", "catkin_lint.checks.misc.project")
        self.assertEqual(exitcode, 0)
        self.assertIn("checked 1 packages and found 0 problems", stdout)

        exitcode, stdout = self.run_catkin_lint(self.ws_srcdir, "-c", "does.not.exist")
        self.assertEqual(exitcode, 1)
        self.assertIn("cannot import 'does.not.exist'", stdout)
        self.assertRaises(ImportError, self.run_catkin_lint, self.wsdir, "-c", "does.not.exist", "--debug")

        exitcode, stdout = self.run_catkin_lint("--pkg", "alpha")
        self.assertEqual(exitcode, 1)
        self.assertIn("no such package: alpha", stdout)

        exitcode, stdout = self.run_catkin_lint("--package-path", self.ws_srcdir, "--pkg", "alpha", "--pkg", "beta")
        self.assertEqual(exitcode, 0)
        self.assertIn("checked 2 packages and found 0 problems", stdout)

        os.environ["ROS_PACKAGE_PATH"] = os.pathsep.join([self.ws_srcdir, self.upstream_ws_srcdir])
        exitcode, stdout = self.run_catkin_lint("--pkg", "alpha", "--pkg", "beta")
        self.assertEqual(exitcode, 0)
        self.assertIn("checked 2 packages and found 0 problems", stdout)
        os.environ["ROS_PACKAGE_PATH"] = self.upstream_ws

        bad_path = os.path.join(self.ws_srcdir, "does_not_exist")
        exitcode, stdout = self.run_catkin_lint(bad_path)
        self.assertEqual(exitcode, 1)
        self.assertIn("not a directory", stdout)
        self.assertIn("no packages to check", stdout)

        empty_path = os.path.join(self.ws_srcdir, "no_packages_here")
        exitcode, stdout = self.run_catkin_lint(empty_path)
        self.assertEqual(exitcode, 0)
        self.assertIn("no packages to check", stdout)

        exitcode, stdout = self.run_catkin_lint("--package-path", os.pathsep.join([self.ws_srcdir, self.upstream_ws_srcdir]), "--pkg", "gamma")
        self.assertEqual(exitcode, 0)

        exitcode, stdout = self.run_catkin_lint("--package-path", os.pathsep.join([self.upstream_ws_srcdir, self.ws_srcdir]), "--pkg", "gamma")
        self.assertEqual(exitcode, 1)

        exitcode, stdout = self.run_catkin_lint("--list-check-ids")
        self.assertEqual(exitcode, 0)
        self.assertIn("\nproject_name\n", stdout)

        exitcode, stdout = self.run_catkin_lint("--dump-cache")
        self.assertEqual(exitcode, 0)
        self.assertIn("alpha", stdout)
        self.assertIn("beta", stdout)
        self.assertIn(self.wsdir, stdout)

        exitcode, stdout = self.run_catkin_lint(os.path.join(self.ws_srcdir, "alpha"), "--ignore", "unknown_depend")
        self.assertEqual(exitcode, 1)
        self.assertIn("messages have been ignored", stdout)

        exitcode, stdout = self.run_catkin_lint("--pkg", "delta", "-W0")
        self.assertEqual(exitcode, 0)
        self.assertIn("warnings have been ignored", stdout)

        exitcode, stdout = self.run_catkin_lint("--pkg", "delta", "--strict")
        self.assertEqual(exitcode, 1)

        exitcode, stdout = self.run_catkin_lint("--clear-cache")
        self.assertEqual(exitcode, 0)
        
        exitcode, stdout = self.run_catkin_lint("--dump-cache")
        self.assertEqual(exitcode, 0)
        self.assertIn("Cached local paths: 0\n", stdout)
        
        del os.environ["ROS_DISTRO"]
        exitcode, stdout = self.run_catkin_lint("--pkg", "invalid_dep")
        self.assertEqual(exitcode, 0)

        exitcode, stdout = self.run_catkin_lint("--pkg", "invalid_dep", "--rosdistro", "kinetic")
        self.assertEqual(exitcode, 1)

        del os.environ["ROS_DISTRO"]
        exitcode, stdout = self.run_catkin_lint(os.path.join(self.ws_srcdir, "alpha"))
        self.assertEqual(exitcode, 0)
        self.assertNotIn("error: unknown package", stdout)

        exitcode, stdout = self.run_catkin_lint(os.path.join(self.ws_srcdir, "alpha"), "--rosdistro", "kinetic")
        self.assertEqual(exitcode, 1)
        self.assertIn("error: unknown package", stdout)

        del os.environ["ROS_DISTRO"]
        exitcode, stdout = self.run_catkin_lint(self.ws_srcdir, "--rosdistro", "kinetic")
        self.assertEqual(exitcode, 0)
        self.assertIn("checked 3 packages and found 0 problems", stdout)
