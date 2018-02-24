"""

parser.py
~~~~~~~~

A module that handles the parsing logic of tweetQuoteBot.

This module takes the given text and parses it into a usable form,
e.g. a list of sentences, that the bot can use to then tweet out.

:copyright: @ 2018
:author: elias julian marko garcia
:license: MIT, see LICENSE
"""

# from nltk.tokenize import sent_tokenize

# from click import echo, command, option, group
import click


@click.command()
def extractTXT(file):
    """Extracts quotes from a .txt file.

    :param file: the file being parsed
    """
    click.echo("extractTXT called!")


@click.command()
def extractPDF(file):
    """Extracts quotes from a .pdf file.

    Given the variation in PDF formatting, with some being more sane than
    others, do not be surprised with awful results from this. Be prepared for
    lots of manual editing.

    :param file: the file being parsed.
    """
    click.echo("extractPDF called!")
