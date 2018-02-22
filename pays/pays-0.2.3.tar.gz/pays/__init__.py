"""
**pays** est une librairie en python 3 pour intégrer des listes de pays dans ses applications.

Les données ISO 3166 retournées proviennent de https://mledoze.github.io/countries/ dont on ne garde
qu'un sous-ensemble :

* `name` : nom commun (France)
* official_name : nom officiel (République Française) 
* cca2 : code alpha-2 (FR)
* cca3 : code alpha-3 (FRA)
* ccn3 : code numérique (250)
* flag : émoji drapeau (🇫🇷)

Les champs `name` & `official_name` sont disponibles en plusieurs langues (Français, Allemand, Anglais, Japonnais, ...).

Import : 

    from pays import Countries

Initialisation :

    countries = Countries(
        # locale 639-2 pour les traductions des noms, 
        # optionnel, *fra* par défaut
        'fra', 
        # codes alpha2 de pays à exclure, 
        # optionnel
        exclude=['ES'],
        # codes alpha2 de pays à utiliser exclusivement, 
        # optionnel
        only=['FR', 'DE']
    )

Itération :

    for country in countries:
        # __str__ retourne nom commun : France
        print(country)  
        # République Française
        print(country.official_name)

Récupération d'un pays précis

    # France
    print(countries.get('FR'))
    # Francia en italien
    print(countries.get('FRA', 'ita'))
    # Frankrijk en Néerlandais
    print(countries.get(250, 'nld'))
    # raise AttributeError
    print(countries.get('XXXX'))

Pour une librairie (beaucoup) plus riche en données & fonctionnalités
je vous invite à utiliser [pycountry](https://pypi.python.org/pypi/pycountry) !
"""
import os
import json
import pkg_resources


class Country:
    """
    `Country` contient les infos sur un pays donné. Il est retourné instancié par `Countries`.
    """
    name = ''
    official_name = ''
    cca2 = ''
    cca3 = ''
    ccn3 = 0
    flag = ''

    def __init__(self, data: dict):
        """
        On l’instancie avec un dictionnaire de données.
        """
        try:
            for attr, value in data.items():
                setattr(self, attr, value)
        except AttributeError:
            raise AttributeError('Country instancié sans data dict')

    def __str__(self):
        """
        La représentation textuelle d’un pays est son nom courant.
        """
        return self.name


class Countries:
    """
    Classe principale de la librairie, c'est celle-ci qu'on importe dans son application.
    """

    def __init__(self,
                 locale: str = 'fra',
                 exclude: list = [],
                 only: list = []):
        """
        Par défaut Countries est initialisé avec les données en français, le paramètre `locale` permet de
        spécifier une autre langue.

        * `exclude=['ES', 'DE']` permet de retirer l’Espagne & l’Allemagne de la liste
        * `only=['FR', 'GB', 'US']` permet de n`utiliser que ces 3 pays
        """
        if exclude and only:
            # Il n'est pas possible d’utiliser exclude & only en même temps
            raise AttributeError('exclude ou only, pas les deux !')
        if not isinstance(exclude, list):
            raise AttributeError('exclude doit être une list')
        if not isinstance(only, list):
            raise AttributeError('only doit être une list')
        self.locale = locale
        self.exclude = exclude
        self.only = only
        self.data = {}

    def __iter__(self):
        """
        Une fois initialisé, `Countries` peut être utilisé comme un générateur de `Country`
        pour, par exemple, afficher un menu déroulant.
        """
        self._load_data()
        for _, data in self.countries.items():
            yield Country(data)

    @property
    def countries(self) -> dict:
        """
        Si le générateur ne convient pas à vos usages, la méthode `countries`
        retourne le dictionnaire des données brutes (sans objet `Country`) de la 
        locale en cours.
        """
        self._load_data()
        return self.data[self.locale]

    def get(self, key, locale: str = None) -> object:
        """
        Méthode de récupération d’un pays précis, par code alpha 2/3 ou par numéro.
        Retourne un objet `Country` identifié par `key` si `locale` est spécifié on l'utilise, 
        sinon on garde celle par défaut.
        En fonction de `key` on appelle la méthode privée qui va bien.
        """
        if not locale:
            locale = self.locale
        self._load_data(locale)
        try:
            int(key)
            method = '_get_by_number'
        except ValueError:
            method = '_get_by_alpha2' if len(key) == 2 else '_get_by_alpha3'
        except TypeError:
            raise KeyError(
                'Aucun pays ne correspond à "{key}"'.format(key=key))

        getter = getattr(self, method)
        try:
            data = getter(key, locale)
        except KeyError:
            raise KeyError(
                'Aucun pays ne correspond à "{key}"'.format(key=key))
        return Country(data)

    def _load_data(self, locale: str = None) -> dict:
        """
        Récupération des données depuis les fichiers .json selon la `locale` demandée.
        Les résultats sont ensuite mis en cache dans `self.data[locale]`.
        """
        if not locale:
            locale = self.locale
        try:
            self.data[locale]
        except KeyError:
            path = '/'.join(['data', locale + '.json'])
            with open(pkg_resources.resource_filename(__name__,
                                                      path)) as json_data:
                data = json.load(json_data)
            # suppression des éléments spécifiés dans `exclude`
            if self.exclude:
                data = {
                    cca2: values
                    for cca2, values in data.items()
                    if cca2 not in self.exclude
                }
            # ou limite de la liste à ceux spécifiés dans `only`
            elif self.only:
                data = {
                    cca2: values
                    for cca2, values in data.items() if cca2 in self.only
                }
            self.data[locale] = data
        return self.data.get(locale)

    def _index_by(self, index: str, locale: str = None) -> dict:
        """
        Afin de rendre accessible les données à partir de plusieurs clés (alpha 2 ou 3 ou numérique)
        On pivote l'indexation du dictionnaire de données. Par défaut on a 
            code alpha2 : { données sur le pays (dont code alpha 2) }
        En utilisant `_index_by('ccn3') on obtient :
            code numérique : { données sur le pays (dont code alpha 2) }
        """
        countries = self.data.get(locale)
        new_data = {data[index]: data for _, data in countries.items()}
        return new_data

    def _get_by_number(self, number: int, locale: str = None) -> dict:
        """
        Méthode privée pour retourner un pays par numéro
        """
        countries = self._index_by('ccn3', locale)
        # note: number en str car c'est une clé de dict
        return countries[str(number)]

    def _get_by_alpha2(self, alpha: str, locale: str = None) -> dict:
        """
        Méthode privée pour retourner un pays par code alpha 2 "XX"
        """
        countries = self.data.get(locale)
        return countries[alpha.upper()]

    def _get_by_alpha3(self, alpha: str, locale: str = None) -> dict:
        """
        Méthode privée pour retourner un pays par numéro code alpha 3 "XXX"
        """
        countries = self._index_by('cca3', locale)
        return countries[alpha.upper()]
