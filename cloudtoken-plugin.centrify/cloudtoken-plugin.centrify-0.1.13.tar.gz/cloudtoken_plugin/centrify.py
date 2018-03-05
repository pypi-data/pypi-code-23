# Centrify plugin for cloudtoken.
#
# Author: Shane Anderson (sanderson@atlassian.com)
#         Ben Lyall (blyall@atlassian.com)
#
# This plugin requires some configuration to be added to your config.yaml.
# Please see README.md.

from urllib.parse import urlparse, parse_qs
from pyquery import PyQuery
import requests
import argparse
import logging
import pickle
import os
import pwd
import time
import yaml

logger = logging.getLogger("cloudtoken.centrify")


class Plugin(object):
    def __init__(self, config):
        self._config = config
        self._name = "centrify"
        self._description = "Authenticate against Centrify IdP."

        self._args = None
        self._centrify_url = None
        self._defaults = {}
        self._defaults_modified = False

        self._cookiejar = None

        self._session = requests.session()
        self._init_session_headers()

        self._required_defaults = {
            "tenant_id": "Centrify Tenant ID",
            "appkey": "Centrify App ID",
        }

        self._max_retries = 3
        self._retry_counter = 0

    def __str__(self):
        return __file__

    @staticmethod
    def unset(args):
        pass

    @staticmethod
    def arguments(defaults):
        parser = argparse.ArgumentParser()
        parser.add_argument("--mfa-passcode",
                            dest="mfa_passcode",
                            default=defaults.get("mfa-passcode", None),
                            help="Provide the MFA passcode instead of prompting for it.")
        parser.add_argument("--mfa-method",
                            dest="mfa_method",
                            default=defaults.get("mfa-method", "push"),
                            choices=["push", "phone", "passcode"],
                            help="Specify the method for MFA (Default: push)")

        return parser

    def _init_session_headers(self):
        """
        Specify the standard headers for each request.
        :return: None
        """
        self._session.headers.update({"X-CENTRIFY-NATIVE-CLIENT": "True"})
        self._session.headers.update({"CONTENT-TYPE": "application/json"})
        self._session.headers.update({"CACHE-CONTROL": "no-cache"})

    def _set_tenant_url(self):
        """
        Determine if the Centrify instance has a vanity URL. If so then use it for future requests, otherwise use
        normal URL based off tenant id.
        :return: Centrify URL.
        """
        if self._get_default("vanity_id"):
            logger.debug("Vanity ID found in configuration.")
            self._centrify_url = "https://{}.my.centrify.com".format(self._get_default("vanity_id"))
        else:
            start_url = "https://{}.my.centrify.com/Security/StartAuthentication".format(self._get_default("tenant_id"))
            start_payload = {
                "User": self._args.username,
                "Version": "1.0",
                "TenantId": self._get_default("tenant_id")
            }

            start_result = self._do_post(start_url, start_payload)

            if 'PodFqdn' in start_result:
                self._centrify_url = "https://{}".format(start_result["PodFqdn"])
                logger.debug("Centrify redirecting us to {}".format(self._centrify_url))
            else:
                self._centrify_url = "https://{}.my.centrify.com".format(self._get_default("tenant_id"))

        logger.debug("Using Centrify URL {}".format(self._centrify_url))
        return self._centrify_url

    def _execute_challenges(self, challenges, session_id):
        """
        Perform each challenge presented by Centrify.
        :param challenges: list of challenges returned by Centrify.
        :param session_id: Centrify session id.
        :return: ASPXAUTH token on success, False on failure.
        """
        mechanism_preferences = self._get_default("auth_preferences")
        if mechanism_preferences:
            logger.debug("Loaded default auth mechanism preferences from config: {}".format(mechanism_preferences))

        for index, challenge in enumerate(challenges):
            logger.debug("Executing challenge {0} of {1}.".format(index + 1, len(challenges)))

            if mechanism_preferences:
                method_index = self._find_preferred_mechanism_index(challenge["Mechanisms"], mechanism_preferences)
                if method_index is None:
                    method_index = self._list_mechanisms(challenge["Mechanisms"])
            else:
                method_index = self._list_mechanisms(challenge['Mechanisms'])

            result = self._execute_mechanism(challenge["Mechanisms"][method_index], session_id)
            logger.debug("Received {}.".format(result["Summary"]))
            if result["Summary"] == "StartNextChallenge":
                continue
            elif result["Summary"] == "LoginSuccess":
                self._set_auth_expiration_cookie()
                return self._session.cookies[".ASPXAUTH"]

        # Failure if no challenge results in LoginSuccess.
        return False

    def _set_auth_expiration_cookie(self, expiration=28800):
        """
        Centrify don't seem to set an expiration on their .ASPXAUTH auth cookie so we set our own cookie with a
        specified epoch expiration time as the value.
        :param expiration: Seconds we should assume the auth cookie is valid for, defaults to 28800 which is 8 hours.
        :return: None
        """
        expiration_string = str(int(time.time()) + expiration)
        self._session.cookies.set(name='cloudtoken_auth_expiration', value=expiration_string)

    @staticmethod
    def _find_preferred_mechanism_index(mechanisms, preferences):
        """
        Given a list of mechanisms dicts and a string list of preferred mechanisms, return the mechanisms index of
        the first preferred mechanism found.
        :param mechanisms: list of mechanism dicts.
        :param preferences: list of mechanism Centrify "UiPrompt" or "PromptSelectMech" strings.
        :return: int or None
        """
        mechanism_list = []
        for mechanism in mechanisms:
            tmp_mech = mechanism["UiPrompt"] if mechanism.get("UiPrompt", None) else mechanism["PromptSelectMech"]
            mechanism_list.append(tmp_mech)

        for preference in preferences:
            try:
                return mechanism_list.index(preference)
            except ValueError:
                continue

        return None

    def _list_mechanisms(self, mechanisms):
        print("Available authentication methods: ")
        for index, mechanism in enumerate(mechanisms):
            name = mechanism["UiPrompt"] if mechanism.get("UiPrompt", None) else mechanism["PromptSelectMech"]
            print("    {0}. {1}".format(index + 1, name))

        if len(mechanisms) == 1:
            print("Auto selecting method: {}".format(name))
            method = 1
        else:
            method = int(input("\nPlease select authentication method: "))

        if method == 0 or type(method) is not int:
            return self._list_mechanisms(mechanisms)

        return method - 1

    def _execute_mechanism(self, mechanism, session_id):
        """
        Execute authentication mechanism presented by a Centrify challenge.
        :param mechanism: dict of mechanism details.
        :param session_id: Centrify session id.
        :return: Centrify /Security/AdvanceAuthentication response.
        """
        mechanism_name = mechanism['Name'].lower()
        logger.debug("Detected authentication mechanism: {}".format(mechanism_name))
        try:
            payload = getattr(self, "_centrify_auth_{}".format(mechanism_name))(mechanism, session_id)
        except AttributeError:
            print("Authentication mechanism '{}' is unsupported. Exiting.".format(mechanism_name))
            exit(1)
        else:
            return self._advance_auth(payload)

    def _centrify_auth_up(self, mechanism, session_id):
        """
        Handle the 'UP' (password) authentication mechanism.
        :param mechanism: dict containing mechanism info.
        :param session_id: Centrify session id.
        :return: dict of payload for 'UP' authentication mechanism.
        """
        payload = {
            "SessionId": session_id,
            "MechanismId": mechanism["MechanismId"],
            "Action": "Answer",
            "Answer": self._args.password,
            "TenantId": self._get_default("tenant_id")
        }

        return payload

    def _centrify_auth_radius(self, mechanism, session_id):
        """
        Handle the 'RADIUS' authentication mechanism. Used for Duo, etc.
        :param mechanism: dict containing mechanism info.
        :param session_id: Centrify session id.
        :return: dict of payload for 'RADIUS' authentication mechanism.
        """

        if self._args.mfa_method == "passcode" and self._args.mfa_passcode:
            answer = self._args.mfa_passcode
        elif self._args.mfa_method == "passcode" and not self._args.mfa_passcode:
            answer = input("Passcode: ")
        else:
            answer = self._args.mfa_method

        payload = {
            "SessionId": session_id,
            "MechanismId": mechanism["MechanismId"],
            "Action": "Answer",
            "Answer": answer,
            "TenantId": self._get_default("tenant_id")
        }

        return payload

    def _advance_auth(self, payload):
        url = "{}/Security/AdvanceAuthentication".format(self._centrify_url)
        response = self._do_post(url, payload)

        if "error" in response:
            print("Failed to authenticate: {}".format(response["error"]))
            exit(1)

        return response

    def _authenticate(self):
        """
        Authenticate with Centrify and obtain a Bearer token.
        :return:
        """
        start_url = "{}/Security/StartAuthentication".format(self._centrify_url)

        start_payload = {
            "User": self._args.username,
            "Version": "1.0",
            "TenantId": self._get_default("tenant_id")
        }

        results = self._do_post(start_url, start_payload)

        if "error" in results:
            raise Exception("Error authenticating during Centrify StartAuthentication.")

        challenges = results["Challenges"]
        session_id = results["SessionId"]

        logger.debug("Found {} authentication challenges.".format(len(challenges)))

        auth_token = self._execute_challenges(challenges, session_id)

        return self._appclick(auth_token)

    def _appclick(self, auth_token):
        headers = {
            "Authorization": "Bearer " + auth_token,
        }

        url = "{0}/uprest/handleAppClick?appkey={1}".format(self._centrify_url, self._get_default("appkey"))

        result = self._do_post(url, headers=headers)

        if "elevate" in result:
            auth_token = self._elevate(result, headers)

        return self._get_saml(auth_token)

    def _elevate(self, data, headers):
        url = "{}/security/startchallenge".format(self._centrify_url)
        payload = {
            "Version": "1.0",
            "elevate": data["elevate"],
            "ChallengeStateId": data["challengeId"]
        }

        logger.debug("Attempting to elevate authentication.")
        results = self._do_post(url, payload=payload, headers=headers)

        session_id = results["SessionId"]
        challenges = results["Challenges"]

        return self._execute_challenges(challenges, session_id)

    def _do_post(self, url, payload=None, headers=None, retries=3, raw=False):
        logger.debug("POST request to {0} with payload: {1} headers: {2} cookies: {3}".format(url,
                                                                                              payload,
                                                                                              headers,
                                                                                              self._session.cookies))
        response = self._session.post(url, headers=headers, json=payload)
        logger.debug("POST response status code: {}".format(response.status_code))
        logger.debug("POST response cookies: {}".format(response.cookies))
        logger.debug("POST response headers: {}".format(response.headers))
        logger.debug("POST response text: {}".format(response.text))

        if response.status_code == 401:
            logger.debug("POST failed with 401: {}".format(response.text))
            retries -= 1
            if retries <= 0:
                response.raise_for_status()

            if self._authenticate():
                return self._do_post(url, payload, retries)
        elif response.status_code == 200:
            # Return the raw response object if requested.
            if raw:
                return response

            # If we need to perform an additional 'elevated' auth
            # then build a dict with the required information and return it.
            if "elevate" in response.url:
                o = urlparse(response.url)
                query_strings = parse_qs(o.query)

                return {
                    "url": response.url,
                    "elevate": query_strings["elevate"][0],
                    "challengeId": query_strings["challengeId"][0],

                }

            result_json = response.json()

            if result_json["success"]:
                return result_json["Result"]

            return {
                "error": result_json["Message"],
            }

        response.raise_for_status()

    def _get_saml(self, auth_token):
        """
        get saml
        :param retries:
        :return:
        """

        headers = {
            "Authorization": "Bearer " + auth_token,
        }

        url = "{0}/uprest/handleAppClick?appkey={1}".format(self._centrify_url, self._get_default("appkey"))

        response = self._do_post(url, headers=headers, raw=True)

        try:
            html = PyQuery(response.text)
            saml_response = html("input[@name='SAMLResponse']")[0].value
            logger.debug("Received the following SAMLResponse from Centrify: {}".format(saml_response))
        except IndexError:
            print("Unable to find SAMLResponse attribute in return data. Attempting to reauthenticate.")
            return self._reauthenticate()
        else:
            return saml_response

    def _reauthenticate(self):
        self._retry_counter += 1

        if self._retry_counter > self._max_retries:
            print("Maximum authentication retries ({}) exceeded. Exiting.".format(self._max_retries))
            exit(1)

        del self._session.cookies[".ASPXAUTH"]
        return self._authenticate()

    def _load_cookies(self):
        """
        Read the cookies cache from disk.
        :return: True on success.
        """
        if os.path.isfile(self._cookiejar) and os.stat(self._cookiejar).st_size != 0:
            with open(self._cookiejar, "rb") as f:
                self._session.cookies = pickle.load(f)
                logging.debug("Loaded cached cookies: {}".format(self._session.cookies))
        self._session.cookies.clear_expired_cookies()

        return True

    def _write_cookies(self):
        """
        Write the cookie cache to disk.
        :return: True on success.
        """
        with open(self._cookiejar, "wb") as f:
            pickle.dump(self._session.cookies, f, protocol=4)
            os.chmod(self._cookiejar, 0o600)

        # Files get written out as root when in daemon mode so this fixes that.
        if self._args.daemon:
            if os.path.isfile(self._cookiejar):
                user = pwd.getpwnam(self._args.username)
                os.chown(self._cookiejar, user.pw_uid, user.pw_gid)

        return True

    def _load_defaults(self):
        if self._config.get("defaults", None) and self._config["defaults"].get("centrify", None):
            for key, value in self._config["defaults"]["centrify"].items():
                self._defaults[key] = value

        message_displayed = False
        for required_default in self._required_defaults.keys():
            if required_default not in self._defaults.keys():
                if not message_displayed:
                    print("Required Centrify configuration keys not found. Please see documentation.")
                    print("You will now be prompted for the required configuration.")
                    message_displayed = True
                self._get_default(required_default)

    def _write_defaults(self):
        # Load config in again incase any other plugin has changed it since it was loaded.
        with open(self._args.config, "r") as fh:
            config = yaml.load(fh)

        if not config.get("defaults", None):
            config["defaults"] = {}

        if not config.get("centrify", None):
            config["defaults"]["centrify"] = {}

        for key, value in self._defaults.items():
            config["defaults"]["centrify"][key] = value

        with open(self._args.config, "w") as fh:
            yaml.dump(config, fh, default_flow_style=False)

    def _get_default(self, key):
        value = self._defaults.get(key, None)

        if not value:
            if key in self._required_defaults.keys():
                value = self._input("{} (required): ".format(self._required_defaults[key]), True)
                self._defaults_modified = True

        self._defaults[key] = value
        return self._defaults[key]

    def _input(self, prompt, required):
        i = input(prompt)

        # Keep prompting for required config.
        if required and not i:
            return self._input(prompt, required)

        # Return None for blank optional config.
        if not i:
            return None

        # Return i for valid required/optional input.
        return i

    def _delete_auth_cookie(self):
        """
        Delete the Centrify auth cookie and our expiration cookie from the CookieJar.
        :return: None
        """
        del self._session.cookies["cloudtoken_auth_expiration"]
        del self._session.cookies[".ASPXAUTH"]

    def _is_auth_cookie_expired(self):
        """
        Check if the auth cookie has expired according to cookie "cloudtoken_auth_expiration".
        :return: True on cookie expiration, False otherwise.
        """
        cookie_value = int(self._session.cookies.get("cloudtoken_auth_expiration", 0))

        # Add 60 seconds on to give ourselves some buffer.
        expiration_time = int(time.time() + 60)

        if cookie_value >= expiration_time:
            return False

        return True

    def _ask_to_write_defaults(self):
        input_string = "Would you like to write out your config file with the details you have entered (y/n)? "
        i = self._input(input_string, required=True)

        i = i.lower()

        if i not in ["y", "n", "yes", "no"]:
            i = self._ask_to_write_defaults()

        if i in ["y", "yes"]:
            self._write_defaults()

        return i

    def execute(self, data, args, flags):
        self._args = args
        self._cookiejar = "{}/cookiejar".format(args.cloudtoken_dir)
        self._load_cookies()

        # Load defaults if they exist.
        self._load_defaults()

        self._set_tenant_url()

        if ".ASPXAUTH" in self._session.cookies:
            logger.debug("Found existing auth cookie.")
            if self._is_auth_cookie_expired():
                self._delete_auth_cookie()
                logger.debug("Auth cookie has expired. Performing full authentication flow.")
                saml_response = self._authenticate()
            else:
                t = int(self._session.cookies["cloudtoken_auth_expiration"])
                valid_until = time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.gmtime(t))
                logger.debug("Auth token valid until {} UTC. Will not reauthenticate.".format(valid_until))
                saml_response = self._get_saml(self._session.cookies[".ASPXAUTH"])

        else:
            logger.debug("No auth cookie found. Performing full authentication flow.")
            saml_response = self._authenticate()

        # Cache cookies to disk.
        self._write_cookies()

        # If prompted for required config then write it out to disk.
        if self._defaults_modified:
            self._ask_to_write_defaults()

        data.append({"plugin": self._name, "data": saml_response})
        return data
