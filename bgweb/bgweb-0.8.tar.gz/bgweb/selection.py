from urllib.parse import urlencode
from collections import defaultdict
from bson.json_util import _json_convert

SELECTION_CLASS = 'selection_class'
DEDUCED_SELECTION = 'deduced'


class SelectionQuerier(object):

    def find_one(self, collection_name, field, value):
        raise NotImplementedError()

    def query(self, collection, limit=None, projection=None, sort=None, where=None, mapkey=None):
        raise NotImplementedError()

    def search(self, type, query=None, limit=None, projection=None, exact=False, mapkey=None):
        raise NotImplementedError()


class BGSelection(SelectionQuerier):

    def __init__(self, conf):

        self._cached = None
        if 'cached' in conf['datasets']:
            self._cached = conf['datasets']['cached']

        self.conf = conf['search']
        self.links = conf['links']
        self.types = [t for t in self.conf]
        self._items = defaultdict(list)

    def items(self):
        return self._items.items()

    def verify_report(self, report, tab=None):
        raise NotImplementedError()

    def search_all(self, value, exact=False):
        items = {}
        for type in self.types:
            conf = self.conf[type]
            for v in self.search(type, value, limit=10, exact=exact):

                # item = {
                #     'color': '#' + conf['color'],
                #     'title': v[conf['title']],
                #     'type': type,
                #     'key': v[conf['key']],
                #     'value': v
                # }
                if type in v and v[type] == value:
                    items[type] = v[type]
                elif type.upper() in v and v[type.upper()] == value:
                    items[type] = v[type.upper()]

        return items

    def items(self):
        return self._items.items()

    def size(self):
        selected_items = 0
        for type, items in self.items():
            selected_items += len(items)
        return selected_items

    def get(self, type):
        if type in self._items:
            return [item['value'] for item in self._items[type]]
        else:
            return []

    def link_remove(self, item):
        items = []
        for key, value in self.items():
            for v in value:
                if v[SELECTION_CLASS] == DEDUCED_SELECTION:
                    continue
                if v['type'] == item['type'] and v['key'] == item['key']:
                    continue
                items.append((v['type'], v['key']))
        return "?" + urlencode(items)

    def link(self):
        items = []
        for key, value in self.items():
            for v in value:
                if v[SELECTION_CLASS] == DEDUCED_SELECTION:
                    continue
                items.append((v['type'], v['key']))
        return "?" + urlencode(items)

    def link_to(self, item):
        items = []
        items.append((item['type'], item['key']))
        return "?" + urlencode(items)

    def link_add(self, **kwargs):
        items = []
        for key, value in self.items():
            for v in value:
                if v['type'] in kwargs or v[SELECTION_CLASS] == DEDUCED_SELECTION:
                    continue
                items.append((v['type'], v['key']))
        for t, k in kwargs.items():
            items.append((t, k))
        return "?" + urlencode(items)

    def link_query(self, collection, limit=None, projection=None, sort=None, where=None):

        items = []
        for key, value in self.items():
            for v in value:
                items.append((v['type'], v['key']))

        items.append(('c', collection))

        if limit is not None:
            items.append(('l', limit))

        if projection is not None:
            items.append(('p', projection))

        if sort is not None:
            items.append(('s', sort))

        if where is not None:
            items.append(('w', where))

        url = "?" + urlencode(items)
        return url

    def verify(self):
        for t in self.types:
            if not self.conf[t]['multiple'] and t in self._items and len(self._items[t]) > 1:
                # select last (newest) in case only one item is allowed
                self._items[t] = [self._items[t][-1]]

    def add_all(self, **kwargs):
        for type in self.types:
            if type in kwargs:
                items = kwargs[type]
                if not isinstance(items, list):
                    items = [items]

                conf = self.conf[type]
                for item in items:
                    collection_name = conf['collection']
                    value = self.find_one(collection_name, conf['key'], item)
                    if value is not None:
                        self.add(type, _json_convert(value))

    def add(self, type, value, selection_class=None):

        conf = self.conf[type]
        if selection_class is None:
            selection_class = 'user-selected'

        item = {
            'color': '#' + conf['color'],
            'description': conf['description'],
            'title': value[conf['title']],
            'type': type,
            'key': value[conf['key']],
            'value': value,
            SELECTION_CLASS: selection_class
        }

        self._items[type].append(item)

        # Remove excluded selections
        if 'exclude' in conf:
            for exclude in conf['exclude'].split(','):
                self._items.pop(exclude.strip(), None)

    def has_only(self, *args):
        """
        Returns true only if the given types are selected (and any more)

        :param args:
        :return:
        """

        has_all = all([self.has(type) for type in args])

        if not has_all:
            return False

        if self.has_any(args):
            return False

        return True

    def has_any(self, exceptions=None):
        if exceptions is None:
            exceptions_set = set()
        else:
            exceptions_set = set(exceptions)

        any_other = any([self.has(type) for type in self.types if type not in exceptions_set])
        return any_other

    def has(self, type):

        if type not in self._items:
            return False

        if len(self._items[type]) == 0:
            return False

        if self._items[type][0][SELECTION_CLASS] == DEDUCED_SELECTION:
            return False

        return True

    def javascript(self):

        result = []

        for type in self.types:
            conf = self.conf[type]
            result.append("""
                            var {0} = new Bloodhound({{
                                  datumTokenizer: Bloodhound.tokenizers.obj.whitespace('{1}'),
                                  queryTokenizer: Bloodhound.tokenizers.whitespace,
                                  remote: 'api?t={0}&q=%QUERY&l=10'
                            }});
                            {0}.initialize();
                            """.format(type, conf['key']))

        parameters = []
        for type in self.types:
            conf = self.conf[type]
            parameters.append("""
                {{
                    name: '{0}',
                    displayKey: '{1}',
                    source: {0}.ttAdapter(),
                    templates: {{
                        header: '<h3>{0}s</h3>',
                        suggestion: function(v) {{
                            return '<span class="badge" style="background-color: #{2};">{0}</span>&nbsp;<span>'+v['{1}']+' - '+v['{3}']+'</span>';
                        }}
                    }}
                }}
            """.format(type, conf['key'], conf['color'], conf['description']))

        result.append("$('#search').typeahead(null, {0});".format(','.join(parameters)))
        result.append("$('#search').on('typeahead:selected', function (event, item, type) {$('#search').closest('form').submit();});")
        return '\n'.join(result)

    def build_filename(self, id, suffix="", prefix=None):

        name = []
        if prefix is not None:
            name.append(prefix)

        tofetch = sorted(self._items.keys())
        for item in tofetch:
            for i in self._items[item]:
                name.append(i['key'])

        name.append(id)

        if suffix != "":
            name.append(suffix.lower())

        return "-".join(name)

    def to_string(self):
        name = []
        tofetch = sorted(self._items.keys())
        for item in tofetch:
            for i in self._items[item]:
                name.append(i['key'])
        return "+".join(name)

    def deduce_selection(self):

        for datatype in self.types:
            selected_item = self._items[datatype]
            if selected_item: #non-emtpy type
                type_collection = self.conf[datatype]['collection']
                if type_collection in self.links:
                    links = self.links[type_collection]
                    for linkedtype in links:
                        if datatype == linkedtype:
                            continue

                        if not self._items[linkedtype]:  # empty linked type
                            field = links[linkedtype][0]
                            item = self.find_one(self.conf[linkedtype]['collection'], field, selected_item[0]['value'][field])
                            self.add(linkedtype, item, DEDUCED_SELECTION)