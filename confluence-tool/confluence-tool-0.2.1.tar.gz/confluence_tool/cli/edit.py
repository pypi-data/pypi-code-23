import yaml, pyaml, sys
from difflib import Differ
from .cli import command, arg, optarg_cql, arg_filter, arg_parent, arg_add_label
from ..storage_editor import StorageEditor

# @command('create', arg_parent, arg_label, arg_space, arg("pagespec")
# )
# def cmd_create(config):


@command('edit',
    optarg_cql,
    arg_filter,
    arg_parent,
    arg_add_label,
    arg('file', nargs="?", help="file to read data from"),
    # need arg_group
    arg('--show', action="store_true", help="show new content"),
    arg('--diff', action="store_true", help="show diff"),
    )
def cmd_edit(config):
    """edit a confluence page using CSS selections

    Pass a dictionary in YAML or JSON format via STDIN or file to
    confluence-tool, which defines edit actions to edit all matching pages.

    """

    confluence = config.getConfluenceAPI()
    first = True

    if not config['file']:
        content = sys.stdin.read()
    else:
        with open(fn, 'r') as f:
            content = f.read()

    try:
        editor_config = yaml.safe_load(content)
    except:
        editor_config = dict(actions=[dict(content=content)])

    if isinstance(editor_config, basestring):
        editor_config = dict(actions=[dict(content=editor_config)])

    if 'page' in editor_config:
        cql = confluence.resolveCQL(editor_config.pop('page'))

    if 'cql' in editor_config:
        cql = editor_config.pop('cql')
    if config['cql']:
        cql = config['cql']

    #editor = StorageEditor(confluence, **editor_config)

    found = False
    for page,content in confluence.editPages(confluence.resolveCQL(cql), filter=config.filter, editor=editor_config):
        found = True
        if not first:
            print "---"
        first = False

        from html5print import HTMLBeautifier
        b = HTMLBeautifier.beautify

        if config.show:
            p = page.dict('id', 'spacekey', 'title')

            p['content'] = b(content, 2)
            pyaml.p(p)

        elif config.diff:
            p = page.dict('id', 'spacekey', 'title')

            old = b(page['body']['storage']['value']).splitlines(1)
            new = b(content).splitlines(1)

            d = Differ()
            result = list(d.compare(old, new))

            p['diff'] = ''.join(result)
            pyaml.p(p)

        else:
            p = page.dict('id', 'title', 'version')
            p['storage'] = content
            p['version'] = int(page['version']['number'])+1

            result = confluence.updatePage(**p)
            pyaml.p(result)

    if not found:
        space, title = cql.split(':', 1)

        editor = StorageEditor(confluence, **editor_config)
        content = editor.edit('<R></R>')[3:-4]
        data = dict(
            page    = dict(
                spacekey = space,
                title    = title,
            ),
            content = content,
            result  = confluence.createPage(
                space = space,
                title = title,
                storage = content,
                parent = config.parent
            ))

@command('update',
    optarg_cql,
    arg_filter,
    arg_parent,
    arg_add_label,
    arg('file', nargs="?", help="file to read data from"),
    # need arg_group
    arg('--show', action="store_true", help="show new content"),
    arg('--diff', action="store_true", help="show diff"),
    )
def cmd_update(config):
    """edit a confluence page using CSS selections

    Pass a dictionary in YAML or JSON format via STDIN or file to
    confluence-tool, which defines edit actions to edit all matching pages.

    """

    confluence = config.getConfluenceAPI()
    first = True

    if not config['file']:
        content = sys.stdin.read()
    else:
        with open(fn, 'r') as f:
            content = f.read()

    # if 'page' in editor_config:
    #     cql = confluence.resolveCQL(editor_config.pop('page'))

    if config['cql']:
        cql = config['cql']

    #editor = StorageEditor(confluence, **editor_config)

    found = False
    for page in confluence.getPages(confluence.resolveCQL(cql), filter=config.filter, expand=['version']):
        p = page.dict('id', 'title', 'version')
        p['storage'] = content
        p['version'] = int(page['version']['number'])+1

        result = confluence.updatePage(**p)
        found = True

        pyaml.p(result)
        #confluence.updatePage(id=page['id'], title=page['title'], body=)

    #def updatePage(self, id, title, body=None, version=None, type='page', storage=None, wiki=None):

    if not found:
        space, title = cql.split(':', 1)

        data = dict(
            page    = dict(
                spacekey = space,
                title    = title,
            ),
            content = content,
            result  = confluence.createPage(
                space = space,
                title = title,
                storage = content,
                parent = config.parent
            ))
        pyaml.p(result)

@command('move', optarg_cql, arg_filter, arg_parent)
def move(config):
    confluence = config.getConfluenceAPI()
    first = True

    parent = confluence.getPage(confluence.resolveCQL(config.parent))
    cql = confluence.resolveCQL(config.cql)
    filter = config.filter

    for page in confluence.getPages(cql, filter=filter, expand=['version']):
        result = confluence.movePage(page, parent=parent)

        if not first:
            print "---"

        pyaml.p(result)

        first = False

    if first:
        print "could not find a page matching %s (%s)" % (cql, filter)
