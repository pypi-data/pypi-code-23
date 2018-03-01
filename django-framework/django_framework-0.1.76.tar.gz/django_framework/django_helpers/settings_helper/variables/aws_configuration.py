
from base_variable import BaseVariable

class AwsConfiguration(BaseVariable):
    
    @property
    def AWS_ACCESS_KEY_ID(self):
        var_name = 'aws_access_key_id'
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_aws_access_key_id(self):
        return self._AWS_ACCESS_KEY_ID, None, None
    
    def _check_aws_access_key_id(self, value):
#         self.assert_type(value = value, expected_type = dict)
        return True


    @property
    def AWS_SECRET_ACCESS_KEY(self):
        var_name = 'aws_secret_access_key'
        return self._get_set_variables(var_name = var_name)
    
    
    def _get_aws_secret_access_key(self):
        return self._AWS_SECRET_ACCESS_KEY, None, None
    
    def _check_aws_secret_access_key(self, value):
#         self.assert_type(value = value, expected_type = dict)
        return True
