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
    files = {'eng': {}}
    with open('vendor/countries/dist/countries.json') as json_data:
        countries = json.load(json_data)
    for country in countries:
        data = {
            'name': country['name']['common'],
            'official_name': country['name']['official'],
            'cca2': country['cca2'],
            'cca3': country['cca3'],
            'ccn3': country['ccn3'],
            'flag': country['flag']
        }
        files['eng'][country['cca2']] = data
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
            files[locale][country['cca2']] = data
    for locale, data in files.items():
        filename = 'data/{locale}.json'.format(locale=locale)
        with open(filename, 'w') as output:
            output.write(json.dumps(data))


class Countries:
    """
    Objet principal de la librairie
    """

    data = {}

    def __init__(self,
                 locale: str = 'fra',
                 exclude: list = [],
                 only: list = []):
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
        if exclude:
            print('to exclude')
        self.only = only
        self.load_data()

    def load_data(self, locale: str = None):
        """
        Récupération des données depuis les fichiers .json.
        Les résultats sont stockés en cache dans `data[locale]`.
        """
        if not locale:
            locale = self.locale
        if not self.data.get(locale):
            path = '/'.join(['..', 'data', locale + '.json'])
            with open(pkg_resources.resource_filename(__name__,
                                                      path)) as json_data:
                data = json.load(json_data)
            # suppression des éléments spécifiés dans `exclude`
            if self.exclude:
                self.data[locale] = {
                    cca2: values
                    for cca2, values in data.items()
                    if cca2 not in self.exclude
                }
            # ou limite de la liste à ceux spécifiés dans `only`
            elif self.only:
                self.data[locale] = {
                    cca2: values
                    for cca2, values in data.items() if cca2 in self.only
                }
            else:
                self.data[locale] = data
        return self.data.get(locale)

    def get(self, key, locale: str = None):
        """
        Méthode de récupération d’un pays précis, par code alpha 2/3 ou par numéro
        Retourne un objet `Country` identifié par `key` si `locale` est spécifié on l'utilise, 
        sinon on garde celle par défaut.
        """
        if not locale:
            locale = self.locale
        self.load_data(locale)
        try:
            int(key)
            method = '_get_by_number'
        except ValueError:
            method = '_get_by_alpha2' if len(key) == 2 else '_get_by_alpha3'

        getter = getattr(self, method)
        data = getter(key, locale)
        if not data:
            raise KeyError('Aucun pays ne trouvé avec {key}'.format(key=key))
        return Country(data)

    def countries(self, locale: str = None):
        """
        `pays` se comporte comme un dictionnaire pour les iterations
        """
        if not locale:
            locale = self.locale
        return self.data[locale]

    def __dict__(self):
        """
        `pays` se comporte comme un dictionnaire pour les iterations
        """
        return self.countries()

    def index_by(self, index: str, locale: str = None):
        """
        Changement de l'index des données
        """
        if not locale:
            locale = self.locale
        countries = self.data.get(locale)
        new_data = {}
        for _, data in countries.items():
            new_data[data[index]] = data
        return new_data

    def _get_by_number(self, number: int, locale: str = None):
        """
        Retourne le pays n° `number`
        """
        countries = self.index_by('ccn3', locale)
        # number en str car c'est une clé de dict
        return countries.get(str(number))

    def _get_by_alpha2(self, alpha: str, locale: str = None):
        """
        retourne le pays par son code alpha XX
        """
        countries = self.data.get(locale)
        return countries.get(alpha.upper())

    def _get_by_alpha3(self, alpha: int, locale: str = None):
        """
        Retourne le pays par son code alpha XXX
        """
        countries = self.index_by('cca3', locale)
        return countries.get(alpha.upper())


class Country:
    """
    L’objet `Country` contient les infos sur un pays donné
    """
    name = ''
    official_name = ''
    cca2 = ''
    cca3 = ''
    ccn3 = 0
    flag = ''

    def __init__(self, data: dict):
        """
        On l’instancie avec un dictionnaire de données
        """
        try:
            for attr, value in data.items():
                setattr(self, attr, value)
        except AttributeError:
            pass

    def __str__(self):
        """
        Par défaut, la représentation textuelle d’un pays est son nom courant
        """
        return self.name
