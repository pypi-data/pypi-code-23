from lib.user_exception import UserException as Ux
substeps = ''


def run_substep(context):
    def wrapped(step_name):
        context.is_substep = True
        if not context.execute_steps(unicode('Then ' + step_name)):
            raise Ux("run_substep: step '%s' not parseable" % step_name)
    return wrapped


