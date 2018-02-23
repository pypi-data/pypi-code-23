from pyconrad import *
import numpy as np

# Compare to Java-Version: CONRAD/src/edu/stanford/rsl/tutorial/iterative/SartCL.java

#, '/localhome/local/projects/CONRADRSL/'
jvm = PyConrad()
jvm.setup()
# jvm.setup(dev_dirs=['/localhome/local/projects/CONRAD/'])

jvm.add_import('edu.stanford.rsl.conrad.data.numeric')
jvm.add_import('edu.stanford.rsl.tutorial.phantoms')
jvm.add_import('edu.stanford.rsl.conrad.phantom')
jvm.add_import('edu.stanford.rsl.conrad.utils')
jvm.add_import('edu.stanford.rsl.tutorial.iterative')
jvm.add_import('edu.stanford.rsl.conrad.geometry.shapes.simple')
jvm.add_import('edu.stanford.rsl.conrad.geometry.trajectories')
jvm.add_import('edu.stanford.rsl.conrad.numerics')
jvm.add_import('edu.stanford.rsl.conrad.geometry')
jvm.add_import('edu.stanford.rsl.tutorial.cone')
jvm.add_import('edu.stanford.rsl.conrad.data.numeric.opencl')

jvm.start_conrad()

helix = False
iterations = 6

jvm['Configuration'].loadConfiguration()
conf = jvm['Configuration'].getGlobalConfiguration()
geo = conf.getGeometry()
traj = conf.getGeometry()

if helix:
    traj = jvm['HelicalTrajectory'](
        jvm['Configuration'].getGlobalConfiguration().getGeometry())

    stepHel = traj.getNumProjectionMatrices()
    physicalDetectorHeight = traj.getDetectorHeight() * traj.getPixelDimensionY()
    stepSize = (physicalDetectorHeight * 0.05 / stepHel)
    volumeZSize = physicalDetectorHeight * 3 * 0.05

    rotation_axis = jvm['SimpleVector']([0., 0., 1.])
    rotation_center = jvm['PointND']([0, 0, volumeZSize / 2])
    sourcetoaxis_dist = jvm['Configuration'].getGlobalConfiguration(
    ).getGeometry().getSourceToAxisDistance()
    angular_inc = traj.getAverageAngularIncrement()
    offset_u = jvm.enumval_from_int(
        'Projection$CameraAxisDirection', traj.getDetectorOffsetU())
    offset_v = jvm.enumval_from_int(
        'Projection$CameraAxisDirection', traj.getDetectorOffsetV())

    traj.setTrajectory(stepHel * 3,
                       sourcetoaxis_dist,
                       angular_inc,
                       traj.getDetectorOffsetU(),
                       traj.getDetectorOffsetV(),
                       offset_u,
                       offset_v,
                       rotation_axis,
                       rotation_center,
                       0.,
                       stepSize)
    conf.setGeometry(traj)


cbp = jvm['ConeBeamProjector']()
grid = jvm['OpenCLGrid3D'](jvm['NumericalSheppLogan3D'](traj.getReconDimensionX(
), traj.getReconDimensionY(), traj.getReconDimensionZ()).getNumericalSheppLoganPhantom())


grid.setOrigin(JArray(JDouble)(
    [-traj.getOriginInPixelsX(), -traj.getOriginInPixelsY(), -traj.getOriginInPixelsZ()]))
grid.setSpacing(JArray(JDouble)(
    [traj.getVoxelSpacingX(), traj.getVoxelSpacingY(), traj.getVoxelSpacingZ()]))
java.lang.System.out.println("GT: %f" % grid.getGridOperator().normL1(grid))
try:
    sino = jvm['OpenCLGrid3D'](jvm['Grid3D'](traj.getDetectorWidth(
    ), traj.getDetectorHeight(), traj.getProjectionStackSize()))
    sino.setOrigin(JArray(JDouble)([0, 0, 0]))
    sino.setSpacing(JArray(JDouble)([1, 1, 1]))
    cbp.fastProjectRayDrivenCL(sino, grid)
    sino.show()
    # sino.save_tiff('/localhome/local/phantom.tif')

    sart = jvm['SartCL'](grid.getSize(), grid.getSpacing(),
                         grid.getOrigin(), sino, 0.8)
    start = java.lang.System.currentTimeMillis()
    sart.iterate(iterations)
    ende = java.lang.System.currentTimeMillis() - start
    print("Time Sart: %.5f seconds\n" % (ende / 1000.0))
    foo = sart.getVol()
    java.lang.System.out.println("L1: %f" % foo.getGridOperator().normL1(foo))
    java.lang.System.out.println(
        "RMSE: " + str(foo.getGridOperator().rmse(foo, grid)))
except JavaException as e:
    e.printStackTrace()

while True:
    a = 1
