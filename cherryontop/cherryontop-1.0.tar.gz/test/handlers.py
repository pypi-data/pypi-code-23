from cherryontop import get, post
from cherryontop import CherryOnTopError
import json


@get("/foo")
def test():
    return {"a": 1}
    # return json.dumps({"a": 1})


@post("/foo")
def blam():
    return {"b": 2}
    # return json.dumps({"b": 2})


@get("/splat")
def busted():
    raise CherryOnTopError("abc", meta={1: 1, "x": "y", "foo": {1: 2}})


@get("/blam")
def foo():
    raise ValueError


class MyError(CherryOnTopError):
    status_code=409

@get('/blast')
def fhdsk():
    raise MyError("hfdjsk")


# @get("/foo")
# def x():
#     return "a"
