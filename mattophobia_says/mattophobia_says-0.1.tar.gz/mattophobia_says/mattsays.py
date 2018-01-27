# Python rewrite of Mattophobia Says by Jack Baron: https://unpkg.com/mattophobia-says@0.3.0/
# Written by DerpyChap

import math
import random

swears = [
    'fuck',
    'shit',
    'cunt',
    'piss',
    'twat',
    'hell',
    'ass',
    'asshole',
    'motherfucker',
    'son of a bitch',
    'piece of shit',
    'wanker',
    'dickhead',
    'bitch',
    'cock',
    'assface',
    'wankface',
    'asshat',
    'penis',
    'shitface',
    'fucker',
    'prick',
    'jesus',
    'bastard',
    'god damn it',
    'shitfuck',
    'fuck',
    'FUCK',
    'FUCK FUCK FUCK',
    'Trump',
    'nyehh',
    'nyehh',
    'nyehh',
    'cunthole',
    'bread',
    'bread fetish',
    '*quack*',
]

ings = [
    'fucking',
    'assing',
    'motherfucking',
    'goddamn',
    'damn',
    'holy',
    'fucking',
    'shitting',
    'pissing',
]

standalone = [
    'Jesus fucking Christ',
    'shut the fuck up',
    "I'm so angry right now",
    'fuck you',
    'shut up',
    'FUCK YOU',
    'I fucked up',
    'jesus christ on a fucking bike',
    'Jesus dicking tits',
    'cunty cunty cunt cunt',
    'sexy sexy bread',
]


class MattSays:

    def __init__(self, swears=swears, ings=ings, standalone=standalone):
        self.swears = swears
        self.ings = ings
        self.standalone = standalone
        self.lastSentence = None

    def randomIntFromInterval(self, min: int, max: int):
        """
        Random number from Min/Max

        Parameters
        ----------
        min: int
            Minimum Value
        max: int
            Maximum Value
        Returns
        -------
        int:
            Randomly generated number from the bounds
        """
        return math.floor((random.random() * (max - min + 1)) + min)

    def randomFromList(self, lst: list, previous: str = None):
        """
        Randomly pick a value from a list

        Parameters
        ----------
        lst: list
            List to pick from
        previous: str
            Previous pick (Prevents Duplication)
        Returns
        -------
        str:
            Random Pick
        """
        selected = lst[math.floor((random.random() * len(lst)))]
        if selected == previous:
            return self.randomFromList(lst, previous)
        return selected

    def randomEnding(self, isQuote: bool, noQuestion: bool = True):
        """
        Get a random sentence ending

        Parameters
        ----------
        isQuote: bool
            Is the sentence a quote?
        noQuestion: bool
            Is the sentence NOT a question
        Returns
        -------
        str
        """
        endings = ['. ', '! ', '. ', '! ', '. ', '? ', '. ']
        ending = self.randomFromList(endings)

        if isQuote:
            return '." '
        elif (noQuestion and ending == '?'):
            return self.randomEnding(isQuote, noQuestion)
        else:
            return ending

    def randomlyPunctuation(self, i: int, count: int, paranthesis: bool,
                            hadOpening: bool, isQuote: bool):
        """
        Randomly select punctuation for mid-sentence

        Parameters
        ----------
        i: int
            I don't know
        count: int
            Count of something
        paranthesis: bool
            Paranthesis yay or nay
        hadOpening: bool
            Has it had an opening recently?
        isQuote: bool
            Is the sentence a quote?
        Returns
        -------
        str
        """
        punctuation = [', ', ' - ', ', ', '; ', ', ', ': ', ', ']
        if (paranthesis and hadOpening and
                self.randomIntFromInterval(0, 50) > 35):
            if isQuote:
                return '] '
            else:
                return ') '
        elif (self.randomIntFromInterval(0, 100) > 95 and i < count - 1):
            return self.randomFromList(punctuation)
        else:
            return ' '

    def capitalize(self, str: str):
        """
        Capitalizes the first character of a string.
        Unlike str.capitalize(), this will only modify the first character of a string.

        Parameters
        ----------
        str: str
            The string to capitalize
        Returns
        -------
        str
        """
        return str[:1].upper() + str[1:]

    def generate(self, min: int = 4, max: int = 18):
        """
        Generate a random Mattophobia Style Sentence

        Parameters
        ----------
        min: int
            Minimum number of words. Default is 4
        max: int
            Maximum number of words. Default is 18
        Returns
        -------
        str
        """
        content = ''
        isQuote = self.randomIntFromInterval(0, 100) > 90

        content += '"' if isQuote else ''

        if self.randomIntFromInterval(0, 100) < 80:
            words = self.randomIntFromInterval(min, max)
            sentence = ''
            lastWord = ''

            if self.randomIntFromInterval(0, 100) > 90:
                paranthesis = True
                hadOpening = False
            else:
                paranthesis = False
                hadOpening = True

            w = 0
            while w < words:
                w += 1
                if (w < 2 and words > 7 and paranthesis and not hadOpening):
                    if isQuote:
                        sentence += ' ['
                    else:
                        sentence += ' ('

                    hadOpening = True

                if (self.randomIntFromInterval(0, 100) < 15 and w < words - 1):
                    lastWord = self.randomFromList(ings, lastWord)
                else:
                    lastWord = self.randomFromList(swears, lastWord)

                punctuation = self.randomlyPunctuation(w, words, paranthesis,
                                                       hadOpening, isQuote)
                if (punctuation == ') ' or punctuation == '] '):
                    paranthesis = False
                sentence += lastWord + punctuation

            content += self.capitalize(
                sentence.strip()) + self.randomEnding(isQuote)
            return content
        else:
            self.lastSentence = self.randomFromList(self.standalone,
                                                    self.lastSentence)
            self.lastSentence = self.lastSentence.capitalize()
            content += self.lastSentence + self.randomEnding(isQuote, True)
            return content
