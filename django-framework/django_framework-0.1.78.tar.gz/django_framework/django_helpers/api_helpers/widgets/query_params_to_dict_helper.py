import ast
import urlparse


from django_framework.helpers.constant_helpers import ALLOWED_FALSE_VALUES, ALLOWED_NONE_VALUES, ALLOWED_TRUE_VALUES


def query_params_to_dict(query_string):
    '''
    Translates a url query string typically things after a: ?format=json....
    into a usuable dictionary.
    
    Things might be wierd if:
    query_string = filter[test]=1&filter[test2]=test&filter=3
      
    
    '''
    # outputs a semi cleaned version of the query_string in form of a dictionary.  ALL values
    # of this dictionary are in a list
    parameters = urlparse.parse_qs(query_string)
    
    # translate the internals
    for key, value in parameters.items():
        
        value = clean_value(value) # translate values to None etc actual booleans
        
        if key[-1] == ']' and '[' in key: # faster search!
            
            # sample key : filter[uuid]
            # we want to split into:   {filter : {uuid : value}}
            
            # outer_key in above example is "filter"
            # inner_key in above example is "uuid]" <-- note the brackets!
            outer_key, inner_key = key.split('[') # if there's more than one you're outta luck
            inner_key = inner_key[0:-1] # remove trailing bracket!!
            
            # possibility of multiple internal keys
            if parameters.get(outer_key) == None:
                parameters[outer_key] = {}
            parameters[outer_key][inner_key] = value
            
            # we really shouldnt need the None here but for safety!
            parameters.pop(key, None)
            
        else:
            parameters[key] = value
            
    return parameters

def clean_value(value):
    if isinstance(value, list) and len(value) == 1:
        value = value[0]
        
        if value[0]=='[' and value[-1]== ']':
            value = ast.literal_eval(value) # this could be a bit risky, but will only translate literals # we dont dig deeper!
            
            
        elif value in ALLOWED_FALSE_VALUES: # translate False
            value = False
        elif value in ALLOWED_NONE_VALUES: # translate None
            value = None
        elif value in ALLOWED_TRUE_VALUES: # translate True
            value = True
            
    return value

def main():
    query_params_to_dict()


if __name__ == '__main__':

    url ='filter[test]=test&haha=3&page[page]=sdff&page[page]=1232&page[show]=p&alist=["alist"]&encoded=%23%23#&spaces=test test %20 and + ha'
    
#     test(query_params = url)



# my CASES
# encoded things
# nested dictionary 2 levels
# conver tto null, None
# booleans
# lists# should we do dics??
