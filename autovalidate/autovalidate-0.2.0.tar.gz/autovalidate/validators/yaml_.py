from autovalidate.validators.core import ValidationResult, Validator, validates


@validates('yaml', 'yml')
class YamlValidator(Validator):
    def validate(self, path):
        import yaml

        try:
            with open(path) as f:
                yaml.load(f)
        except (yaml.parser.ParserError, RuntimeError) as e:
            return ValidationResult(path, False, str(e))
        else:
            return ValidationResult(path, True)
