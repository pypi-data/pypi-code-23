# -*- coding: utf-8 -*-
# -*- coding: utf8 -*-
"""Autogenerated file - DO NOT EDIT
If you spot a bug, please report it on the mailing list and/or change the generator."""

import os

from ...base import (CommandLine, CommandLineInputSpec, SEMLikeCommandLine,
                     TraitedSpec, File, Directory, traits, isdefined,
                     InputMultiPath, OutputMultiPath)


class BRAINSResampleInputSpec(CommandLineInputSpec):
    inputVolume = File(
        desc="Image To Warp", exists=True, argstr="--inputVolume %s")
    referenceVolume = File(
        desc=
        "Reference image used only to define the output space. If not specified, the warping is done in the same space as the image to warp.",
        exists=True,
        argstr="--referenceVolume %s")
    outputVolume = traits.Either(
        traits.Bool,
        File(),
        hash_files=False,
        desc="Resulting deformed image",
        argstr="--outputVolume %s")
    pixelType = traits.Enum(
        "float",
        "short",
        "ushort",
        "int",
        "uint",
        "uchar",
        "binary",
        desc=
        "Specifies the pixel type for the input/output images.  The \'binary\' pixel type uses a modified algorithm whereby the image is read in as unsigned char, a signed distance map is created, signed distance map is resampled, and then a thresholded image of type unsigned char is written to disk.",
        argstr="--pixelType %s")
    deformationVolume = File(
        desc=
        "Displacement Field to be used to warp the image (ITKv3 or earlier)",
        exists=True,
        argstr="--deformationVolume %s")
    warpTransform = File(
        desc=
        "Filename for the BRAINSFit transform (ITKv3 or earlier) or composite transform file (ITKv4)",
        exists=True,
        argstr="--warpTransform %s")
    interpolationMode = traits.Enum(
        "NearestNeighbor",
        "Linear",
        "ResampleInPlace",
        "BSpline",
        "WindowedSinc",
        "Hamming",
        "Cosine",
        "Welch",
        "Lanczos",
        "Blackman",
        desc=
        "Type of interpolation to be used when applying transform to moving volume.  Options are Linear, ResampleInPlace, NearestNeighbor, BSpline, or WindowedSinc",
        argstr="--interpolationMode %s")
    inverseTransform = traits.Bool(
        desc=
        "True/False is to compute inverse of given transformation. Default is false",
        argstr="--inverseTransform ")
    defaultValue = traits.Float(
        desc="Default voxel value", argstr="--defaultValue %f")
    gridSpacing = InputMultiPath(
        traits.Int,
        desc=
        "Add warped grid to output image to help show the deformation that occured with specified spacing.   A spacing of 0 in a dimension indicates that grid lines should be rendered to fall exactly (i.e. do not allow displacements off that plane).  This is useful for makeing a 2D image of grid lines from the 3D space",
        sep=",",
        argstr="--gridSpacing %s")
    numberOfThreads = traits.Int(
        desc="Explicitly specify the maximum number of threads to use.",
        argstr="--numberOfThreads %d")


class BRAINSResampleOutputSpec(TraitedSpec):
    outputVolume = File(desc="Resulting deformed image", exists=True)


class BRAINSResample(SEMLikeCommandLine):
    """title: Resample Image (BRAINS)

category: Registration

description: This program collects together three common image processing tasks that all involve resampling an image volume: Resampling to a new resolution and spacing, applying a transformation (using an ITK transform IO mechanisms) and Warping (using a vector image deformation field).  Full documentation available here: http://wiki.slicer.org/slicerWiki/index.php/Documentation/4.1/Modules/BRAINSResample.

version: 3.0.0

documentation-url: http://www.slicer.org/slicerWiki/index.php/Documentation/4.1/Modules/BRAINSResample

license: https://www.nitrc.org/svn/brains/BuildScripts/trunk/License.txt

contributor: This tool was developed by Vincent Magnotta, Greg Harris, and Hans Johnson.

acknowledgements: The development of this tool was supported by funding from grants NS050568 and NS40068 from the National Institute of Neurological Disorders and Stroke and grants MH31593, MH40856, from the National Institute of Mental Health.

"""

    input_spec = BRAINSResampleInputSpec
    output_spec = BRAINSResampleOutputSpec
    _cmd = " BRAINSResample "
    _outputs_filenames = {'outputVolume': 'outputVolume.nii'}
    _redirect_x = False
