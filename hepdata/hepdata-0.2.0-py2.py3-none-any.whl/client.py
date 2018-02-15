# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import logging
try:
    from urllib.parse import urlencode
except ImportError:
    # Python 2!
    from urllib import urlencode as base_urlencode

    def urlencode(params):
        clean_data = {}
        for k, v in params.iteritems():
            clean_data[k] = unicode(v).encode('utf-8')
        return base_urlencode(clean_data)

import requests
import xmltodict

from hepdata import exceptions

logger = logging.getLogger('hepdata')

SEARCH_PARAMS = [
    "parent_only",
    "city",
    "state",
    "distribution_frequency",
    "previous_cycle",
    "online_form",
    "gift_ratio_greater_11",
    "inclusion",
    "exclusion",
]

ELIGIBILITY_PARAMS = [
    "four_year_college_universities",  # Four Year College eligibility
    "grad_professional_schools",  # Graduate School eliggibility
    "community_junior_college",  # Community Coll. eligibilityy
    "seminaries",  # Rel. EDU eligibility
    "secondary_schools",  # Secondary School eligibility
    "elementary_schools",  # Elementary School eligibility
    "technical_schools",  # Technical Schoolsl eligibility
    "law_schools",  # Law School eligibility
    "middle_schools",  # Middle School eligibility
    "pre_schools",  # Proge School eligibility
    "educational_services",  # Educational Services eligibility
    "educational_fund",  # Educational Fund eligibilityty
    "education_foundation",  # Educational Foundation eligibility
    "healthcare",  # ",  # "St Judes) eligibilty
    "museum",  # Museum eligibility
    "social_services",  # ",  # "NYC Rescue) eligibility
    "performing_arts",  # ",  # "Wolftrap) eligibility
    "college_university_radio_tv",  # ",  # "WNMU-FM) eligibility
    "public_radio_tv",  # ",  # "NPR)                                    eligibility
    "religious",  # Church eligibility
    "environmental_conservation",  # ",  # "Greenpeace) eligibility
    "cultural",  # ",  # "Wolftrap) eligibility
    "charities",  # Charity eligibility
    "fraternity_sorority",  # Fraternities eligibility
    "hospitals",  # culturalNon-profit Hosp. eligibility
    "professional_societies",  # (NRA) eligibility
    "unitedway",  # United Way eligibility
    "redcross",  # Red Cross eligibility
    "hospices",  # Hospice eligibility
    "zoos",  # Zoo eligibility
    "libraries",  # Public Library eligibility
    "foodbanks",  # Food Bank eligibility
    "youthorganizations",  # Youth Orgs. eligibility
    "animalprotection",  # BankAnimal Protect. eligibility
    "religiousbasedhumansocialservices",  # Rel. Social Serv. eligibility
    "nursing_home",  # Nursing Home eligibility
    "community_development",  # Community Development elg
    "affordable_housing",  # Affordable Housing elig.
    "fire_rescue",  # Fire & Rescue Org. elig.
    "special_needs_schools",  # Special Needs Schools elig.
    "disasterrelief",  # Disaster Relief elgligibility
    "single_disease",  # Non-profit Hosp. eligibility
    "athletics",  # Athletic eligibility
    "volunteer_programs",  # Volunteer Prog. Eligibility
]


VALID_PARAMS = set(SEARCH_PARAMS + ELIGIBILITY_PARAMS)


def clean_data(data):
    """
    The API returns the company results as a list for multiple results
    and a dictionary for just a single result. This requires unnecessary
    type checking everywhere else so just enforcing a list here is the
    simplest thing to do. It makes the result more consistent.
    """
    try:
        if not isinstance(data['companies']['company'], list):
            data['companies']['company'] = [data['companies']['company']]
    except KeyError:
        pass
    return data


class GiftsClient(object):
    """
    API wrapper for the HEPdata Matching Gifts database API
    """

    def __init__(self, key):
        self.key = key
        self.url = "https://automatch.matchinggifts.com/{{action}}/xml/{key}/".format(key=key)

    def _get_url(self, action, param=None, **query):
        url = self.url.format(action=action)
        if param:
            url += "{param}/".format(param=param)

        if query:
            url += "?{q}".format(q=urlencode(query))
        return url

    def _req(self, action, param=None, **query):
        """
        Issues an HTTP request and returns the response as a Python dictionary.
        """
        response = requests.get(self._get_url(action, param, **query))

        if response.status_code != 200:
            raise exceptions.HEPError(code=response.status_code, response=response)

        data = xmltodict.parse(response.content)

        error = data.get('error', None)
        if error:
            raise exceptions.HEPError(error)

        return clean_data(data)

    def profile(self, profile_id):
        """
        Returns detailed profile information about a company.
        """
        return self._req(action="profiles", param=profile_id)

    def search(self, search_value, path="searches", **query):
        """
        """
        for k in query.keys():
            if k not in VALID_PARAMS:
                logger.warn("'{}' is not a valid matching gifts search parameter".format(k))

        return self._req(action=path, param=search_value, **query)

    def search_names(self, search_value, **query):
        return self.search(search_value, path="name_searches", **query)
