def test_errorbar3d():
  """Test 3D errorbar plotting"""
  from caspyr.plotting import errorbar3d
  import matplotlib.pyplot as plt
  import numpy as np

  fig = plt.figure(dpi=100)
  ax = fig.add_subplot(111, projection='3d')

  # data
  x = sorted(np.random.random(9))
  y = sorted(np.random.random(9))
  z = sorted(np.random.random(9))
  sx = np.random.random(9) / 10
  sy = np.random.random(9) / 10
  sz = np.random.random(9) / 10

  # optional configure axes
  ax.set_xlim3d(0, 1)
  ax.set_ylim3d(0, 1)
  ax.set_zlim3d(0, 1)
  ax.set_xlabel('x')
  ax.set_ylabel('y')
  ax.set_zlabel('z')

  errorbar3d(ax, x, y, z, sz, sy, sx, linestyle=":")
  plt.show()


def test_Plt():
  """Test Plt"""
  from caspyr.plotting import Plt
  import matplotlib.pyplot as pyplot

  Plt.set_dims(2, 2)  # optionally set subplot dimensions
  Plt.fig()
  pyplot.plot(range(10))
  Plt.fig()
  pyplot.plot(range(10, 0, -1))
  Plt.set_dims()  # back to figure mode
  Plt.fig()
  pyplot.plot([1] * 5 + [2] * 5)
  Plt.set_dims(2, 2)  # optionally set subplot dimensions
  Plt.fig()
  pyplot.plot(range(10, 0, -1))
  pyplot.show()
