#!/usr/bin/env python3
"""Script to set up an environment for the toolbelt"""
from os import path
import yaml
# Must be set before pkg_resources import
#__requires__ = ["argus_cli > 0.5"] 
import pkg_resources

DEFAULT_SETTING_LOCATION = path.join(path.expanduser("~"), ".argus_cli.yaml")
LOGGING_TEMPLATE = pkg_resources.resource_filename("argus_cli", "resources/logging_settings.yaml")


def default_input(prompt, default):
    """Wrapper for input() with default value

    :param prompt: Prompt text
    :param default: Value to default to
    :return: User input or default value
    :rtype: str
    """
    return input("%s [%s]: " % (prompt, default)) or default


def mandatory_input(prompt, error="An answer is required!"):
    """Wrapper for input() that requires a value

    :param prompt: Propt text
    :param error: Error message to display if the user did not provide an input
    :return: User input
    :rtype: str
    """
    answer = input("%s: " % prompt)
    while not answer:
        print(error)
        answer = input("%s: " % prompt)

    return answer


def multiple_input(prompt, repeat_text="Add more?"):
    """Wrapper for input() that gets multiple values

    :param prompt: Prompt text
    :param repeat_text: Add more items prompt text
    :return: User inputs
    :rtype: list
    """
    answer = []
    keep_going = True
    while keep_going:
        answer.append(mandatory_input(prompt))
        keep_going = default_input(repeat_text, "no")

        if keep_going == "yes" or keep_going == "y":
            keep_going = True
        else:
            keep_going = False

    return answer


def api_setup():
    """Creates settings for argus_api

    :return: Settings for argus_api
    :rtype: dict
    """
    print("\n--- Argus API Setup ---\n")
    settings = {}

    settings["api_url"] = default_input("Enter the API url", "https://portal.mnemonic.no")

    auth_method = default_input("Do you want to use: apikey, ldap, totp, or radius?", "apikey")
    settings["method"] = auth_method
    if auth_method == "apikey":
        settings["api_key"] = mandatory_input("Enter your API key")
    else:
        settings["username"] = mandatory_input("Enter your username")
        settings["password"] = mandatory_input("Enter your password")

    return settings


def cli_setup():
    """Creates settings for argus_cli

    :return: Settings for argus_cli
    :rtype: dict
    """
    print("\n--- Argus CLI Setup ---\n")
    settings = {}

    settings["plugins"] = multiple_input("Enter a plugin directory", "Add more directories?")

    return settings


def logging_setup():
    """Creates settings for logging

    :returns: The logging template
    :rtype: dict
    """
    print("\n--- Logging setup ---\n")
    with open(LOGGING_TEMPLATE, 'r') as f:
        template = yaml.load(f)["logging"]

    template["handlers"]["console"]["level"] = default_input("What logging level do you want?", "INFO")
    template["handlers"]["console"]["formatter"] = default_input("Do you want simple or verbose logging?", "simple")

    return template


def create_settings_file(location, data):
    """Dumps the settings to a YAML file

    :param str location: Where to place the settings file
    :param dict data: Data to populate the file with
    """
    print("Writing settings...")

    with open(location, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, indent=4)

    print("Settings writen to file.")


def main():
    """Main function of the """
    print("\n--- Argus Toolbelt Setup ---\n")

    settings_location = default_input("Where do you want to store your settings?", DEFAULT_SETTING_LOCATION)

    settings = {
        "api": api_setup(),
        "cli": cli_setup(),
        "logging": logging_setup(),
    }

    create_settings_file(settings_location, settings)
    print("\n--- Done! Have fun! ---\n")


if __name__ == "__main__":
    main()
