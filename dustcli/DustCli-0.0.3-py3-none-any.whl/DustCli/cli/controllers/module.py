from cement.ext.ext_argparse import ArgparseController, expose

class ModuleController(ArgparseController):
  class Meta:
    label = 'module'
    description = '创建一个模块'
    stacked_on = 'base'
    stacked_type = 'nested'
    arguments = [
        (['-n', '--name'],
          dict(help='名称') ),
        ]

  @expose(help='创建一个模块: project module -n NAME')
  def default(self):
    self.app.log.info('create a new project')