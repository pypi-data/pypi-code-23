import pyconrad
import pyconrad.utils


def project(volume):
    volume_cl = _.OpenCLGrid3D(volume)
    projector = _.ConeBeamProjector()
    sino = _.OpenCLGrid3D(_.Grid3D(*pyconrad.utils.get_sino_size()))
    projector.fastProjectRayDrivenCL(sino, volume_cl)
    return sino


def back_project(sino):
    back_projector = _.ConeBeamBackprojector()
    return back_projector.backprojectPixelDrivenCL(sino)


pyconrad.setup_pyconrad(max_ram='8G', dev_dirs=[
                        '/localhome/local/projects/CONRAD/'])
pyconrad.start_gui()

_ = pyconrad.ClassGetter(
    'edu.stanford.rsl.conrad.phantom',
    'edu.stanford.rsl.tutorial.cone',
    'edu.stanford.rsl.conrad.utils',
    'edu.stanford.rsl.conrad.data.numeric.opencl'
)

geo = pyconrad.utils.get_geometry()

phantom = _.NumericalSheppLogan3D(
    *pyconrad.utils.get_reco_size()).getNumericalSheppLoganPhantom()
phantom.show('Phatom')


sino = project(phantom)
sino.show('Sinogram')

cosine_filter = _.edu.stanford.rsl.conrad.filtering.CosineWeightingTool()
cosine_filter.configure()
sino = _.ImageUtil.applyFilterInParallel(sino, cosine_filter, True)
sino.show('Cosine filtered')

# Parker weights missing

filter = _.edu.stanford.rsl.conrad.filtering.rampfilters.SheppLoganRampFilter()
filter.configure()
filtertool = _.edu.stanford.rsl.conrad.filtering.RampFilteringTool()
filtertool.setRamp(filter)
sino = _.ImageUtil.applyFilterInParallel(sino, filtertool, True)
sino.show('Ramp filtered')

reconstruction = back_project(sino)
reconstruction.show('Reconstruction')
