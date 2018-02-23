import pyconrad

_ = pyconrad.ClassGetter(
    'edu.stanford.rsl.conrad.utils',
    'java.beans',
    'java.io',
    'edu.stanford.rsl.conrad.geometry.trajectories'
)


def get_conf() -> pyconrad.AutoCompleteConrad.edu.stanford.rsl.conrad.utils.Configuration:
    conf = _.Configuration.getGlobalConfiguration()

    return conf


def get_geometry() -> pyconrad.AutoCompleteConrad.edu.stanford.rsl.conrad.geometry.trajectories.Trajectory:
    #  #TODO load config on pyconrad startup
    geo = _.Configuration.getGlobalConfiguration().getGeometry()
    return geo


def get_sino_shape() -> tuple:
    conf = _.Configuration.getGlobalConfiguration()
    geo = conf.getGeometry()
    return (geo.getProjectionStackSize(), geo.getDetectorHeight(), geo.getDetectorWidth())


def get_sino_size() -> list:
    return (reversed(get_sino_shape()))


def get_reco_shape() -> tuple:
    conf = _.Configuration.getGlobalConfiguration()
    geo = conf.getGeometry()  # type: AutoCompleteConrad.edu.stanford.rsl
    return (geo.getReconDimensionZ(), geo.getReconDimensionY(), geo.getReconDimensionX())


def get_reco_size() -> list:
    return [*reversed(get_reco_shape())]


def get_reco_origin() -> tuple:
    conf = _.Configuration.getGlobalConfiguration()
    geo = conf.getGeometry()  # type: AutoCompleteConrad.edu.stanford.rsl
    return (geo.getOriginX(), geo.getOriginY(), geo.getOriginZ())


def get_reco_spacing() -> tuple:
    conf = _.Configuration.getGlobalConfiguration()
    geo = conf.getGeometry()  # type: AutoCompleteConrad.edu.stanford.rsl
    return (geo.getVoxelSpacingX(), geo.getVoxelSpacingY(), geo.getVoxelSpacingZ())


def set_reco_spacing(spacing):
    conf = _.Configuration.getGlobalConfiguration()
    geo = conf.getGeometry()  # type: AutoCompleteConrad.edu.stanford.rsl
    geo.setVoxelSpacingX(spacing[0])
    geo.setVoxelSpacingY(spacing[1])
    geo.setVoxelSpacingZ(spacing[2])


def set_reco_origin(origin):
    conf = _.Configuration.getGlobalConfiguration()
    geo = conf.getGeometry()  # type: AutoCompleteConrad.edu.stanford.rsl

    geo.setOriginInWorld(_.PointND([origin[0], origin[1], origin[2]]))


def set_reco_shape(shape):
    conf = _.Configuration.getGlobalConfiguration()
    geo = conf.getGeometry()  # type: AutoCompleteConrad.edu.stanford.rsl

    geo.setReconDimensionX(shape[2])
    geo.setReconDimensionY(shape[1])
    geo.setReconDimensionZ(shape[0])


def set_reco_size(size):
    conf = _.Configuration.getGlobalConfiguration()
    geo = conf.getGeometry()  # type: AutoCompleteConrad.edu.stanford.rsl

    geo.setReconDimensionX(size[0])
    geo.setReconDimensionY(size[1])
    geo.setReconDimensionZ(size[2])


def center_volume():

    reco_size = get_reco_size()
    spacing = get_reco_spacing()
    origin_in_world = [-(reco_size[i] - 1.0) / 2. * spacing[i]
                       for i in range(3)]
    get_geometry().setOriginInWorld(_.PointND(origin_in_world))
