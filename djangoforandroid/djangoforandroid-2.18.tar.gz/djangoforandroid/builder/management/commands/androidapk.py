from django.core.management.base import BaseCommand, CommandError
import os
import shutil
import platform

from ._tools import get_p4a_args, update_apk, parcefiles, overwrite_p4a, post_update_apk, read_configuration, read_apk_args

from djangoforandroid.framework.shortcuts import brython_render
from djangoforandroid.core.toolchain import ToolchainCL
#from pythonforandroid.toolchain import ToolchainCL

#P4A = "p4a"
# P4A = "python /home/yeison/Documents/development/djangoforandroid/example/pythonforandroid/toolchain.py"

class Command(BaseCommand):
    help = 'Generate .apk for debug'
    can_import_settings = True

    #----------------------------------------------------------------------
    def add_arguments(self, parser):
        """"""

        parser.add_argument(
            '--debug',
            action='store_true',
            dest='debug',
            default=True,
            help='Debug apk with',
        )

        parser.add_argument(
            '--release',
            action='store_true',
            dest='release',
            default=False,
            help='Release unsigned apk',
        )

        parser.add_argument(
            '--install',
            action='store_true',
            dest='install',
            default=False,
            help='Install apk with adb.',
        )

        parser.add_argument(
            '--run',
            action='store_true',
            dest='run',
            default=False,
            help='Run apk with adb.',
        )

        parser.add_argument(
            '--logcat',
            action='store_true',
            dest='logcat',
            default=False,
            help='Log apk with adb.',
        )


        #parser.add_argument(
            #'--brython',
            #action='store_true',
            #dest='brython',
            #default=False,
            #help='Compile a Django less app with Brython.',
        #)



    #----------------------------------------------------------------------
    def handle(self, *args, **options):
        """"""
        from django.conf import settings


        #if options['brython']:
            #os.environ['D4A_BRYTHON'] = '1'
        #else:
            #os.environ['D4A_BRYTHON'] = '0'

        update_apk(settings)
        overwrite_p4a(settings)

        NAME = os.path.split(settings.BASE_DIR)[-1]
        build_dir = os.path.join(settings.ANDROID['BUILD']['build'], NAME)
        #build_dir = os.path.join(settings.ANDROID['BUILD']['build'])
        name = settings.ANDROID['APK']['name']
        version = settings.ANDROID['APK']['version']
        apk_debug = os.path.join(build_dir, '{}-{}-debug.apk'.format(name, version)).replace(' ', '')
        apk_release = os.path.join(build_dir, '{}-{}-release.apk'.format(name, version)).replace(' ', '')
        package = settings.ANDROID['APK']['package']

        #collectstatic
        app_dir = os.path.join(settings.ANDROID['BUILD']['build'], NAME, 'app')
        #app_dir = os.path.join(settings.ANDROID['BUILD']['build'], 'app')
        os.chdir(os.path.join(app_dir, NAME))
        host_python = "python{}.{}".format(*platform.python_version_tuple()[:2])
        os.system('{} manage.py collectstatic --noinput'.format(host_python ))
        os.system('{} manage.py compilestatic'.format(host_python ))

        post_update_apk(settings)

        os.chdir(build_dir)
        argv = read_configuration(settings)


        #if settings.ANDROID['BRYTHON']:

            #brython_app = os.path.join(app_dir, 'brython_app')
            #os.makedirs(brython_app)

            #response = brython_render(None, 'base.py', 0, {'show_splash': True})
            #index = response.getvalue()
            #with open(os.path.join(brython_app, 'index.html'), 'wb') as file:
                #file.write(index)

            #src = os.path.join('app', NAME, os.path.split(settings.STATIC_ROOT)[-1])
            #dst = os.path.join(brython_app, settings.STATIC_URL.strip('/'))


            #main_src = settings.ANDROID['BRYTHON']['module']
            #main_dst = os.path.join(brython_app, os.path.split(main_src)[-1])
            #if os.path.exists(main_src):
                #shutil.copyfile(main_src, main_dst)

            ##shutil.copyfile(src, dst, follow_symlinks=True)
            #shutil.copytree(src, dst)
            #shutil.rmtree(os.path.join(app_dir, NAME))


            #dst = os.path.join(settings.BASE_DIR, 'brython_app')
            #shutil.rmtree(dst)
            #shutil.copytree(brython_app, os.path.join(dst, 'brython_app'))

            #shutil.copyfile(main_src, main_dst)
            #shutil.copyfile(os.path.join(app_dir, 'main.py'), os.path.join(dst, 'main.py'))


        if options['release']:
            if os.path.exists(apk_release):
                os.remove(apk_release)


            keystore = settings.ANDROID['KEY']['RELEASE_KEYSTORE'].replace('.keystore', '') + ".upload.jks"
            if not os.path.exists(keystore):
                keystore = settings.ANDROID['KEY']['RELEASE_KEYSTORE']

            os.environ['P4A_RELEASE_KEYSTORE'] = keystore
            os.environ['P4A_RELEASE_KEYALIAS'] = settings.ANDROID['KEY']['RELEASE_KEYALIAS']
            os.environ['P4A_RELEASE_KEYSTORE_PASSWD'] = settings.ANDROID['KEY']['RELEASE_KEYSTORE_PASSWD']
            os.environ['P4A_RELEASE_KEYALIAS_PASSWD'] = settings.ANDROID['KEY']['RELEASE_KEYALIAS_PASSWD']


            argv.c['build_mode'] = 'release'

            #self.p4a_sign(settings, argv, apk_release)

            tc = ToolchainCL(argv)
            tc.apk(release=True)
            shutil.copy(apk_release, settings.BASE_DIR)
            run_apk = apk_release


        elif options['debug']:
            if os.path.exists(apk_debug):
                os.remove(apk_debug)

            #host_python = "python{}.{}".format(*platform.python_version_tuple()[:2])
            #os.system('{} apk {}'.format(P4A, argv))

            argv.c['build_mode'] = 'debug'
            #ToolchainCL(argv)

            tc = ToolchainCL(argv)
            tc.apk(release=False)
            shutil.copy(apk_debug, settings.BASE_DIR)
            run_apk = apk_debug



        if options['install']:
            print("Installing...")
            os.system("adb start-server")
            os.system("adb install -r {}".format(apk_release))

            if options['run']:
                print("Running...")
                os.system("adb shell monkey -p {PACKAGE} -c android.intent.category.LAUNCHER 1".format(PACKAGE=package))

            if options['logcat']:
                print("Log:")
                os.system("adb logcat")





