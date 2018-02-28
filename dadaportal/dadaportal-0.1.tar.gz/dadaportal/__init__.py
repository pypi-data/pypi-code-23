import logging
import csv
from pathlib import Path
from . import config, render, links, skeleton

logger = logging.getLogger(__name__)

def build(configuration: Path, *, force: bool=False,
          noclean=False, yes=False):
    '''
    Build a dada portal website.

    :param pathlib.Path configuration: This is the configuration file
        for the dada portal.
    :param bool force: Force rebuilding of all files instead of only
        building stale files.
    :param bool noclean: Keep unnecessary files that are in the output
        directory, rather than deleting them.
    :param bool yes: Automatically answer yes when asked whether to
        delete files.
    '''
    with configuration.open() as fp:
        c = config.configuration_file(fp)

    wd = configuration.parent
    out = wd / c['output']

    if c['redirects'] and (wd / c['redirects']).is_file():
        redirects = _csv(wd / c['redirects'])
    else:
        redirects = []

    results = set()

    if c['fossil-repositories']:
        results.add(render.fossil(
            c['fossil-executable'],
            wd / c['fossil-repositories'],
            (wd / c['fossil-debug'] if c['fossil-debug'] else None),
            out / c['fossil-route'],
        ))
    if c['root-directory']:
        results.update(render.articles(force,
                                       wd / c['root-directory'], out,
                                       outroot=out))

    results.update(render.lib(c['gzip'] != None, c['root-address'], redirects,
                              wd / c['404'], wd / c['fossil-route'], out))

    results.update(render.sitemap(c['root-address'], results, out))
            
    results.update(render.gz(out / '.htaccess', out / c['fossil-route'],
                             force, out))
    
    if not noclean:
        unlinks = []
        result_paths = set(page.route for page in results)
        for outpath in (out).glob('**/*'):
            if outpath.is_file() and outpath not in result_paths:
                unlinks.append(outpath)
                gz = outpath.with_name(outpath.name + '.gz')
                if gz.is_file():
                    unlinks.append(gz)
        if unlinks:
            def delete():
                for unlink in unlinks:
                    unlink.unlink()
            if yes:
                delete()
            else:
                print('Stale files in output directory:')
                print('')
                for unlink in unlinks:
                    print('  %s' % unlink)
                print('')
                while True:
                    response = input('Is it okay to remove these files? [y/N] ')
                    if response in {'n', 'N', ''}:
                        break
                    elif response == 'y':
                        delete()
                        break
        _rmdirs(out)

def _rmdirs(parent):
    if parent.is_dir():
        children = list(parent.iterdir())
        if 0 < len(children):
            for child in children:
                _rmdirs(child)
        else:
            parent.rmdir()

def check(configuration: Path,
          absentindexes=False, external=False,
          allsources=False, alltargets=False):
    '''
    Check for broken, absolute, and missing links in a tree of HTML files.

    :param pathlib.Path configuration: This is the configuration file
        for the dada portal.
    :param bool absentindexes: When an index file does not exist,
        print the links that are missing from it.
    :param bool external: Check whether external links are alive.
    :param bool allsources: Check for broken links from all files, not
        just from index files.
    :param bool alltargets: Check for missing links to all files in a
        directory, not just to subdirectories.
    '''
    def _print(link):
        kind, src, dst = link
        return '%08s: %s -> %s' % (kind.name, src, dst)

    wd = configuration.parent
    with configuration.open() as fp:
        c = config.configuration_file(fp)

    if c['extra-link-checks']:
        extra_link_checks = _csv(wd / c['extra-link-checks'])
    else:
        extra_link_checks = []

    directory = wd / c['output']
    for link in _check(c['root-address'], c['fossil-route'], allsources, absentindexes, alltargets, external, directory):
        yield _print(link)

    for source, target in extra_link_checks:
        for link in links.missing_links(absentindexes,
                                        alltargets,
                                        directory / source,
                                        directory / target):
            yield _print(link)

def _check(root_address, fossil_route, allsources, absentindexes, alltargets, external, start):
    if start.is_dir():
        yield from links.missing_links(absentindexes, alltargets, start, start)
        for child in start.iterdir():
            yield from _check(root_address, fossil_route, allsources, absentindexes, alltargets, external, child)
    elif start.is_file() and start.suffix == '.html':
        if (allsources or start.name == 'index.html'):
            yield from links.bad_links(root_address, external, fossil_route, start)

def _csv(path):
    if path.is_file():
        with path.open() as fp:
            for row in csv.reader(fp):
                if len(row) < 2:
                    pass
                elif len(row) == 2:
                    yield tuple(cell.strip() for cell in row)
                else:
                    msg = 'Too many elements in csv row: %s'
                    raise ValueError(msg % tuple(row))
