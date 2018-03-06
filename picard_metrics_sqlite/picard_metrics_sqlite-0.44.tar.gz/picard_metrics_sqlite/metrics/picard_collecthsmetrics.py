import os

from .metrics_util import picard_select_tsv_to_df

def picard_CollectHsMetrics_to_df(metric_path, logger):
    select = 'BAIT_SET'
    df = picard_select_tsv_to_df(metric_path, select, logger)
    return df

def picard_CollectHsMetrics_histogram_to_df(metric_path, logger):
    select = 'coverage_or_base_quality'
    df = picard_select_tsv_to_df(metric_path, select, logger)
    return df

def run(job_uuid, metric_path, bam, input_state, engine, logger, metric_name):
    table_name = 'picard_' + metric_name
    df = picard_CollectHsMetrics_to_df(metric_path, logger)
    df['bam'] = bam
    df['input_state'] = input_state
    df['job_uuid'] = job_uuid
    df.to_sql(table_name, engine, if_exists='append')

    table_name += '_histogram'
    df = picard_CollectHsMetrics_histogram_to_df(metric_path, logger)
    df['bam'] = bam
    df['input_state'] = input_state
    df['job_uuid'] = job_uuid
    df.to_sql(table_name, engine, if_exists='append')    
    return
