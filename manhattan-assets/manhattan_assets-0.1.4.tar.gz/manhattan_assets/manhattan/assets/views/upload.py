"""
Generic upload asset chain.

NOTE: The generic upload chain is designed to handle a single file upload,
multiple file uploads client side should result in multiple calls to the upload
chain.
"""

import flask
from manhattan.assets.transforms.images import Fit, Output
from manhattan.assets.backends import exceptions
from manhattan.chains import Chain, ChainMgr

from manhattan.manage.views import factories
from manhattan.manage.views import utils

__all__ = ['upload_chains']


# Define the chains
upload_chains = ChainMgr()

# POST
upload_chains['post'] = Chain([
    'config',
    'authenticate',
    'store_temporary_asset',
    'render_json'
])


# Define the links
upload_chains.set_link(factories.config())
upload_chains.set_link(factories.authenticate())

@upload_chains.link
def store_temporary_asset(state):
    """
    Store the file uploaded as a temporary asset.

    The client request is expected to include a file under the parameter name of
    `file`.

    If the file is successfully stored this links adds an `asset` key to the
    state containing the `Asset` instance representing the uploaded file.

    IMPORTANT: Validation of the asset itself is the responsibility of the view
    that is storing the associated parent document, not the upload chain. The
    upload chain merely validates that a file was provided and could be stored.
    """

    # Check a file was provided
    if 'file' not in flask.request.files \
            or not flask.request.files['file'].filename:
        return utils.json_fail('No file sent')

    # Attempt to store the file
    file = flask.request.files['file']
    asset_mgr = flask.current_app.asset_mgr
    try:
        state.asset = asset_mgr.store_temporary((file.filename, file))
    except exceptions.StoreError as e:
        return utils.json_fail(str(e))

    # If the asset is an image then create a base variation
    if state.asset.type == 'image':

        # The `--base--` variation is used to allow the user to perform and
        # preview transforms against the image, a `Fit` transform is applied to
        # the image initially to restrict the size of the image and help with
        # performance.
        #
        # The `--thumb--` variation is used to provide a thumbnail view of the
        # image.
        try:
            config = flask.current_app.config
            draft_size = config.get('ASSET_DRAFT_SIZE', [600, 600])
            thumb_size = config.get('ASSET_THUMB_SIZE', [300, 300])

            draft_transforms = [
                Fit(thumb_size[0], thumb_size[1]),
                Output('jpg', 50)
                ]
            thumb_transforms = [
                Fit(draft_size[0], draft_size[1]),
                Output('jpg', 75)
                ]

            asset_mgr.generate_variations(
                state.asset,
                {
                    '--draft--': draft_transforms,
                    '--thumb--': thumb_transforms
                }
            )

            # Store the transform information against the variations
            draft_transforms = [t.to_json_type() for t in draft_transforms]
            state.asset.variations['--draft--'].local_transforms = \
                    draft_transforms

            thumb_transforms = [t.to_json_type() for t in thumb_transforms]
            state.asset.variations['--thumb--'].local_transforms = \
                    thumb_transforms

            asset_mgr.update_cache(state.asset)

        except exceptions.StoreError as e:
            return utils.json_fail(str(e))

@upload_chains.link
def render_json(state):
    """
    Return a successful response with the uploaded `asset` included in the
    payload.
    """
    return utils.json_success({'asset': state.asset.to_json_type()})