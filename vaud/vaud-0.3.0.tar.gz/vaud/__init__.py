from .al_audio import AlAudio
from .decoder import Decoder

__version__ = '0.3.0'


def decode(uid, url):
    return Decoder(uid).decode(url)
