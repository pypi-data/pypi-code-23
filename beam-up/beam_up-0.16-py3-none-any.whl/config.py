import yaml
import os

def load_includes(config, include_path):
    if isinstance(config, dict):
        d = {}
        for key, value in config.items():
            if key == '$include':
                path = os.path.abspath(os.path.join(include_path[-1], os.path.abspath(value)))
                if path in include_path:
                    raise ValueError("Recursive import of {} (path: {})"\
                        .format(path, '->'\
                        .join(['"{}"'\
                        .format(s) for s in include_path])))
                d.update(load_config(path, include_path=include_path+[path]))
            else:
                d[key] = load_includes(value, include_path=include_path)
        return d
    elif isinstance(config, list):
        return [load_includes(i, include_path=include_path) for i in config]
    return config
            

def load_config(filename, include_path=None):
    if include_path is None:
        include_path = [os.path.abspath(filename)]
    with open(filename) as input_file:
        config = yaml.load(input_file.read())
    return load_includes(config, include_path=include_path)
