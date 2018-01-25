import os.path
from jinja2 import FileSystemLoader
from notebook.utils import url_path_join
from notebook.base.handlers import IPythonHandler, path_regex


class PublishHandler(IPythonHandler):
    '''Just a default handler'''
    def initialize(self, hosting):
        self.hosting = hosting

    def post(self, path):
        name = path.rsplit('/', 1)[-1]
        notebook = self.request.body.decode('utf8')
        self.hosting[name] = notebook

    def get(self, path):
        name = path.rsplit('/', 1)[-1]
        if name not in self.hosting:
            self.write('Notebook not currently being published')
        else:
            to_render = str(self.hosting[name])
            to_render = to_render.replace('\\n', '')
            self.write(self.render_template('publish.html', notebook=to_render, notebook_name=name))

    def get_template(self, name):
        t = os.path.join(os.path.dirname(__file__), 'templates')
        return FileSystemLoader(t).load(self.settings['jinja2_env'], name)


def load_jupyter_server_extension(nb_server_app):
    web_app = nb_server_app.web_app
    host_pattern = '.*$'
    route_pattern = url_path_join(web_app.settings['base_url'], r'/publish%s' % path_regex)
    web_app.add_handlers(host_pattern, [(route_pattern, PublishHandler, {'hosting': {}})])
    print('Installing lantern publish endpoints')
