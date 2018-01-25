# -*- coding: utf-8 -*-
# -*- coding: utf8 -*-
"""Autogenerated file - DO NOT EDIT
If you spot a bug, please report it on the mailing list and/or change the generator."""

from nipype.interfaces.base import CommandLine, CommandLineInputSpec, SEMLikeCommandLine, TraitedSpec, File, Directory, traits, isdefined, InputMultiPath, OutputMultiPath
import os


class RobustStatisticsSegmenterInputSpec(CommandLineInputSpec):
    expectedVolume = traits.Float(
        desc="The approximate volume of the object, in mL.",
        argstr="--expectedVolume %f")
    intensityHomogeneity = traits.Float(
        desc=
        "What is the homogeneity of intensity within the object? Given constant intensity at 1.0 score and extreme fluctuating intensity at 0.",
        argstr="--intensityHomogeneity %f")
    curvatureWeight = traits.Float(
        desc=
        "Given sphere 1.0 score and extreme rough bounday/surface 0 score, what is the expected smoothness of the object?",
        argstr="--curvatureWeight %f")
    labelValue = traits.Int(
        desc="Label value of the output image", argstr="--labelValue %d")
    maxRunningTime = traits.Float(
        desc="The program will stop if this time is reached.",
        argstr="--maxRunningTime %f")
    originalImageFileName = File(
        position=-3,
        desc="Original image to be segmented",
        exists=True,
        argstr="%s")
    labelImageFileName = File(
        position=-2,
        desc="Label image for initialization",
        exists=True,
        argstr="%s")
    segmentedImageFileName = traits.Either(
        traits.Bool,
        File(),
        position=-1,
        hash_files=False,
        desc="Segmented image",
        argstr="%s")


class RobustStatisticsSegmenterOutputSpec(TraitedSpec):
    segmentedImageFileName = File(
        position=-1, desc="Segmented image", exists=True)


class RobustStatisticsSegmenter(SEMLikeCommandLine):
    """title: Robust Statistics Segmenter

category: Segmentation.Specialized

description: Active contour segmentation using robust statistic.

version: 1.0

documentation-url: http://wiki.slicer.org/slicerWiki/index.php/Documentation/4.1/Modules/RobustStatisticsSegmenter

contributor: Yi Gao (gatech), Allen Tannenbaum (gatech), Ron Kikinis (SPL, BWH)

acknowledgements: This work is part of the National Alliance for Medical Image Computing (NAMIC), funded by the National Institutes of Health

"""

    input_spec = RobustStatisticsSegmenterInputSpec
    output_spec = RobustStatisticsSegmenterOutputSpec
    _cmd = "RobustStatisticsSegmenter "
    _outputs_filenames = {
        'segmentedImageFileName': 'segmentedImageFileName.nii'
    }


class EMSegmentCommandLineInputSpec(CommandLineInputSpec):
    mrmlSceneFileName = File(
        desc="Active MRML scene that contains EMSegment algorithm parameters.",
        exists=True,
        argstr="--mrmlSceneFileName %s")
    resultVolumeFileName = traits.Either(
        traits.Bool,
        File(),
        hash_files=False,
        desc=
        "The file name that the segmentation result volume will be written to.",
        argstr="--resultVolumeFileName %s")
    targetVolumeFileNames = InputMultiPath(
        File(exists=True),
        desc=
        "File names of target volumes (to be segmented).  The number of target images must be equal to the number of target images specified in the parameter set, and these images must be spatially aligned.",
        argstr="--targetVolumeFileNames %s...")
    intermediateResultsDirectory = Directory(
        desc=
        "Directory where EMSegmenter will write intermediate data (e.g., aligned atlas data).",
        exists=True,
        argstr="--intermediateResultsDirectory %s")
    parametersMRMLNodeName = traits.Str(
        desc=
        "The name of the EMSegment parameters node within the active MRML scene.  Leave blank for default.",
        argstr="--parametersMRMLNodeName %s")
    disableMultithreading = traits.Int(
        desc=
        "Disable multithreading for the EMSegmenter algorithm only! Preprocessing might still run in multi-threaded mode. -1: Do not overwrite default value. 0: Disable. 1: Enable.",
        argstr="--disableMultithreading %d")
    dontUpdateIntermediateData = traits.Int(
        desc=
        "Disable update of intermediate results.  -1: Do not overwrite default value. 0: Disable. 1: Enable.",
        argstr="--dontUpdateIntermediateData %d")
    verbose = traits.Bool(desc="Enable verbose output.", argstr="--verbose ")
    loadTargetCentered = traits.Bool(
        desc="Read target files centered.", argstr="--loadTargetCentered ")
    loadAtlasNonCentered = traits.Bool(
        desc="Read atlas files non-centered.",
        argstr="--loadAtlasNonCentered ")
    taskPreProcessingSetting = traits.Str(
        desc="Specifies the different task parameter. Leave blank for default.",
        argstr="--taskPreProcessingSetting %s")
    keepTempFiles = traits.Bool(
        desc=
        "If flag is set then at the end of command the temporary files are not removed",
        argstr="--keepTempFiles ")
    resultStandardVolumeFileName = File(
        desc=
        "Used for testing.  Compare segmentation results to this image and return EXIT_FAILURE if they do not match.",
        exists=True,
        argstr="--resultStandardVolumeFileName %s")
    dontWriteResults = traits.Bool(
        desc=
        "Used for testing.  Don't actually write the resulting labelmap to disk.",
        argstr="--dontWriteResults ")
    generateEmptyMRMLSceneAndQuit = traits.Either(
        traits.Bool,
        File(),
        hash_files=False,
        desc=
        "Used for testing.  Only write a scene with default mrml parameters.",
        argstr="--generateEmptyMRMLSceneAndQuit %s")
    resultMRMLSceneFileName = traits.Either(
        traits.Bool,
        File(),
        hash_files=False,
        desc=
        "Write out the MRML scene after command line substitutions have been made.",
        argstr="--resultMRMLSceneFileName %s")
    disableCompression = traits.Bool(
        desc="Don't use compression when writing result image to disk.",
        argstr="--disableCompression ")
    atlasVolumeFileNames = InputMultiPath(
        File(exists=True),
        desc=
        "Use an alternative atlas to the one that is specified by the mrml file - note the order matters ! ",
        argstr="--atlasVolumeFileNames %s...")
    registrationPackage = traits.Str(
        desc=
        "specify the registration package for preprocessing (CMTK or BRAINS or PLASTIMATCH or DEMONS)",
        argstr="--registrationPackage %s")
    registrationAffineType = traits.Int(
        desc=
        "specify the accuracy of the affine registration. -2: Do not overwrite default, -1: Test, 0: Disable, 1: Fast, 2: Accurate",
        argstr="--registrationAffineType %d")
    registrationDeformableType = traits.Int(
        desc=
        "specify the accuracy of the deformable registration. -2: Do not overwrite default, -1: Test, 0: Disable, 1: Fast, 2: Accurate",
        argstr="--registrationDeformableType %d")


class EMSegmentCommandLineOutputSpec(TraitedSpec):
    resultVolumeFileName = File(
        desc=
        "The file name that the segmentation result volume will be written to.",
        exists=True)
    generateEmptyMRMLSceneAndQuit = File(
        desc=
        "Used for testing.  Only write a scene with default mrml parameters.",
        exists=True)
    resultMRMLSceneFileName = File(
        desc=
        "Write out the MRML scene after command line substitutions have been made.",
        exists=True)


class EMSegmentCommandLine(SEMLikeCommandLine):
    """title:
  EMSegment Command-line


category:
  Segmentation.Specialized


description:
  This module is used to simplify the process of segmenting large collections of images by providing a command line interface to the EMSegment algorithm for script and batch processing.


documentation-url: http://www.slicer.org/slicerWiki/index.php/Documentation/4.0/EMSegment_Command-line

contributor: Sebastien Barre, Brad Davis, Kilian Pohl, Polina Golland, Yumin Yuan, Daniel Haehn

acknowledgements: Many people and organizations have contributed to the funding, design, and development of the EMSegment algorithm and its various implementations.


"""

    input_spec = EMSegmentCommandLineInputSpec
    output_spec = EMSegmentCommandLineOutputSpec
    _cmd = "EMSegmentCommandLine "
    _outputs_filenames = {
        'generateEmptyMRMLSceneAndQuit': 'generateEmptyMRMLSceneAndQuit',
        'resultMRMLSceneFileName': 'resultMRMLSceneFileName',
        'resultVolumeFileName': 'resultVolumeFileName.mhd'
    }


class BRAINSROIAutoInputSpec(CommandLineInputSpec):
    inputVolume = File(
        desc="The input image for finding the largest region filled mask.",
        exists=True,
        argstr="--inputVolume %s")
    outputROIMaskVolume = traits.Either(
        traits.Bool,
        File(),
        hash_files=False,
        desc="The ROI automatically found from the input image.",
        argstr="--outputROIMaskVolume %s")
    outputClippedVolumeROI = traits.Either(
        traits.Bool,
        File(),
        hash_files=False,
        desc="The inputVolume clipped to the region of the brain mask.",
        argstr="--outputClippedVolumeROI %s")
    otsuPercentileThreshold = traits.Float(
        desc="Parameter to the Otsu threshold algorithm.",
        argstr="--otsuPercentileThreshold %f")
    thresholdCorrectionFactor = traits.Float(
        desc=
        "A factor to scale the Otsu algorithm's result threshold, in case clipping mangles the image.",
        argstr="--thresholdCorrectionFactor %f")
    closingSize = traits.Float(
        desc=
        "The Closing Size (in millimeters) for largest connected filled mask.  This value is divided by image spacing and rounded to the next largest voxel number.",
        argstr="--closingSize %f")
    ROIAutoDilateSize = traits.Float(
        desc=
        "This flag is only relavent when using ROIAUTO mode for initializing masks.  It defines the final dilation size to capture a bit of background outside the tissue region.  At setting of 10mm has been shown to help regularize a BSpline registration type so that there is some background constraints to match the edges of the head better.",
        argstr="--ROIAutoDilateSize %f")
    outputVolumePixelType = traits.Enum(
        "float",
        "short",
        "ushort",
        "int",
        "uint",
        "uchar",
        desc=
        "The output image Pixel Type is the scalar datatype for representation of the Output Volume.",
        argstr="--outputVolumePixelType %s")
    numberOfThreads = traits.Int(
        desc="Explicitly specify the maximum number of threads to use.",
        argstr="--numberOfThreads %d")


class BRAINSROIAutoOutputSpec(TraitedSpec):
    outputROIMaskVolume = File(
        desc="The ROI automatically found from the input image.", exists=True)
    outputClippedVolumeROI = File(
        desc="The inputVolume clipped to the region of the brain mask.",
        exists=True)


class BRAINSROIAuto(SEMLikeCommandLine):
    """title: Foreground masking (BRAINS)

category: Segmentation.Specialized

description: This tool uses a combination of otsu thresholding and a closing operations to identify the most prominant foreground region in an image.


version: 2.4.1

license: https://www.nitrc.org/svn/brains/BuildScripts/trunk/License.txt

contributor: Hans J. Johnson, hans-johnson -at- uiowa.edu, http://wwww.psychiatry.uiowa.edu

acknowledgements: Hans Johnson(1,3,4); Kent Williams(1); Gregory Harris(1), Vincent Magnotta(1,2,3);  Andriy Fedorov(5), fedorov -at- bwh.harvard.edu (Slicer integration); (1=University of Iowa Department of Psychiatry, 2=University of Iowa Department of Radiology, 3=University of Iowa Department of Biomedical Engineering, 4=University of Iowa Department of Electrical and Computer Engineering, 5=Surgical Planning Lab, Harvard)

"""

    input_spec = BRAINSROIAutoInputSpec
    output_spec = BRAINSROIAutoOutputSpec
    _cmd = "BRAINSROIAuto "
    _outputs_filenames = {
        'outputROIMaskVolume': 'outputROIMaskVolume.nii',
        'outputClippedVolumeROI': 'outputClippedVolumeROI.nii'
    }
