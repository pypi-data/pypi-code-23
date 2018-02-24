"""The DNDGen Character Generator"""

from random import randint, choice
from argparse import ArgumentParser
import requests

__version__ = "0.1.0"


def get_data():
    r = requests.get('https://raw.githubusercontent.com/dominictarr/random-name/master/names.json')
    list_json = r.json()
    name = choice(list_json)
    return name


class Entity():
    def __init__(self, **kwargs):
        self.defaultname = kwargs.get('namelist') or  ['Jerry Seinfeld', 'Noor', "Z The 1st"]
        self.name = kwargs.get('name') or choice(self.defaultname)
        self.strength = kwargs.get('strength') or self.d20()
        self.charisma = kwargs.get('charisma') or self.d20()
        self.wisdom = kwargs.get('wisdom') or self.d20()
        self.intelligence = kwargs.get('intelligence') or self.d20()
        self.dexterity = kwargs.get('dexterity') or self.d20()
        self.constitution = kwargs.get('constitution') or self.d20()
        self.health = kwargs.get('health') or self.d20() + int(self.constitution / 5)

    def d20(self):
        return randint(1, 20)

    def __repr__(self):
        attributes = {'name': self.name, 'strength': self.strength, 'charisma': self.charisma, 'wisdom': self.wisdom, 'intelligence': self.intelligence, 'dexterity': self.dexterity, 'constitution': self.constitution, 'health': self.health, 'enemy': self.type}
        return f'{attributes}'

    def __str__(self):
        self.output = f'{self.name}: Health: {self.health} Charisma: {self.charisma} Strength: {self.strength} Wisdom: {self.wisdom} Intelligence: {self.intelligence} Dexterity: {self.dexterity} Constitution: {self.constitution}'
        return self.output


class Player(Entity):
    def __init__(self, **kwargs):
        super().__init__(
                         name=kwargs.get('name'),
                         namelist=kwargs.get('namelist'),
                         strength=kwargs.get('strength'),
                         charisma=kwargs.get('charisma'),
                         wisdom=kwargs.get('wisdom'),
                         intelligence=kwargs.get('intelligence'),
                         dexterity=kwargs.get('dexterity'),
                         constitution=kwargs.get('constitution'),
                         health=kwargs.get('health')
                         )


if __name__ == '__main__':
    parser = ArgumentParser(description="DND Character Generator")
    parser.add_argument('-n', '--name', type=str, help='Define the name for your DND Character')
    parser.add_argument('-chr', '--charisma', type=int, help="Define the Character's Charisma")
    parser.add_argument('-str', '--strength', type=int, help="Define a Character's Strength")
    parser.add_argument('-wis', '--wisdom', type=int, help="Define a Character's Wisdom")
    parser.add_argument('-int', '--intelligence', type=int, help="Define a Character's Intelligence")
    parser.add_argument('-dex', '--dexterity', type=int, help="Define a Character's Intelligence")
    parser.add_argument('-const', '--constitution', type=int, help="Define a Character's Constitution")
    parser.add_argument('-hp', '--health', type=int, help="Define a Character's Health")
    args = parser.parse_args()
    p = Player(name=args.name or get_data(), charisma=args.charisma, wisdom=args.wisdom, dexterity=args.dexterity, health=args.health, intelligence=args.intelligence, strength=args.strength, constitution=args.constitution)
    print(p)
