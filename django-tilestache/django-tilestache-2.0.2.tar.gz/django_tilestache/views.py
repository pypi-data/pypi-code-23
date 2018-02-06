# coding: utf-8
import TileStache
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.http import HttpResponse
from django_tilestache.configuration import (
    get_config,
    get_tilestache_config,
)


class TileStacheConfiguration(APIView):

    """
    View that outputs the current tilestache
    configuration
    """

    def get(self, request, format='json'):

        """Returns the configuration"""
        return Response(get_config())


class TileStacheTile(APIView):
    """
    renders tilestache tiles
    """
    def get(self, request, layer_name, z, x, y, extension):
        """
        Fetch tiles with tilestache.
        """
        try:
            extension = extension.upper()
            config = get_tilestache_config()
            path_info = "%s/%s/%s/%s.%s" % (layer_name, z, x, y, extension)
            coord, extension = TileStache.splitPathInfo(path_info)[1:]
            try:
                tilestache_layer = config.layers[layer_name]
            except:
                return Response({'status': 'layer not found'}, status=status.HTTP_404_NOT_FOUND)

            status_code, headers, content = tilestache_layer.getTileResponse(coord, extension)
            mimetype = headers.get('Content-Type')
            if len(content) == 0:
                status_code = 404

            response = HttpResponse(
                content,
                **{
                    'content_type': mimetype,
                    'status': status_code
                }
            )
            if hasattr(tilestache_layer, 'allowed origin'):
                response['Access-Control-Allow-Origin'] = tilestache_layer.get('allowed origin')
            return response
        except Exception as ex:
            return Response(
                {
                    'status': 'error',
                    'message': ex.message
                },
                status=status.HTTP_404_NOT_FOUND
            )
