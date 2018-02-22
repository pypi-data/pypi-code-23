"""
    pygclip.html
    ~~~~~~~~~~~~~~

    HTML-related functions.

    :copyright: © 2018 by Bryan Lee McKelvey.
    :license: MIT, see LICENSE for more details.
"""

import logging
import re
import sys
from typing import Dict, Union
import xml.etree.ElementTree as ETree

from pygclip.colors import darken_color
from pygclip.io import run_shell_command


def _create_options_text(
    style: Union[str, None],
) -> str:
    options = ['noclasses']
    if style is not None:
        options.append('style=' + style)
    return ','.join(options)


def _get_styles(node: ETree.Element) -> Dict[str, str]:
    style_text = node.attrib.get('style', '')
    styles = {}
    for pair in style_text.split(';'):
        key, value = pair.split(':')
        styles[key.strip()] = value.strip()
    return styles


def _override_styles(node: ETree.Element, overrides: Dict[str, str]) -> None:
    styles = _get_styles(node)
    styles.update(overrides)
    pairs = ['{}: {}'.format(k, v) for k, v in styles.items()]
    style_text = '; '.join(pairs)
    node.set('style', style_text)


def _modify_html(html: str) -> str:
    root = ETree.fromstring(html)
    pre = root.find('pre')
    if pre is None:
        raise ValueError("Can't find <pre> node in `pygmentize` output:\n{}".format(html))

    styles = {
        'font-family': 'monospace',
        'padding': '1em',
    }
    background = _get_styles(root).get('background')
    if background is not None:
        border_color = darken_color(background, 0.5)
        styles['background'] = background
        styles['border'] = 'solid 1px {}'.format(border_color)
    _override_styles(pre, styles)

    return ETree.tostring(root, encoding='utf-8').decode('utf-8')


def generate_html(
    lexer: Union[str, None],
    style: Union[str, None],
    path: Union[str, None],
    clipboard: bool,
) -> str:
    logger = logging.getLogger(__name__)
    opts_text = _create_options_text(style)
    cmd = ['pygmentize', '-O', opts_text, '-f', 'html']
    if lexer:
        cmd.extend(['-l', lexer])
    if path is None:
        if clipboard:
            text = run_shell_command(['pbpaste', '-Prefer', 'txt'])
            if not text.strip():
                raise ValueError('No plain-text content in clipboard.')
            html = run_shell_command(cmd, stdin=text)
        else:
            html = run_shell_command(cmd, stdin=sys.stdin.read())
    else:
        cmd.append(path)
        html = run_shell_command(cmd)

    # Remove extraneous newlines at end of code block
    html = re.sub(r'\n+(?=</pre></div>$)', '', html)

    html = _modify_html(html)

    logger.debug(html)
    return html
