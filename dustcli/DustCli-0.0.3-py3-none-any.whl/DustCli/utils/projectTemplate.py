from cement.utils import shell
from pathlib import Path
import shutil

tempPath = str(Path.home()) + '/.dust/ProjectTemplates' 

class ProjectTemplate:

  @staticmethod
  def clone():
    if Path(tempPath).is_dir():
      shutil.rmtree(tempPath)
    shell.exec_cmd2(['git', 'clone', 'git@git.souche-inc.com:SCFEE/project-template.git', '%s' % tempPath])
  
  @staticmethod
  def cloneIfNeed():
    if Path(tempPath).is_dir():
      return True
    exitcode = shell.exec_cmd2(['git', 'clone', 'git@git.souche-inc.com:SCFEE/project-template.git', '%s' % tempPath])
    return exitcode == 0

  