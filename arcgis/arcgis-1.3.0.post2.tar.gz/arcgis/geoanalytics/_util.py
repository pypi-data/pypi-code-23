import json
import string
import random

import arcgis
from arcgis.gis import Layer
from arcgis.features import FeatureCollection
    
def _id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def _feature_input(self, input_layer):
    input_layer_url = ""
    if isinstance(input_layer, arcgis.gis.Item):
        if input_layer.type.lower() == 'feature service':
            input_param =  {'url': input_layer.layers[0].url}
        elif input_layer.type.lower() == 'feature collection':
            fcdict = input_layer.get_data()
            fc = FeatureCollection(fcdict['layers'][0])
            input_param =  fc.layer
        else:
            raise TypeError("item type must be feature service or feature collection")

    elif isinstance(input_layer, arcgis.features.FeatureLayerCollection):
        input_layer_url = input_layer.layers[0].url
        input_param =  {"url": input_layer_url }

    elif isinstance(input_layer, FeatureCollection):
        input_param =  input_layer.properties

    elif isinstance(input_layer, Layer):
        input_layer_url = input_layer.url
        input_param =  {"url": input_layer_url }

    elif isinstance(input_layer, dict):
        input_param =  input_layer

    elif isinstance(input_layer, str):
        input_layer_url = input_layer
        input_param =  {"url": input_layer_url }

    else:
        raise Exception("Invalid format of input layer. url string, feature service Item, feature service instance or dict supported")

    return input_param


def _set_context(params):
    out_sr = arcgis.env.out_spatial_reference
    process_sr = arcgis.env.process_spatial_reference
    out_extent = arcgis.env.analysis_extent
    output_datastore = arcgis.env.output_datastore
    
    context = {}
    set_context = False
    
    if out_sr is not None:
        context['outSR'] = {'wkid': int(out_sr)}
        set_context = True
    if out_extent is not None:
        context['extent'] = out_extent
        set_context = True
    if process_sr is not None:
        context['processSR'] = {'wkid': int(process_sr)}
        set_context = True
    if output_datastore is not None:
        context['dataStore'] = output_datastore
        set_context = True

    if set_context:
        params["context"] = json.dumps(context)



def _create_output_service(gis, output_name, output_service_name='Analysis feature service', task='GeoAnalytics'):
    ok = gis.content.is_service_name_available(output_name, 'Feature Service')
    if not ok:
        raise RuntimeError("A Feature Service by this name already exists: " + output_name)

    createParameters = {
            "currentVersion": 10.2,
            "serviceDescription": "",
            "hasVersionedData": False,
            "supportsDisconnectedEditing": False,
            "hasStaticData": True,
            "maxRecordCount": 2000,
            "supportedQueryFormats": "JSON",
            "capabilities": "Query",
            "description": "",
            "copyrightText": "",
            "allowGeometryUpdates": False,
            "syncEnabled": False,
            "editorTrackingInfo": {
                "enableEditorTracking": False,
                "enableOwnershipAccessControl": False,
                "allowOthersToUpdate": True,
                "allowOthersToDelete": True
            },
            "xssPreventionInfo": {
                "xssPreventionEnabled": True,
                "xssPreventionRule": "InputOnly",
                "xssInputRule": "rejectInvalid"
            },
            "tables": [],
            "name": output_service_name.replace(' ', '_'),
            "options": {
                "dataSourceType": "spatiotemporal"
            }
        }

    output_service = gis.content.create_service(output_name, create_params=createParameters, service_type="featureService")
    description = "Feature Service generated from running the " + task + " tool."
    item_properties = {
            "description" : description,
            "tags" : "Analysis Result, " + task,
            "snippet": output_service_name
            }
    output_service.update(item_properties)
    return output_service
    
