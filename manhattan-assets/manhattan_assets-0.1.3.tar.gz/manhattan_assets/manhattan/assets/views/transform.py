"""
Generic transform asset chain.
"""

import json

import flask
from manhattan.assets import Asset
from manhattan.assets.transforms import *
from manhattan.assets.transforms.base import BaseTransform
from manhattan.assets.backends import exceptions
from manhattan.chains import Chain, ChainMgr

from manhattan.manage.views import factories
from manhattan.manage.views import utils

__all__ = ['transform_chains']


# Define the chains
transform_chains = ChainMgr()

# POST
transform_chains['post'] = Chain([
    'config',
    'authenticate',
    'get_asset',
    'transform_asset',
    'render_json'
])


# Define the links
transform_chains.set_link(factories.config())
transform_chains.set_link(factories.authenticate())

@transform_chains.link
def get_asset(state):
    """
    Get a temporary asset from the cache by key.

    This link adds the `asset` key to the state which contains the temporary
    asset looked up.
    """
    asset_mgr = flask.current_app.asset_mgr

    # Attempt to find the temporary asset by key
    key = flask.request.values.get('key', '')
    asset = asset_mgr.get_temporary_by_key(key)
    if not asset:
        return utils.json_fail('Asset not found')

    # Store the asset against the state
    state.asset = asset

@transform_chains.link
def transform_asset(state):
    """
    Set the base transforms for a temporary asset and update all associated
    variations.
    """
    asset_mgr = flask.current_app.asset_mgr

    # Convert the transform param from JSON to JSON type data
    transform_str = flask.request.values.get('transforms', '[]')
    try:
        json_transforms = json.loads(transform_str)
    except ValueError:
        return utils.json_fail('`transforms` is not valid JSON')

    # Convert the transforms from JSON type data to asset transforms
    base_transforms = [
        BaseTransform.from_json_type(t) for t in json_transforms]

    # Set the base transforms to the asset
    state.asset.base_transforms = json_transforms

    # Build a map of variations for each child variation
    local_transforms = {}
    full_transforms = {}
    for name, variation in state.asset.variations.items():

        # Extract the existing transforms
        local_transforms[name] = variation.local_transforms

        # Build the full transform required for the variation
        full_transforms[name] = base_transforms
        full_transforms[name] += [
            BaseTransform.from_json_type(t) for t in local_transforms[name]]

    # Regenerate the variations for the asset
    asset_mgr.generate_variations(state.asset, full_transforms)

    # Add the transform information back to each new variation
    for name in local_transforms.keys():
        state.asset.variations[name].local_transforms = local_transforms[name]

    # Update the asset in the cache
    asset_mgr.update_cache(state.asset)

@transform_chains.link
def render_json(state):
    """
    Return a successful response with the transformed `asset` included in the
    payload.
    """
    return utils.json_success({'asset': state.asset.to_json_type()})