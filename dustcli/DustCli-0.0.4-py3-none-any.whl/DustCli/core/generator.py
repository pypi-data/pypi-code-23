from DustCli.utils.projectTemplate import tempPath, customTempPath, ProjectTemplate
from pathlib import Path, PurePath
from datetime import datetime
import shutil
import os

iOSMap = {
  "name": "%{SCFEE_Template_Project_Name}%",
  "author": "%{SCFEE_Template_Author}%",
  "createDate": "%{SCFEE_Template_Create_Date}%",
  "displayName": "%{SCFEE_Template_Display_Name}%"
}

androidMap = {
}

class AndroidGenerator:
  def generate(self):
    pass

class iOSGenerator:
  def __init__(self, name, display, lang, webview, rn, tool, push, messageCenter):
    self.name = name
    self.display = display
    self.lang = lang
    self.webview = webview
    self.rn = rn
    self.tool = tool
    self.push = push
    self.messageCenter = messageCenter
    self.author = os.getlogin()
    self.date = datetime.now().strftime("%Y-%m-%d") 
  
  def _tempPath(self):
    custom = customTempPath.joinpath('iOS', self.lang, iOSMap["name"])
    default = tempPath.joinpath('iOS', self.lang, iOSMap["name"])
    if custom.is_dir():
      return str(custom)
    elif default.is_dir():
      return str(default)
    else:
      ProjectTemplate.cloneIfNeed()
      return str(default)

  def generate(self):
    temp = self._tempPath()
    target = str(Path.home().joinpath('Desktop', self.name))
    shutil.copytree(temp, target)
    [self._process(str(path)) for path in Path(target).rglob('*')]

    os.system('cd %s && pod install && open %s.xcworkspace' % (target, self.name))

  def _process(self, _path):
    path = Path(_path)
    target_path = Path(_path.replace(iOSMap["name"], self.name))
    path.rename(target_path)

    if target_path.is_file():
      content = target_path.read_text()

      content = content.replace(iOSMap["name"], self.name)
      content = content.replace(iOSMap["displayName"], self.display)
      content = content.replace(iOSMap["author"], self.author)
      content = content.replace(iOSMap["createDate"], self.date)
      target_path.write_text(content)
