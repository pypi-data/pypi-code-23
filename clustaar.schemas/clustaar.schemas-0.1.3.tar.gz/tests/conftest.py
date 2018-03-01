import os
import pytest


PROJECT_PATH = os.path.join(os.path.dirname(__file__), "..")
PACKAGE_PATH = os.path.join(PROJECT_PATH, "src")
os.sys.path.insert(0, PROJECT_PATH)
os.sys.path.insert(0, PACKAGE_PATH)
