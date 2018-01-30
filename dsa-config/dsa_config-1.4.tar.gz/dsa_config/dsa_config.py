#!/usr/bin/python
import os.path
import sys
import logging
from datetime import datetime
import tdtestpy  # noqa: E402 # @UnresolvedImport
from dsa_rest import DsaREST

CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
LOG_DIR = os.path.join(CURRENT_DIR, 'logs')


if __name__ == "__main__":
    parser = tdtestpy.TdArgParser()
    parser.add_argument("--configure_dsc_s3", help="Configure DSC server")
    parser.add_argument("--configure_system", help="Configure DBS system")
    parser.add_argument("--dsc_server", help="DSC server")
    parser.add_argument("--dsc_root_password", help="DSC root password")
    parser.add_argument("--dbs_root_password", help="DBS root password")

    args = parser.parse_args()

    configure_dsc_s3 = args['configure_dsc_s3']
    configure_system = args['configure_system']
    dbs_root_password = args['dbs_root_password']
    dsc_root_password = args['dsc_root_password']
    dsc_server = args['dsc_server']
    dbs_name = args['dbs_name'].lower()
    dbc_password = args['dbc_password']

    timestamp = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    logname = "dsa_config_{}.log".format(timestamp)

    media_server_name = dsc_server + '_S3_media'
    target_media_name = "TARGET_S3"
    prefix_name = "dsa_storage/"

    logger = tdtestpy.TdLogger(LOG_DIR, logname, standalone=True)
    logger.logger.addHandler(logging.StreamHandler(sys.stdout))

    logger.start("DSA configuration", args=args)
    dsa_rest = DsaREST(
        dsc_server=dsc_server,
        dsc_password=dsc_root_password,
        media_server_name=media_server_name,
        target_media_name=target_media_name,
        prefix_name=prefix_name)

    try:

        if configure_system == "true":
            registered_systems = dsa_rest.get_registered_systems()
            print(registered_systems)
            sys_status = dsa_rest.register_system(
                dbs=dbs_name,
                dbc_password=dbc_password,
                registered_systems=registered_systems)

            if sys_status:
                logger.info("Restarting bardsmain in source system")
                sys_connection = tdtestpy.RemoteConn(
                    sys_name=dbs_name,
                    user_password=dbs_root_password)
                sys_connection.restart_bardsmain()

                dsa_rest.enable_system(system=dbs_name)

        if configure_dsc_s3 == "true":

            # Configure media server
            logger.info("configure media server")
            dsc_connection = tdtestpy.RemoteConn(
                sys_name=dsc_server,
                user_password=dsc_root_password)
            # Get media servers list already configured with DSC server.
            logger.info("get media servers")
            media_servers = dsa_rest.get_media_servers()
            logger.info("Media servers: {}".format(media_servers))

            # Get default media server configured along with DSC installation.
            logger.info("get default media servers")
            ms_name = dsa_rest.get_dsc_media_server_name(media_servers=media_servers)

            # Configure AWS with DSC server.
            dsa_rest.config_aws()

            # Create target group for S3.
            dsa_rest.create_s3_target_group(ms_name)

        logger.passed("dsa_config.py")

    except Exception as e:
        logger.failed(error=e)
        sys.exit(1)
