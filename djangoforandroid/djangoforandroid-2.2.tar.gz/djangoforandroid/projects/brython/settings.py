import os

#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.environ['BASE_DIR'] = BASE_DIR

from djangoforandroid.framework.brython.settings import *


ANDROID = {

    'APK': {
        'name': "d4a",
        'version': '1.0',
        'package': 'com.d4a.app',
        'icon': os.path.join(BASE_DIR, 'android', 'static', 'images', 'icon.png'),
        'statusbarcolor': '#ff4081',
        'navigationbarcolor': '#ff4081',
        'orientation': 'portrait',
    },


    'BRYTHON': {
        'module': os.path.join(BASE_DIR, 'android', 'core'),
        'class': 'Brython',

    },

    'APP': {
        'multithread': False,
        #'logs': '/storage/emulated/0',
    },


    'PORT': '1234',
    'IP': '0.0.0.0',

    'PERMISSIONS': [],

    'BUILD': {
        'requirements': ['static', 'pystache'],
        'exclude_dirs': ['djangoforandroid', 'pythonforandroid', '.hg', 'brython_app'],
        'include_exts': ['py', 'png', 'sqlite3', 'html', 'css', 'js', 'svg', 'ttf', 'eot', 'woff', 'woff2', 'otf', 'xml'],
        },

    'ANDROID': {
        'ARCH': 'armeabi-v7a',
        'SDK': '/home/yeison/Development/android/sdk-tools-linux',
        'API': '21',
        'CRYSTAX_NDK': '/home/yeison/Development/android/crystax-ndk-10.3.2',
        'CRYSTAX_NDK_VERSION': '10.3.2',
        'BUILD_TOOL': 'ant',
    },

    'SPLASH': {
        'static_html': os.path.join(BASE_DIR, 'android', 'templates', 'splash.html'),
        'resources': [os.path.join(BASE_DIR, 'android', 'static', 'images', 'icon.png'),
                     ],
    },

    'CUSTOM': {
        #'sufix': piton_sufix,
        #'background': '#ff4081',

    },

    'THEME': {
        #'colors': os.path.join(BASE_DIR, 'colors.xml'),
    },



}