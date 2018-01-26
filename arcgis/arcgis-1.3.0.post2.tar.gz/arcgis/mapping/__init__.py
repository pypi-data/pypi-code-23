"""
The arcgis.mapping module provides components for visualizing GIS data and analysis.
This module includes WebMap and WebScene components that enable 2D and 3D
mapping and visualization in the GIS. This module also includes mapping layers like
MapImageLayer and VectorTileLayer
"""

from ._types import WebMap, WebScene, MapImageLayer, MapImageLayerManager, VectorTileLayer
from ._utils import export_map, get_layout_templates
__all__ = ['WebMap', 'WebScene', 'MapImageLayer', 'MapImageLayerManager', 'VectorTileLayer',
           'export_map', 'get_layout_templates']
