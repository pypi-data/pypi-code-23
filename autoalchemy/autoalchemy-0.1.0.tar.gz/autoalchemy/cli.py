import os

import click
from autoalchemy.build_database import AutoAlchemyWrapper
from autoalchemy.dataframe_parser import DataframeParser
from autoalchemy.schema_code_generator import generate_sqlalchemy_schema_code
from autoalchemy.utils import listdir_full, print_highlighted, time_function


def read_dataframes(dir_path):
    """Read all the dataframes from a directory, returning a list of DataframeParsers."""
    files = listdir_full(dir_path)
    df_parser_list = []
    for file_path in files:
        if (file_path.endswith('.txt') or file_path.endswith('.csv')):
            dfparser = DataframeParser(file_path=file_path)
            df_parser_list.append(dfparser)
    return df_parser_list


@time_function
def build_database(directory, config, generated, drop_existing):
    """Read tables, generate a schema, and push to the database.

    Args:
        directory (str): Path to the directory containing .txt and .csv data.
        config (str): Path to the database configuration (config.json).
        generated (Optional[str]): Path to write the generated schema.
        drop_existing (bool): If True, will drop all existing table and views in the database.
    """
    # 1. Pull the dataframe info
    df_parser_list = read_dataframes(directory)

    # 2. Generate schema code based on the dataframe list
    print_highlighted('AUTOMAGICALLY GENERATING SCHEMA CODE...')
    generate_sqlalchemy_schema_code(df_list=df_parser_list, out_file=generated)

    # 3. Run schema code using import
    import importlib.util
    spec = importlib.util.spec_from_file_location("schema", location=generated)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    Base = module.Base

    # 4. Pass the  parse_config,SQLAlchemy engine object to Base.metadata() to push the schema
    print_highlighted('PUSHING SCHEMA...')
    alchemy_wrapper = AutoAlchemyWrapper(config_path=config)
    if drop_existing:
        alchemy_wrapper.drop_all_tables()
        alchemy_wrapper.drop_all_views()
    alchemy_wrapper.create_new_schema(declarative_base=Base)

    # 5. Push all the dataframes over
    print_highlighted('PUSHING TABLES...')
    alchemy_wrapper.create_all_tables(df_parser_list)

    # Print finished message
    print_highlighted('DATABASE CREATION COMPLETE.')
    msg = 'NUM TABLES: {0}\nDATABASE: {1}\nHOST: {2}@{3}:{4}\nCONNECTION STRING: {5}\n'
    print(msg.format(len(df_parser_list),
                     alchemy_wrapper.auth['db'],
                     alchemy_wrapper.auth['user'],
                     alchemy_wrapper.auth['host'],
                     alchemy_wrapper.auth['port'],
                     alchemy_wrapper._connection_string))

    # TODO: Automatically remove generated schema when done


@click.command(context_settings=dict(help_option_names=['-h', '--help']))
@click.argument('directory', type=click.Path(exists=True), nargs=1)
@click.argument('config', type=click.Path(exists=True), nargs=1)
@click.option('-g', '--generated', type=click.Path(exists=False), default='GENERATED_SCHEMA.py', nargs=1)
@click.option('--drop-existing', type=bool, default=False)
def cli(directory, config, generated, drop_existing):
    """Read tables, generate a schema, and push to a SQL database.

    Ex: autoalchemy /path/to/data_directory /path/to/config.json
    """
    build_database(directory=directory,
                   config=config,
                   generated=generated,
                   drop_existing=drop_existing)


if __name__ == '__main__':
    cli()
