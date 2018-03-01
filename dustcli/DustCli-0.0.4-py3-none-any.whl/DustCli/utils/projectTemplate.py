from cement.utils import shell
from pathlib import Path
import shutil

tempPath = Path.home().joinpath('.dust', 'ProjectTemplates')
customTempPath = Path.home().joinpath('.dust', 'CustomProjectTemplates')

class ProjectTemplate:

  @staticmethod
  def clone():
    if tempPath.is_dir():
      shutil.rmtree(str(tempPath))
    shell.exec_cmd2(['git', 'clone', 'git@git.souche-inc.com:SCFEE/project-template.git', str(tempPath)])
  
  @staticmethod
  def cloneIfNeed():
    if tempPath.is_dir():
      return True
    exitcode = shell.exec_cmd2(['git', 'clone', 'git@git.souche-inc.com:SCFEE/project-template.git', str(tempPath)])
    return exitcode == 0

  @staticmethod
  def cloneCustomTemplate(git):
    if Path(customTempPath).is_dir():
      shutil.rmtree(customTempPath)
    shell.exec_cmd2(['git', 'clone', git, str(customTempPath)])

  @staticmethod 
  def copyCustomTemplate(path):
    if Path(customTempPath).is_dir():
      shutil.rmtree(customTempPath)
    
    shutil.copytree(path, customTempPath)

  @staticmethod
  def cleanCustomTemplate():
    if Path(customTempPath).is_dir():
      shutil.rmtree(customTempPath)


  