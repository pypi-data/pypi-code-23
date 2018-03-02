
from base_variable import BaseVariable

class PermissionConfiguration(BaseVariable):
    '''This sets whether or not we need to check if the user has permissions to view certain rows (usually yes)
    and also whether to check PUT/POSTs so that modifications are still owned by the end user.
    
    For instance if profile_id is used to link a row back to the give profile = 1,
    if a POST {"profile_id" : 5} would create a row for profile=5 even if you were not.
    if a PUT {"profile_id" : 3} woudl assign your own row to profile=3
    
    '''
    @property
    def CHECK_MODEL_DATA_WITH_PERMISSIONS(self):

        var_name = 'check_model_data_with_permissions'
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_check_model_data_with_permissions(self):
        try:
            values = self._CHECK_MODEL_DATA_WITH_PERMISSIONS, None, None
        except:
            
            print('CHECK_MODEL_DATA_WITH_PERMISSIONS was not set properly, defaulting to True (strongest permissions)')
            values = True, None, None
            
        return values
    
    def _check_check_model_data_with_permissions(self, value):
        self.assert_boolean(value = value)
        if value == False:
            print('PERMISSION WARNING : CHECK_MODEL_DATA_WITH_PERMISSIONS is set to False!  Will allow users to create/reassign rows to other users')
        return True

    @property
    def GET_MODEL_WITH_PERMISSIONS(self):
        var_name = 'get_model_with_permissions'
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_get_model_with_permissions(self):
        
        try:
            values = self._GET_MODEL_WITH_PERMISSIONS, None, None
        except:
            
            print('GET_MODEL_WITH_PERMISSIONS was not set properly, defaulting to True (strongest permissions)')
            values = True, None, None
        
        
        return values
    
    def _check_get_model_with_permissions(self, value):
        self.assert_boolean(value = value)
        
        if value == False:
            print('PERMISSION WARNING : GET_MODEL_WITH_PERMISSIONS is set to False!  Will allow users to view rows of other users')
        
        return True

