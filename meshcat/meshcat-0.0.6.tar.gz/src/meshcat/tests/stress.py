import meshcat
import random

v = meshcat.Visualizer("tcp://127.0.0.1:6003")
v.wait()

for i in range(100):
    path = [str(random.randint(0, 10)) for i in range(random.randint(0, 6))]
    path = "/" + "/".join(path)
    v[path].set_object(meshcat.geometry.Box([0.5, 0.5, 0.5]))
    v[path].set_transform(meshcat.transformations.translation_matrix([random.random() for i in range(3)]))

