# coding: utf-8
from django.utils.translation import ugettext_lazy as _

EXTERNAL_SOURCE_TYPE = (
    (u"SHAPEFILE",_(u"Shapefile")),
    (u"GEOJSON",_(u"GeoJson")),
    (u"WFS",_(u"WFS (Web Feature Service)")),
)

EXTERNAL_SOURCE_FORMAT = (
    (u"SHP",_(u"Shapefile")),
    (u"JSON", _(u"GeoJson")),
    (u"ZIP", _(u"Zip")),
    (u"TAR.GZ", _(u"Tarball")),
    (u"REQUEST", _(u"Request HTTP"))
)

FIELD_TYPE_GEO = "GEO"
FIELD_TYPE_INT = "INT"
FIELD_TYPE_FLOAT = "FLOAT"
FIELD_TYPE_STRING = "STRING"
FIELD_TYPE_DATA = "DATA"
FIELD_TYPE_DATA_HORA = "DATA-HORA"
FIELD_TYPE_FK = "FK"

FIELD_TYPE = (
    (FIELD_TYPE_GEO, _(u"Geometria")),
    (FIELD_TYPE_INT, _(u"Inteiro")),
    (FIELD_TYPE_FLOAT, _(u"Decimal")),
    (FIELD_TYPE_STRING, _(u"Texto")),
    (FIELD_TYPE_DATA, _(u"Data")),
    (FIELD_TYPE_DATA_HORA, _(u"Data/Hora")),
    (FIELD_TYPE_FK, _(u"Chave Estrangeira"))
)

FIELD_MAPPING_ERROR_TYPE = ((_(u"MISSING_FIELD"), _(u"Campo Não Existe")),
                            (_(u"INCOMPATIBLE_TYPE"), _(u"Tipo Incompatível")),
                            (_(u"INCOMPATIBLE_SIZE"), _(u"Tamanho Incompatível"))
)
