#!/usr/bin/env python3

"external api"
from fredhutch_batch_wrapper.client import Client

def get_client():
    "get a rest client"
    return Client()
