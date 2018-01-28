from .__meta__ import version_info, __version__

from .widget import HelloWorld, Slider

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'jupyter-widget-d3-slider',
        'require': 'jupyter-widget-d3-slider/extension'
    }]
