# coding=utf-8
from __future__ import unicode_literals

import textwrap
import unittest

from opvoeden_api import article_utils

EXAMPLE_TEXT = '''
<h2>{Jgz}</h2>

<p>{Het jgz} is onderdeel van de Jeugdgezondheidszorg. Veel {jgzs} organiseren bijeenkomsten.
Je kunt altijd bij een van {de jgzs} terecht. Neem daarvoor contact op met {het jgz} bij jou in de buurt.</p>

<p>Only specific strings between {accolades} are placeholders.</p>
'''


class TextReplaceJgz(unittest.TestCase):
    def test_default_replacements(self):
        expected = textwrap.dedent('''
            <h2>Centrum voor Jeugd en Gezin (CJG)</h2>

            <p>Het Centrum voor Jeugd en Gezin (CJG) is onderdeel van de Jeugdgezondheidszorg. Veel CJG’s organiseren bijeenkomsten.
            Je kunt altijd bij een van de CJG’s terecht. Neem daarvoor contact op met het Centrum voor Jeugd en Gezin (CJG) bij jou in de buurt.</p>

            <p>Only specific strings between {accolades} are placeholders.</p>
            ''')
        self.assertEqual(expected, article_utils.replace_jgz(EXAMPLE_TEXT))

    def test_substitutions_override(self):
        expected = textwrap.dedent('''
            <h2>CJG</h2>

            <p>Het CJG is onderdeel van de Jeugdgezondheidszorg. Veel centra organiseren bijeenkomsten.
            Je kunt altijd bij een van de centra terecht. Neem daarvoor contact op met het CJG bij jou in de buurt.</p>

            <p>Only specific strings between {accolades} are placeholders.</p>
            ''')
        self.assertEqual(expected, article_utils.replace_jgz(EXAMPLE_TEXT, substitutions={
            'Jgz': 'CJG',
            'het jgz': 'het CJG',
            'Het jgz': 'Het CJG',
            'jgzs': 'centra',
            'de jgzs': 'de centra'
        }))


class TestReplaceLinks(unittest.TestCase):
    def test_replace_links(self):
        external_id_to_href = {
            '1': '/example/',
            '2': '/example/more/'
        }

        def get_link_tag(external_id, link_text):
            """
            Get the url for an article and return an HTML snippet
            that links to this url with the given text.

            """
            href = external_id_to_href.get(external_id, None)
            if href:
                return '<a href="{}">{}</a>'.format(href, link_text)

        example_text = textwrap.dedent('''
            <p>This is an [a=1,example], do you need [a=2,more information]?</p>
            <p>The next link is [a=3,not replaced]</p>
            ''')

        expected = textwrap.dedent('''
            <p>This is an <a href="/example/">example</a>, do you need <a href="/example/more/">more information</a>?</p>
            <p>The next link is [a=3,not replaced]</p>
            ''')

        self.assertEqual(expected, article_utils.replace_links(example_text, get_link_tag))


class TestReplaceImages(unittest.TestCase):
    def test_replace_images(self):
        image_id_to_src = {
            '1': '/media/1.gif',
            '2': '/media/2.gif'
        }

        def get_image_tag(image_id):
            src = image_id_to_src.get(image_id, None)
            if src:
                return '<img src="{}">'.format(src)

        example_text = textwrap.dedent('''
            <p>Look at this image:
                [img=1]</p>

            <p>[img=2] is the best image</p>

            <p>[img=3] is not replaced</p>
            ''')

        expected = textwrap.dedent('''
            <p>Look at this image:
                <img src="/media/1.gif"></p>

            <p><img src="/media/2.gif"> is the best image</p>

            <p>[img=3] is not replaced</p>
            ''')

        self.assertEqual(expected, article_utils.replace_images(example_text, get_image_tag))


class TestReplaceVideos(unittest.TestCase):
    def test_replace_videos_with_links(self):

        def get_video_link(video_id, embed_url, external_url):
            """Create an iframe to embed the video"""
            return '<iframe src="{}">'.format(embed_url)

        example_text = '<p>[youtube=1-A-z_]</p>'

        expected = '<p><iframe src="//www.youtube-nocookie.com/embed/1-A-z_?rel=0"></p>'

        self.assertEqual(expected, article_utils.replace_videos(example_text, get_video_link))

    def test_replace_videos_with_embeds(self):

        def get_video_embed(video_id, embed_url, external_url):
            """Create a link to the video player"""
            return '<a href="{}" target="_blank">Watch the video</a>'.format(
                external_url)

        example_text = '<p>[youtube=1]</p>'

        expected = '<p><a href="https://youtu.be/1" target="_blank">Watch the video</a></p>'

        self.assertEqual(expected, article_utils.replace_videos(example_text, get_video_embed))
