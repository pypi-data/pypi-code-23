from eryx_deploy.tasks.deploy_task import DeployTask
from eryx_deploy.tasks.first_deploy_task import FirstDeployTask
from eryx_deploy.tasks.sync_local_db_task import SyncLocalDBTask
from .assets import *
from .app_stacks import *
from .default_config import *

deploy = DeployTask()
first_deploy = FirstDeployTask()
sync_local_db = SyncLocalDBTask()
