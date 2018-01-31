"""Tests for user client API"""
# pylint: disable=unused-argument
import json

import pytest


def test_list_users(api_client):
    """Test list users for correct request"""
    resp = api_client.users.list()
    assert resp.status_code == 200
    assert resp.json() == [{
        "id": 39,
        "username": "01BQRHXRDP1J63DF8QQB6B8TKA",
        "profile": {
            "name": "name",
            "image": "test1.jpg",
            "image_small": "test2.jpg",
            "image_medium": "test3.jpg"
        }
    }]


def test_create_user(api_client):
    """Test create user"""
    resp = api_client.users.create(
        email='user@example.com',
        profile=dict(
            name="my name",
            image="image1.jpg",
            image_small="image2.jpg",
            image_medium="image3.jpg",
            email_optin=True
        )
    )
    assert json.loads(resp.request.body) == {
        "email": "user@example.com",
        "profile": {
            "name": "my name",
            "image": "image1.jpg",
            "image_small": "image2.jpg",
            "image_medium": "image3.jpg",
            "email_optin": True,
        }
    }
    assert resp.status_code == 201
    assert resp.json() == {
        "id": 127,
        "username": "01C53XW2FCHQE1PAPHZMH036HF",
        "profile": {
            "name": "my name",
            "image": "image1.jpg",
            "image_small": "image2.jpg",
            "image_medium": "image3.jpg"
        }
    }


def test_create_user_no_profile_props(api_client):
    """Updating with no args raises error"""
    with pytest.raises(AttributeError) as err:
        api_client.users.create()
    assert str(err.value) == "No fields provided to create"


def test_create_user_invalid_profile_props(api_client):
    """Updating with invalid arg raises error"""
    with pytest.raises(AttributeError) as err:
        api_client.users.create(profile=dict(bad_arg=2))
    assert str(err.value) == "Profile attribute bad_arg is not supported"


def test_get_user(api_client, use_betamax):
    """Test get user"""
    resp = api_client.users.get("01BRMT958T3DW02ZAYDG7N6QCB")
    assert resp.status_code == 200
    assert resp.json() == {
        "id": 41,
        "username": "01BRMT958T3DW02ZAYDG7N6QCB",
        "profile": {
            "name": "my name",
            "image": "image1.jpg",
            "image_small": "image4.jpg",
            "image_medium": "image3.jpg",
        }
    }


def test_update_user(api_client):
    """Test patch user"""
    resp = api_client.users.update("01BRMT958T3DW02ZAYDG7N6QCB", profile=dict(image_small="image4.jpg"))
    assert json.loads(resp.request.body) == {
        "profile": {
            "image_small": "image4.jpg",
        }
    }
    assert resp.status_code == 200
    assert resp.json() == {
        "id": 41,
        "username": "01BRMT958T3DW02ZAYDG7N6QCB",
        "profile": {
            "name": "my name",
            "image": "image1.jpg",
            "image_small": "image4.jpg",
            "image_medium": "image3.jpg"
        }
    }


def test_update_user_no_profile_props(api_client):
    """Updating with no args raises error"""
    with pytest.raises(AttributeError) as err:
        api_client.users.update("01BRMT958T3DW02ZAYDG7N6QCB")
    assert str(err.value) == "No fields provided to update"


def test_update_user_invalid_profile_props(api_client):
    """Updating with invalid arg raises error"""
    with pytest.raises(AttributeError) as err:
        api_client.users.update("01BRMT958T3DW02ZAYDG7N6QCB", profile=dict(bad_arg=2))
    assert str(err.value) == "Profile attribute bad_arg is not supported"
