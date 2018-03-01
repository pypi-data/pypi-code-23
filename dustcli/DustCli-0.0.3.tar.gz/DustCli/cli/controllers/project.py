"""DustCli application controller."""

from cement.ext.ext_argparse import ArgparseController, expose
from cement.utils import shell
from DustCli.utils.projectTemplate import ProjectTemplate
from DustCli.core.generator import iOSGenerator
import os

class ProjectController(ArgparseController):
  class Meta:
    label = 'project'
    description = '项目相关命令'
    stacked_on = 'base'
    stacked_type = 'nested'
    arguments = []

  @expose(hide=True)
  def default(self):
    os.system('dust project --help')
  
  @expose(aliases=['t'], 
          help="创建新的项目",
          arguments=[
                    (['-i', '--ios'], 
                    dict(action='store_true', help='创建 iOS 项目'),
                    ),
                    (['-a', '--android'], 
                    dict(action='store_true', help='创建 Android 项目'),
                    )
                ])
  def new(self):
    name = shell.Prompt("项目名称(project name):").input
    display = shell.Prompt("App 展示名称(display name, 默认为项目名称):", default=name).input

    if self.app.pargs.ios:
      lang = shell.Prompt(
        "选择项目使用的语言",
        options=[
            'Swift',
            'Objective-C',
            ],
        numbered = True,
        ).input
      if lang != 'Swift':
        self.app.log.info('暂时不支持除了 Swift 之外的语言')
        return

      needWebview = shell.Prompt('是否集成 WebView? (y/n)').input == 'y' 
      needRN = shell.Prompt('是否集成 RN? (y/n)').input == 'y'
      needTool = shell.Prompt('是否集成开发工具? (y/n)').input == 'y' 
      needPush = shell.Prompt('是否集成推送? (y/n)').input == 'y'
      needMessageCenter = shell.Prompt('是否集成消息中心? (y/n)').input == 'y'

      #check templete
      if not ProjectTemplate.cloneIfNeed():
        self.app.log.warning('获取项目模板失败')
        return

      self.app.log.info('正在为你生成项目，完成后将自动打开...')
      iOSGenerater(name, display, lang, needWebview, needRN, needTool, needPush, needMessageCenter).generate()

    else:
      # gen android project
      self.app.log.warning('暂时不支持创建安卓项目')
