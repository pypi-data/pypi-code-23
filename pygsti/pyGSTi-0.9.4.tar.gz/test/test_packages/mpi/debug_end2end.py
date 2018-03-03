import pygsti
from pygsti.construction import std1Q_XYI

from mpi4py import MPI
comm = MPI.COMM_WORLD

gs_target = std1Q_XYI.gs_target
fiducials = std1Q_XYI.fiducials
germs = std1Q_XYI.germs
maxLengths = [1]#,2,4]

gs_datagen = gs_target.depolarize(gate_noise=0.1, spam_noise=0.001)
listOfExperiments = pygsti.construction.make_lsgst_experiment_list(
    list(gs_target.gates.keys()), fiducials, fiducials, germs, maxLengths)
ds = pygsti.construction.generate_fake_data(gs_datagen, listOfExperiments,
                                            nSamples=1000,
                                            sampleError="binomial",
                                            seed=1234, comm=comm)

results = pygsti.do_long_sequence_gst(ds, gs_target, fiducials, fiducials,
                                      germs, maxLengths, comm=comm)

pygsti.report.create_standard_report(results, "mpi_test_report",
                                     "MPI test report", confidenceLevel=95,
                                     verbosity=2, comm=comm)
