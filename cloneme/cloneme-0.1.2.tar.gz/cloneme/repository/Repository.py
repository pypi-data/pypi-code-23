import re
import subprocess

class Repository:
    def __init__(self, repo):
        self.repo = repo

    def clone(self):
        subprocess.run("git clone https://github.com/{}.git".format(
            self.repo).split())
