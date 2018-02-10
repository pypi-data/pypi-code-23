# -*- coding: utf-8 -*-
# MIT License
#
# Copyright (c) 2018 fyrestone (https://github.com/fyrestone/svnbranch)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

__author__ = 'fyrestone'
__email__ = 'fyrestone@outlook.com'
__version__ = '1.1'

import shlex
import argparse
import json
import logging
import os
import io
import sys
import shutil
import locale
import string
import tempfile
import time
import collections
import xml.dom.minidom

import url_normalize
import gevent
from gevent import sleep
from gevent.subprocess import Popen, PIPE
from six.moves.urllib import parse as urlparse
from six.moves import range
from six import text_type
from six import iteritems, itervalues, iterkeys
from six import PY3

_DEBUG = False  # if value is True, gevent concurrency will be disabled
_LOCAL_TMP_DIR = True  # the place to exec co-propset-ci operation, if True use current work dir else use system tmp dir
_CONFIG_FILE_VERSION = 1  # a number to distinguish different versions of config file
_UUID_FORMATTER = u'{uuid}'
_LOG_FORMAT = u'%(asctime)-8s [%(filename)s] %(message)s'

_TYPE_URL = 'URL type'
_TYPE_LOCAL = 'local path type'

_CONFIG_KEY_VERSION = u'version'
_CONFIG_KEY_BRANCH_MAP = u'branch_map'
_CONFIG_KEY_EXTERNAL_CACHE = u'external_cache'
_CONFIG_KEY_URL_LIST = u'url_list'

if _DEBUG:
    gevent.spawn = lambda func, *args, **kwargs: func(*args, **kwargs)
    gevent.wait = lambda *args, **kwargs: None


class NoUnicodeEscapeStreamHandler(logging.StreamHandler):
    def format(self, record):
        s = super(NoUnicodeEscapeStreamHandler, self).format(record)
        try:
            return s.decode('unicode_escape')
        except:
            return s


def _get_logger():
    try:
        logger = logging.getLogger(os.path.basename(__file__))
    except NameError:
        logger = logging.getLogger('svnbranch')
    logger.setLevel(logging.DEBUG if _DEBUG else logging.INFO)
    if len(logger.handlers) == 0:
        stream_handler = NoUnicodeEscapeStreamHandler()
        stream_handler.setFormatter(logging.Formatter(fmt=_LOG_FORMAT))
        logger.addHandler(stream_handler)
    return logger


_logger = _get_logger()


class ArgParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(ArgParser, self).__init__(*args, **kwargs)
        self._check_dependency()

    def _check_dependency(self):
        cmd = ''
        try:
            # these commands will be checked at startup
            for cmd in ['svn']:
                Popen(cmd, stdout=PIPE, stderr=PIPE, shell=False)
        except:
            self.error('Can not find dependency %s.' % cmd)

    def error(self, message):
        self.print_help(sys.stderr)
        from gettext import gettext as _

        self.exit(2, _('\n%s got error from %s\n') % (self.prog, message))


class BranchOperationException(Exception):
    def __init__(self, message, *args):
        assert isinstance(message, text_type)
        message = message % args
        if not PY3:
            message = message.encode('utf-8')
        super(BranchOperationException, self).__init__(message)


class CmdDecorator(object):
    GLOBAL_PARAMS = None

    def __init__(self, fn):
        self._func = fn

    def __call__(self, cmd, *args, **kwargs):
        if self.GLOBAL_PARAMS:
            target = '--non-interactive'
            cmd = cmd.replace(target, ' '.join([self.GLOBAL_PARAMS, target]))
        return self._func(cmd, *args, **kwargs)

    @classmethod
    def parse_global_option(cls, **kwargs):
        params = []

        def _decorate_key(k):
            return '--' + k.replace('_', '-')

        def _decorate_value(v):
            return '"' + v + '"'

        def _build_arg(key):
            value = kwargs.get(key)
            if value:
                params.append(_decorate_key(key))
                params.append(_decorate_value(value))

        for k in ['username', 'password', 'config_dir', 'config_option']:
            _build_arg(k)

        def _build_action(key):
            value = kwargs.get(key)
            if value:
                params.append(_decorate_key(key))

        for k in ['no_auth_cache']:
            _build_action(k)

        if params:
            cls.GLOBAL_PARAMS = ' '.join([str(p) for p in params])
        else:
            cls.GLOBAL_PARAMS = ''


ExternalItem = collections.namedtuple(
    'ExternalItem',
    ['external_line', 'external_url', 'external_abs_url', 'peg_rev', 'opt_rev'])


class RemoteExternals(object):
    _global_urls = set()
    _global_greenlets = []
    _data = {}

    @staticmethod
    @CmdDecorator
    def _safe_popen(cmd):
        while True:
            try:
                _logger.debug(u'[cmd] ' + cmd)
                if PY3:
                    cmd_parts = shlex.split(cmd)
                else:
                    # shlex can not handle unicode in Python 2,
                    # refer to: https://stackoverflow.com/questions/14218992/shlex-split-still-not-supporting-unicode
                    cmd_parts = shlex.split(cmd.encode(locale.getpreferredencoding()))
                pipe = Popen(cmd_parts, stdout=PIPE, stderr=PIPE, shell=False)
                data, err = pipe.communicate()  # err is a multi-bytes string
                if pipe.returncode != 0 and not u'W200017'.encode('utf-8') in err:  # W200017: svn property not found
                    _logger.error(u'Exec cmd failed: %s, ret: %s\nstdout: %s\nstderr: %s\n',
                                  cmd, pipe.returncode, data, err)
                    sys.exit(-1)
                return data, err
            except (OSError, IOError) as ex:
                if ex.errno == 24:  # open fd count exceeds system limits
                    sleep(1)  # wait for subprocess finished which will increase available fds
                    continue
                else:
                    raise
            except Exception as ex:
                _logger.error(u'Exec cmd failed: %s,\nex: %s', cmd, ex)
                sys.exit(-1)  # make sure any exception crash

    @staticmethod
    def _parse_property_xml(data):
        try:
            dom = xml.dom.minidom.parseString(data)
        except Exception:
            return []
        else:
            targets = dom.getElementsByTagName('target')
            target_paths = [t.getAttribute('path') for t in targets]
            properties = dom.getElementsByTagName('property')
            externals = [p.childNodes[0].data for p in properties]
            return zip(target_paths, externals)

    @staticmethod
    def _parse_list_xml(data, kind):
        try:
            dom = xml.dom.minidom.parseString(data)
        except Exception:
            return []
        else:
            entries = dom.getElementsByTagName('entry')
            entries_kind = [e.getAttribute('kind') for e in entries]
            filenames = dom.getElementsByTagName('name')
            filenames = [n.childNodes[0].data for n in filenames]
            return [n + u'/' for k, n in zip(entries_kind, filenames) if k == kind]

    @staticmethod
    def _parse_info_xml(data, tag):
        try:
            dom = xml.dom.minidom.parseString(data)
        except Exception:
            return ''
        else:
            repository = dom.getElementsByTagName(tag)
            return repository[0].childNodes[0].data

    @classmethod
    def get_repo_url(cls, url, cache=None):
        assert cache is None or isinstance(cache, collections.MutableSet)

        def _real_get_repo_url():
            cmd = u'svn info --non-interactive --xml "%s"' % url
            data, err = cls._safe_popen(cmd)
            return Utils.norm_url(cls._parse_info_xml(data, u'root'))

        def _memo_get_repo_url():
            for norm_repo_url in cache:
                if url.startswith(norm_repo_url):
                    return norm_repo_url

            norm_repo_url = _real_get_repo_url()
            cache.add(norm_repo_url)
            return norm_repo_url

        if cache is None:
            return _real_get_repo_url()
        else:
            return _memo_get_repo_url()

    @classmethod
    def get_url(cls, path):
        cmd = u'svn info --non-interactive --xml "%s"' % path
        data, err = cls._safe_popen(cmd)
        return Utils.norm_url(cls._parse_info_xml(data, 'url'))

    @staticmethod
    def _parse_external_line(external_line):
        # svn_wc__parse_externals_description from externals.c
        # There are six different formats of externals:
        #
        # 1) DIR URL
        # 2) DIR -r N URL
        # 3) DIR -rN  URL
        # 4) URL DIR
        # 5) -r N URL DIR
        # 6) -rN URL DIR
        #
        # The last three allow peg revisions in the URL.
        #
        # With relative URLs and no '-rN' or '-r N', there is no way to
        # distinguish between 'DIR URL' and 'URL DIR' when URL is a
        # relative URL like /svn/repos/trunk, so this case is taken as
        # case 4).

        def _get_opt_rev(parts):
            """
            To make it easy to check for the forms, find and remove -r N
            or -rN from the line item array.
            :param parts: external line parts
            :return: (-r token index, opt_rev string)
            """
            for i, token in enumerate(parts):
                if token.startswith('-r'):
                    if len(token) == 2:  # token == '-r'
                        if len(parts) != 4:
                            break
                        opt_rev = parts[i + 1]
                        parts[:] = parts[:i] + parts[i + 2:]
                    else:  # token == '-rN'
                        if len(parts) != 3:
                            break
                        opt_rev = token[2:]
                        parts[:] = parts[:i] + parts[i + 1:]
                    return i, opt_rev
            else:
                # No revision was found, so there must be exactly two items in the line array
                if len(parts) == 2:
                    return -1, ''
            raise Exception(u'Parse external line failed, invalid value: {}'.format(external_line))

        def _get_peg_rev(u):
            url_parts = u.split('@')
            if len(url_parts) <= 1 or '/' in url_parts[-1]:  # revision specifiers can't contain '/'
                external_url = url_parts[0]
                peg_rev = ''
            else:
                external_url = '@'.join(url_parts[:-1])
                peg_rev = url_parts[-1]
            return external_url, peg_rev

        external_parts = external_line.split()
        if len(external_parts) < 2 or len(external_parts) > 4:
            raise BranchOperationException(u'Parse external line failed, invalid value: {}'.format(external_line))

        opt_idx, opt_rev = _get_opt_rev(external_parts)
        token0_is_url = Utils.is_url(external_parts[0])
        token1_is_url = Utils.is_url(external_parts[1])

        if token0_is_url and token1_is_url:
            raise Exception(u'Found two URLs in one external line, invalid value: {}'.format(external_line))
        if 0 == opt_idx and token1_is_url:
            err_msg = u'Cannot use a URL as the target directory for an external definition, invalid value: {}'
            raise Exception(err_msg.format(external_line))
        if 1 == opt_idx and token0_is_url:
            err_msg = u'Cannot use a URL as the target directory for an external definition, invalid value: {}'
            raise Exception(err_msg.format(external_line))

        # The appearance of -r N or -rN forces the type of external.
        # If -r is at the beginning of the line or the first token is
        # an absolute URL or if the second token is not an absolute
        # URL, then the URL supports peg revisions.
        if 0 == opt_idx or (-1 == opt_idx and (token0_is_url or not token1_is_url)):  # case 4, 5, 6
            # [-r REV] URL[@PEG] LOCALPATH, introduced in Subversion 1.5
            external_dir = external_parts[1]
            external_url, peg_rev = _get_peg_rev(external_parts[0])

        else:  # case 1, 2, 3
            # LOCALPATH [-r PEG] URL
            external_dir, external_url = external_parts
            peg_rev = opt_rev

        return external_dir, external_url, peg_rev, opt_rev

    @staticmethod
    def build_external_line(external_dir, external_url, peg_rev, opt_rev):
        if peg_rev:
            external_url = u'@'.join([external_url, peg_rev])
        if opt_rev:
            opt_rev = u' '.join([u'-r', opt_rev])
        return ' '.join([opt_rev, external_url, external_dir]).strip()

    @classmethod
    def resolve_external_url(cls, current_url, external_url):
        # refer to: http://svnbook.red-bean.com/nightly/en/svn.advanced.externals.html
        # svn_wc__resolve_relative_external_url from externals.c

        if Utils.is_url(external_url):
            return Utils.norm_url(external_url)

        if external_url[:3] == '../':
            # Relative to the URL of the directory on which the svn:externals property is set
            result = urlparse.urljoin(current_url, external_url)
        elif external_url[:2] == '^/':
            # Relative to the root of the repository in which the svn:externals property is versioned
            repo_url = cls.get_repo_url(current_url)
            result = urlparse.urljoin(repo_url, external_url[2:])
        elif external_url[:2] == '//':
            # Relative to the scheme of the URL of the directory on which the svn:externals property is set
            parse = urlparse.urlparse(current_url)
            result = parse.scheme + ':' + external_url
        elif external_url[0] == '/':
            # Relative to the root URL of the server on which the svn:externals property is versioned
            parse = urlparse.urlparse(current_url)
            data = (parse.scheme, parse.netloc or parse.path, external_url, parse.params, parse.query, parse.fragment)
            result = urlparse.urlunparse(data)
        else:
            raise BranchOperationException(u'Unknown external URL format: {}'.format(external_url))

        return Utils.norm_url(result)

    @classmethod
    def _get_externals(cls, cmd, recursive=False):
        data, err = cls._safe_popen(cmd)
        external_list = cls._parse_property_xml(data)

        for path, data in external_list:
            path = Utils.norm_url(path)
            data = data.strip()
            _logger.info(u"List svn:externals of %s:\n%s", path, data)
            for line in data.splitlines():
                external_dir, external_url, peg_rev, opt_rev = cls._parse_external_line(line)
                external_abs_url = cls.resolve_external_url(path, external_url)
                item = ExternalItem(line, external_url, external_abs_url, peg_rev, opt_rev)
                cls._data.setdefault(path, {}).setdefault(external_dir, item)
                if recursive:
                    cls._global_greenlets.append(
                        gevent.spawn(cls._process_dir, external_abs_url))

    @classmethod
    def _update_global_urls(cls, url):
        url = Utils.norm_url(url)
        for u in cls._global_urls:
            if url.startswith(u):  # already run propget from parent url recursively (with -R)
                return False
            elif u.startswith(url):
                cls._global_urls.discard(u)
                cls._global_urls.add(url)
                break
        else:
            cls._global_urls.add(url)
        return True

    @classmethod
    def _process_dir(cls, url):
        if not cls._update_global_urls(url):
            return

        # propget svn:externals on url, then recursive propget svn:externals on sub directories,
        # to slightly concurrent propget operation on svn server.
        cmd = u'svn propget svn:externals --non-interactive --xml "%s"' % url
        cls._global_greenlets.append(gevent.spawn(cls._get_externals, cmd))

        data, err = cls._safe_popen(u'svn list --non-interactive --xml "%s"' % url)
        dir_list = cls._parse_list_xml(data, u'dir')
        for node in dir_list:
            cmd = u'svn propget svn:externals --non-interactive --xml -R "%s"' % urlparse.urljoin(url, node)
            cls._global_greenlets.append(gevent.spawn(cls._get_externals, cmd))

    @classmethod
    def get_from_url(cls, url_list):
        cls._data = {}

        for url in url_list:
            cls._global_greenlets.append(
                gevent.spawn(cls._process_dir, url))

        while len(cls._global_greenlets) > 0:
            wait_list = cls._global_greenlets
            cls._global_greenlets = []
            gevent.wait(wait_list)

        return cls._data

    @classmethod
    def _get_externals_local(cls, cmd):
        data, err = cls._safe_popen(cmd)
        external_list = cls._parse_property_xml(data)

        for path, data in external_list:
            path = cls.get_url(path)
            data = data.strip()
            _logger.info(u"List svn:externals of %s:\n%s", path, data)
            for line in data.splitlines():
                external_dir, external_url, peg_rev, opt_rev = cls._parse_external_line(line)
                external_abs_url = cls.resolve_external_url(path, external_url)
                item = ExternalItem(line, external_url, external_abs_url, peg_rev, opt_rev)
                cls._data.setdefault(path, {}).setdefault(external_dir, item)

    @classmethod
    def _process_dir_local(cls, path):
        cmd = u'svn propget svn:externals --non-interactive --xml -R "%s"' % path
        cls._global_greenlets.append(gevent.spawn(cls._get_externals_local, cmd))

    @classmethod
    def get_from_local(cls, path_list):
        cls._data = {}

        for path in path_list:
            cls._process_dir_local(path)

        while len(cls._global_greenlets) > 0:
            wait_list = cls._global_greenlets
            cls._global_greenlets = []
            gevent.wait(wait_list)

        return cls._data


class BranchOperation(object):
    @staticmethod
    @CmdDecorator
    def _system_cmd(cmd, test=False):
        _logger.info(u'[cmd] ' + cmd)
        if test:
            return
        if not PY3:
            cmd = cmd.encode(locale.getpreferredencoding())
        ret = os.system(cmd)
        if ret != 0:
            raise BranchOperationException(u'Exec cmd failed, ret value: %s.', ret)

    @staticmethod
    def _apply_branch_map(url, config):
        for src, dst in iteritems(config):
            url = url.replace(src, dst)
        return url

    @staticmethod
    def _gen_branch_map(url_list, externals):
        url_set = set(url_list)
        for path, external_info in iteritems(externals):
            url_set.add(path)
            for external_item in itervalues(external_info):
                if not external_item.peg_rev and not external_item.opt_rev:
                    # only externals without specific revisions can be mapped
                    url_set.add(external_item.external_abs_url)

        merged_urls = {}
        repo_cache = set()  # optimize for get_repo_url

        for u in sorted(url_set):
            repo_url = RemoteExternals.get_repo_url(u, repo_cache)
            if repo_url and u.startswith(repo_url):
                url_path = u[len(repo_url):]
                repo_branch = merged_urls.setdefault(repo_url, {})
                if not any(url_path.startswith(p) for p in iterkeys(repo_branch)):
                    repo_branch.setdefault(url_path, '')

        return merged_urls

    @staticmethod
    def _gen_external_cache(externals):
        external_cache = {}
        for path, external_info in iteritems(externals):
            external_data = external_cache.setdefault(path, {})
            for external_dir, item in iteritems(external_info):
                external_data[external_dir] = (item.external_url, item.peg_rev, item.opt_rev)
        return external_cache

    @staticmethod
    def create_branch(config, comment, uuid, test, **kwargs):
        branch_map = config.get(_CONFIG_KEY_BRANCH_MAP, {})
        if not branch_map:
            raise BranchOperationException(u'Branch map in config is empty!')
        branch_map = Utils.format_branch_map(branch_map, uuid=uuid)

        external_cache = config.get(_CONFIG_KEY_EXTERNAL_CACHE)
        if external_cache:
            _logger.info(u'Using external cache from config.')
        elif external_cache is not None:  # the external cache already exists (empty), skip scan external_cache
            _logger.info(u'Found empty external cache from config. ')
        else:  # external_cache is None, no _CONFIG_KEY_EXTERNAL_CACHE is found in config, rescan external_cache
            url_list = config.get(_CONFIG_KEY_URL_LIST, [])
            if not url_list:
                raise BranchOperationException(u'{} in config is emtpy.'.format(_CONFIG_KEY_URL_LIST))
            _logger.info(u'Scanning externals of %s...', url_list)
            externals = RemoteExternals.get_from_url(url_list)
            external_cache = BranchOperation._gen_external_cache(externals)

        branch_externals = {}
        repo_cache = set()  # optimize for get_repo_url

        for path, external_info in iteritems(external_cache):
            path_repo_url = RemoteExternals.get_repo_url(path, repo_cache)
            mapped_path = BranchOperation._apply_branch_map(path, branch_map)
            branch_externals.setdefault(mapped_path, [])

            for external_dir, (external_url, peg_rev, opt_rev) in iteritems(external_info):
                external_abs_url = RemoteExternals.resolve_external_url(path, external_url)
                external_repo_url = RemoteExternals.get_repo_url(external_abs_url, repo_cache)

                if not peg_rev and not opt_rev:
                    # only external with no specific revisions can be mapped to a new url
                    external_abs_url = BranchOperation._apply_branch_map(external_abs_url, branch_map)

                # if externals link to the same repository, use relative external url
                if external_repo_url == path_repo_url and external_abs_url.startswith(external_repo_url):
                    external_relative_url = external_abs_url[len(external_repo_url) - 1:]
                    external_relative_url = '^' + external_relative_url  # relative to the root of the repository
                    external_line = RemoteExternals.build_external_line(
                        external_dir, external_relative_url, peg_rev, opt_rev)
                    branch_externals[mapped_path].append(external_line)
                else:  # else use absolute external url
                    external_line = RemoteExternals.build_external_line(
                        external_dir, external_abs_url, peg_rev, opt_rev)
                    branch_externals[mapped_path].append(external_line)

        _logger.info(u'Create branch copy...')
        for src_url, dst_url in iteritems(branch_map):
            cmd = u'svn copy --non-interactive -m "%s" --parents %s %s' % (comment, src_url, dst_url)
            BranchOperation._system_cmd(cmd, test)

        _logger.info(u'Update branch externals...')
        tmp_root_dir = tempfile.mkdtemp(prefix='svnbranch.', dir=os.getcwd() if _LOCAL_TMP_DIR else None)
        try:
            for branch_url, external_lines in iteritems(branch_externals):
                temp_dir = tempfile.mkdtemp(dir=tmp_root_dir)
                # co-propset-ci is better than svnmucc, svnmucc (1.9.3) has bug to decode prop file.
                cmd = u'svn co %s "%s" --depth "empty"' % (branch_url, temp_dir)
                BranchOperation._system_cmd(cmd, test)

                # write to file and use -F to avoid encoding problems
                with tempfile.NamedTemporaryFile(dir=tmp_root_dir, delete=False) as fp:
                    branch_data = u'\n'.join(external_lines)
                    _logger.info(u"List svn:externals of %s from %s:\n%s", branch_url, fp.name, branch_data)
                    fp.write(branch_data.encode('utf-8'))

                cmd = u'svn propset svn:externals --non-interactive --encoding "utf-8" -F "%s" %s' % (fp.name, temp_dir)
                BranchOperation._system_cmd(cmd, test)

                cmd = u'svn ci -m "%s" "%s"' % (comment, temp_dir)
                BranchOperation._system_cmd(cmd, test)
        finally:
            if not _DEBUG:
                try:
                    shutil.rmtree(tmp_root_dir, ignore_errors=True)
                except:
                    pass

        _logger.info(u'Create branch success!')

    @staticmethod
    def delete_branch(config, comment, uuid, test, **kwargs):
        branch_map = config.get(_CONFIG_KEY_BRANCH_MAP, {})
        if not branch_map:
            raise BranchOperationException(u'{} in config is empty.'.format(_CONFIG_KEY_BRANCH_MAP))

        branch_map = dict((k, Utils.get_partial_url(v, _UUID_FORMATTER))  # rstrip to the '/' near {uuid} formatter
                          for k, v in iteritems(branch_map)
                          if _UUID_FORMATTER in v)  # filter by {uuid} formatter
        branch_map = Utils.format_branch_map(branch_map, uuid=uuid)

        _logger.info(u'Delete branch copy...')
        exec_urls = []
        for url in sorted(set(itervalues(branch_map))):
            if any(url.startswith(u) for u in exec_urls):
                continue
            exec_urls.append(url)

            cmd = u'svn delete --non-interactive -m "%s" %s' % (comment, url)
            try:
                BranchOperation._system_cmd(cmd, test)
            except BranchOperationException as ex:
                _logger.error(u'[%s] %s' % (BranchOperationException.__name__, ex))

        _logger.info(u'Delete branch finished!')

    @classmethod
    def create_config(cls, url_or_path_list, output, **kwargs):
        input_type = url_or_path_list[0].type
        if not all(v.type == input_type for v in url_or_path_list):
            raise BranchOperationException(u'Expect all items in url_or_path_list is type {}'.format(input_type))

        url_or_path_list = [v.value for v in url_or_path_list]
        _logger.info(u'Scanning externals of %s...', url_or_path_list)
        if input_type == _TYPE_URL:
            externals = RemoteExternals.get_from_url(url_or_path_list)
        elif input_type == _TYPE_LOCAL:
            externals = RemoteExternals.get_from_local(url_or_path_list)
            url_or_path_list = [RemoteExternals.get_url(p) for p in url_or_path_list]
        else:
            raise BranchOperationException(u'Unknown type {}'.format(input_type))

        config_dict = {
            _CONFIG_KEY_VERSION: _CONFIG_FILE_VERSION,
            _CONFIG_KEY_BRANCH_MAP: cls._gen_branch_map(url_or_path_list, externals),
            _CONFIG_KEY_EXTERNAL_CACHE: cls._gen_external_cache(externals),
            _CONFIG_KEY_URL_LIST: sorted(url_or_path_list),
        }
        config = json.dumps(config_dict, ensure_ascii=False, indent=4, sort_keys=True)

        _logger.info(u'Save config to %s.\n%s', output, config)
        with io.open(output, 'w', encoding='utf-8') as fp:
            fp.write(config)

        _logger.info(u'Create config success!')


InputTarget = collections.namedtuple('InputTarget', ['type', 'value'])


class Utils(object):
    @staticmethod
    def is_url(url):
        try:
            parse = urlparse.urlparse(url)
            # windows path c:\\file will get 'c' as scheme
            if parse.scheme and parse.scheme.lower() not in string.ascii_lowercase:
                return True
        except Exception:
            pass
        return False

    @staticmethod
    def norm_url(url, with_slash=True):
        if not url:
            return url
        url = url_normalize.url_normalize(url)
        return url.strip(u' /') + (u'/' if with_slash else u'')

    @staticmethod
    def format_branch_url(url, **kwargs):
        class FormatDict(dict):
            def __missing__(self, key):
                return u"{" + key + u"}"

        formatter = string.Formatter()
        kwargs = FormatDict(kwargs)

        try:
            return Utils.norm_url(formatter.vformat(url, (), kwargs))
        except KeyError:
            return Utils.norm_url(url)

    @staticmethod
    def format_branch_map(branch_map, **kwargs):
        return dict((k, Utils.format_branch_url(v, **kwargs)) for k, v in iteritems(branch_map))

    @staticmethod
    def init_branch_map(branch_map):
        format_branch_info = {}
        for repo_url, branch_info in iteritems(branch_map):
            repo_url = Utils.norm_url(repo_url)
            # refer to: https://stackoverflow.com/questions/10893374/python-confusions-with-urljoin
            for src, dst in iteritems(branch_info):
                src = src.lstrip('/')  # make urljoin work as expected
                dst = dst.lstrip('/')  # make urljoin work as expected
                src_url = urlparse.urljoin(repo_url, src)
                dst_url = urlparse.urljoin(repo_url, dst)
                if src_url.startswith(dst_url):
                    raise BranchOperationException(
                        u'Can not branch from {} to {}'.format(src_url, dst_url))
                format_branch_info[src_url] = dst_url
        return format_branch_info

    @staticmethod
    def get_partial_url(url, item):
        n = url.find(item)
        if n != -1:
            m = url.find(u'/', n + len(item))
            if m != -1:
                return url[:m]  # must not normalize the result URL in order to preserve the {uuid} formatter
        return url

    @staticmethod
    def validate_url_or_path(input_target):
        if not isinstance(input_target, text_type):
            input_target = input_target.decode(locale.getpreferredencoding())
        try:
            if os.path.exists(input_target):
                return InputTarget(_TYPE_LOCAL, input_target)
        except:
            pass
        try:
            if Utils.is_url(input_target):
                return InputTarget(_TYPE_URL, Utils.norm_url(input_target))
        except:
            pass
        err_msg = u'"%s" should be a valid URL or an existing path.' % input_target
        raise argparse.ArgumentTypeError(err_msg)

    @staticmethod
    def validate_json(jsonfile):
        ex_str = u''
        try:
            with open(jsonfile, 'rb') as fp:
                data = json.load(fp)
            branch_map = data.get(_CONFIG_KEY_BRANCH_MAP, {})
            branch_map = Utils.init_branch_map(branch_map)
            data[_CONFIG_KEY_BRANCH_MAP] = branch_map
            return data
        except Exception as ex:
            ex_str = text_type(ex)
        err_msg = u'"%s" should be a valid config file.\ndetails: %s' % (jsonfile, ex_str)
        raise argparse.ArgumentTypeError(err_msg)

    @staticmethod
    def to_unicode(s):
        if not isinstance(s, text_type):
            return s.decode(locale.getpreferredencoding())
        return s


def main():
    program_name = os.path.basename(__file__)
    parser = ArgParser(
        description='%s: A simple svn branch tool with externals support.' % program_name)
    parser.add_argument('-v', '--version', default=False, action='store_true',
                        help='print version number')

    sub_parsers = parser.add_subparsers(help='branch operations')
    sp = sub_parsers.add_parser(BranchOperation.create_config.__name__)
    sp.set_defaults(operation=BranchOperation.create_config.__name__)
    sp.add_argument('url_or_path_list', type=Utils.validate_url_or_path, nargs='+',
                    help='target svn URL list or local path list to create config file')
    sp.add_argument('-o', '--output', type=Utils.to_unicode, default='config_template.json',
                    help='output config file, default is config_template.json')
    sp.add_argument('-u', '--username', type=Utils.to_unicode,
                    help='<svn ARG> specify a username ARG')
    sp.add_argument('-p', '--password', type=Utils.to_unicode,
                    help='<svn ARG> specify a password ARG (caution: on many operating systems, '
                         'other users will be able to see this)')
    sp.add_argument('--config-dir', type=Utils.to_unicode,
                    help='<svn ARG> read user configuration files from directory ARG')
    sp.add_argument('--config-option', type=Utils.to_unicode,
                    help='<svn ARG> set user configuration option in the format: FILE:SECTION:OPTION=[VALUE], '
                         'For example: servers:global:http-library=serf')
    sp.add_argument('--no-auth-cache', default=False, action='store_true',
                    help='<svn ARG> do not cache authentication tokens')

    sp = sub_parsers.add_parser(BranchOperation.create_branch.__name__)
    default_comment = '[%s] by %s' % (BranchOperation.create_branch.__name__, program_name)
    default_uuid = time.strftime("%Y%m%dT%H%M")
    sp.set_defaults(operation=BranchOperation.create_branch.__name__)
    sp.add_argument('config', type=Utils.validate_json,
                    help='config file to create branch (json format)')
    sp.add_argument('-m', '--comment', type=Utils.to_unicode, default=default_comment,
                    help='create branch comment, default is "%s"' % default_comment)
    sp.add_argument('-uid', '--uuid', type=Utils.to_unicode, default=default_uuid,
                    help='unique string to distinguish different branches, '
                         'used to fill the {uuid} formatter in branch URL, '
                         'default is the datetime string, for example: %s' % default_uuid)
    sp.add_argument('-t', '--test', default=False, action='store_true',
                    help='only print svn operations, no effect on target svn repository')
    sp.add_argument('-u', '--username', type=Utils.to_unicode,
                    help='<svn ARG> specify a username ARG')
    sp.add_argument('-p', '--password', type=Utils.to_unicode,
                    help='<svn ARG> specify a password ARG (caution: on many operating systems, '
                         'other users will be able to see this)')
    sp.add_argument('--config-dir', type=Utils.to_unicode,
                    help='<svn ARG> read user configuration files from directory ARG')
    sp.add_argument('--config-option', type=Utils.to_unicode,
                    help='<svn ARG> set user configuration option in the format: FILE:SECTION:OPTION=[VALUE], '
                         'For example: servers:global:http-library=serf')
    sp.add_argument('--no-auth-cache', default=False, action='store_true',
                    help='<svn ARG> do not cache authentication tokens')

    sp = sub_parsers.add_parser(BranchOperation.delete_branch.__name__)
    default_comment = '[%s] by %s' % (BranchOperation.delete_branch.__name__, program_name)
    sp.set_defaults(operation=BranchOperation.delete_branch.__name__)
    sp.add_argument('config', type=Utils.validate_json,
                    help='config file to delete branch (json format)')
    sp.add_argument('uuid', type=Utils.to_unicode,
                    help='unique string to identify which branch to delete, '
                         'used to fill the {uuid} formatter in branch URL')
    sp.add_argument('-m', '--comment', type=Utils.to_unicode, default=default_comment,
                    help='branch comment, default is "%s"' % default_comment)
    sp.add_argument('-t', '--test', default=False, action='store_true',
                    help='only print svn operations, no effect on target svn repository')
    sp.add_argument('-u', '--username', type=Utils.to_unicode,
                    help='<svn ARG> specify a username ARG')
    sp.add_argument('-p', '--password', type=Utils.to_unicode,
                    help='<svn ARG> specify a password ARG (caution: on many operating systems, '
                         'other users will be able to see this)')
    sp.add_argument('--config-dir', type=Utils.to_unicode,
                    help='<svn ARG> read user configuration files from directory ARG')
    sp.add_argument('--config-option', type=Utils.to_unicode,
                    help='<svn ARG> set user configuration option in the format: FILE:SECTION:OPTION=[VALUE], '
                         'For example: servers:global:http-library=serf')
    sp.add_argument('--no-auth-cache', default=False, action='store_true',
                    help='<svn ARG> do not cache authentication tokens')

    args = parser.parse_args()

    version = getattr(args, 'version', False)
    if version:
        print('%s v%s' % (program_name, __version__))
        sys.exit(0)

    # args will be an empty Namespace object in Python 3
    operation = getattr(args, 'operation', None)
    if not operation:
        parser.print_help()
        sys.exit(0)

    operation = getattr(BranchOperation, operation)
    try:
        CmdDecorator.parse_global_option(**args.__dict__)
        operation(**args.__dict__)
    except BranchOperationException as ex:
        _logger.error(u'[%s] %s' % (BranchOperationException.__name__, ex))
        sys.exit(1)


if __name__ == '__main__':
    main()
