"""Module for batch converting images to JPEG 2000 format.

Takes an input directory and recreates the directory structure, with
converted images, in the specified output directory.

WARNING: If the same directory contains two or more images with the
same name (excepting the extension), only one of these images will
end up converted.

WARNING: kdu_compress does not handle filenames containing a comma,
even if the entire string is quoted or the comma quoted with a \.

"""

import copyreg
import logging
import multiprocessing
import os
import shlex
import subprocess
import types

import progressbar as pb

CONVERT_TO_JP2_LOSSLESS = 'kdu_compress -i "%s" -o "%s" -rate - Creversible=yes Clevels=5 Stiles="{1024,1024}" Cblk="{64,64}" Corder=RPCL'
CONVERT_TO_JP2_LOSSY = 'kdu_compress -i "%s" -o "%s" -rate -,4,2.34,1.36,0.797,0.466,0.272,0.159,0.0929,0.0543,0.0317,0.0185 Stiles="{1024,1024}" Cblk="{64,64}" Creversible=no Clevels=5 Corder=RPCL Cmodes=BYPASS'
CONVERT_TO_TIFF = 'convert -compress None -alpha off "%s" "%s"'

class JP2Converter (object):

    def __init__ (self, in_dir, out_dir, force=False, show_progress=False):
        """Initialise this object.

        :param in_dir: path to directory containing images to be converted
        :type in_dir: `str`
        :param out_dir: path to directory to output converted images
        :type out_dir: `str`
        :param force: whether to overwrite existing converted images
        :type force: `bool`
        :param show_progress: whether to show a progress bar during conversion
        :type show_progress: `bool`

        """
        self._in_dir = os.path.abspath(in_dir)
        self._out_dir = os.path.abspath(out_dir)
        self._force = force
        self._progress = show_progress
        self._bar = None
        self._has_errors = False

        if not self._check_kdu():
            raise EnvironmentError('kdu_compress not on path.')

    def convert (self, lossless=False):
        """Converts images.

        Returns True if there were no errors.

        :param compress: whether to use a lossless conversion
        :type compress: `bool`
        :rtype: `bool`

        """
        self._has_errors = False
        if self._progress:
            max_val = 0
            for root, dirs, files in os.walk(self._in_dir):
                max_val += len(files)
            self._bar = pb.ProgressBar(widgets=[pb.Percentage(), pb.Bar()],
                                       maxval=max_val).start()
        pool = multiprocessing.Pool()
        command = CONVERT_TO_JP2_LOSSY
        if lossless:
            command = CONVERT_TO_JP2_LOSSLESS
        for root, dirs, files in os.walk(self._in_dir):
            out_rel_path = os.path.relpath(root, self._in_dir)
            out_full_path = os.path.abspath(
                os.path.join(self._out_dir, out_rel_path))
            try:
                os.mkdir(out_full_path)
            except OSError:
                # It is not an error for the directory to already exist.
                pass
            for name in files:
                basename = os.path.splitext(name)[0]
                in_file = os.path.join(root, name)
                base_out_file = os.path.join(out_full_path, basename)
                tiff_file = '%s.tif' % base_out_file
                jp2_file = '%s.jp2' % base_out_file
                if self._force or not(os.path.isfile(jp2_file)):
                    params = (in_file, tiff_file, jp2_file, command)
                    pool.apply_async(self._convert, params,
                                     callback=self._result_callback)
                elif self._progress:
                    self._bar.update(self._bar.currval + 1)
        pool.close()
        pool.join()
        if self._progress:
            self._bar.finish()
        return not(self._has_errors)

    def _convert (self, in_file, tiff_file, jp2_file, jp2_command):
        command = CONVERT_TO_TIFF % (in_file, tiff_file)
        proc = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        err = proc.communicate()[1]
        if err:
            logging.error('Error converting %s to TIFF: %s' % (in_file, err))
            # In some cases, at least, an error may be reported
            # (typically "unknown field") but the TIFF is in fact
            # converted in a visually satisfactory way. In such cases,
            # where the converted TIFF file is created, continue on
            # with the JPEG 2000 conversion.
            if not os.path.exists(tiff_file):
                return False
        command = jp2_command % (tiff_file, jp2_file)
        proc = subprocess.Popen(
            shlex.split(command), stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        err = proc.communicate()[1]
        if err:
            logging.error('Error converting %s to JPEG 2000: %s' %
                          (tiff_file, err))
            return False
        try:
            os.remove(tiff_file)
        except (IOError, OSError) as e:
            logging.warn('Error removing TIFF %s: %s' % (tiff_file, e))
        return True

    def _result_callback (self, result):
        if not result:
            self._has_errors = True
        if self._progress:
            self._bar.update(self._bar.currval + 1)


    def _check_kdu(self):
        program = 'kdu_compress'
        def is_exe(fpath):
            return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return True
            else:
                return False


# Support pickling methods, as required by the multiprocessing
# code. Code taken from
# http://bytes.com/topic/python/answers/552476-why-cant-you-pickle-instancemethods#edit2155350
def _pickle_method (method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name, obj, cls)

def _unpickle_method (func_name, obj, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)

copyreg.pickle(types.MethodType, _pickle_method, _unpickle_method)

