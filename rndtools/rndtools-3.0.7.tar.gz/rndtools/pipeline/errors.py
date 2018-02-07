def has_step_error(result, e=None):
    # type: (dict, Optional[StepError]) -> bool
    if e is None:
        return 'error' in result

    return e.name == result.get('error', {}).get('name', None)


class StepError(dict):
    name = None

    def __init__(self, message, **kwargs):
        super(StepError, self).__init__(
            {
                'error': {
                    'message': message,
                    'name': self.name
                }
            }
        )
