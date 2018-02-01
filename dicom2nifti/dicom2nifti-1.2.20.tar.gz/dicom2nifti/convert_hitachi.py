# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""

from __future__ import print_function

import dicom2nifti.patch_pydicom_encodings

dicom2nifti.patch_pydicom_encodings.apply()

import logging

try:
    import pydicom.config as pydicom_config
    from pydicom.tag import Tag
except ImportError:
    import dicom.config as pydicom_config
    from dicom.tag import Tag

import dicom2nifti.convert_generic as convert_generic

pydicom_config.enforce_valid_values = False
logger = logging.getLogger(__name__)


def is_hitachi(dicom_input):
    """
    Use this function to detect if a dicom series is a hitachi dataset

    :param dicom_input: directory with dicom files for 1 scan of a dicom_header
    """
    # read dicom header
    header = dicom_input[0]

    if 'Manufacturer' not in header or 'Modality' not in header:
        return False  # we try generic conversion in these cases

    # check if Modality is mr
    if header.Modality.upper() != 'MR':
        return False

    # check if manufacturer is hitachi
    if 'HITACHI' not in header.Manufacturer.upper():
        return False

    return True


def dicom_to_nifti(dicom_input, output_file):
    """
    This is the main dicom to nifti conversion fuction for hitachi images.
    As input hitachi images are required. It will then determine the type of images and do the correct conversion

    Examples: See unit test

    :param output_file: file path to the output nifti
    :param dicom_input: directory with dicom files for 1 scan
    """

    assert is_hitachi(dicom_input)

    # TODO add validations and conversion for DTI and fMRI once testdata is available

    logger.info('Assuming anatomical data')
    return convert_generic.dicom_to_nifti(dicom_input, output_file)


