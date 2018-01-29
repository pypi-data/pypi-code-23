
import datetime
import sys
from .. import env
from ..utils import convert_path_to_name, format_exception, create_id


def log(func):
    def catch_args(*args, **kwargs):
        env.mode = env.SCRIPT

        from ..models import ScriptLog

        path = sys.argv[0]
        script_log = None
        if env.configured and env.SCRIPTS_DIR and env.SCRIPTS_DIR in path:
            script_log = ScriptLog()
            script_log.id = create_id()
            script_log.name = convert_path_to_name(path, 'script')
            script_log.start_at = datetime.datetime.now()
            script_log.save()

        try:
            ret = func(*args, **kwargs)
            return ret
        except:
            if script_log:
                ScriptLog.objects(id=script_log.id).update(set__traceback=format_exception())
            else:
                raise
        finally:
            if script_log:
                ScriptLog.objects(id=script_log.id).update(set__end_at=datetime.datetime.now())

    return catch_args
