from .settings import SETTINGS
from urllib.parse import urlparse
import datetime
import shutil
import copy
import math
import os

from beam.config import load_config

def update(d, ud, overwrite=True):
    for key, value in ud.items():
        if key not in d:
            d[key] = value
        elif isinstance(value, dict):
            update(d[key], value, overwrite=overwrite)
        elif isinstance(value, list) and isinstance(d[key], list):
            d[key] += value
        else:
            if key in d and not overwrite:
                return
            d[key] = value

class Site(object):

    """
    Describes a site.
    """

    def __init__(self, config):
        self.config = copy.deepcopy(config)
        self._original_config = config
        self.processors = SETTINGS['processors']
        self.loaders = SETTINGS['loaders']
        self._static_paths = None
        self._theme_config = None
        self._translations = None

        self.process_config()

    @property
    def title(self):
        return self.config.get('title', '')

    @property
    def subtitle(self):
        return self.config.get('subtitle', '')

    @property
    def src_path(self):
        return self.config.get('src-path', 'src')

    @property
    def build_path(self):
        return self.config.get('build-path', 'build')

    @property
    def site_path(self):
        return self.config.get('path','/')

    @property
    def translations(self):
        if self._translations is not None:
            return self._translations
        translations = {}
        for d in (self.config, self.theme_config):
            if 'translations' in d:
                for key, trs in d['translations'].items():
                    if not key in translations:
                        translations[key] = {}
                    translations[key].update(trs)
        self._translations = translations
        return translations

    @property
    def theme_config(self):
        if self._theme_config is not None:
            return self._theme_config
        config_path = os.path.join(self.theme_path, 'theme.yml')
        if os.path.exists(config_path):
            self._theme_config = load_config(config_path)
        else:
            self._theme_config = {}
        return self._theme_config

    @property
    def theme_path(self):
        return self.config.get('theme-path', 'theme')

    def process_config(self):
        if '$all' in self.config.get('languages', {}):
            all_params = self.config['languages']['$all']
            del self.config['languages']['$all']
            for language, params in self.config['languages'].items():
                update(params, all_params)

    def translate(self, language, key):
        translations = self.translations
        if not key in translations:
            return "[no translation for key {}]".format(key)
        if not language in translations[key]:
            return "[no translation for language {} and key {}]".format(language, key)
        return translations[key][language]

    def get_blog_prefix(self, language):
        return self.config['languages'][language].get('blog-path', 'blog')

    def get_language_prefix(self, language):
        return self.config['languages'][language].get('prefix', language)

    def get_src_path(self, path):
        return os.path.abspath(os.path.join(self.src_path, path))

    def get_build_path(self, path):
        return os.path.abspath(os.path.join(self.build_path, path))

    def parse_pages(self, pages, language):
        return self.parse_objs(pages, language)

    def parse_articles(self, articles, language):
        parsed_articles = self.parse_objs(articles, language, prefix=self.get_blog_prefix(language))
        for article in parsed_articles:
            article['date'] = datetime.datetime.strptime(article['date'], '%Y-%m-%d %H:%M')
        return parsed_articles

    def parse_objs(self, objs, language, prefix=''):
        parsed_objs = []
        for obj in objs:
            obj = obj.copy()
            if not 'src' in obj:
                raise ValueError("No source given!")
            if not 'slug' in obj:
                obj['slug'] = ''.join(os.path.basename(obj['src']).split('.')[:-1])
            if not 'dst' in obj:
                obj['dst'] = os.path.join(self.get_language_prefix(language), prefix, obj['slug'])+'.html'
            if obj['src'].find('://') == -1:
                obj['src'] = 'file://{}'.format(obj['src'])
            if not 'type' in obj:
                s = obj['src'].split('.')
                if len(s) < 2:
                    raise ValueError
                obj['type'] = s[-1]
            parsed_objs.append(obj)
        return parsed_objs

    def write(self, content, path):
        full_path = self.get_build_path(path)
        dirname = os.path.dirname(full_path)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(full_path, 'w') as output_file:
            output_file.write(content)

    def get_static_paths(self):
        if self._static_paths is not None:
            return self._static_paths
        paths = [os.path.join(self.src_path, 'static'),
                os.path.join(self.theme_path, 'static')]
        for language in self.config.get('languages', {}):
            static_path = os.path.join(self.src_path, '{}/static'.format(language))
            if os.path.exists(static_path):
                paths.append(static_path)
        self._static_paths = paths
        return paths

    def resolve_path(self, path):
        dirs = self.get_static_paths()
        for dir in dirs:
            full_path = os.path.join(dir, path)
            if os.path.exists(full_path):
                return full_path
        raise IOError("Path {} not found!".format(path))

    def copy_static_files(self):
        dirs = self.get_static_paths()
        for dir in dirs:
            for path, dirs, files in os.walk(dir):
                relpath = os.path.relpath(path, dir)
                for dirname in dirs:
                    dest_path = os.path.join(self.build_path, 'static', relpath, dirname)
                    if os.path.exists(dest_path) and not os.path.isdir(dest_path):
                        shutil.rmtree(dest_path)
                    elif not os.path.exists(dest_path):
                        os.makedirs(dest_path)
                for filename in files:
                    src_path = os.path.join(path, filename)
                    dest_path = os.path.join(self.build_path, 
                                             'static',
                                             relpath,
                                             filename)
                    if not os.path.exists(dest_path) or \
                      os.stat(dest_path).st_mtime < os.stat(src_path).st_mtime:
                        shutil.copy(src_path, dest_path)

    def copy(self, path):
        full_path = self.resolve_path(path)
        return os.path.join(self.site_path, 'static', path)

    def href(self, language, url):
        link = self.get_link(language, url)
        return link

    def scss(self, filename):
        return filename

    def load(self, params):
        o = urlparse(params['src'])
        for loader_params in self.loaders:
            if loader_params['scheme'] == o.scheme:
                break
        else:
            raise TypeError("No loader for scheme: {}".format(o.scheme))
        loader = loader_params['loader'](self)
        path = params['src'][len(o.scheme)+3:]
        return loader.load(path)

    def process(self, input, params, vars, language):
        for processor_params in self.processors:
            if params['type'] == processor_params['type']:
                break
        else:
            raise TypeError("No processor for file type: {}".format(filename))
        output = input
        for processor_cls in processor_params['processors']:
            processor = processor_cls(self, params, language)
            output = processor.process(output, vars)
        return output

    def build_links(self, pages_by_language, articles_by_language):
        self.links = {}
        for language, pages in pages_by_language.items():
            self.links[language] = {}
            for page in pages:
                self.links[language][page['name']] = page['dst']
                if page.get('index'):
                    self.links[language][''] = page['dst']
        for language, articles in articles_by_language.items():
            for article in articles:
                self.links[language][article['name']] = article['dst']

    def get_filename(self, language, name):
        if '/' in name:
            language, name = name.split('/')
        return self.links[language][name]

    def get_link(self, language, name):
        try:
            return '{}{}'.format(self.site_path, self.get_filename(language, name))
        except KeyError:
            return None

    def build(self):
        pages_by_language = {}
        articles_by_language = {}
        links = {}
        for language, params in self.config.get('languages', {}).items():
            params['name'] = language
            pages = self.parse_pages(params.get('pages', []), language)
            pages_by_language[language] = pages
            articles = self.parse_articles(params.get('articles', []), language)
            articles_by_language[language] = articles
        self.copy_static_files()
        self.build_links(pages_by_language, articles_by_language)
        for language, articles in articles_by_language.items():
            self.build_blog(articles, language)
        for language, pages in pages_by_language.items():
            for page in pages:
                self.build_page(page, language)

    def build_page(self, page, language):
        vars = {
            'language' : self.config['languages'][language],
            'page' : page,
            'site' : self
        }
        input = self.load(page)
        output = self.process(input, page, vars, language)
        filename = self.get_filename(language, page['name'])
        self.write(output, filename)

    def sort_articles(self, articles):
        return sorted(articles, key=lambda x : x.get('date',x.get('title')))

    def paginate_articles(self, articles):
        app = self.config.get('articles-per-page', 10)
        return [articles[i*app:(i+1)*app] for i in range(math.ceil(len(articles)/app))]

    def build_blog(self, articles, language):
        """
        Build the indexes, meta-pages and articles.
        """
        pages = self.paginate_articles(self.sort_articles(articles))
        for i, page in enumerate(pages):
            self.build_index_site(i, len(pages), articles, page, language)
            for article in page:
                self.build_article(article, i, language)

    def build_index_site(self, i, n, articles, page, language):
        input = "{% extends('index.html') %}"
        vars = {
            'page' : page,
            'site' : self,
            'articles' : articles,
            'i' : i,
            'n' : n,
            'language' : self.config['languages'][language]
        }
        output = self.process(input, {'type' : 'html'}, vars, language)
        filename = os.path.join(
            self.get_language_prefix(language),
            self.get_blog_prefix(language),
            'index{}.html'.format('{}'.format(i+1) if i != 0 else ''))
        self.links[language]['blog-{}'.format(i)] = filename
        self.write(output, filename)

    def build_article(self, article, page, language):
        """
        Build an individual blog article.
        """
        vars = {
            'language' : self.config['languages'][language],
            'article' : article,
            'page' : page,
            'index_link' : self.get_link(language, 'blog-{}'.format(page)),
            'site' : self
        }
        input = self.load(article)
        output = self.process(input, article, vars, language)
        filename = self.get_filename(language, article['name'])
        self.write(output, filename)
