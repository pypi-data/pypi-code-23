from aloft.chart_config import get_charts_to_use
from aloft.cluster import get_default_domain_from_cluster_config


def get_create_vpc_args(arguments):
    return get_vpc_args(arguments)


def get_delete_vpc_args(arguments):
    return get_vpc_args(arguments)


def get_vpc_args(arguments):
    vpc_id = arguments['<vpc_id>']
    return vpc_id


def get_apply_chart_args(arguments):
    return get_chart_args(arguments)


def get_delete_chart_args(arguments):
    return get_chart_args(arguments)


def get_lock_volumes_args(arguments):
    return get_chart_args(arguments)


def get_unlock_volumes_args(arguments):
    return get_chart_args(arguments)


def get_chart_args(arguments):
    release_id, chart_set, sandbox_name = get_release_args(arguments)
    charts = get_charts(arguments, chart_set)
    return release_id, chart_set, charts, sandbox_name


def get_release_args(arguments):
    release_id = arguments['<release_id>']
    chart_set = arguments['<chart_set>']
    sandbox_name = arguments['--sandbox']
    return release_id, chart_set, sandbox_name


def get_charts(arguments, chart_set):
    charts = arguments['--charts']
    if charts is not None:
        charts = charts.split(',')
    else:
        charts = get_charts_to_use(chart_set)
    return charts


def get_get_current_cluster_args(arguments):
    output_type = arguments['--output']
    return output_type


def get_get_clusters_args(arguments):
    domain = arguments['<domain>']
    output_type = arguments['--output']
    if domain is None:
        domain = get_default_domain_from_cluster_config()
    return domain, output_type


def get_create_cluster_args(arguments):
    return get_cluster_args(arguments)


def get_use_cluster_args(arguments):
    return get_cluster_args(arguments)


def get_validate_cluster_args(arguments):
    return get_cluster_args(arguments)


def get_delete_cluster_args(arguments):
    return get_cluster_args(arguments)


def get_cluster_args(arguments):
    cluster_id = arguments['<cluster_id>']
    return cluster_id


def get_use_namespace_args(arguments):
    namespace = arguments['<namespace>']
    return namespace
