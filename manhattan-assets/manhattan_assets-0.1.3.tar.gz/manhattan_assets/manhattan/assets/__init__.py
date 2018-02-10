from .assets import *
from . import fields
from . import makers
from . import static
from . import transforms
from . import validators


from manhattan.assets import Asset
from manhattan.assets.views.transform import transform_chains
from manhattan.assets.views.upload import upload_chains


__all__ = ['Assets']


class Assets:
    """
    The `Assets` class provides the initialization code for the package.
    """

    def __init__(
        self,
        app,
        root,
        backend,
        settings=None,
        upload_path='/upload-asset',
        transform_path='/transform-asset'
        ):
        self._app = app

        # Configure the URL root for assets
        Asset._asset_root = root

        # Set up the asset manager
        self._app.asset_mgr = backend.AssetMgr(**(settings or {}))

        # Set up views for managing assets

        # Upload
        self._app.add_url_rule(
            upload_path,
            endpoint='upload_asset',
            view_func=upload_chains.copy().flask_view(),
            methods=['POST']
            )

        # Transform
        self._app.add_url_rule(
            transform_path,
            endpoint='transform_asset',
            view_func=transform_chains.copy().flask_view(),
            methods=['POST']
            )
