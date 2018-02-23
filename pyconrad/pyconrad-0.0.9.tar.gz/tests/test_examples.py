import warnings
import pyconrad
import time
import pyconrad
import os
import pytest


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true", reason="Skipping this test on Travis CI.")
def test_basic_example():
    import pyconrad_examples.first_steps._1_basic_example
    pyconrad.ij().WindowManager.closeAllWindows()
    return


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true", reason="Skipping this test on Travis CI.")
def test_numpy_example():
    import pyconrad_examples.first_steps._3_numpy_and_conrad
    pyconrad.ij().WindowManager.closeAllWindows()
    return


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true", reason="Skipping this test on Travis CI.")
def test_opencl_example():
    import pyconrad_examples.opencl
    pyconrad.ij().WindowManager.closeAllWindows()
    return


@pytest.mark.skipif("TRAVIS" in os.environ and os.environ["TRAVIS"] == "true", reason="Skipping this test on Travis CI.")
def test_opencl_custom_kernel_example():
    import pyconrad_examples.opencl_custom_kernel
    pyconrad.ij().WindowManager.closeAllWindows()
    return


if __name__ == "__main__":
    # test_basic_example()
    test_numpy_example()
