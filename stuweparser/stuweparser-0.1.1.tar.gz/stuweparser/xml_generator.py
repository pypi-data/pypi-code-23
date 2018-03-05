#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
xml_generator.py provides functionality to create xml files with the menues
offered by the `Studierendenwerk Tübingen-Hohenheim <https://www.my-stuwe.de/>`_
"""

import xml.etree.cElementTree as ET


def generate_xml(menues, out_file, current_day=None, current_date=None):
    """
    writes menues to an XML file

    - **parameters**, **types**, **return** and **return types**::
        :param menues: a list of menues
        :type menues: list of collections.namedtuple
        :param out_file: path where the XML file should be stored
        :type out_file: string
        :param current_day: a string of the current day
        :type current_day: string
        :param current_date: a string of the current date
        :type current_date: string
    """
    root = ET.Element("mensa")

    if current_day is not None:
        ET.SubElement(root, "day").text = current_day

    if current_date is not None:
        ET.SubElement(root, "date").text = current_date

    for menue in menues:
        xml_menue = ET.SubElement(root, "menue")

        food = menue.food.rstrip('\r\n').split('\n')
        food = [y for y in [x.lstrip() for x in food] if y != '']

        ET.SubElement(xml_menue, "name").text = menue.name
        ET.SubElement(xml_menue, "food").text = ''.join(food)
        ET.SubElement(xml_menue, "studentPrice").text = menue.student_price
        ET.SubElement(xml_menue, "guestPrice").text = menue.guest_price

    tree = ET.ElementTree(root)

    tree.write(out_file)
