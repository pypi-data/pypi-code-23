# coding=utf-8
"""
Makes a PDF document from a source folder
"""

import shutil
import urllib.parse
from pathlib import Path

import elib

from edlm import LOGGER
from edlm.convert import Context
from edlm.external_tools import PANDOC

from ._check_for_unused_images import check_for_unused_images
from ._get_includes import get_includes
from ._get_index import get_index_file
from ._get_media_folders import get_media_folders
from ._get_settings import get_settings
from ._get_template import get_template
from ._pdf_info import add_metadata_to_pdf, skip_file
from ._preprocessor import process_latex, process_markdown
from ._temp_folder import TempDir

WIDTH_MODIFIER = 0.8

PAPER_FORMATS_WIDTH = {
    'a0': 841 * WIDTH_MODIFIER,
    'a1': 594 * WIDTH_MODIFIER,
    'a2': 420 * WIDTH_MODIFIER,
    'a3': 29 * WIDTH_MODIFIER,
    'a4': 210 * WIDTH_MODIFIER,
    'a5': 148 * WIDTH_MODIFIER,
    'a6': 105 * WIDTH_MODIFIER,
    'a7': 74 * WIDTH_MODIFIER,
}

BASE_URL = r'http://132virtualwing.org/docs/'


def _download_existing_file(ctx: Context):
    if not ctx.out_file.exists():
        ctx.info(f'trying to download {ctx.out_file.name}')
        url = BASE_URL + urllib.parse.quote(ctx.out_file.name)
        if elib.downloader.download(url, ctx.out_file):
            ctx.info('download successful')
        else:
            ctx.info('download failed')


def _set_max_image_width(ctx: Context):
    paper_size = ctx.paper_size.lower()
    if paper_size not in PAPER_FORMATS_WIDTH:
        raise ValueError(paper_size)
    ctx.image_max_width = int(PAPER_FORMATS_WIDTH[paper_size])


def _remove_artifacts():
    for item in Path('.').iterdir():
        assert isinstance(item, Path)
        if item.is_dir() and item.name.startswith('__TMP') or item.name.startswith('tex2pdf.'):
            shutil.rmtree(str(item.absolute()))


def _build_folder(ctx: Context):
    ctx.info(f'making PDF')

    with TempDir(ctx):

        get_media_folders(ctx)

        get_template(ctx)

        get_index_file(ctx)

        get_settings(ctx)

        get_includes(ctx)

        ctx.template_file = Path(ctx.temp_dir, 'template.tex').absolute()

        title = ctx.source_folder.name
        ctx.title = title

        out_folder = elib.path.ensure_dir('.', must_exist=False, create=True)
        ctx.out_folder = out_folder

        for paper_size in ctx.settings.papersize:
            ctx.paper_size = paper_size
            _set_max_image_width(ctx)

            if paper_size.lower() == 'a4' or len(ctx.settings.papersize) == 1:
                ctx.out_file = Path(out_folder, f'{title}.PDF').absolute()
            else:
                ctx.out_file = Path(out_folder, f'{title}_{paper_size}.PDF').absolute()

            _download_existing_file(ctx)

            if skip_file(ctx):
                continue

            process_markdown(ctx)

            check_for_unused_images(ctx)

            process_latex(ctx)

            ctx.source_file = Path(ctx.temp_dir, 'source.md').absolute()
            ctx.source_file.write_text(ctx.markdown_text, encoding='utf8')

            ctx.info(f'building format: {paper_size}')

            ctx.debug(f'context:\n{elib.pretty_format(ctx.__repr__())}')

            # noinspection SpellCheckingInspection
            pandoc_cmd = [
                '-s',
                '--toc',
                f'--template "{ctx.template_file}"',
                f'--listings "{ctx.source_file}"',
                f'-o "{ctx.out_file}"',
                '-V geometry:margin=1.5cm',
                '-V test',
                '-V geometry:headheight=17pt',
                '-V geometry:includehead',
                '-V geometry:includefoot',
                '-V geometry:heightrounded',
                '-V lot',
                '-V lof',
                '--pdf-engine=xelatex',
                f'-V papersize:{ctx.paper_size}',
                '-N',
            ]

            PANDOC(' '.join(pandoc_cmd))

            add_metadata_to_pdf(ctx)


def _is_source_folder(folder: Path) -> bool:
    if not folder.is_dir():
        return False
    return Path(folder, 'index.md').exists()


def make_pdf(ctx: Context, source_folder: Path):
    """
    Makes a PDF document from a source folder

    Args:
        ctx: Context
        source_folder: source folder
    """
    _remove_artifacts()

    source_folder = elib.path.ensure_dir(source_folder).absolute()

    LOGGER.info(f'analyzing folder: "{source_folder}"')

    if _is_source_folder(source_folder):
        ctx.source_folder = source_folder
        _build_folder(ctx)

    else:
        for child in source_folder.iterdir():
            if _is_source_folder(child):
                ctx.source_folder = child.absolute()
                _build_folder(ctx)
