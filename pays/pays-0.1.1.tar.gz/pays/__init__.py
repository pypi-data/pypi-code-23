"""
**pays** est une librairie en python 3 pour intégrer des listes de pays dans ses applications.
"""
import os
import json
import pkg_resources


def update_data():
    """
    Génère les fichiers data/*.json à partir de vendor/countries/dist/countries.json
    """
    files = {}
    with open('vendor/countries/dist/countries.json') as json_data:
        countries = json.load(json_data)
    for country in countries:
        for locale, translation in country['translations'].items():
            if not files.get(locale):
                files[locale] = {}
            data = {
                'name': translation['common'],
                'official_name': translation['official'],
                'cca2': country['cca2'],
                'cca3': country['cca3'],
                'ccn3': country['ccn3'],
                'flag': country['flag']
            }
            files[locale][translation['common']] = data
    for locale, data in files.items():
        filename = 'data/{locale}.json'.format(locale=locale)
        with open(filename, 'w') as output:
            output.write(json.dumps(data))


class Pays:
    """
    Objet principal de la librairie
    """

    data = {}

    def __init__(self,
                 locale: str = 'fra',
                 exclude: list = None,
                 only: list = None):
        """
        Instantiation de `pays`:
            countries = pays(
                'fra',  # locale 639-2 pour les traductions des noms, , optionnel, fra par défaut
                # liste de codes alpha2 de pays à exclure, optionnel
                exclude=['ES'],
                # liste de codes alpha2 de pays à retourner, optionnel
                only=['FR', 'DE']
                # note: on ne peut utiliser que exclude OU only, pas les deux à la fois
            )
        """
        if exclude and only:
            raise AttributeError('exclude ou only, pas les deux !')
        self.locale = locale
        self.exclude = exclude
        self.only = only
        self.load_data()

    def load_data(self, locale: str = None):
        """
        """
        if not locale:
            locale = self.locale
        if not self.data.get(locale):
            path = '/'.join(['..', 'data', locale + '.json'])
            with open(pkg_resources.resource_filename(__name__,
                                                      path)) as json_data:
                data = json.load(json_data)
            self.data[locale] = data
        return self.data.get(locale)

    def get(self, key, locale: str = None):
        """
        retourne un objet `Contree` identifié par `key` 
        si locale est spécifié on l'utilise, sinon on garde celle par défaut
        """
        if not locale:
            locale = self.locale
        try:
            int(key)
            method = '_get_by_number'
        except ValueError:
            method = '_get_by_alpha2' if len(key) == 2 else '_get_by_alpha3'

        getter = getattr(self, method)
        data = getter(key, locale)
        if data:
            return Contree(data)
        raise KeyError('Aucun pays ne trouvé avec {key}'.format(key=key))

    def index_by(self, index: str, locale: str = None):
        """
        Changement de l'index des données
        """
        if not locale:
            locale = self.locale
        countries = self.data.get(locale)
        new_data = {}
        for name, data in countries.items():
            new_data[data[index]] = data
            # = country
        return new_data

    def _get_by_number(self, number: int, locale: str = None):
        """
        retourne le pays n° `number`
        """
        countries = self.index_by('ccn3', locale)
        return countries.get(number)

    def _get_by_alpha2(self, alpha: str, locale: str = None):
        """
        retourne le pays n° `number`
        """
        countries = self.index_by('cca2', locale)
        return countries.get(alpha.upper())

    def _get_by_alpha3(self, alpha: int, locale: str = None):
        """
        retourne le pays n° `number`
        """
        countries = self.index_by('cca3', locale)
        return countries.get(alpha.upper())


class Contree:
    """
    Un pays
    """
    __slots__ = ('name', 'official_name', 'cca2', 'cca3', 'ccn3', 'flag')

    def __init__(self, data: dict):
        """
        Récupération des valeurs à partir de data
        """
        try:
            for attr, value in data.items():
                setattr(self, attr, value)
        except AttributeError:
            pass
