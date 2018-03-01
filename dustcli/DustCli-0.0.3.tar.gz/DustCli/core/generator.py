from DustCli.utils.projectTemplate import tempPath
from pathlib import Path, PurePath
from datetime import datetime
import shutil
import os

replaceMap = {
  "name": "%{SCFEE_Template_Swift_Project_Name}%",
  "author": "%{SCFEE_Template_Swift_Author}%",
  "createDate": "%{SCFEE_Template_Swift_Create_Date}%",
  "displayName": "%{SCFEE_Template_Swift_Display_Name}%"
}

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

  def generate(self):
    temp = tempPath + '/iOS/%s/%s' % (self.lang, replaceMap["name"])
    target = str(Path.home()) + '/Desktop/%s' % self.name
    shutil.copytree(temp, target)
    [self._process(str(path)) for path in Path(target).rglob('*')]

    os.system('cd %s && pod install' % target)
    os.system('cd %s && open %s.xcworkspace' % (target, self.name))

  def _process(self, _path):
    path = Path(_path)
    target_path = Path(_path.replace(replaceMap["name"], self.name))
    path.rename(target_path)

    if target_path.is_file():
      content = target_path.read_text()

      content = content.replace(replaceMap["name"], self.name)
      content = content.replace(replaceMap["displayName"], self.display)
      content = content.replace(replaceMap["author"], self.author)
      content = content.replace(replaceMap["createDate"], self.date)
      target_path.write_text(content)
