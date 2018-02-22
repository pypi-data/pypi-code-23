import requests
import datetime
import json
from .config import Config
from easydict import EasyDict as edict
from .exceptions import ValidationError, NetworkError, ServerError, Error
import copy
class IOT:


    """Used for communicating with the SPRW IoT Server.

    Using the access token generated in the SPRW IoT Dashboard, the class can be instantiated.

    Example:
        The following example shows how to instantiate this class::

            from sprw.io import IOT
            ACCESS_TOKEN = '<your-access-token>'
            sp_server = IOT(ACCESS_TOKEN)

    Attributes:
        access_token (int): Access token used to communincate with the SPRW IoT Server.

    """

    __headers = None;
    __network_error_message = 'Please check your internet connection. Could not connect with ' + Config.APP_URL
    __server_error_message = 'SPRW Server Error'
    __generic_error_message = 'Failed to communicate with the server'

    
    def __init__(self, access_token):
        
        Config.access_token = access_token
        self.set_access_token(access_token)


    def set_access_token(self, access_token):
        """Sets the access token which will be used to communicate with the SPRW IoT Server.
        
        Parameters:
            access_token (str): Access token generated in IoT Dashboard.  
        """
        self.access_token = access_token
        self.__headers = {
            'Accept': 'application/json',
	        'Authorization' : 'Bearer ' + self.access_token
    }

    def get_things(self):
            
        """Returns the list of created things
        
        Returns:
            list: A list of dictionaries which maps various attributes of the things with corresponding values.

        Example:
            
            The following example shows how to retreive all the created things::
                
                things = sp_server.get_things()
                iotprint(things)

            **Expected Output**::

                [
                    {
                        "attributes": [],
                        "category": "INPUT_DEVICE",
                        "created_at": {
                            "date": "2017-11-13 15:02:56.000000",
                            "timezone": "UTC",
                            "timezone_type": 3
                        },
                        "description": null,
                        "desired_state": {
                            "value": 0
                        },
                        "device": "BUTTON",
                        "id": 1,
                        "name": "Light Switch",
                        "reported_state": {
                            "value": 0
                        },
                        "updated_at": {
                            "date": "2017-11-13 15:08:16.000000",
                            "timezone": "UTC",
                            "timezone_type": 3
                        }
                    },
                    {
                        "attributes": [],
                        "category": "OTHERS",
                        "created_at": {
                            "date": "2017-11-13 15:02:56.000000",
                            "timezone": "UTC",
                            "timezone_type": 3
                        },
                        ...
                        ...
                    },
                    ...
                ]

        """
        try:
            json_response = requests.get(Config.SPRWIO_GATEWAY_URL + 'things', headers=self.__headers);

        except requests.exceptions.ConnectionError:
            raise NetworkError(0, self.__network_error_message)

        try:
            response = edict(json.loads(json_response.text))
        except ValueError as e:
            raise ServerError(json_response.status_code,
                              self.__server_error_message)

        if json_response.status_code == 200 or json_response.status_code == 201:
            return response.data
        elif json_response.status_code == 422:
            raise ValidationError(json_response.status_code,
                                  response)
        elif json_response.status_code == 500:
            if hasattr(response, 'message'):
                raise ServerError(json_response.status_code, response.message)
            else:
                raise ServerError(json_response.status_code, response)

        else:
            raise Error(Exception(response))



    def get_thing(self, thing_id):
        
        """Returns the thing specified by the ``thing_id``.

        Parameters:
            thing_id (int): Id of the thing which is to be retreived 
        Returns:
            dict: A dictionary mapping various attributes with corresponding values of the thing.
        Example:
            The following example shows how to retreive a thing using thing id::
            
                led_thing = sp_server.get_thing(2)
                iotprint(led_thing)
            
            **Expected Output**::

                {
                    "attributes": {
                        "pin_number": "2"
                    },
                    "category": "INPUT_DEVICE",
                    "created_at": {
                        "date": "2017-12-29 13:16:34.000000",
                        "timezone": "UTC",
                        "timezone_type": 3
                    },
                    "description": null,
                    "desired_state": {
                        "value": 0
                    },
                    "device": "BUTTON",
                    "id": 20,
                    "name": "My Switch",
                    "reported_state": {
                        "value": 0
                    },
                    "updated_at": {
                        "date": "2017-12-29 13:16:34.000000",
                        "timezone": "UTC",
                        "timezone_type": 3
                    }
                }

        """
        try:
            json_response = requests.get(Config.SPRWIO_GATEWAY_URL + 'things/' + str(thing_id), headers=self.__headers);

        except requests.exceptions.ConnectionError:
            raise NetworkError(0, self.__network_error_message)

        try:
            response = edict(json.loads(json_response.text))
        except ValueError as e:
            raise ServerError(json_response.status_code,
                              self.__server_error_message)

        if json_response.status_code == 200 or json_response.status_code == 201:
            return response.data
        
        elif json_response.status_code == 422:
            raise ValidationError(json_response.status_code,
                                  response)
        elif json_response.status_code == 500:
            if hasattr(response, 'message'):
                raise ServerError(json_response.status_code, response.message)
            else:
                raise ServerError(json_response.status_code, response)

        else:
            raise Error(Exception(response))

    def create_thing(self, name, category, device, **kwargs):

        """Creates a thing with the specified parameters.

        Parameters:
            name (str): Unique name for the thing.
            category (str): Category of the thing. Should be one of the following: 
                ``INPUT_DEVICE``, 
                ``OUTPUT_DEVICE``, 
                ``OTHERS``.
            device (str): Type of device. Should be one of the following: 
                ``DIGITAL_IP``
                ``ANALOG_IP``,
                ``BUTTON``,
                ``PROXIMITY``,
                ``LIGHT``,
                ``TEMPERATURE``,
                ``LED``,
                ``RGB_LED``,
                ``MOTOR``,
                ``DIGITAL_OP``,
                ``PWM_OP``,
                ``ASSISTANT``

        Following is the list of devices corresponding to each category,
        
        +------------------------+-----------------------------------+
        | Category               | Device                            |
        |                        |                                   |
        +========================+===================================+
        | INPUT_DEVICE           | DIGITAL_IP                        |
        |                        +-----------------------------------+
        |                        | ANALOG_IP                         |
        |                        +-----------------------------------+
        |                        | BUTTON                            |
        |                        +-----------------------------------+
        |                        | PROXIMITY                         |
        |                        +-----------------------------------+
        |                        | LIGHT                             |
        |                        +-----------------------------------+                        
        |                        | TEMPERATURE                       |
        +------------------------+-----------------------------------+        
        | OUTPUT_DEVICE          | DIGITAL_OP                        |                
        |                        +-----------------------------------+
        |                        | PWM_OP                            |
        |                        +-----------------------------------+              
        |                        | MOTOR                             |
        |                        +-----------------------------------+  
        |                        | LED                               |
        |                        +-----------------------------------+
        |                        | RGB_LED                           |
        +------------------------+-----------------------------------+
        | OTHERS                 | ASSISTANT                         |
        +------------------------+-----------------------------------+        

        
        Keyword Arguments:
            any_user_defined_attribute : Keyword arguments (key-value pairs) of any other custom attributes to be set for the thing.
                
                **Example**::

                    pin_number = 2, color='BLUE'
        
        Returns:
            dict: A dictionary mapping various attributes with corresponding values of the thing.

        Example:

            The following example shows how to create a thing::

                button_thing = sp_server.create_thing('My Button', 'INPUT_DEVICE', 'BUTTON', pin_number = 2, color='BLUE')
                iotprint(button_thing)
            
            **Expected Output**::

                {
                    "attributes": {
                        "pin_number": "2",
                        "color": "BLUE"
                    },
                    "category": "INPUT_DEVICE",
                    "created_at": {
                        "date": "2017-12-29 13:16:34.000000",
                        "timezone": "UTC",
                        "timezone_type": 3
                    },
                    "description": null,
                    "desired_state": {
                        "value": 0
                    },
                    "device": "BUTTON",
                    "id": 20,
                    "name": "My Button",
                    "reported_state": {
                        "value": 0
                    },
                    "updated_at": {
                        "date": "2017-12-29 13:16:34.000000",
                        "timezone": "UTC",
                        "timezone_type": 3
                    }
                }

        """

        data_dict = dict()

        data_dict['name'] = name
        data_dict['category'] = category
        data_dict['device'] = device
        for key in kwargs:

            data_dict['attributes[' + key + ']'] = kwargs[key]

        try:
            json_response = requests.post(Config.SPRWIO_GATEWAY_URL + 'things', headers=self.__headers, data=data_dict)

        except requests.exceptions.ConnectionError:
            raise NetworkError(0, self.__network_error_message)

        try:
            response = edict(json.loads(json_response.text))
        except ValueError as e:
            raise ServerError(json_response.status_code,
                              self.__server_error_message)
       
        if json_response.status_code == 200 or json_response.status_code == 201:
            return response.data
        elif json_response.status_code == 422:
            raise ValidationError(json_response.status_code,
                                  response)
        elif json_response.status_code == 500:
            if hasattr(response, 'message'):
                raise ServerError(json_response.status_code, response.message)
            else:
                raise ServerError(json_response.status_code, response)

        else:
            raise Error(Exception(response))

    def delete_thing(self, thing_id):
        
        """Deletes the thing specified by the ``thing_id``.

        Parameters:
            thing_id (int): Id of the thing which is to be deleted 
        Returns:
            dict: Dictionary containing the status and message of the delete operation.

        Example:

            The following example shows how to delete a thing::

                status = sp_server.delete_thing(thing_id=button_thing.id)
                print(status)
                
            **Expected Output**::

                {'message': 'Deleted'}
                

        """

        try:
            json_response = requests.delete(Config.SPRWIO_GATEWAY_URL + 'things/' + str(thing_id), headers=self.__headers, data={'id' : thing_id});
        except requests.exceptions.ConnectionError:
            raise NetworkError(0, self.__network_error_message)

        try:
            response = edict(json.loads(json_response.text))
        except ValueError as e:
            raise ServerError(json_response.status_code,
                              self.__server_error_message)

        if json_response.status_code == 200 or json_response.status_code == 201:
            return response
        elif json_response.status_code == 422:
            raise ValidationError(json_response.status_code,
                                  response)
        elif json_response.status_code == 500:
            if hasattr(response, 'message'):
                raise ServerError(json_response.status_code, response.message)
            else:
                raise ServerError(json_response.status_code, response)

        else:
            raise Error(Exception(response))

    def update_thing_state_attributes(self, thing_id, **kwargs):
        
        """Updates the state attributes of the thing specified by the ``thing_id``.

        Parameters:
            thing_id (int): Id of the thing whose state is to be updated.
        
        Keyword Arguments:
            state_attributes : Keyword arguments (key-value pairs) of the state attributes to be set for the thing.
                
                **Examples**::

                    1. value = 1
                    2. value = 0.5
                    3. value_r = 0.5
                    4. direction = 'FORWARD'

                Following is the list of state attributes applicable for the IoT Devices.
                
                +------------------------+-------------------+----------------+
                | Device                 | State attribute   | State attribute|
                |                        | name              | value range    |
                +========================+===================+================+
                | All Input Devices      | value             | User-defined   |
                +------------------------+-------------------+----------------+        
                | LED                    | value             | 0 to 1         |                
                +------------------------+-------------------+----------------+
                | RGB_LED                | value_r, value_g, | 0 to 1         |
                |                        | value_b           |                |
                +------------------------+-------------------+----------------+        
                | PWM_OP                 | value             | 0 to 1         |
                +------------------------+-------------------+----------------+        
                | MOTOR                  | direction         |'FORWARD',      |
                |                        |                   |'BACKWARD',     |
                |                        |                   |'STOP'          |                
                +------------------------+-------------------+----------------+        
                | DIGITAL_OP             | value             | 0 or 1         |
                +------------------------+-------------------+----------------+        
   

        Returns:
            dict: Dictionary containing the status of the update operation.

        Example:

            The following example shows how to update state attributes of a thing::

                led_thing = sp_server.create_thing('LED 1', 'OUTPUT_DEVICE', 'LED', pin_number = 3, color='Red')
                status = sp_server.update_thing_state_attributes(thing_id=led_thing.id, value=0.5)           
                print(status)


            **Expected Output**::

                {'message': 'State saved'}

        """

        state_json = json.dumps(kwargs)

        try:
            json_response = requests.post(Config.SPRWIO_GATEWAY_URL + 'things/' + str(thing_id) + '/states', headers=self.__headers, data={'id': thing_id, 'state_type': 'REPORTED', 'state': state_json})
        
        except requests.exceptions.ConnectionError:
            raise NetworkError(0, self.__network_error_message)

        try:
            response = edict(json.loads(json_response.text))
        except ValueError as e:
            raise ServerError(json_response.status_code,
                              self.__server_error_message)

        if json_response.status_code == 200 or json_response.status_code == 201:
            return response
        elif json_response.status_code == 422:
            raise ValidationError(json_response.status_code,
                                  response)
        elif json_response.status_code == 500:
            if hasattr(response, 'message'):
                raise ServerError(json_response.status_code, response.message)
            else:
                raise ServerError(json_response.status_code, response)

        else:
            raise Error(Exception(response))

    def update_thing_custom_attributes(self, thing_id, **kwargs):
        
        """Updates the custom attributes of the thing specified by the ``thing_id``.

        Parameters:
            thing_id (int): Id of the thing which is to be deleted.
        
        Keyword Arguments:
            any_user_defined_attribute : Keyword arguments (key-value pairs) of any other custom attributes to be set for the thing.
                
                **Example**::

                    pin_number = 2, color='BLUE'    
        
        Returns:
            dict: Dictionary containing the status of the update operation.

        Example:

            The following example shows how to update custom attributes of a thing::

                motor_thing = sp_server.create_thing('My Motor', 'OUTPUT_DEVICE', 'MOTOR')
                
                status = sp_server.update_thing_custom_attributes(thing_id = motor_thing.id, rpm = 150)
                print(status)
               
            
            **Expected Output**::

                {'message': 'Attributes saved'}

        """

        data_dict = dict()
        for key in kwargs:
            data_dict['attributes[' + key + ']'] = kwargs[key]

        try:
            json_response = requests.post(Config.SPRWIO_GATEWAY_URL + 'things/' + str(thing_id) + '/attributes', headers=self.__headers, data=data_dict);
        except requests.exceptions.ConnectionError:
            raise NetworkError(0, self.__network_error_message)

        try:
            response = edict(json.loads(json_response.text))
        except ValueError as e:
            raise ServerError(json_response.status_code,
                              self.__server_error_message)

        if json_response.status_code == 200 or json_response.status_code == 201:
            return response
        elif json_response.status_code == 422:
            raise ValidationError(json_response.status_code,
                                  response)
        elif json_response.status_code == 500:
            if hasattr(response, 'message'):
                raise ServerError(json_response.status_code, response.message)
            else:
                raise ServerError(json_response.status_code, response)

        else:
            raise Error(Exception(response))

    def update_thing_multi_state_attributes(self, thing_id, **kwargs):
        
        """Updates the multi-state attributes of the thing specified by the ``thing_id``.

        Parameters:
            thing_id (int): Id of the thing which is to be deleted.
        
        Keyword Arguments:
            reminder : Reminder to be created (or) updated. Following are the attributes for a reminder,
                

                    id (int): Id of the reminder.
                    name (str): Name of the reminder.
                    message (str): Message for the reminder.abs
                    time (datetime): Time of the reminder.                     
                
        Returns:
            dict: Dictionary containing the status of the update operation.

        Example:

            The following example shows how to update multi-state attributes of a thing::

                assistant_thing = sp_server.create_thing('My Assistant', 'OTHERS', 'ASSISTANT')

                reminder_condition = {
                    'time': '2017-12-25 4:05 PM',
                    'status' : 'ACTIVE'
                }

                multi_state_attributes = sp_server.get_thing_multi_state_attributes(
                    thing_id=2, reminder_condition=reminder_condition)

                reminders = multi_state_attributes.reminders

                reminder_to_update = reminders[0]
                reminder_to_update.status = 'DISMISSED'
                status = sp_server.update_thing_multi_state_attributes(thing_id=assistant_thing.id, reminder=reminder_to_update)
                print(status)
               
            
            **Expected Output**::

                {'message': 'State saved'}

        """

        kwargs_copy = copy.deepcopy(kwargs)
        for key in kwargs_copy:
            if (key == 'reminder'):
                if isinstance(kwargs_copy[key], dict):
                    kwargs_copy[key] = edict(kwargs_copy[key])
                if isinstance(kwargs_copy[key].time, datetime.datetime):
                    datetime_without_seconds = kwargs_copy[key].time.replace(
                         second=0, microsecond=0)
                    
                    kwargs_copy[key].time = self.__convert_datetime_to_str(
                        datetime_without_seconds)
              
        state_json = json.dumps(kwargs_copy),

        try:
            json_response = requests.post(Config.SPRWIO_GATEWAY_URL + 'things/' + str(thing_id) + '/states', headers=self.__headers, data={'id' : thing_id, 'state_type' : 'REPORTED', 'state' : state_json});
        except requests.exceptions.ConnectionError:
            raise NetworkError(0, self.__network_error_message)

        try:
            response = edict(json.loads(json_response.text))
        except ValueError as e:
            raise ServerError(json_response.status_code,
                              self.__server_error_message)

        if json_response.status_code == 200 or json_response.status_code == 201:
            return response
        elif json_response.status_code == 422:
            raise ValidationError(json_response.status_code,
                                  response)
        elif json_response.status_code == 500:
            if hasattr(response, 'message'):
                raise ServerError(json_response.status_code, response.message)
            else:
                raise ServerError(json_response.status_code, response)

        else:
            raise Error(Exception(response))
    
    def get_thing_state_attributes(self, thing_id) :
        
        """Returns the state attributes of the thing specified by the ``thing_id``.

        Parameters:
            thing_id (int): Id of the thing whose state attributes are to be retreived.

        Returns:
            dict: Dictionary containing the state attributes of the thing.

        Example:

            The following example shows how to retreive the state attributes of a thing::

                led_thing = sp_server.create_thing('LED 1', 'OUTPUT_DEVICE', 'LED', pin_number = 3, color='Red')
                thing_state = sp_server.get_thing_state_attributes(thing_id=led_thing.id)
                print(thing_state)
               
            
            **Expected Output**::

                {'value': 0}


        """

        try:
            json_response = requests.get(Config.SPRWIO_GATEWAY_URL + 'things/' + str(thing_id) + '/states', headers=self.__headers);
        except requests.exceptions.ConnectionError:
            raise NetworkError(0, self.__network_error_message)

        try:
            response = edict(json.loads(json_response.text))
        except ValueError as e:
            raise ServerError(json_response.status_code,
                              self.__server_error_message)

        if json_response.status_code == 200 or json_response.status_code == 201:
            return response.data.state
        elif json_response.status_code == 422:
            raise ValidationError(json_response.status_code,
                                  response)
        elif json_response.status_code == 500:    
            if hasattr(response, 'message'):
                raise ServerError(json_response.status_code, response.message)
            else:
                raise ServerError(json_response.status_code, response)

        else:
            raise Error(Exception(response))

    def get_thing_multi_state_attributes(self, thing_id, **kwargs) :

        """Returns the multi-state attributes of the thing specified by the ``thing_id``.

        Parameters:
            thing_id (int): Id of the thing whose state attributes are to be retreived.

        Keyword Arguments:
            reminder_condition : A dictionary containing the conditions based on which reminders should be retrieved.
                
                **Example**::

                    reminder_condition = {
                        'time': '2012-12-25 4:05 PM',
                        'status' : 'ACTIVE'
                    }
                    multi_states = sp_server.get_thing_multi_state_attributes(thing_id=2,
                        reminder_condition=reminder_condition)     

        Returns:
            dict: Dictionary containing the multi state attributes of the thing.

        
        Example:

            The following example shows how to retreive the multi-state attributes of a thing::

                reminder_condition = {
                    'time': '2017-12-25 04:05 PM',
                    'status' : 'ACTIVE'
                }

                multi_state_attributes = sp_server.get_thing_multi_state_attributes(thing_id=2, reminder_condition=reminder_condition)
                reminders = multi_state_attributes.reminders
                iotprint(reminders) 
            
            **Expected Output**::

                [
                    {
                        "id": 1,
                        "message": "Hello",
                        "name": "Test",
                        "status": "ACTIVE",
                        "time": "2017-12-25 04:00 PM"
                    },
                    {
                        "id": 5,
                        "message": "This is a test reminder",
                        "name": "Test Reminder",
                        "status": "ACTIVE",
                        "time": "2017-12-25 03:45 PM"
                    }
                ]


        """

        kwargs_copy = copy.deepcopy(kwargs)
        data_dict = dict()
        for key in kwargs_copy:
            for multi_state_key in kwargs_copy[key]:
                if multi_state_key == 'time' and isinstance(kwargs_copy[key][multi_state_key], datetime.datetime):
                    datetime_copy = copy.copy(
                        kwargs_copy[key][multi_state_key])
                    datetime_without_seconds = datetime_copy.replace(
                        second=0, microsecond=0)
                    kwargs_copy[key][multi_state_key] = self.__convert_datetime_to_str(
                        datetime_without_seconds)
                data_dict[key + '[' + multi_state_key +
                          ']'] = kwargs_copy[key][multi_state_key]

        try:
            json_response = requests.get(Config.SPRWIO_GATEWAY_URL + 'things/' + str(thing_id) + '/states', headers=self.__headers, params=data_dict)
        except requests.exceptions.ConnectionError:
            raise NetworkError(0, self.__network_error_message)

        try:
            response = edict(json.loads(json_response.text))
        except ValueError as e:
            raise ServerError(json_response.status_code,
                              self.__server_error_message)
        if json_response.status_code is 200 or json_response.status_code is 201:
            reminders = response.data.state.reminders
           
            index = 0
            for current_reminder in reminders:
                reminder_datetime = self.__convert_str_to_datetime(current_reminder.time)
                reminders[index].time = reminder_datetime
                index += 1
            
            response.data.state.reminders = reminders 
            return response.data.state
        elif json_response.status_code == 422:
            raise ValidationError(json_response.status_code,
                                  response)
        elif json_response.status_code == 500:
            if hasattr(response, 'message'):
                raise ServerError(json_response.status_code, response.message)
            else:
                raise ServerError(json_response.status_code, response)

        else:
            raise Error(Exception(response))


    def __convert_str_to_datetime(self, time_str):

        return datetime.datetime.strptime(time_str, Config.datetime_format)
    
    def __convert_datetime_to_str(self, time):

        return datetime.datetime.strftime(time, Config.datetime_format)

    def get_thing_custom_attributes(self, thing_id) :
        
        """Returns the custom attributes of the thing specified by the ``thing_id``.

        Parameters:
            thing_id (int): Id of the thing whose custom attributes are to be retreived.

        Returns:
            dict: Dictionary containing the custom attributes of the thing.

        Example:

            The following example shows how to retreive the custom attributes of a thing::

                
                led_custom_attributes = sp_server.get_thing_custom_attributes(thing_id=led_thing.id)
                print(led_custom_attributes)
               
            
            **Expected Output**::

                {'color': 'Red', 'pin_number': '3'}

        """

        try:
            json_response = requests.get(Config.SPRWIO_GATEWAY_URL + 'things/' + str(thing_id) + '/attributes', headers=self.__headers);
        except requests.exceptions.ConnectionError:
            raise NetworkError(0, self.__network_error_message)

        try:
            response = edict(json.loads(json_response.text))
        except ValueError as e:
            raise ServerError(json_response.status_code,
                              self.__server_error_message)

        if json_response.status_code == 200 or json_response.status_code == 201:
            return response.data
        elif json_response.status_code == 422:
            raise ValidationError(json_response.status_code,
                                  response)
        elif json_response.status_code == 500:
            if hasattr(response, 'message'):
                raise ServerError(json_response.status_code, response.message)
            else:
                raise ServerError(json_response.status_code, response)

        else:
            raise Error(Exception(response))

    def acknowledge_thing_state_attribute(self, thing_id, **kwargs):
        
        """Acknowledges the received state attributes of the thing specified by the ``thing_id``.

        Parameters:
            thing_id (int): Id of the thing whose state attribute is to be acknowledged.
        
        Keyword Arguments:
            state_attributes : Keyword arguments (key-value pairs) of the state attributes to be acknowledged for the thing.
        
        Returns:
            dict: Dictionary containing the status of the acknowledgement.
        
        Example:

            The following example shows how to acknowledge the state changed from the dashboard of a thing::

                
                led_thing_state = sp_server.get_thing_state_attributes(thing_id=led_thing.id)

                status = sp_server.acknowledge_thing_state_attribute(thing_id=led_thing.id, value=led_thing_state.value)
                print(status)
               
            
            **Expected Output**::
                
                {'message': 'State acknowledged'}

        """

        state_json = json.dumps(kwargs)

        try:
            json_response = requests.post(Config.SPRWIO_GATEWAY_URL + 'things/' + str(thing_id) + '/states/acknowledge', headers=self.__headers, data={'id': thing_id, 'state_type': 'ACKNOWLEDGEMENT', 'state': state_json})
        except requests.exceptions.ConnectionError:
            raise NetworkError(0, self.__network_error_message)

        try:
            response = edict(json.loads(json_response.text))
        except ValueError as e:
            raise ServerError(json_response.status_code,
                              self.__server_error_message)

        if json_response.status_code == 200 or json_response.status_code == 201:
            return response
        elif json_response.status_code == 422:
            raise ValidationError(json_response.status_code,
                                  response)
        elif json_response.status_code == 500:
            if hasattr(response, 'message'):
                raise ServerError(json_response.status_code, response.message)
            else:
                raise ServerError(json_response.status_code, response)

        else:
            raise Error(Exception(response))


    def __convert_to_dict(self, obj):
        if hasattr(obj, "_asdict"): # detect namedtuple
            return OrderedDict(zip(obj._fields, (self.__convert_to_dict(item) for item in obj)))
        elif isinstance(obj, str):  # iterables - strings
            return obj
        elif hasattr(obj, "keys"): # iterables - mapping
            return OrderedDict(zip(obj.keys(), (self.__convert_to_dict(item) for item in obj.values())))
        elif hasattr(obj, "__iter__"): # iterables - sequence
            return type(obj)((self.__convert_to_dict(item) for item in obj))
        else: # non-iterable cannot contain namedtuples
            return obj
