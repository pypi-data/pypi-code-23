#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
################################################################################
#                                                                              #
# megaparsex_example_1                                                         #
#                                                                              #
################################################################################
#                                                                              #
# LICENCE INFORMATION                                                          #
#                                                                              #
# This program is an example of megaparsex parsing.                            #
#                                                                              #
# copyright (C) 2017 William Breaden Madden                                    #
#                                                                              #
# This software is released under the terms of the GNU General Public License  #
# version 3 (GPLv3).                                                           #
#                                                                              #
# This program is free software: you can redistribute it and/or modify it      #
# under the terms of the GNU General Public License as published by the Free   #
# Software Foundation, either version 3 of the License, or (at your option)    #
# any later version.                                                           #
#                                                                              #
# This program is distributed in the hope that it will be useful, but WITHOUT  #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or        #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for     #
# more details.                                                                #
#                                                                              #
# For a copy of the GNU General Public License, see                            #
# <http://www.gnu.org/licenses/>.                                              #
#                                                                              #
################################################################################
"""

import time
import sys

import megaparsex

name    = "megaparsex_example_1"
version = "2018-02-12T1546Z"

def main():
    """
    Loop over a list of input text strings. Parse each string using a list of
    parsers, one included in megaparsex and one defined in this script. If a
    confirmation is requested, seek confirmation, otherwise display any response
    text and engage any triggered functions.
    """
    for text in [
        "how are you",
        "ip address",
        "restart",
        "run command",
        "rain EGPF",
        "reverse SSH"
        ]:
        print("\nparse text: " + text + "\nWait 3 seconds, then parse.")
        time.sleep(3)
        response = megaparsex.multiparse(
            text         = text,
            parsers      = [
                           megaparsex.parse,
                           parse_networking
                           ],
            help_message = "Does not compute. I can report my IP address and I "
                           "can restart my script."
        )
        if type(response) is megaparsex.confirmation:
            while response.confirmed() is None:
                response.test(
                    text = megaparsex.get_input(
                        prompt = response.prompt() + " "
                    )
                )
            if response.confirmed():
                print(response.feedback())
                response.run()
            else:
                print(response.feedback())
        elif type(response) is megaparsex.command:
            output = response.engage_command(
                command    = megaparsex.get_input(
                    prompt = response.prompt() + " "
                ),
                background = False
            )
            if output:
                print("output:\n{output}".format(output = output))
        else:
            print(response)

def parse_networking(
    text = None
    ):
    triggers = []
    triggers.extend([
        megaparsex.trigger_keyphrases(
            text                          = text,
            keyphrases                    = [
                                            "reverse SSH",
                                            "reverse ssh"
                                            ],
            function                      = megaparsex.engage_command,
            kwargs                        = {"command": "ssh -R 10000:localhost:22 www.sern.ch"},
            confirm                       = True,
            confirmation_prompt           = "Do you want to reverse SSH "
                                            "connect? (y/n)",
            confirmation_feedback_confirm = "confirm reverse SSH connect",
            confirmation_feedback_deny    = "deny reverse SSH connect"
        )
    ])
    if any(triggers):
        responses = [response for response in triggers if response]
        if len(responses) > 1:
            return responses
        else:
            return responses[0]
    else:
        return False

if __name__ == "__main__":

    main()
