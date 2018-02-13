from kooki.tools import get_extension
import yaml
import toml
import json
import munch


class Metadata(munch.Munch):

    def update(self, *args, **kwargs):
        for arg in args:
            if isinstance(arg, dict):
                super().update(arg)
            else:
                raise Exception('arg provided is not a dict')
        super().update(**kwargs)

    def copy(self):
        copy = Metadata()
        for key, value in self.items():
            if isinstance(value, Metadata):
                copy[key] = self._copy(value)
            elif isinstance(value, list):
                new_value = []
                for i in value:
                    new_value.append(self._copy(i))
                copy[key]
            else:
                copy[key] = value
        return copy

    def _copy(self, data):
        copy = Metadata()
        for key, value in data.items():
            if isinstance(value, Metadata):
                copy[key] = self._copy(value)
            else:
                copy[key] = value
        return copy


def parse_metadata(document_metadata):
    print('parse metadata')
    metadata = Metadata()
    for file_path, file_content in document_metadata.items():
        new_metadata = load(file_path, file_content)
        metadata = data_merge(new_metadata, metadata)
    return Metadata.fromDict(metadata)


def load(file_path, file_content):

    extension = get_extension(file_path)

    if extension == 'yaml' or extension == 'yml':
        metadata = yaml.safe_load(file_content)
    elif extension == 'toml':
        metadata = toml.loads(file_content)
    elif extension == 'json':
        metadata = json.loads(file_content)
    else:
        raise Exception('No loader for this type of file \'.{}\''.format(extension))

    return metadata


def data_merge(a, b):

    class MergeError(Exception):
        pass

    key = None

    try:
        if a is None or isinstance(a, str) or isinstance(a, bytes) \
           or isinstance(a, int) or isinstance(a, float):
            a = b
        elif isinstance(a, list):
            if isinstance(b, list):
                a.extend(b)
            else:
                a.append(b)
        elif isinstance(a, dict):
            if isinstance(b, dict):
                for key in b:
                    if key in a:
                        a[key] = data_merge(a[key], b[key])
                    else:
                        a[key] = b[key]
            else:
                raise MergeError('Cannot merge non-dict "%s" into dict "%s"' % (b, a))
        else:
            raise MergeError('NOT IMPLEMENTED "%s" into "%s"' % (b, a))
    except TypeError as e:
        raise MergeError('TypeError "%s" in key "%s" when merging "%s" into "%s"' % (e, key, b, a))
    return a
