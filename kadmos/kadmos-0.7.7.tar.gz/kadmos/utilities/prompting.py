def user_prompt_string(**kwargs):
    """
    This function prompts the user to provide a string. Must have at least one character.

    :param kwargs: message
    :return: inp: user input string
    """

    # define message printed above input prompt
    message = ""
    if "message" in kwargs:
        message = kwargs["message"]

    allow_empty = False
    if "allow_empty" in kwargs:
        allow_empty = kwargs["allow_empty"]

    # check which one user want to select
    while True:

        # ask user to include all found nodes or not
        prompt = "{}\n".format(message)
        inp = str(raw_input(prompt))

        if not allow_empty:
            if len(inp) < 1:
                print "String must have at least one character."
                continue
            else:
                break

    return inp


def user_prompt_yes_no(**kwargs):
    """
    This function takes in a prompt string and asks the user to select "0" or "1" for No and Yes, respectively. User
    choice is returned as integer 0 or 1.

    :param kwargs: message: User prompt that is displayed in console.
    :return: selection: User selection (integer 0 or 1)
    """
    message = ""
    if "message" in kwargs:
        message = kwargs["message"]

    # check which one user want to select
    while True:

        # ask user to include all found nodes or not
        prompt = "\n{}\n[0] No\n[1] Yes\n".format(message)

        try:
            selection = int(raw_input(prompt))
        except ValueError:
            print "\nOnly a single integer value allowed as input."
            continue

        if selection not in [0, 1]:
            print "Selection invalid. Please choose [0] for 'No' or [1] for 'Yes'."
            continue
        else:
            break

    return selection


def user_prompt_select_options(*args, **kwargs):
    """
    This function lets the user select elements of a list by its index in that list. The user can select any of the
    given options by providing its index (mulitple selections possible). Only integers can be used as input. If no
    input provided, function is exited. Can be used in combination with "print_indexed_list()".

    example use:
    select_tools_from_list = user_prompt_select_options(message, *list_of_tools)

    :param args: Arguments that printed in an indexed column
    :param kwargs: message: Message that is printed above the indexed column
    :param kwargs: allow_empty: If set to True, prompt can be exited with empty selection; otherwise not
                                (user must select); Default: True
    :param kwargs: allow_multi: If set to False, only one element can be selected; Default: False
    :return: kwargs: selectedArgs: Arguments selected by the user, or empty list
    :rtype: list
    """

    # message to print above list
    print_message = ""
    if "message" in kwargs:
        print_message = str(kwargs["message"])

    # check if allow_empty is set
    allow_empty = True
    if "allow_empty" in kwargs:
        allow_empty = kwargs['allow_empty']
        assert isinstance(allow_empty, bool), 'Argument must be of type "boolean".'

    # check if multiple selections allowed
    allow_multi = True
    if "allow_multi" in kwargs:
        allow_multi = kwargs["allow_multi"]
        assert isinstance(allow_multi, bool), 'Argument must be of type "boolean".'

    # add arguments to list (necessary due to index-functionality of list)
    arg_list = list(arg for arg in args)

    # prompt user to select tools to be ignored
    selected_args = []
    while True:

        # get input from user
        selected_idxs = raw_input("\n{} \n\n".format(print_message)).split()

        # check input for proper input; if no input, function is exited
        if selected_idxs:
            try:
                selected_idxs = [int(elem) for elem in selected_idxs]
            except ValueError:
                print "\nOnly integers are allowed!"
                continue
        else:
            if allow_empty:
                print "No elements selected."
                break
            else:
                print "No empty selection allowed."
                continue

        # make selection integers unique
        selected_idxs = list(set(selected_idxs))

        # check if multiple selected
        if not allow_multi and len(selected_idxs) > 1:
            print "\nOnly one option can be selected!"
            continue

        # check whether input is within the selection range
        if not all([0 <= elem <= len(arg_list) - 1 for elem in selected_idxs]):
            print "\nOnly provided options can be selected!"
            continue

        # add selected arguments to list, print them and return
        selected_args = [arg_list[idx] for idx in selected_idxs]
        if len(selected_args) > 1:
            print "\nThe following were selected: "
            for pr in selected_args:
                print pr
            break
        else:
            print "\nThe following was selected: "
            print next(iter(selected_args))
            break

    return selected_args
