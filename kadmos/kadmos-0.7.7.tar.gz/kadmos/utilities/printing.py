from tabulate import tabulate


def print_indexed_list(*args, **kwargs):
    """
    This function prints an indexed column of the given arguments in the console. The provided message is printed above
    the indexed column. Can be used in combination with user_prompt_select_options().

    example use:
    print_indexed_list(message = "These are the tools: ", index_bracket = "round", *list_of_tools)

    :param kwargs: message: Message printed above indexed column
    :param kwargs: index_bracket: Type of bracket used for indeces in list ("round" or "squared"), default is round
    :param args: Arguments listed in column by index
    :return:
    """

    if "message" in kwargs:
        assert isinstance(kwargs["message"], basestring), "'message'-argument must be of type 'string'."
        print_message = kwargs["message"]
    else:
        print_message = ""

    brac1, brac2 = "[", "]"
    if "index_bracket" in kwargs:
        assert kwargs["index_bracket"] in ["round", "squared"], "'index_bracket'-argument must either be 'round' or " \
                                                                "'squared'."
        if kwargs["index_bracket"] == "round":
            brac1, brac2 = "(", ")"

    print_args = list(arg for arg in args)
    print "\n{}".format(print_message) \
          + "".join(["\n{}{}{}  {}".format(brac1, print_args.index(arg), brac2, arg) for arg in print_args])

    return


def print_in_table(print_container, **kwargs):
    """
    This function prints a table using the provided data and the headers. The "tabulate" library is used.

    print_container: container for iterables --> [[row1], [row2], ...]

    :return:
    """
    # headers = None, print_indeces = False
    message = ""
    if "message" in kwargs:
        message = "{0}{1}{0}".format("\n", kwargs["message"])

    # set headers to empty list if none provided
    headers = []
    if "headers" in kwargs:
        headers = kwargs["headers"]

    # add indeces to iterables
    print_indeces = False
    if "print_indeces" in kwargs:
        print_indeces = kwargs["print_indeces"]

    # if print_indeces, add index as first element
    if print_indeces:

        # insert index in each list
        repl_cont = []
        for idx, iterable in enumerate(print_container):
            it = list(iterable)
            it.insert(0, idx)
            repl_cont.append(it)

        # insert "#" at appropriate position
        if headers:
            headers.insert(0, "#")

        print_container = repl_cont

    print "{}\n".format(message), tabulate(print_container, headers=headers, numalign="right")

    return
