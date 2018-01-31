from autology.commands.subcommands.updaters import update_0_1_0_agent_information
from autology.commands.subcommands.updaters import update_0_2_0_date_time_values


def update_files(search_path, file_path):
    """
    Run the updates in order so that they will update the log files in place.
    :param search_path:
    :param file_path:
    :return:
    """
    update_0_1_0_agent_information.add_agent_information(search_path, file_path)
    update_0_2_0_date_time_values.change_date_time_values(search_path, file_path)
