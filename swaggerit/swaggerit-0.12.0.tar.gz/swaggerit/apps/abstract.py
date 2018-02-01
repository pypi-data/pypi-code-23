

from ddpy.constants import SWAGGER_JSON_TEMPLATE, SWAGGER_SPEC_SCHEMA

from connexion.apps.abstract import AbstractApp as ConnexionAbstractApp
from connexion.resolver import Resolver


class AbstractApp(ConnexionAbstractApp):

    def add_api(self, core_subdomain, support_subdomains=[], generic_subdomains=[],
                spec_template=SWAGGER_JSON_TEMPLATE, spec_schema=SWAGGER_SPEC_SCHEMA,
                base_path=None, arguments=None, auth_all_paths=None, validate_responses=False,
                strict_validation=False, resolver=Resolver(), resolver_error=None,
                pythonic_params=False, options=None, **old_style_options):
        spec_dict = type(self).build_spec_dict(core_subdomain, support_subdomains,
                                               generic_subdomains, spec_template)
        ConnexionAbstractApp.add_api(self, spec_dict, base_path=base_path, arguments=arguments,
                                     auth_all_paths=auth_all_paths,
                                     validate_responses=validate_responses,
                                     strict_validation=strict_validation, resolver=resolver,
                                     resolver_error=resolver_error,
                                     pythonic_params=pythonic_params,
                                     options=options, **old_style_options)

    @classmethod
    def build_spec_dict(self, core_subdomain, support_subdomains=[], generic_subdomains=[],
                        spec_template=SWAGGER_JSON_TEMPLATE):
        return SWAGGER_JSON_TEMPLATE
