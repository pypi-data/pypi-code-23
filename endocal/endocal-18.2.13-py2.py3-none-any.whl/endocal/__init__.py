#!/usr/bin/env python

try:
    from cv2 import VideoCapture, imshow, waitKey,\
        imwrite, putText, FONT_HERSHEY_PLAIN, drawChessboardCorners
except ImportError as e:
    print('OpenCV does not seem to be installed on your system.')
    print('See http://opencv.org for how to install it.')
    print('The detailed error message was:')
    print(str(e))
    quit()

from argparse import ArgumentParser
from numpy import zeros, uint8
import pkg_resources
from os.path import join
import endocal.calibration as calibration
from endocal.utils import check_positive_int

KEY_QUIT = 27
KEY_TOGGLE_ACQUISITION = ord(calibration.State.KEYS[calibration.State.ACQUIRING])
KEY_ABORT_ACQUISITION = ord(calibration.State.KEYS[calibration.State.CORRECTING])


def __frame_size(video_source_desc):
    cap = VideoCapture(video_source_desc)
    ret, tmp_image = cap.read()
    cap.release()
    if not ret:
        raise RuntimeError('Could not read ' + str(video_source_desc))
    return [0, 0, tmp_image.shape[1], tmp_image.shape[0]]


def __run(video_source_desc, roi, pattern_specs, calibration_file,
          output_folder, max_num_frames = float('inf')):
    full = __frame_size(video_source_desc)
    if roi is None:
        roi = full

    pattern_specs = tuple(pattern_specs)
    calibrator = calibration.Calibrator(pattern_specs=pattern_specs,
                                        file_path=calibration_file,
                                        # i.e. None handled internally:
                                        roi=roi,
                                        full=full)
    state = calibration.State(calibrator)
    source = VideoCapture(video_source_desc)
    file_io = calibration.FileIO(output_folder)

    if not source.isOpened():
        raise RuntimeError('Could not open ' + str(video_source_desc))

    frame = zeros((roi[3], 2 * roi[2], 3), dtype=uint8)
    num_frames = 0
    while True:
        ret, image = source.read()
        if not ret:
            source = VideoCapture(video_source_desc)
            continue
        image = image[roi[1]:roi[1]+roi[3],
                      roi[0]:roi[0]+roi[2]]
        frame[0:roi[3], roi[2]:2*roi[2]] = zeros(image.shape)
        if state.is_correcting():
            ret, corrected_image = calibrator.correct(image)
            if ret:
                frame[0:roi[3], roi[2]:2*roi[2]] = corrected_image
        elif state.is_acquiring():
            if num_frames < max_num_frames:
                ret, blobs = calibrator.append(image)
                if ret:
                    num_frames += 1

                    file_path = file_io.next_image()
                    if file_path is not None:
                        imwrite(file_path, image)

                    drawChessboardCorners(image, calibrator.pattern_dims, blobs, ret)
        elif state.is_calibrating():
            if calibrator.done():
                state.correcting()

        frame[0:roi[3], 0:roi[2]] = image
        putText(frame, state.what(), (30, 30), FONT_HERSHEY_PLAIN, 2, (0, 0, 255))
        imshow('Optical distortion calibration', frame)

        # user input
        key = waitKey(50)
        if (0xFF & key == KEY_QUIT) or image.size == 0:
            break
        elif 0xFF & key == KEY_TOGGLE_ACQUISITION:
            if state.is_correcting():
                file_io.new_session()
                source.release()
                source = VideoCapture(video_source_desc)
                calibrator.reset()
                state.acquiring()
            elif state.is_acquiring():
                num_frames = 0
                if calibrator.can():
                    calibrator.start(file_io.calibration())
                    state.calibrating()
                else:
                    calibrator.reset()
                    state.correcting()
        elif 0xFF & key == KEY_ABORT_ACQUISITION:
            if state.is_acquiring():
                num_frames = 0
                calibrator.reset()
                state.correcting()

    source.release()


def main():
    # parse arguments
    parser = ArgumentParser()
    parser.add_argument('--input', type=str,
                        help='Video file, video folder or device id (e.g. 1 for /dev/video1)',
                        required=True)
    parser.add_argument('--calibration-file', type=str,
                        help='YAML file with calibration parameters',
                        required=False)
    parser.add_argument('--output-folder', type=str,
                        help='Where to log results',
                        required=True)
    parser.add_argument('--roi', nargs=4, type=int,
                        help='Sub-frame specs: <x> <y> <width> <height>',
                        required=False)
    parser.add_argument('--pattern-specs', nargs=4, type=float,
                        help='Calibration pattern dimensions: <rows> <cols> '
                             '<row_spacing> <col_spacing> (rows a.k.a. width, '
                             'cols a.k.a. height)',
                        required=True)
    parser.add_argument('--max-views', type=check_positive_int,
                        help='Maximum number of views to use when calibrating',
                        required=False, default=float('inf'))
    args = parser.parse_args()

    # do work
    try:
        video_source_desc = int(args.input)
    except ValueError:
        video_source_desc = args.input

    __run(video_source_desc=video_source_desc, roi=args.roi,
          pattern_specs=args.pattern_specs, calibration_file=args.calibration_file,
          output_folder=args.output_folder, max_num_frames=args.max_views)


def test():
    dataset_desc = 'sample_002'
    file_wildcard = 'frame_%03d.jpg'
    data_dir = pkg_resources.resource_filename('endocal', join('data', dataset_desc))
    __run(video_source_desc=join(data_dir, file_wildcard),
          max_num_frames=11,
          roi=None,
          pattern_specs=[3, 11, 3, 1],
          calibration_file=None,
          output_folder='./tmp-' + dataset_desc)
