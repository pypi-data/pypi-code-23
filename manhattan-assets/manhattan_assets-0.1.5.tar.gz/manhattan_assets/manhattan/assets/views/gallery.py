"""
Generic gallery chain.

: `gallery_field`
    The field against the document that stores the gallery of assets (required).

: `projection`
    The projection used when requesting the document from the database (defaults
    to None which means the detault projection for the frame class will be
    used).

    NOTE: The `gallery_field` must be one of the projected fields otherwise the
    gallery will always appear to be empty.

: `validators`
    A list of validators (see manhattan.assets.validators) that will be used to
    validate assets within to the gallery (defaults to None, as in no
    validation).

"""

import json

import flask
from manhattan.assets import Asset
from manhattan.chains import Chain, ChainMgr
from manhattan.forms import BaseForm
from manhattan.nav import Nav, NavItem
from werkzeug.datastructures import MultiDict

from manhattan.manage.views import (
    factories as manage_factories,
    utils as manage_utils
)

__all__ = ['gallery_chains']


# Define the chains
gallery_chains = ChainMgr()

# GET
gallery_chains['get'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'get_assets',
    'decorate',
    'render_template'
    ])

# POST
gallery_chains['post'] = Chain([
    'config',
    'authenticate',
    'get_document',
    'get_assets',
    'validate',
    [
        [
            'store_assets',
            'redirect'
        ],
        [
            'decorate',
            'render_template'
        ]
    ]
])


# Define the links
gallery_chains.set_link(manage_factories.config(
    gallery_field=None,
    gallery_validators=None
    ))
gallery_chains.set_link(manage_factories.authenticate())
gallery_chains.set_link(manage_factories.get_document())
gallery_chains.set_link(manage_factories.render_template('gallery.html'))
gallery_chains.set_link(manage_factories.redirect('view', include_id=True))

@gallery_chains.link
def decorate(state):
    """
    Add decor information to the state (see `utils.base_decor` for further
    details on what information the `decor` dictionary consists of).

    This link adds a `decor` key to the state.
    """
    document = state[state.manage_config.var_name]
    state.decor = manage_utils.base_decor(
        state.manage_config,
        state.view_type,
        document
    )

    # Title
    state.decor['title'] = state.manage_config.titleize(document)

    # Breadcrumbs
    if Nav.exists(state.manage_config.get_endpoint('list')):
        state.decor['breadcrumbs'].add(
            manage_utils.create_breadcrumb(state.manage_config, 'list')
        )
    if Nav.exists(state.manage_config.get_endpoint('view')):
        state.decor['breadcrumbs'].add(
            manage_utils.create_breadcrumb(
                state.manage_config,
                'view',
                document
            )
        )
    state.decor['breadcrumbs'].add(NavItem('Gallery'))

@gallery_chains.link
def get_assets(state):
    """
    Get the asset information for the gallery from the document (GET) or the
    request (POST).

    This link adds `assets` to the state which contains the list of assets to
    be stored against the gallery field, and `assets_json_type` which is a used
    in the template to provide the frontend JS with a serialzied version of the
    assets.
    """
    document = state[state.manage_config.var_name]

    # Get the existing assets
    assets = []
    assets_table = {}
    for asset in (getattr(document, state.gallery_field) or []):
        if not isinstance(asset, Asset):
            asset = Asset(asset)
        assets.append(asset)
        assets_table[asset.key] = asset

    # Get the list of updated assets
    if flask.request.method == 'POST':
        # Merge exisitng with the updated assets
        assets = []
        updated_assets = json.loads(flask.request.form.get('assets'))

        for asset in updated_assets:
            if not isinstance(asset, Asset):
                asset = Asset(asset)

            if asset.key in assets_table:
                existing_asset = assets_table[asset.key]
                existing_asset.user_meta.update(asset.user_meta)
                asset = existing_asset

            else:
                # Find the temporary asset
                asset = flask.current_app.asset_mgr.get_temporary_by_key(
                    asset.key
                )

            if asset:
                assets.append(asset)

    state.assets = assets
    state.assets_json_type = [a.to_json_type() for a in state.assets]

@gallery_chains.link
def validate(state):
    """
    Validate the gallery of assets.

    If there's an error against one or more of the assets in the gallery then
    this link will add `asset_errors` to the state. This is dictionary if
    errors with the asset `key` property as the key and the error message as
    the value.
    """

    # Check at least one validators has been specified
    if not state.gallery_validators:
        return True

    # Define a form against which we can perform the validation
    class AssetForm(BaseForm):

        asset = AssetField('Asset', validators=state.validators)

    # Validate every asset in the gallery
    asset_errors = {}
    for asset in assets:
        form = AssetForm(MultiDict({'asset': json.dumps(asset.to_json_type())}))
        if not form.validate():
            asset_errors[key] = form.errors['asset'][0]

    return len(asset_errors.keys()) == 0

@gallery_chains.link
def store_assets(state):
    """
    Convert temporary assets to permenant assets and store any other changes
    to asset information.
    """
    asset_mgr = flask.current_app.asset_mgr
    document = state[state.manage_config.var_name]

    assert state.gallery_field, 'No gallery field defined'

    # Store temporay assets as permenant assets
    if state.assets:
        for asset in state.assets:

            # Ignore any value that's not a temporary asset
            if not asset.temporary:
                continue

            # Store the asset permenantly
            flask.current_app.asset_mgr.store(asset)

            # Check if any variations are defined for the field
            if not hasattr(state.manage_config, \
                    state.gallery_field + '_variations'):
                continue

            variations = getattr(
                state.manage_config,
                state.gallery_field + '_variations'
            )

            # Generate the variations for the asset
            asset_mgr.generate_variations(asset, variations)

    # Update the database
    setattr(document, state.gallery_field, state.assets)
    document.update(state.gallery_field)
