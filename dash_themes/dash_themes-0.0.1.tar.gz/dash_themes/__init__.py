import os as _os
import dash as _dash
import sys as _sys
from .version import __version__
_current_path = _os.path.dirname(_os.path.abspath(__file__))

_components = _dash.development.component_loader.load_components(
    _os.path.join(_current_path, 'metadata.json'),
    'dash_themes'
)

_this_module = _sys.modules[__name__]


_js_dist = [
    {
        "relative_package_path": "bundle.js",
        "external_url": (
            "https://unpkg.com/dash-themes@{}"
            "/dash_themes/bundle.js"
        ).format(__version__),
        "namespace": "dash_themes"
    }
]

_css_dist = [
    {
        "relative_package_path": "normalize.css",
        "namespace": "dash_themes"
    },
    {
        "relative_package_path": "base.css",
        "namespace": "dash_themes"
    },
    {
        "relative_package_path": "rc-slider@6.1.2.css",
        "namespace": "dash_themes"
    },
    {
        "relative_package_path": "react-dates@12.3.0.css",
        "namespace": "dash_themes"
    },
    {
        "relative_package_path": "react-select@1.0.0-rc.3.css",
        "namespace": "dash_themes"
    },
    {
        "relative_package_path": "react-virtualized-select@3.1.0.css",
        "namespace": "dash_themes"
    },
    {
        "relative_package_path": "react-virtualized@9.9.0.css",
        "namespace": "dash_themes"
    },
    {
        "relative_package_path": "var-base.css",
        "namespace": "dash_themes"
    },
    {
        "relative_package_path": "var-rc-slider@6.1.2.css",
        "namespace": "dash_themes"
    },
    {
        "relative_package_path": "var-react-dates@12.3.0.css",
        "namespace": "dash_themes"
    },
    {
        "relative_package_path": "var-react-select@1.0.0-rc.3.css",
        "namespace": "dash_themes"
    },
    {
        "relative_package_path": "var-react-virtualized-select@3.1.0.css",
        "namespace": "dash_themes"
    },
    {
        "relative_package_path": "var-react-virtualized@9.9.0.css",
        "namespace": "dash_themes"
    },
    {
        "relative_package_path": "override-base.css",
        "namespace": "dash_themes"
    },
    {
        "relative_package_path": "override-react-dates@12.3.0.css",
        "namespace": "dash_themes"
    },
    {
        "relative_package_path": "override-react-select@1.0.0-rc.3.css",
        "namespace": "dash_themes"
    },
    {
        "relative_package_path": "override-react-virtualized-select@3.1.0.css",
        "namespace": "dash_themes"
    },
    {
        "relative_package_path": "editor.css",
        "namespace": "dash_themes"
    },
]


for _component in _components:
    setattr(_this_module, _component.__name__, _component)
    setattr(_component, '_js_dist', _js_dist)
    setattr(_component, '_css_dist', _css_dist)
