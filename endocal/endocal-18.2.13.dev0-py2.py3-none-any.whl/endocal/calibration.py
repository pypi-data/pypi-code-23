from cv2 import __version__, findCirclesGrid,\
    CALIB_CB_ASYMMETRIC_GRID, calibrateCamera, undistort,\
    CALIB_FIX_K4, CALIB_FIX_K5, CALIB_ZERO_TANGENT_DIST, projectPoints
from yaml import dump
import numpy as np
from threading import Thread
from time import strftime
from os.path import join, isdir
from os import makedirs
from random import choice
from string import ascii_uppercase
opencv_version = -1
if __version__.startswith('2'):
    opencv_version = 2
    from cv2 import SimpleBlobDetector
elif __version__.startswith('3'):
    opencv_version = 3
    from cv2 import SimpleBlobDetector_create
else:
    raise RuntimeError('OpenCV version not supported')


class State:

    """Keeps app state, providing query functions.

    See member functions for available states.

    """
    CORRECTING = 1
    CALIBRATING = 2 * CORRECTING
    ACQUIRING = 3 * CORRECTING
    KEYS = {ACQUIRING: 's', CALIBRATING: 's',
            CORRECTING: 'x'}

    def __init__(self, calibrator):
        """Initialise current state to recording.

        :param calibrator: `Calibrator` object for
        use in reporting, e.g. nr. of frames added
        """
        self.current = State.CORRECTING
        self.calibrator = calibrator

    def is_correcting(self):
        """

        :return: ``True`` if app currently online,
        i.e. correcting optical distortions
        """
        return self.current == State.CORRECTING

    def correcting(self):
        """Set current state to correcting.

        """
        self.current = State.CORRECTING

    def is_calibrating(self):
        """

        :return: ``True`` if app currently
        performing calibration
        """
        return self.current == State.CALIBRATING

    def calibrating(self):
        """Set current state to calibrating.

        """
        self.current = State.CALIBRATING

    def is_acquiring(self):
        """

        :return: ``True`` if app currently
        acquiring data for calibration
        """
        return self.current == State.ACQUIRING

    def acquiring(self):
        """Set current state to acquiring.

        """
        self.current = State.ACQUIRING

    def what(self):
        """

        :return: A string representing current
        state
        """
        if self.is_acquiring():
            msg = 'Acquired '
            if self.calibrator.grid_candidates:
                num_frames = len(self.calibrator.grid_candidates)
            else:
                num_frames = 0

            msg += str(num_frames)
            msg += ' frames '
            msg += '(min: '
            msg += str(Calibrator.MIN_FRAME_COUNT)
            msg += '), '
            if num_frames >= Calibrator.MIN_FRAME_COUNT:
                msg += State.KEYS[State.CALIBRATING]
                msg += ': calibrate, '
            msg += State.KEYS[State.CORRECTING]
            msg += ': abort acquisition'
        elif self.is_calibrating():
            msg = 'Performing calibration'
        elif self.is_correcting():
            msg = 'Correcting for optical distortions, '
            msg += State.KEYS[State.CALIBRATING]
            msg += ': start acquisition'
        msg += ', ESC: quit app'
        return msg


class Calibrator:

    """Keeps all data structures pertaining to calibration.

    """

    def __init__(self, pattern_specs, full, file_path=None, roi=None):
        """

        :param pattern_specs: Specs of used calibration
        pattern: ``width, height, row-spacing, col-spacing``
        :param full: Full frame specs: ``x, y, width, height``
        :param file_path: YAML file with calibration params
        :param roi: Sub frame specs: ``x, y, width, height``
        """
        self.pattern_dims = tuple(int(val) for val in pattern_specs[:2])
        self.pattern_spacing = pattern_specs[2:]
        if opencv_version == 2:
            self.detector = SimpleBlobDetector()
        elif opencv_version == 3:
            self.detector = SimpleBlobDetector_create()
        d_y = self.pattern_spacing[0]  # 3.0
        d_x = self.pattern_spacing[1]  # 1.0
        width = int(pattern_specs[0])
        height = int(pattern_specs[1])
        self.grid = np.zeros((width * height, 3), np.float32)
        self.grid[:, :2] = np.mgrid[0:width, 0:height].T.reshape(-1, 2)
        self.grid[:, 0] *= d_y
        self.grid[:, 1] *= d_x
        for start in range(width, width*height, 2*width):
            self.grid[start:start + width, 0] += d_y / 2
        self.grids = None
        self.grid_candidates = None
        self.image_size = None
        self.camera_matrix = None
        self.dist_coeffs = None
        self.reproj_errs = None
        Calibrator.MIN_FRAME_COUNT = 10
        self.calibration_thread = None
        self.roi = full
        if roi is not None:
            self.roi = roi
        self.full = full
        self.reset()
        # TODO file_path
        pass

    def reset(self):
        """Reset all data saved so far.

        """
        self.grids = []
        self.grid_candidates = []
        self.image_size = []
        self.camera_matrix = None  # TODO identity
        self.dist_coeffs = None  # TODO identity (??)
        self.reproj_errs = None
        # TODO
        pass

    def can(self):
        """

        :return: ``True`` if calibration can
        be performed.
        """
        return len(self.grid_candidates) >= Calibrator.MIN_FRAME_COUNT

    def correct(self, image):
        """Correct passed image.

        :param image:
        :return: ``retval`` flag and corrected image
        """
        ret = False
        corrected_image = None
        if self.camera_matrix is not None and \
           self.dist_coeffs is not None:
            corrected_image = undistort(image,
                                        self.camera_matrix,
                                        self.dist_coeffs)
            ret = True
        # TODO - if using identity?
        return ret, corrected_image

    def __calibrate(self, file_path):
        """Perform calibration, to be called as a separate
        thread.

        :param file_path: Where to save resulting calibration
        """
        ret, camera_matrix, dist_coeffs, rvecs, tvecs = \
            calibrateCamera(objectPoints=self.grids,
                            imagePoints=self.grid_candidates,
                            imageSize=self.image_size,
                            cameraMatrix=None,
                            distCoeffs=None,
                            flags=CALIB_FIX_K4 |
                            CALIB_FIX_K5 |
                            CALIB_ZERO_TANGENT_DIST)
        if ret:
            self.camera_matrix = camera_matrix
            self.dist_coeffs = dist_coeffs
            self.reproj_errs = np.full((len(self.grids),), np.inf)
            err = 0
            num_pts = 0
            # pv = per-view
            for v, (pv_obj_pts, pv_img_pts, pv_rvec, pv_tvec) in enumerate(zip(self.grids, self.grid_candidates,
                                                                               rvecs, tvecs)):
                pv_proj_img_pts, jacobians = projectPoints(
                    objectPoints=pv_obj_pts, rvec=pv_rvec, tvec=pv_tvec,
                    cameraMatrix=self.camera_matrix, distCoeffs=self.dist_coeffs)
                pv_reproj_errs = list(map(lambda img_pt, proj_img_pt: np.linalg.norm(img_pt - proj_img_pt),
                                          pv_img_pts, pv_proj_img_pts))
                pv_err_sq = np.dot(pv_reproj_errs, pv_reproj_errs)
                pv_num_pts = len(pv_reproj_errs)
                self.reproj_errs[v] = np.sqrt(pv_err_sq / pv_num_pts)

                err += pv_err_sq
                num_pts += pv_num_pts
            if file_path is not None:
                calibration_file = open(file_path, 'w')
                calibration = dict(camera_matrix=str(self.camera_matrix),
                                   dist_coeffs=str(self.dist_coeffs),
                                   per_view_reproj_errs=str(self.reproj_errs),
                                   reproj_err=ret,
                                   roi=str(self.roi),
                                   full=str(self.full))
                calibration_file.write(dump(calibration,
                                            default_flow_style=False))
                calibration_file.close()

    def start(self, file_path):
        """Start calibration thread.

        :param file_path: Where to save calibration upon
        success
        :return: ``True`` if thread started successfully.
        """
        if self.calibration_thread is None:
            self.calibration_thread = Thread(target=self.__calibrate,
                                             kwargs={'file_path': file_path})
            try:
                self.calibration_thread.start()
            except RuntimeError:
                self.calibration_thread = None
                return False
            else:
                return True
        return True

    def done(self):
        """

        :return: Whether calibration thread has finished.
        """
        if self.calibration_thread is None:
            return True

        if not self.calibration_thread.is_alive():
            self.calibration_thread = None
            return True

        return False

    def append(self, image):
        """Append image as one of frames to be used in
        calibration.

        :param image:
        :return: ``True`` if `image` usable, ``False``
        otherwise, in addition to detected circle grid
        of blobs
        """
        blobs = None
        ret, blobs = findCirclesGrid(image, self.pattern_dims,
                                     blobs, CALIB_CB_ASYMMETRIC_GRID)
        if ret:
            self.image_size = image.shape[:2]
            self.image_size = self.image_size[::-1]
            self.grid_candidates.append(blobs)
            self.grids.append(self.grid)

        return ret, blobs


class FileIO:

    """Manages file IO parameters, like session folders.

    """

    def __init__(self, output_folder):
        """

        :param output_folder: Creates session folders
        inside this one
        """
        self.output_folder = output_folder
        self.session_folder = None
        self.current_image = 1

    def new_session(self):
        """Create a new session folder to save current
        calibration data.

        """
        unique_suffix = ''.join(choice(ascii_uppercase) for _ in range(5))
        session_folder = join(self.output_folder,
                              strftime('%Y-%m-%d-%H-%M-%S') +
                              '-' + unique_suffix)
        makedirs(session_folder)
        if isdir(session_folder):
            self.session_folder = session_folder
        self.current_image = 1

    def calibration(self):
        """

        :return: File path where current calibration is
        to be saved
        """
        if self.session_folder is None:
            return None

        return join(self.session_folder, 'calibration.yml')

    def next_image(self):
        """Increment image count and get file path for
        saving next image.

        :return: File path where an image appended to
        calibration data is to be saved
        """
        if self.session_folder is None:
            return None

        file_path = join(self.session_folder,
                         'frame_' +
                         str(self.current_image).zfill(3) +
                         '.jpg')
        self.current_image += 1
        return file_path
