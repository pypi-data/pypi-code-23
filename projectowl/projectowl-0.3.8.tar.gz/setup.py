import os
from setuptools import setup, find_packages

try:
  import GPUtil
except:
  # install package.
  os.system("pip install gputil")
  import GPUtil


def if_gpu_exist():
  deviceIDs = GPUtil.getAvailable(
      order="first", limit=1, maxLoad=0.1, maxMemory=0.1)
  return len(deviceIDs) > 0


with open("./configs/requirements.txt", "r") as f:
  dep_packages = f.readlines()
  # remove local install.
  dep_packages = [x.strip() for x in dep_packages if not x.startswith("-e")]
  for dep_id, dep in enumerate(dep_packages):
    # select version of tensorflow.
    if dep in ["tensorflow-gpu", "tensorflow"]:
      package_name, package_ver = dep.split("==")
      if if_gpu_exist():
        package_name = "tensorflow-gpu"
      else:
        package_name = "tensorflow"
      dep_packages[dep_id] = "{}=={}".format(package_name, package_ver)

setup(
    name="projectowl",
    version="0.3.8",
    description="high level computer vision library",
    keywords="computer vision image feature pipeline",
    url="https://flyfj@bitbucket.org/flyfj/owl.git",
    author="Jie Feng",
    author_email="jiefengdev@gmail.com",
    packages=find_packages("./"),
    install_requires=dep_packages,
    include_package_data=True,
    zip_safe=False)
