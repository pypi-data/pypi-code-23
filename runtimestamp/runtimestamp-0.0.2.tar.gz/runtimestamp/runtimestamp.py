import os
import datetime
import platform

def runtimestamp():
    '''
    Returns Runtime Metadata for Jupyter Notebooks
    '''
    user = os.environ.get("USER")
    today = datetime.datetime.now()
    version = platform.python_version()
    os_platform = platform.platform()
    
    print(
        "Updated {today}\nBy {user}\nUsing Python {version}\nOn {os_platform}".format(
            today = today,
            user = user,
            version = version,
            os_platform = os_platform
        )
    )