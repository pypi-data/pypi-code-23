import click
import random

ALBUMS = [
    "Savage Sinusoid by Igorrr",
    "White Flag by Branches",
    "Out of Love by Mister Heavenly",
    "Talon of the Hawk by The Front Bottoms",
    "King Con by Alex Winston",
    "Wildlife Pop by Stepdad",
    "The Far Field by Future Islands"
]


def _pick_intro():
    intros = ["Have you tried {}?",
              "Maybe you should listen to {}.",
              "What about {}?",
              "You should play {}."]
    return random.choice(intros)


@click.command()
@click.option('--more-devin',
              is_flag=True,
              help="""Yo dawg. I hear you like Devin.
                   So I put some devin in your devin, so you can devin while
                   you devin.
                   """)
def devin_main(more_devin=False):
    intro = _pick_intro()
    album = random.choice(ALBUMS)
    rec = intro.format(album)
    if more_devin:
        click.echo(rec, nl=False)
        click.echo(" It's a good good album.")
    else:
        click.echo(rec)
