from django.contrib.sites.shortcuts import get_current_site
from django.middleware.common import CommonMiddleware
from django import http
from typing import Optional
from .models import RootFile


class PCartCommonMiddleware(CommonMiddleware):
    """ This middleware modifies the standard CommonMiddleware for
    changing the default redirect status from 301 to 302.
    """
    response_redirect_class = http.HttpResponseRedirect


class RootFileRouterMiddleware(object):
    """ Router middleware for root files.
    """
    def __init__(self, get_response):
        """ One-time configuration and initialization.
        """
        self.get_response = get_response

    @staticmethod
    def _get_root_file_instance(site, path: str) -> Optional[RootFile]:
        """ Looking for a file existence and returns the particular RootFile
        instance if found one.

        :param site: the Site object
        :param path: root file path
        :return: RootFile instance
        """
        from django.core.cache import cache
        cache_key = 'rootfiles-list-%s' % site.id
        root_files_route = cache.get(cache_key)

        # We're using caching for saving all necessary routes
        if root_files_route is None:
            """ Generating a dict like that:
            
            {
                '/robots.txt': 'id1',
                '/some_another_file', 'another_id',
                ...
            }
            """
            root_files_route = {
                '/%s' % k: v
                for k, v in RootFile.objects.filter(site=site, published=True).values_list('file_name', 'id')}
            cache.set(cache_key, root_files_route, 3600)

        # Looking for file path existence in the routes list
        _id = root_files_route.get(path)
        if _id is not None:
            try:
                result = RootFile.objects.get(pk=_id)
                return result
            except RootFile.DoesNotExist:
                # Return None if the file is not exist
                pass

    def __call__(self, request):
        """ Code to be executed for each request before
        the view (and later middleware) is called.
        """
        site = get_current_site(request)
        root_file = self._get_root_file_instance(site, request.get_full_path())
        if root_file is not None:
            response = root_file.view(request)
            return response

        response = self.get_response(request)
        return response
