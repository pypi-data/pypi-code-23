#!/bin/python

from setuptools import setup

setup(  name        = "roomai",
        version     = "0.1.14",
        description = "A toolkit for developing and comparing imperfect information game bots",
        url         = "https://github.com/roomai/RoomAI",
        author      = "algorithmdog",
        author_email= "lili1987mail@gmail.com",
        license     = "MIT",
        packages    = ["models","roomai","roomai.kuhn","roomai.common","roomai.texas","roomai.fivecardstud","roomai.sevenking","roomai.bridge"],
        zip_safe    = False)
