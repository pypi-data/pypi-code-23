
def clean_user_input(user_input):
    return str(user_input).replace('\\ ', ' ')


def get_pretty_user_var(user_input_variable):
    return user_input_variable.replace('{', '').replace('}', '')


def list_to_comma_newline_separated_string(input_list):
    output_string = ''
    for item in input_list:
        output_string = "{0}{1}\n".format(output_string, item)
    return output_string
