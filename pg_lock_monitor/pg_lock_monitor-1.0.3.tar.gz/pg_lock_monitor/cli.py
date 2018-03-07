#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals
import argparse


def parse_args():
    parser = argparse.ArgumentParser(
        description="Мониторинг блокировок в PostgreSQL",
    )
    parser.add_argument("--config", "-c", type=str,
                        help="Путь к конфигурационному файлу", required=True)
    parser.add_argument("--duration", "-d", type=int,
                        help="Длительность минимально допустимой блокировки в секундах", default=0)
    return parser.parse_args()
