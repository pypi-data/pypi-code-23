"""Configuration helpers."""

# Copyright 2016-2018 ASI Data Science
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

SHERLOCKML_ENV = os.getenv('SHERLOCKML_ENV', 'prod')


def subdomain_from_env(environment):
    """Determine platform subdomain from environment."""
    if environment == 'prod':
        return 'platform'
    return 'platform-' + environment


def url_for_service(service, environment=SHERLOCKML_ENV):
    """Return URL for the given service in the given environment."""
    subdomain = subdomain_from_env(environment)
    return 'https://{}.{}.asidata.science'.format(service, subdomain)


def casebook_url(environment=SHERLOCKML_ENV):
    """Return URL for Casebook in the given environment."""
    return url_for_service('casebook', environment)


def hudson_url(environment=SHERLOCKML_ENV):
    """Return URL for Hudson in the given environment."""
    return url_for_service('hudson', environment)


def galleon_url(environment=SHERLOCKML_ENV):
    """Return URL for Galleon in the given environment."""
    return url_for_service('galleon', environment)


def baskerville_url(environment=SHERLOCKML_ENV):
    """Return URL for Baskerville in the given environment."""
    return url_for_service('baskerville', environment)


def frontend_url(environment=SHERLOCKML_ENV):
    """Return URL for the SherlockML frontend in the given environment."""
    if environment == 'prod':
        return 'https://sherlockml.com'
    return 'https://{}.sherlockml.com'.format(environment)
