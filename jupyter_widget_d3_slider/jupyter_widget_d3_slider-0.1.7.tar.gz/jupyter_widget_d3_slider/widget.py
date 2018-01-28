import ipywidgets as widgets
from traitlets import Unicode, Float

@widgets.register
class HelloWorld(widgets.DOMWidget):
    """An example widget."""
    _view_name = Unicode('HelloView').tag(sync=True)
    _model_name = Unicode('HelloModel').tag(sync=True)
    _view_module = Unicode('jupyter-widget-d3-slider').tag(sync=True)
    _model_module = Unicode('jupyter-widget-d3-slider').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)
    value = Unicode('Hello World!').tag(sync=True)

@widgets.register
class Slider(widgets.DOMWidget):
    """An example widget."""
    _view_name = Unicode('SliderView').tag(sync=True)
    _model_name = Unicode('SliderModel').tag(sync=True)
    _view_module = Unicode('jupyter-widget-d3-slider').tag(sync=True)
    _model_module = Unicode('jupyter-widget-d3-slider').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)
    value = Float(80.0).tag(sync=True)

