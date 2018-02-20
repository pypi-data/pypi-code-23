import click
import random

ALBUMS = [
    "Guppy by Charly Bliss",
    "The Far Field by Future Islands",
    "Sprained Ankle by Julien Baker",
    "King Con by Alex Winston",
    "Wildlife Pop by Stepdad",
    "Talon of the Hawk by Front Bottoms",
    "Out of Love by Mister Heavenly",
    "White Flag by Branches",
    "Holy Ghost by Modern Baseball",
    "Moth by Chairlift",
    "Vacation by BTMI",
    "Hallelejah by Igorrr",
    "Rabbit Habits by Man Man",
    "Flood Network by Katie Dey",
    "Dandelion Gum by BMSR",
    "People Who Can Eat People by AJJ",
    "Endless Fantasy by Anamanaguchi",
    "Bonito Generation by Kero Kero Bonito",
    "You're a Woman, I'm a Machine by DFA1979",
    "GT Ultra by Guerilla Toss",
    "Shroud by Chester Gwazda",
    "Emotion by CRJ",
    "Go by Jónsi",
    "Gliss Riffer by Dan Deacon",
    "We Will Never Run Out of Love by Terror Pigeon",
    "Beat Down (single) by Mister Heavenly",
    "The Hungarian Album by Venetian Snares",
    "Teens of Denial by Car Seat Headrest",
    "Bug Thief (single) by Iglooghost",
    "Bambi's Dilemma by Melt Banana",
    "Lost and Safe by The Books",
    "CHAM! by Macross 82-99",
    "Bending Bridges by Mary Halvorson Quintet",
    "Something for your Mind (single) by Superorganism",
    "III by BBNG",
    "Antisocialites by Alvvays",
    "Do Whatever You Want All The Time by Ponytail",
    "The Album or Get Real by Math the Band",
    "Worlds by Porter Robinson",
    "Topcoat by Venosci",
    "Yes! We're Open by groceries",
    "Next Thing by Frankie Cosmos",
    "PC Music vol 1, 2 by PC Music",
    "Memory Mirror by Octopus Project",
    "BLUE by iamamiwhoami",
    "Boxing the Moonlight by Mister Heavenly",
    "Too Real by Giraffage",
    "A Man Alive by Thao & The Get Down Stay Down",
    "WWCOHWWG by The Unicorns",
    "Return to the Sea by Islands",
    "Neo Wax Bloom by Iglooghost?",
    "Eon Break (single) by Virtual Self",
    "GN by The Ratboys",
    "Art Angels by Grimes",
    "EP B/C EP by Battles",
    "Heart Sky by Emily Yacina",
    "Spirit Phone by Lemon Demon",
    "Out of the Garden by Tancred",
    "The Black Box by Aivi & Surasshu",
    "Rented World by Menzingers",
    "Satellite Young by Satellite Young",
    "Humans Become Machines by Aristophanes",
    "Richard D James Album by Aphex Twin",
    "Outrun by Kavinsky",
    "Soft Machine by Teddy Bears",
    "Virtual Self EP by Virtual Self",
    "In Silico by Pendulum",
    "Future Cake by YUC'e",
    "Miami Garden Club by Kitty",
    "Hue (EP) by Mili",
    "Healing (EP) by In Love With a Ghost",
    "Adventure (Deluxe) by Madeon",
    "Skyriser by Maxo",
    "Turn Out the Lights by Julien Baker",
    "Eingang by New Shack",
    "Smidley by Smidley",
    "Kirinardi by Gevende",
    "Madrugada by Benjamin Poole",
    "The Void by Sidewalks and Skeletons",
    "Manic Revelations by Pokey LeFarge",
    "Glistening Pleasure 2.0 by Brite Futures",
    "Homey by Chon"
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
