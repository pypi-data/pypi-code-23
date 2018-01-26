import os
from datetime import datetime, date
import time
from xml.etree import ElementTree

from flask import current_app, url_for
from flask_script import Command, Option
from manhattan.seo import BaseSEOMeta
from mongoframes import And, Q

__all__ = ['add_commands']


class GenerateSitemapXML(Command):
    """Generate a sitemap.xml file for the site"""

    def add_url(self, url_set_elm, seo_meta):
        """Add a URL element to a URL set element"""
        props = seo_meta.props

        # Check the document/view is visible to the sitemap
        if not props.sitemap_visible:
            return

        url_elm = ElementTree.SubElement(url_set_elm, 'url')

        # Location
        loc_elm = ElementTree.SubElement(url_elm, 'loc')
        loc_elm.text = props.url

        # Priority
        priority_elm = ElementTree.SubElement(url_elm, 'priority')
        priority_elm.text = str(props.sitemap_priority)

        # Change frequency
        if props.sitemap_frequency:
            changefreq_elm = ElementTree.SubElement(url_elm, 'changefreq')
            changefreq_elm.text = props.sitemap_frequency

        # Last modifed
        if props.sitemap_lastmod:
            lastmod = props.sitemap_lastmod
            lastmod_elm = ElementTree.SubElement(url_elm, 'lastmod')
            if isinstance(lastmod, (date, datetime)):
                lastmod = lastmod.strftime('%Y-%m-%d')
            lastmod_elm.text = lastmod

    def find_seo_classes(self):
        """Find all SEOMeta classes"""
        seo_classes = []
        sub_classes = BaseSEOMeta.__subclasses__()
        while len(sub_classes) > 0:
            sub_class = sub_classes.pop()
            if len(sub_class.__subclasses__()):
                sub_classes += sub_class.__subclasses__()
            seo_classes.append(sub_class)

        return seo_classes

    def run(self):

        # Create the base element
        elm = ElementTree.Element('urlset')
        elm.set('xmlns', 'http://www.sitemaps.org/schemas/sitemap/0.9')

        # Find all SEO meta classes
        seo_classes = self.find_seo_classes()

        # Add SEO meta decorated views
        for seo_cls in seo_classes:
            for seo_meta in seo_cls.decorated():
                self.add_url(elm, seo_meta)

        # Add SEO meta documents
        for seo_cls in seo_classes:
            seo_metas = seo_cls.many()
            for seo_meta in seo_metas:
                self.add_url(elm, seo_meta)

        # Write the sitemap to file
        with open('nginx_static/sitemap.xml', 'w') as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
            xml = ElementTree.tostring(elm, encoding='unicode')
            xml = xml.replace('<url>', '\n<url>')
            xml = xml.replace('</urlset>', '\n</urlset>')
            f.write(xml)


def add_commands(manager):
    """Add commands within the module to the specified command manager"""
    manager.add_command('generate-sitemap-xml', GenerateSitemapXML)
