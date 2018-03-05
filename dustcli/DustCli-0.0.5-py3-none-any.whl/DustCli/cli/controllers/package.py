import os
from cement.ext.ext_argparse import ArgparseController, expose
from pathlib import Path
from cement.utils import shell


class PackageController(ArgparseController):
    class Meta:
        label = 'package'
        description = '打包相关命令'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = []

    @expose(hide=True)
    def default(self):
        os.system('dust package --help')

    @expose(help="让自己的机器成为打包机器")
    def firme(self):
        # find Xcode
        if not Path('/').joinpath('Applications', 'Xcode.app').exists():
            self.app.log.error('未检测到安装 Xcode，请先安装 Xcode')
            return

        # install rvm
        os.system('curl -sSL https://get.rvm.io | bash -s stable')

        # install ruby 2.3.0
        os.system('rvm install 2.3.0 && rvm use 2.3.0')

        # install flappy
        os.system(
            'git clone git@git.souche-inc.com:flappy/flappy-cli.git && cd flappy-cli && gem build flappy-cli.gemspec '
            '&& gem install flappy-cli-0.3.2.gem')

        # download slave file
        print(
            '例子：%s' % 'slave.jar -jnlpUrl http://jenkins.souche-inc.com/computer/mac-pro/slave-agent.jnlp -secret '
                      '1a35dec8f55c89ded1a84725ac2fb4d900c43533c8042f0f26fb23681796498f')
        cmd = shell.Prompt('输入你在 jenkins 创建的 slave.jar 的运行命令:').input
        os.system('curl -O http://jenkins.souche-inc.com/jnlpJars/slave.jar')

        os.system(cmd)
