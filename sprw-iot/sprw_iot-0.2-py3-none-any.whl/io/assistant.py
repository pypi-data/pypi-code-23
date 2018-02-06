import datetime
import boto3
import json
import requests
from contextlib import closing
from pprint import pprint
import time
import pygame
from random import randint
import sys
from .config import Config
from easydict import EasyDict as edict
from .exceptions import ValidationError, NetworkError, ServerError, Error

class Assistant:

    """Used for Home Assistant functionalities.

    Using the access token generated in the SPRW IoT Dashboard, the class can be instantiated.

    Example:
        The following example shows how to instantiate this class::

            from sprw.io import Assistant
            ACCESS_TOKEN = '<your-access-token>'
            assistant = Assistant(ACCESS_TOKEN)

    Attributes:
        access_token (int): Access token used to communincate with the SPRW IoT Server.

    """

    __aws_credentials = None
    
    __datetime_format = None
    __polly_client = None
    __initialised_assistant = False
    __voices = None
    
    __headers = None
    __number_in_words = ["One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine",
        "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen", "Sixteen",
        "Seventeen", "Eighteen", "Nineteen", "Twenty", "Twenty one",
        "Twenty two", "Twenty three", "Twenty four", "Twenty five",
        "Twenty six", "Twenty seven", "Twenty eight", "Twenty nine", "Thirty",
        "Thirty one", "Thirty two", "Thirty three", "Thirty four", "Thirty five", "Thirty six",  "Thirty seven",
        "Thirty eight", "Thirty nine", "Fourty", "Fourty one", "Fourty two", "Fourty three", "Fourty four", "Fourty five", "Fourty six", "Fourty seven",
        "Fourty eight", "Fourty nine", "Fifty", "Fifty one", "Fifty two", "Fifty three", "Fifty four", "Fifty five", "Fifty six", "Fifty seven", "Fifty eight", "Fifty nine"
    ]
    __month_in_words = ['January', 'February', 'March', 'April', 'May', 
        'June', 'July', 'August', 'September',
        'October', 'Novemeber', 'December'
    ]

    __network_error_message = 'Please check your internet connection. Could not connect with ' + Config.APP_URL
    __server_error_message = 'SPRW Server Error'
    __generic_error_message = 'Failed to communicate with the server'

    def __init__(self, access_token):
        Config.set_access_token(access_token)
        self.__set_access_token(access_token)
        self.__initialise_assistant()

    def __set_access_token(self, access_token):
        self.access_token = access_token
        self.__headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + access_token
        }

    def __get_error_message(self, status_code):
        error_message = {
            'error': 'Failed to communicate with the server',
            'status_code': status_code
        }
        return error_message
    
    def __get_status_message(self, status, message):
        speech_status = {
            'status': status,
            'message': message
        }
        return speech_status

    def __initialise_assistant(self):
        self.__fetch_aws_credentials()
        

        self.__polly_client = boto3.client(
            'polly',
            aws_access_key_id=self.__aws_credentials.access_key_id,
            aws_secret_access_key=self.__aws_credentials.secret_key,
            region_name=self.__aws_credentials.region_name
        )
        
        self.__initialised_assistant = True
        self.__voices = self.get_voices()

    
    def get_voices(self):

        """Returns the list of voices that are available for use.

        Returns:
            list: A list of dictionaries containing different voices with their properties.

        Example:

            The following example shows how to delete a thing::

                voices = assistant.get_voices()
                print(voices)

            **Expected Output**::

                [
                    {
                        "Gender": "Female",
                        "Id": "Joanna",
                        "LanguageCode": "en-US",
                        "LanguageName": "US English",
                        "Name": "Joanna"
                    },
                    {
                        "Gender": "Female",
                        "Id": "Salli",
                        "LanguageCode": "en-US",
                        "LanguageName": "US English",
                        "Name": "Salli"
                    },
                   ...
                ]
        """

        polly_voices = []

        response = self.__polly_client.describe_voices(LanguageCode='en-US')
        for voice in response['Voices']:

            polly_voices.append(voice)
        
        response = self.__polly_client.describe_voices(LanguageCode='en-GB')
        
        for voice in response['Voices']:

            polly_voices.append(voice)

        response = self.__polly_client.describe_voices(LanguageCode='en-AU')
        
        for voice in response['Voices']:
            polly_voices.append(voice)
        
        response = self.__polly_client.describe_voices(LanguageCode='en-IN')

        for voice in response['Voices']:
            polly_voices.append(voice)
        # sorted_voice_list = sorted(
        #     response['Voices'], key=lambda k: k['LanguageCode'])
        return polly_voices

    def speak(self, text, voice_id='Joanna'):

        """Speaks the given text.

        Parameters:
            text (str): Text to speak.
            voice_id (str, optional): The voice Id to be used. 

        Returns:
            dict: A dictionary containing the status of the text to speech conversion.

        Example:

            The following example shows how to delete a thing::

                status = assistant.speak('Hii! Hello. Welcome!')
                print(status)
                # status = assistant.speak('Hii! Hello. Welcome!', 'Amy')
                # print(status)
        
            **Expected Output**::

                {'status': 'SUCCESS', 'message': 'Speech Completed'}


        """
        # voice_index = voice_index - 1

        # if ((voice_index < 0) or (voice_index > len(self.__voices) - 1)):
        #     return self.__get_status_message('ERROR', 'Invalid voice id. Please specify a voice id between 1 to ' + str(len(self.__voices)))

        # voice = self.__voices[voice_index]

        if not any(voice['Id'] == voice_id for voice in self.__voices):
            raise ValidationError(422, 'Invalid Voice Id')

        if not self.__initialised_assistant:
            self.__initialise_assistant()

        response = self.__polly_client.synthesize_speech(
            OutputFormat='ogg_vorbis',
            Text=text,
            TextType='text',
            VoiceId=voice_id,
        )
        
        if "AudioStream" in response:
            with closing(response["AudioStream"]) as stream:
                output_mp3 = "speech.ogg"

                try:
                    # Open a file for writing the output as a binary stream
                    with open(output_mp3, "wb") as file:
                        file.write(stream.read())
                    pygame.mixer.init()
                    pygame.mixer.music.load(output_mp3)
                    pygame.mixer.music.play()
                    
                    while pygame.mixer.music.get_busy():
                        pygame.time.Clock().tick(10)

                except IOError as error:
                    raise error

        else:
            return self.__get_status_message('ERROR', 'No audio stream received from server')

        return self.__get_status_message('SUCCESS', 'Speech Completed')
    
    def get_current_datetime(self):
        """Return the current local date and time.

        Returns:
            datetime: Object containing current local date and time.

        Example:
            The following example shows how to retreive the current date and time::
                
                now = assistant.get_current_datetime()
                print(now)

            **Expected Output**::

                2017-12-31 16:23:46.391277

        """

        return datetime.datetime.now()

    def datetime_offset(self, days=0, seconds=0, microseconds=0, milliseconds=0, minutes=0, hours=0, weeks=0):
        """Returns a duration which can be used for manipulating dates and times.
        
        All parameters are optional and default to 0. Parameters may be ints, longs, or floats, and may be positive or negative.

        Parameters:
            days: Number of days.
            seconds: Number of seconds.
            microseconds: Number of microseconds.
            milliseconds: Number of milliseconds.
            minutes: Number of minutes.
            hours: Number of minutes.
            weeks: Number of weeks.

        Returns:
            datetime.timedelta: A timedelta object representing a duration.


        Example:
            The following example shows how to add certain duration to a datetime::
                
                now = assistant.get_current_datetime()
                print(now)
                updated_time = now + assistant.datetime_offset(hours=2)
                print(updated_time)

            **Expected Output**::

                2017-12-31 16:23:46.391277
                2017-12-31 18:23:46.391277

        """  
        return datetime.timedelta(days=days, seconds=seconds, microseconds=microseconds,
            milliseconds=milliseconds, minutes=minutes, hours=hours, weeks=weeks)

    # def convert_to_datetime(self, time):
        
    #     return datetime.datetime.strptime(time, "%Y-%m-%d %I:%M %p")
    
    def get_time_in_words(self, hours=0, minutes=0):
        
        """Returns the time specified using hours and minutes in words format.
        
        Parameters:
            hours: Number of hours
            minutes: Number of minutes
        
        Returns:
            str: Time in words

        Example:
            The following example shows how to convert the given time to words::
                
                now = assistant.get_current_datetime()
                print(now)
                time_in_words = assistant.get_time_in_words(now.hour, now.minute)
                print(time_in_words)

            **Expected Output**::

                2017-12-31 16:23:46.391277
                Four Twenty three PM

        """
        if ((hours < 0) or (hours > 23)):
            return self.__get_status_message('ERROR', 'Hours should be between 0 to 23')
        if ((minutes < 0) or (minutes > 59)):
            return self.__get_status_message('ERROR', 'Minutes should be between 0 to 59')
        msg = ""

        hours_in_12 = hours % 12
        if (hours_in_12 == 0):
            hours_in_12 = 12

        if (minutes == 0):
            hour_in_words = self.__number_in_words[hours_in_12 - 1]
            msg = hour_in_words + " o'clock"  # in the morn,eve,afternoon,nite
            if (hours == 0):
                msg = msg + " in the midnight"
            elif (hours > 0 and hours < 12):
                msg = msg + " in the morning"
            elif (hours == 12):
                msg = msg + " in the noon"
            elif (hours > 12 and hours < 17):
                msg = msg + " in the afternoon"
            elif (hours >= 17 and hours < 20):
                msg = msg + " in the evening"
            elif (hours >= 20 and hours < 24):
                msg = msg + " in the night"


        else:
            time_meridian = ''
            if hours >= 0 and hours < 12:
                time_meridian = 'AM'
            else:
                time_meridian = 'PM'
            hour_in_words = self.__number_in_words[hours_in_12 - 1]
            minutes_in_words = self.__number_in_words[(minutes - 1)]

            minutes_in_words = self.__number_in_words[(minutes - 1)]
            msg = str(hour_in_words) + ' ' + \
                str(minutes_in_words) + ' ' + time_meridian

            # hour_in_words = self.words[hours_in_12 - 1]
            # minutes_in_words = self.words[(60 - minutes - 1)]
            # msg = header + minutes_in_words + " to " + hour_in_words + "."

        return msg

    # def get_time_in_words(self, time):
    #     hours = time.hour
    #     minutes = time.minute

    #     if ((hours < 0) or (hours > 23)):
    #         return self.__get_status_message('ERROR', 'Hours should be between 0 and 23')
    #     if ((minutes < 0) or (minutes > 59)):
    #         return self.__get_status_message('ERROR', 'Minutes should be between 0 and 59')
        
    #     msg = ""

    #     hours_in_12 = hours % 12
    #     if (hours_in_12 == 0):
    #         hours_in_12 = 12

    #     if (minutes == 0):
    #         hour_in_words = self.__number_in_words[hours_in_12 - 1]
    #         msg = hour_in_words + " o'clock"  # in the morn,eve,afternoon,nite
    #         if (hours == 0):
    #             msg = msg + " in the midnight"
    #         elif (hours > 0 and hours < 12):
    #             msg = msg + " in the morning"
    #         elif (hours == 12):
    #             msg = msg + " in the noon"
    #         elif (hours > 12 and hours < 17):
    #             msg = msg + " in the afternoon"
    #         elif (hours >= 17 and hours < 20):
    #             msg = msg + " in the evening"
    #         elif (hours >= 20 and hours < 24):
    #             msg = msg + " in the night"

    #     else:
    #         time_meridian = ''
    #         if hours >= 0 and hours < 12:
    #             time_meridian = 'AM'
    #         else:
    #             time_meridian = 'PM'
    #         hour_in_words = self.__number_in_words[hours_in_12 - 1]
    #         minutes_in_words = self.__number_in_words[(minutes - 1)]

    #         minutes_in_words = self.__number_in_words[(minutes - 1)]
    #         msg = str(hour_in_words) + ' ' + \
    #             str(minutes_in_words) + ' ' + time_meridian

    #         # hour_in_words = self.words[hours_in_12 - 1]
    #         # minutes_in_words = self.words[(60 - minutes - 1)]
    #         # msg = header + minutes_in_words + " to " + hour_in_words + "."

    #     return msg
    # def get_month_in_words(self, date):
    #     month_number = date.month
    #     month_text = self.__month_in_words[month_number-1]
    #     return month_text

    def get_month_in_words(self, month_number):
        
        """Returns the name of the month for the given month number.
        
        Parameters:
            month_number: Month Number
        
        Returns:
            str: Name of the month

        Example:
            The following example shows how to convert the given month number to name::
                
                now = assistant.get_current_datetime()
                print(now)
                
                month = assistant.get_month_in_words(now.month)
                print(month)

            **Expected Output**::

                2017-12-31 16:23:46.391277
                December

        """

        if ((month_number < 1) or (month_number > 12)):
            return self.__get_status_message('ERROR', 'Month should be between 1 and 12')

        month_text = self.__month_in_words[month_number - 1]
        return month_text
    
    def get_random_message(self, message_list):
        """Returns a random message chosen from the given list.
        
        Parameters:
            message_list (list): List of messages.
        
        Returns:
            str: A randomly selected message.
        
        Example:
            
            The following example shows how to retrieve a random message from a list of messages::
                
                messages = [
                    "Hello", "Hi", "Test", "Testing", "Good", "Bye"
                ]

                random_message = assistant.get_random_message(messages)
                print(random_message)

            **Expected Output**::

                Test

        """

        max_range = len(message_list) - 1
        random_index = randint(0, max_range)
        return message_list[random_index]
    
    def __fetch_aws_credentials(self):
        try:
            json_response = requests.get(
                Config.SPRWIO_GATEWAY_URL + 'aws-credentials', headers=self.__headers)

        except requests.exceptions.ConnectionError:
            raise NetworkError(0, self.__network_error_message)

        try:
            response = edict(json.loads(json_response.text))
        except ValueError as e:
            raise ServerError(json_response.status_code,
                              self.__server_error_message)

        if json_response.status_code == 200 or json_response.status_code == 201:
            self.__aws_credentials = response.data
        elif json_response.status_code == 500:
            if hasattr(response, 'message'):
                raise ServerError(json_response.status_code, response.message)
            else:
                raise ServerError(json_response.status_code, response)

        else:
            raise Error(Exception(response))
