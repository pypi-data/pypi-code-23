# -*- coding: utf8 -*-
"""PyTistory CLI 기능 구현하는 모듈입니다.
"""
from . import PyTistory

def main():
    """PyTistory CLI를 시작합니다.
    """
    pytistory = PyTistory()
    pytistory.configure()
    print(pytistory.blog.info())
