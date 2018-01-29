#!/usr/bin/env python
# -*- coding: utf-8  -*-

import re

REGEX_DIGIT = re.compile(r"\d+")

REGEX_INNER_SQUARE_BRACKETS = re.compile(r"\[(.*)\]")

REGEX_INNER_BRACES = re.compile(r"\{(.*)\}")

REGEX_INNER_PARENTHESE = re.compile(r"\((.*)\)")

REGEX_INNER_ANGLE_BRACKETS = re.compile(r"\<(.*)\>")