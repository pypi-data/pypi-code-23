import cherrypy
from bgweb.selection import BGSelection


class BGWebApp(object):

    def __init__(self, conf=None, env=None):
        self.conf = conf
        self.env = env

    @cherrypy.expose
    def index(self):
        raise cherrypy.HTTPRedirect("search")

    @cherrypy.expose
    def search(self, q=None, **kwargs):
        raise NotImplementedError()

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def api(self, **kwargs):
        raise NotImplementedError()

    @staticmethod
    def redirect_to_selection(items, selection:BGSelection=None, **kwargs):

        report = None
        tab = None

        for k, v in items.items():
            if k == 'report':
                report = v
            elif k == 'tab':
                tab = v
            else:
                item = selection.search(k, v, limit=10, exact=True)
                if len(item) > 0:
                    selection.add(k, item[0])

                    # Replace fixed selections (and their excludes relatives)
                    kwargs.pop(k, None)
                    for type in selection.types:
                        if 'exclude' in selection.conf[type]:
                            for exclude in selection.conf[type]['exclude'].split(','):
                                if exclude == k:
                                    kwargs.pop(type, None)

        selection.add_all(**kwargs)
        redirect = "search{}".format(selection.link())
        if report is not None:
            report_and_tab = selection.verify_report(report, tab)
            redirect = redirect + '#' + report_and_tab

        raise cherrypy.HTTPRedirect(redirect)
