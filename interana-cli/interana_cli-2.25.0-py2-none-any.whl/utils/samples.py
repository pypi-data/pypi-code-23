# Copyright 2017 Interana, Inc.

EVENT_TABLE_CREATE_SAMPLE = '''
{
    "table": {
        "name": "music",
        "type": "Event",
        "time_column": "ts",
        "time_column_format": "milliseconds",
        "shard_keys": ["userId", "artist"],
        # "columns" are optional, but it allows you to create columns upon table creation, instead of
        # waiting for the columns to appear in your data
        "columns": [
            {
                "name": "ts",
                "display_name": "ts",
                "type": "milliseconds",
                "conversion_params": "",
                "attributes": [
                    "filterable"
                ]
            },
            {
                "name": "userId",
                "display_name": "userId",
                "type": "int",
                "conversion_params": "",
                "attributes": [
                    "filterable",
                    "Groupable"
                ]
            },
            {
                "name": "artist",
                "display_name": "artist",
                "type": "string",
                "conversion_params": "",
                "attributes": [
                    "filterable",
                    "Groupable"
                ]
            },
            {
                "name": "song_length",
                "display_name": "song_length",
                "type": "int",
                "conversion_params": "",
                "attributes": [
                    "filterable",
                    "Aggregable"
                ]
            }
        ]
    },

    # "ingest" is optional, but it is available for the convenience of creating ingest pipelines when creating the table
    "ingest": [
        {
            "name": "music_pipeline",
            "data_source_type": "file_system",
            "table_name": "music",

            "data_source_parameters": {
                "file_pattern": "/log_files/{year}/{month:02d}/{day:02d}/*.json",
            },

            "data_transformations": [
                ["decode", {"encoding": "utf-8"}],
                ["json_load"],
                ["json_dump"]
            ]
        }
    ]
}
'''

LOOKUP_TABLE_CREATE_SAMPLE = '''
{
    "table": {
        "name": "events_lookup",
        "type": "Lookup",
        "event_table_name": "events",
        "event_table_column_name": "shard_key",
        "lookup_column_name": "id",
        # "columns" are optional, but it allows you to create columns upon table creation, instead of
        # waiting for the columns to appear in your data
        "columns": [
            {
                "name": "id",
                "display_name": "id",
                "type": "int",
                "conversion_params": "",
                "attributes": [
                    "filterable",
                    "Groupable"
                ]
            },
            {
                "name": "name",
                "display_name": "name",
                "type": "string",
                "conversion_params": "",
                "attributes": [
                    "filterable",
                    "Groupable"
                ]
            }
        ]
    },

    # "ingest" is optional, but it is available for the convenience of creating ingest pipelines when creating the table
    "ingest": [
        {
            "name": "events_lookup_import",
            "data_source_type": "file_system",
            "table_name": "events_lookup",

            "data_source_parameters": {
                "file_pattern": "/home/myuser/lookup/*.json",
            }
        }
    ]
}
'''

PIPELINE_CREATE_SAMPLE = '''
{
    "ingest": [
        {
            "name": "simple_events_pipeline",
            "data_source_type": "file_system",
            "table_name": "events",

            "data_source_parameters": {
                "file_pattern": "/home/myuser/logs/*.json",
            }
        },
        {
            "name": "hooli_log_pipeline",
            "data_source_type": "aws",
            "table_name": "usage_stats",

            "data_source_parameters": {
                "file_pattern": "hooli1/{year:04d}/{month:02d}/{day:02d}/{hour:02d}/",
                "s3_bucket": "hooli-logs",
                "s3_access_key": "AKIAIOSFODNN7EXAMPLE",
                "s3_secret_access_key": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
            },

            "advanced_parameters": {
                "minimum_disk_space": 6000000000,
                "concat_file_size": 500000000,
                "wait_seconds": 30,
            },

            "data_transformations": [
                ["gunzip"],
                ["decode"],
                ["json_load"],
                ["merge_keys", {"column_1": "lookup_id","column_2": "query_id", "output_column": "session_id"}],
                ["merge_keys", {"column_1": "anonymous_id","column_2": "user_id", "output_column": "actor"}],
                ["add_label", {"column": "customer", "label": "hooli"}],
                ["json_dump"]
            ]
        },
       # Can create multiple pipelines for different pipelines
        {
            "name": "music-pipeline",
            "data_source_type": "azure_blob",
            "table_name": "music",
            "data_source_parameters": {
                "container": "music-log-files",
                "file_pattern": "Music",
                "storage_key": "ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890/EIEIO==",
                "storage_account": "interana-music"
            },
            "advanced_parameters": {
                "wait_seconds": 60,
                "minimum_disk_space": 20000000000,
                "concat_file_size": 1000000000
            },
            "data_transformations": [
                # load the JSON from disk
                ["decode", {"encoding": "utf-8"}],
                ["json_load"],

                # add a "customer" label to every single event
                ["add_label", {"column": "event_type", "label": "client_event"}],

                # merge first/last name into a single column and then anonymize into an int
                ["join", {"columns": ["firstName", "lastName"], "separator": " ", "output_column": "fullName"}],
                ["omit", {"columns": ["firstName", "lastName"]}],
                ["anonymize", {"column": "fullName"}],

                # replace the M/F option with more descriptive male/female
                ["dictionary_replace", {"mapping": {"M": "male","F": "female"}, "column": "gender"}],

                # split up "location":"Chicago-Naperville-Elgin, IL-IN-WI" into city/state arrays
                ["regex_extract", {"column": "location", "output_columns": ["city", "state"], "regex": r"(.*), (.*)"}],
                ["convert_to_array", {"column": "city", "separator": "-"}],
                ["convert_to_array", {"column": "state", "separator": "-"}],

                # round the song length to an integer (don't need decimals here)
                ["code_snippet", {"code":\'''
if 'length' in line:
    line['length'] = round(line['length'])
                \'''}],

                # write the JSON back to disk
                ["json_dump"]
            ]
        }
    ]
}
'''

PIPELINE_UPDATE_SAMPLE = '''
{
    "ingest": [
        {
            "name": "hooli_log_pipeline",
            "new_name": "hooli_log_pipeline_legacy",

            "data_source_parameters": {
                "file_pattern": "hooli1/{year:04d}-{month:02d}-{day:02d}/",
                "s3_region": "eu-west-2"
            },

            "advanced_parameters": {
                "minimum_disk_space": 9000000000,
                "concat_file_size": 800000000,
                "wait_seconds": 33,
            },

            "data_transformations": [
                ["gunzip"],
                ["decode"],
                ["json_load"],
                ["merge_keys", {"column_1": "batch_id","column_2": "query_api_id", "output_column": "transaction_id"}],
                ["merge_keys", {"column_1": "pipeline_shard_id","column_2": "user_id", "output_column": "shard_key"}],
                ["add_label", {"column": "customer", "label": "experticity"}],
                ["add_label", {"column": "version", "label": "2.23"}],
                ["json_dump"]
            ]
        },
        {
            "name": "music-pipeline",

            "advanced_parameters": {
                "minimum_disk_space": 1200000000,
                "concat_file_size": 570000000,
                "wait_seconds": 51,
            }

        },
    ]
}
'''

PURGE_CREATE_SAMPLE = '''
{
    "user_id": ["eccbc87e-cfcd2084-45c48cce-45c48cce", "66e7dff9-28308fd9-66e7dff9-ea1afc51"],
    "anonymous_id": ["6505913639713474836", "8143414483406512381"]
}

NOTE: Filters are OR'd together, meaning an event will be deleted if user_id is one of
["eccbc87e-cfcd2084-45c48cce-45c48cce", "66e7dff9-28308fd9-66e7dff9-ea1afc51"] OR anonymous_id is
one of ["6505913639713474836", "8143414483406512381"].
'''

SELECTIVE_DELETE_CREATE_SAMPLE = '''
{
    "table_name": "music",
    "start_time": 0,
    "end_time": 1510016107744,
    "filters": {
        "user_id": ["eccbc87e-cfcd2084-45c48cce-45c48cce", "66e7dff9-28308fd9-66e7dff9-ea1afc51"],
        "anonymous_id": ["6505913639713474836", "8143414483406512381"]
    }
}

NOTE: Filters are AND'd together, meaning an event will only be deleted if user_id is one of
["eccbc87e-cfcd2084-45c48cce-45c48cce", "66e7dff9-28308fd9-66e7dff9-ea1afc51"] AND anonymous_id is
one of ["6505913639713474836", "8143414483406512381"].
'''
