from .rule import Rule


def parse_document_rules(config):
    document_names = parse_documents_name(config)
    default_rules = parse_default_document_rules(config)
    document_rules = {}
    for document_name in document_names:
        result = parse_specific_document_rules(document_name, config[document_name], default_rules)
        document_rules[document_name] = result
    return document_rules


def parse_documents_name(config):
    document_names = []
    for key, value in config.items():
        if key not in Rule.reserved:
            document_names.append(key)
    return document_names


def parse_default_document_rules(config):
    default_rule = Rule('default', config)
    return default_rule


def parse_specific_document_rules(document_name, config, default_rules):
    specific = default_rules.copy()
    specific.document_name = document_name
    specific.set_config(config)
    return specific
