# coding=utf-8
"""
Manages TTS utilities
"""
import typing
from pathlib import Path

import gtts

import elib.custom_logging
import elib.path
from elib import LOGGER


def text_to_speech(text: str, file_path: typing.Union[str, Path], overwrite: bool = False) -> Path:
    """
    Creates MP3 file from text

    Args:
        text: text to encode
        file_path: path to MP3 file
        overwrite: whether or not to overwrite existing file

    Returns: path to saved MP3

    """
    LOGGER.debug(f'{text}\n->{file_path}')
    file_path = elib.path.ensure_path(file_path, must_exist=False)
    if file_path.exists() and not overwrite:
        LOGGER.error(f'"{file_path}" already exists')
        raise FileExistsError(file_path)
    LOGGER.debug('encoding text')
    tts = gtts.gTTS(text=text, lang='en', slow=False)
    LOGGER.debug('saving MP3 file')
    tts.save(str(file_path))
    return file_path
