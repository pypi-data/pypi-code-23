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
  
  @expose(aliases=['n'], 
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

      self.app.log.info('正在为你生成项目，完成后将自动打开...')
      iOSGenerator(name, display, lang, needWebview, needRN, needTool, needPush, needMessageCenter).generate()

    else:
      # gen android project
      self.app.log.warning('暂时不支持创建安卓项目')

  @expose(
    help='设置自定义模板',
    arguments=[
      (['-g', '--git'],
      dict(action='store', help="指定 git 地址")),
      (['-p', '--path'],
      dict(action='store', help="指定本地目录")),
      (['-c', '--clean'],
      dict(action='store_true', help="清除自定义模板")),
    ])
  def template(self):
    if self.app.pargs.clean:
        ProjectTemplate.cleanCustomTemplate()
        self.app.log.info('清空完成，你现在使用的是默认的项目模板，详情请查看：https://git.souche-inc.com/SCFEE/project-template')
        return

    git = self.app.pargs.git
    path = self.app.pargs.path

    if git:
      ProjectTemplate.cloneCustomTemplate(git)
    elif path:
      ProjectTemplate.copyCustomTemplate(path)
    else:
      self.app.log.warning('请指定一个地址')
    
