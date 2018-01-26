"""
Reads shapefiles, feature classes, table into a spatial dataframe
"""
from __future__ import print_function
from __future__ import division
import os
import six
import copy
import logging
import tempfile
from warnings import warn
import numpy as np
import pandas as pd
from six import iteritems, integer_types
from datetime import datetime
from ..utils import NUMERIC_TYPES, STRING_TYPES, DATETIME_TYPES
from ..utils import sanitize_field_name
from .....geometry import _types
try:
    import arcpy
    from arcpy import da
    HASARCPY = True
except:
    HASARCPY = False
try:
    import shapefile
    HASPYSHP = True
except:
    HASPYSHP = False
_log=logging.getLogger(__name__)

def _pyshp_to_shapefile(df, out_path, out_name):
    """
    Saves a SpatialDataFrame to a Shapefile using pyshp

    :Parameters:
     :df: spatail dataframe
     :out_path: folder location to save the data
     :out_name: name of the shapefile
    :Output:
     path to the shapefile or None if pyshp isn't installed or
     spatial dataframe does not have a geometry column.
    """
    from .....geometry._types import Geometry
    if HASPYSHP:
        GEOMTYPELOOKUP = {
            "Polygon" : shapefile.POLYGON,
            "Point" : shapefile.POINT,
            "Polyline" : shapefile.POLYLINE,
            'null' : shapefile.NULL
        }
        if os.path.isdir(out_path) == False:
            os.makedirs(out_path)
        out_fc = os.path.join(out_path, out_name)
        if out_fc.lower().endswith('.shp') == False:
            out_fc += ".shp"
        geom_field = df.geometry.name
        if geom_field is None:
            return
        geom_type = "null"
        idx = df[geom_field].first_valid_index()
        if idx > -1:
            geom_type = df.loc[idx][geom_field].type
        shpfile = shapefile.Writer(GEOMTYPELOOKUP[geom_type])
        shpfile.autoBalance = 1
        for c in df.columns:
            idx = df[c].first_valid_index()
            if idx > -1:
                if isinstance(df[c].loc[idx],
                              Geometry):
                    geom_field = (c, "GEOMETRY")
                else:
                    if isinstance(df[c].loc[idx], six.string_types):
                        shpfile.field(name=c, size=255)
                    elif isinstance(df[c].loc[idx], six.integer_types):
                        shpfile.field(name=c, fieldType="N", size=5)
                    elif isinstance(df[c].loc[idx], (np.int, np.int32, np.int64)):
                        shpfile.field(name=c, fieldType="N", size=10)
                    elif isinstance(df[c].loc[idx], (np.float, np.float64)):
                        shpfile.field(name=c, fieldType="F", size=19, decimal=11)
                    elif isinstance(df[c].loc[idx], (datetime, np.datetime64)):
                        shpfile.field(name=c, fieldType="D", size=8)
                    elif isinstance(df[c].loc[idx], (bool, np.bool)):
                        shpfile.field(name=c, fieldType="L", size=1)
            del c
            del idx
        for idx, row in df.iterrows():
            geom = row[df.geometry.name]
            if geom.type == "Polygon":
                shpfile.poly(geom['rings'])
            elif geom.type == "Polyline":
                shpfile.line(geom['path'])
            elif geom.type == "Point":
                shpfile.point(x=geom.x, y=geom.y)
            else:
                shpfile.null()
            shpfile.record(*row.tolist()[:-1])
            del idx
            del row
            del geom
        shpfile.save(out_fc)
        del shpfile
        return out_fc
    return None
#--------------------------------------------------------------------------
def from_featureclass(filename, **kwargs):
    """
    Returns a GeoDataFrame from a feature class.
    Inputs:
     filename: full path to the feature class
    Optional Parameters:
     sql_clause: sql clause to parse data down
     where_clause: where statement
     sr: spatial reference object
     fields: list of fields to extract from the table
    """
    from .. import SpatialDataFrame
    if HASARCPY:
        sql_clause = kwargs.pop('sql_clause', (None,None))
        where_clause = kwargs.pop('where_clause', None)
        sr = kwargs.pop('sr', None)
        fields = kwargs.pop('fields', None)
        desc = arcpy.Describe(filename)
        if not fields:
            fields = [field.name for field in arcpy.ListFields(filename) \
                      if field.type not in ['Geometry']]

            if hasattr(desc, 'areaFieldName'):
                afn = desc.areaFieldName
                if afn in fields:
                    fields.remove(afn)
            if hasattr(desc, 'lengthFieldName'):
                lfn = desc.lengthFieldName
                if lfn in fields:
                    fields.remove(lfn)
        geom_fields = fields + ['SHAPE@']
        flds = fields + ['SHAPE']
        vals = []
        geoms = []
        geom_idx = flds.index('SHAPE')
        shape_type = desc.shapeType
        default_polygon = _types.Geometry(arcpy.Polygon(arcpy.Array([arcpy.Point(0,0)]* 3)))
        default_polyline = _types.Geometry(arcpy.Polyline(arcpy.Array([arcpy.Point(0,0)]* 2)))
        default_point = _types.Geometry(arcpy.PointGeometry(arcpy.Point()))
        default_multipoint = _types.Geometry(arcpy.Multipoint(arcpy.Array([arcpy.Point()])))
        with arcpy.da.SearchCursor(filename,
                                   field_names=geom_fields,
                                   where_clause=where_clause,
                                   sql_clause=sql_clause,
                                   spatial_reference=sr) as rows:

            for row in rows:
                row = list(row)
                g = _types.Geometry(row.pop(geom_idx))
                if g == {}:
                    if shape_type.lower() == 'point':
                        g = default_point
                    elif shape_type.lower() == 'polygon':
                        g = default_polygon
                    elif shape_type.lower() == 'polyline':
                        g = default_point
                    elif shape_type.lower() == 'multipoint':
                        g = default_multipoint
                geoms.append(g)
                vals.append(row)
                del row
            del rows
        df = pd.DataFrame(data=vals, columns=fields)
        sdf = SpatialDataFrame(data=df, geometry=geoms)
        sdf.reset_index(drop=True, inplace=True)
        del df
        if sdf.sr is None:
            if sr is not None:
                sdf.sr = sr
            else:
                sdf.sr = sdf.geometry[sdf.geometry.first_valid_index()].spatialReference
        return sdf
    elif HASARCPY == False and \
         HASPYSHP == True and\
         filename.lower().find('.shp') > -1:
        geoms = []
        records = []
        reader = shapefile.Reader(filename)
        fields = [field[0] for field in reader.fields if field[0] != 'DeletionFlag']
        for r in reader.shapeRecords():
            atr = dict(zip(fields, r.record))
            g = r.shape.__geo_interface__
            g = _geojson_to_esrijson(g)
            geom = _types.Geometry(g)
            atr['SHAPE'] = geom
            records.append(atr)
            del atr
            del r, g
            del geom
        sdf = SpatialDataFrame(records)
        sdf.set_geometry(col='SHAPE')
        sdf.reset_index(inplace=True)
        return sdf
    return
#--------------------------------------------------------------------------
def to_featureclass(df, out_name, out_location=None,
                    overwrite=True, out_sr=None,
                    skip_invalid=True):
    """
    converts a SpatialDataFrame to a feature class

    Parameters:
     :out_location: path to the workspace
     :out_name: name of the output feature class table
     :overwrite: True, the data will be erased then replaced, else the
      table will be appended to an existing table.
     :out_sr: if set, the data will try to reproject itself
     :skip_invalid: if True, the cursor object will not raise an error on
      insertion of invalid data, if False, the first occurence of invalid
      data will raise an exception.
    Returns:
     path to the feature class
    """
    fc = None
    if HASARCPY:
        cols = []
        dt_idx = []
        invalid_rows = []
        idx = 0
        max_length = None
        if out_location:
            if os.path.isdir(out_location) == False and \
               out_location.lower().endswith('.gdb'):
                out_location = arcpy.CreateFileGDB_management(out_folder_path=os.path.dirname(out_location),
                                                             out_name=os.path.basename(out_location))[0]
            elif os.path.isdir(out_location) == False and \
                 out_name.lower().endswith('.shp'):
                os.makedirs(out_location)
            elif os.path.isfile(out_location) == False and \
                 out_location.lower().endswith('.sde'):
                raise ValueError("The sde connection file does not exist")
        else:
            if out_name.lower().endswith('.shp'):
                out_location = tempfile.gettempdir()
            elif HASARCPY:
                out_location = arcpy.env.scratchGDB
            else:
                out_location = tempfile.gettempdir()
                out_name = out_name + ".shp"
        fc = os.path.join(out_location, out_name)
        df = df.copy() # create a copy so we don't modify the source data.
        if out_name.lower().endswith('.shp'):
            max_length = 10
        for col in df.columns:
            if col.lower() != 'shape':
                if df[col].dtype.type in NUMERIC_TYPES:
                    df[col] = df[col].fillna(0)
                elif df[col].dtype.type in DATETIME_TYPES:
                    dt_idx.append(idx)
                else:
                    df.loc[df[col].isnull(), col] = ""
                idx += 1
                col = sanitize_field_name(s=col,
                                          length=max_length)
            cols.append(col)
            del col
        df.columns = cols

        if arcpy.Exists(fc) and \
           overwrite:
            arcpy.Delete_management(fc)
        if arcpy.Exists(fc) ==  False:
            sr = None
            if df.sr is None:
                sr = df['SHAPE'].loc[df['SHAPE'].first_valid_index()].spatial_reference
                if isinstance(sr, dict) and \
                   'wkid' in sr:
                    sr = arcpy.SpatialReference(sr['wkid'])
                elif isinstance(sr, arcpy.SpatialReference):
                    sr = sr
                else:
                    sr = None
            else:
                sr = df.sr.as_arcpy
            fc = arcpy.CreateFeatureclass_management(out_path=out_location,
                                                     out_name=out_name,
                                                     geometry_type=df.geometry_type.upper(),
                                                     spatial_reference=sr)[0]
        desc = arcpy.Describe(fc)
        oidField = desc.oidFieldName
        col_insert = copy.copy(df.columns).tolist()
        if hasattr(desc, 'areaFieldName'):
            af = desc.areaFieldName.lower()
        else:
            af = None
        if hasattr(desc, 'lengthFieldName'):
            lf = desc.lengthFieldName.lower()
        else:
            lf = None
        col_insert = [f for f in col_insert if f.lower() not in ['oid', 'objectid', 'fid', desc.oidFieldName.lower(), af, lf]]
        df_cols = col_insert.copy()
        lower_col_names = [f.lower() for f in col_insert if f.lower() not in ['oid', 'objectid', 'fid']]
        idx_shp = None

        if oidField.lower() in lower_col_names:
            val = col_insert.pop(lower_col_names.index(oidField.lower()))
            del df[val]
            col_insert = copy.copy(df.columns).tolist()
            lower_col_names = [f.lower() for f in col_insert]
        if hasattr(desc, "areaFieldName") and \
           desc.areaFieldName.lower() in lower_col_names:
            val = col_insert.pop(lower_col_names.index(desc.areaFieldName.lower()))
            del df[val]
            col_insert = copy.copy(df.columns).tolist()
            lower_col_names = [f.lower() for f in col_insert]
        elif 'shape_area' in lower_col_names:
            val = col_insert.pop(lower_col_names.index('shape_area'))
            del df[val]
            col_insert = copy.copy(df.columns).tolist()
            lower_col_names = [f.lower() for f in col_insert]
        if hasattr(desc, "lengthFieldName") and \
           desc.lengthFieldName.lower() in lower_col_names:
            val = col_insert.pop(lower_col_names.index(desc.lengthFieldName.lower()))
            del df[val]
            col_insert = copy.copy(df.columns).tolist()
            lower_col_names = [f.lower() for f in col_insert]
        elif 'shape_length' in lower_col_names:
            val = col_insert.pop(lower_col_names.index('shape_length'))
            del df[val]
            col_insert = copy.copy(df.columns).tolist()
            lower_col_names = [f.lower() for f in col_insert]
        if "SHAPE" in df.columns:
            idx_shp = col_insert.index("SHAPE")
            col_insert[idx_shp] = "SHAPE@"
        existing_fields = [field.name.lower() for field in arcpy.ListFields(fc)]
        for col in col_insert:
            if col.lower() != 'shape@' and \
               col.lower() != 'shape' and \
               col.lower() not in existing_fields:
                try:
                    t = _infer_type(df, col)
                    if t == "TEXT" and out_name.lower().endswith('.shp') == False:
                        l = int(df[col].str.len().max()) or 0
                        if l < 255:
                            l = 255
                        arcpy.AddField_management(in_table=fc, field_name=col,
                                                  field_length=l,
                                                  field_type=_infer_type(df, col))
                    else:
                        arcpy.AddField_management(in_table=fc, field_name=col,
                                              field_type=t)
                except:
                    print('col %s' % col)
        icur = da.InsertCursor(fc, col_insert)
        for index, row in df[df_cols].iterrows():
            if len(dt_idx) > 0:
                row = row.tolist()
                for i in dt_idx:
                    row[i] = row[i].to_pydatetime()
                    del i
                try:
                    if idx_shp:
                        row[idx_shp] = row[idx_shp].as_arcpy
                    icur.insertRow(row)
                except:
                    invalid_rows.append(index)
                    if skip_invalid == False:
                        raise Exception("Invalid row detected at index: %s" % index)
            else:
                try:
                    row = row.tolist()
                    if isinstance(idx_shp, int):
                        row[idx_shp] = row[idx_shp].as_arcpy
                    icur.insertRow(row)
                except:
                    invalid_rows.append(index)
                    if skip_invalid == False:
                        raise Exception("Invalid row detected at index: %s" % index)

            del row
        del icur
        if len(invalid_rows) > 0:
            t = ",".join([str(r) for r in invalid_rows])
            _log.warning('The following rows could not be written to the table: %s' % t)
    elif HASARCPY == False and \
         HASPYSHP:
        return _pyshp_to_shapefile(df=df,
                                   out_path=out_location,
                                   out_name=out_name)
    else:
        raise Exception("Cannot Export the data without ArcPy or PyShp modules. "+ \
                        "Please install them and try again.")
    return fc
#--------------------------------------------------------------------------
def _infer_type(df, col):
    """
    internal function used to get the datatypes for the feature class if
    the dataframe's _field_reference is NULL or there is a column that does
    not have a dtype assigned to it.

    Input:
     dataframe - spatialdataframe object
    Ouput:
      field type name
    """
    nn = df[col].notnull()
    nn = list(df[nn].index)
    if len(nn) > 0:
        val = df[col][nn[0]]
        if isinstance(val, six.string_types):
            return "TEXT"
        elif isinstance(val, tuple(list(six.integer_types) + [np.int32])):
            return "INTEGER"
        elif isinstance(val, (float, np.int64 )):
            return "FLOAT"
        elif isinstance(val, datetime):
            return "DATE"
    return "TEXT"
#--------------------------------------------------------------------------
def _geojson_to_esrijson(geojson):
    """converts the geojson spec to esri json spec"""
    if geojson['type'] in ['Polygon', 'MultiPolygon']:
        return {
            'rings' : geojson['coordinates']
        }
    elif geojson['type'] == "Point":
        return {
            "x" : geojson['coordinates'][0],
            "y" : geojson['coordinates'][1]
        }
    elif geojson['type'] == "MultiPoint":
        return {
            "points" : geojson['coordinates'],
        }
    elif geojson['type'] in ['LineString', 'MultiLineString']:
        return {
            "paths" : geojson['coordinates'],
        }
    return geojson
#--------------------------------------------------------------------------
def _geometry_to_geojson(geom):
    """converts the esri json spec to geojson"""
    if 'rings' in geom and \
       len(geom['rings']) == 1:
        return {
            'type' : "Polygon",
            "coordinates" : geom['rings']
        }
    elif 'rings' in geom and \
       len(geom['rings']) > 1:
        return {
            'type' : "MultiPolygon",
            "coordinates" : geom['rings']
        }
    elif geom['type'] == "Point":
        return {
            "coordinates" : [geom['x'], geom['y']],
            "type" : "Point"
        }
    elif geom['type'] == "MultiPoint":
        return {
            "coordinates" : geom['points'],
            'type' : "MultiPoint"
        }
    elif geom['type'].lower() == "polyline" and \
         len(geom['paths']) <= 1:
        return {
            "coordinates" : geom['paths'],
            'type' : "LineString"
        }
    elif geom['type'].lower() == "polyline" and \
         len(geom['paths']) > 1:
        return {
            "coordinates" : geom['paths'],
            'type' : "MultiLineString"
        }
    return geom
