from autovalidate.validators.core import ValidationResult, Validator, validates


@validates('json')
class JsonValidator(Validator):
    def validate(self, path):
        import json

        try:
            with open(path) as f:
                json.load(f)
        except (ValueError, RuntimeError) as e:
            return ValidationResult(path, False, str(e))
        else:
            return ValidationResult(path, True)
