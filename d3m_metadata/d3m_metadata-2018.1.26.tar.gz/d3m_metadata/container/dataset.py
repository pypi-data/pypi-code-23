import abc
import hashlib
import json
import os
import os.path
import typing
from urllib import parse as url_parse

import dateparser  # type: ignore
import networkx  # type: ignore
import numpy  # type: ignore
import pandas  # type: ignore
from pandas.io import common as pandas_io_common  # type: ignore
from sklearn import datasets  # type: ignore

from .. import metadata as metadata_module

__all__ = ('Dataset',)


UNITS = {
    'B': 1, 'KB': 10**3, 'MB': 10**6, 'GB': 10**9, 'TB': 10**12, 'PB': 10**15,
    'KiB': 2*10, 'MiB': 2*20, 'GiB': 2*30, 'TiB': 2*40, 'PiB': 2*50,
}

# A map between D3M dataset constants and semantic type URIs.
# TODO: Define properly those semantic types at those URIs.
SEMANTIC_TYPES = {
    # Resource types.
    'image': 'http://schema.org/ImageObject',
    'video': 'http://schema.org/VideoObject',
    'audio': 'http://schema.org/AudioObject',
    'text': 'http://schema.org/Text',
    'speech': 'https://metadata.datadrivendiscovery.org/types/Speech',
    'graph': 'https://metadata.datadrivendiscovery.org/types/Graph',
    'table': 'https://metadata.datadrivendiscovery.org/types/Table',
    'timeseries': 'https://metadata.datadrivendiscovery.org/types/Timeseries',
    # Column types.
    'boolean': 'http://schema.org/Boolean',
    'integer': 'http://schema.org/Integer',
    'real': 'http://schema.org/Float',
    'string': 'http://schema.org/Text',
    'categorical': 'https://metadata.datadrivendiscovery.org/types/CategoricalData',
    'dateTime': 'https://metadata.datadrivendiscovery.org/types/Time',
    # Column roles.
    'index': 'https://metadata.datadrivendiscovery.org/types/PrimaryKey',
    'key': 'https://metadata.datadrivendiscovery.org/types/UniqueKey',
    'attribute': 'https://metadata.datadrivendiscovery.org/types/Attribute',
    'suggestedTarget': 'https://metadata.datadrivendiscovery.org/types/SuggestedTarget',
    'timeIndicator': 'https://metadata.datadrivendiscovery.org/types/Time',
    'locationIndicator': 'https://metadata.datadrivendiscovery.org/types/Location',
    'boundaryIndicator': 'https://metadata.datadrivendiscovery.org/types/Boundary',
    'instanceWeight': 'https://metadata.datadrivendiscovery.org/types/InstanceWeight',
}


def parse_size(size_string: str) -> int:
    number, unit = [string.strip() for string in size_string.split()]
    return int(float(number) * UNITS[unit])


class Loader(abc.ABC):
    """
    A base class for dataset loaders.
    """

    @abc.abstractmethod
    def can_load(self, dataset_uri: str) -> bool:
        """
        Return ``True`` if this loader can load a dataset from a given URI ``dataset_uri``.

        Parameters
        ----------
        dataset_uri : str
            A URI to load a dataset from.

        Returns
        -------
        bool
            ``True`` if this loader can load a dataset from ``dataset_uri``.
        """

    @abc.abstractmethod
    def load(self, dataset_uri: str, *, dataset_id: str = None, dataset_version: str = None, dataset_name: str = None) -> 'Dataset':
        """
        Loads the dataset at ``dataset_uri``.

        Parameters
        ----------
        dataset_uri : str
            A URI to load.
        dataset_id : str
            Override dataset ID determined by the loader.
        dataset_version : str
            Override dataset version determined by the loader.
        dataset_name : str
            Override dataset name determined by the loader.

        Returns
        -------
        Dataset
            A loaded dataset.
        """


class D3MDatasetLoader(Loader):
    """
    A class for loading of D3M datasets.

    Loader support only loading from a local file system.
    URI should point to the ``datasetDoc.json`` file in the D3M dataset directory.
    """

    CURRENT_VERSION = '3.0'

    def can_load(self, dataset_uri: str) -> bool:
        try:
            parsed_uri = url_parse.urlparse(dataset_uri)
        except Exception:
            return False

        if parsed_uri.scheme != 'file':
            return False

        if parsed_uri.netloc not in ['', 'localhost']:
            return False

        if not parsed_uri.path.startswith('/'):
            return False

        if os.path.basename(parsed_uri.path) != 'datasetDoc.json':
            return False

        return True

    def load(self, dataset_uri: str, *, dataset_id: str = None, dataset_version: str = None, dataset_name: str = None) -> 'Dataset':
        assert self.can_load(dataset_uri)

        parsed_uri = url_parse.urlparse(dataset_uri)

        dataset_doc_path = parsed_uri.path
        dataset_path = os.path.dirname(dataset_doc_path)

        with open(dataset_doc_path, 'r') as dataset_doc_file:
            dataset_doc = json.load(dataset_doc_file)

        if dataset_doc.get('about', {}).get('datasetSchemaVersion', None) != self.CURRENT_VERSION:
            raise NotImplementedError("Only supporting dataset descriptions whose schema version is {version}.".format(version=self.CURRENT_VERSION))

        resources = {}
        metadata = metadata_module.DataMetadata()

        for data_resource in dataset_doc['dataResources']:
            if data_resource['isCollection']:
                resources[data_resource['resID']], metadata = self._load_collection(dataset_path, data_resource, metadata)
            else:
                loader = getattr(self, '_load_resource_type_{resource_type}'.format(resource_type=data_resource['resType']), None)
                if loader is None:
                    raise NotImplementedError("Resource type '{resource_type}' is not supported.".format(resource_type=data_resource['resType']))

                resources[data_resource['resID']], metadata = loader(dataset_path, data_resource, metadata)

        dataset_metadata = {
            'schema': metadata_module.CONTAINER_SCHEMA_VERSION,
            'structural_type': Dataset,
            'id': dataset_id or dataset_doc['about']['datasetID'],
            # "datasetVersion" is required by the schema, but we want to be compatible with
            # dataset problem descriptions which do not adhere to the schema.
            'version': dataset_version or dataset_doc['about'].get('datasetVersion', '1.0'),
            'name': dataset_name or dataset_doc['about']['datasetName'],
            'location_uris': [
                # We reconstruct the URI to normalize it.
                'file://{dataset_doc_path}'.format(dataset_doc_path=dataset_doc_path),
            ],
            'dimension': {
                'name': 'resources',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/DatasetResource'],
                'length': len(resources),
            },
        }

        if dataset_doc['about'].get('description', None):
            dataset_metadata['description'] = dataset_doc['about']['description']

        if dataset_doc['about'].get('approximateSize', None):
            try:
                dataset_metadata['approximate_stored_size'] = parse_size(dataset_doc['about']['approximateSize'])
            except Exception as error:
                raise ValueError("Unable to parse 'approximateSize': {approximate_size}".format(approximate_size=dataset_doc['about']['approximateSize'])) from error

        if dataset_doc['about'].get('datasetURI', None):
            typing.cast(typing.List[str], dataset_metadata['location_uris']).append(dataset_doc['about']['datasetURI'])

        dataset_source = {
            'license': dataset_doc['about']['license'],
            'redacted': dataset_doc['about']['redacted'],
            # "humanSubjectsResearch" is required by the schema, but we want to be compatible with
            # dataset problem descriptions which do not adhere to the schema.
            'human_subjects_research': dataset_doc['about'].get('humanSubjectsResearch', False),
        }

        if dataset_doc['about'].get('source', None):
            dataset_source['name'] = dataset_doc['about']['source']

        if dataset_doc['about'].get('citation', None):
            dataset_source['citation'] = dataset_doc['about']['citation']

        if dataset_doc['about'].get('publicationDate', None):
            try:
                # If no timezone information is provided, we assume UTC. If there is timezone information, we convert
                # timestamp to UTC, but then remove timezone information before formatting to not have "+00:00" added
                # and we then manually add "Z" instead (which has equivalent meaning).
                dataset_source['published'] = dateparser.parse(dataset_doc['about']['publicationDate'], settings={'TIMEZONE': 'UTC'}).replace(tzinfo=None).isoformat('T') + 'Z'
            except Exception as error:
                raise ValueError("Unable to parse 'publicationDate': {publication_date}".format(publication_date=dataset_doc['about']['publicationDate'])) from error

        if dataset_doc['about'].get('sourceURI', None):
            dataset_source['uris'] = [dataset_doc['about']['sourceURI']]

        dataset_metadata['source'] = dataset_source

        if dataset_doc['about'].get('applicationDomain', None):
            # Application domain has no vocabulary specified so we map it to keywords.
            dataset_metadata['keywords'] = [dataset_doc['about']['applicationDomain']]

        metadata = metadata.update((), dataset_metadata)

        return Dataset(resources, metadata)

    def _load_collection(self, dataset_path: str, data_resource: typing.Dict, metadata: metadata_module.DataMetadata) -> typing.Tuple[numpy.ndarray, metadata_module.DataMetadata]:
        assert data_resource['isCollection']

        collection_path = os.path.join(dataset_path, data_resource['resPath'])

        # We sort to get a stable list which is everywhere the same.
        filenames = []
        for filename in sorted(os.listdir(collection_path)):
            if not os.path.isfile(os.path.join(collection_path, filename)):
                continue

            filenames.append(filename)

        data = numpy.array(filenames, dtype=object).reshape((len(filenames), 1))

        metadata = metadata.update((data_resource['resID'],), {
            'structural_type': type(data),
            'semantic_types': [SEMANTIC_TYPES[data_resource['resType']]],
            'dimension': {
                'name': 'rows',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularRow'],
                'length': len(data),
            },
        })

        metadata = metadata.update((data_resource['resID'], metadata_module.ALL_ELEMENTS), {
            'dimension': {
                'name': 'columns',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularColumn'],
                'length': 1,
            },
        })

        location_base_uri = 'file://{collection_path}'.format(collection_path=collection_path)
        if not location_base_uri.endswith('/'):
            location_base_uri += '/'

        metadata = metadata.update((data_resource['resID'], metadata_module.ALL_ELEMENTS, 0), {
            'name': 'filename',
            'structural_type': str,
            'location_base_uris': [
                location_base_uri,
            ],
            'mime_types': data_resource['resFormat'],
            'semantic_types': [
                'https://metadata.datadrivendiscovery.org/types/PrimaryKey',
                'https://metadata.datadrivendiscovery.org/types/FileName',
            ],
        })

        return data, metadata

    def _load_resource_type_table(self, dataset_path: str, data_resource: typing.Dict, metadata: metadata_module.DataMetadata) -> typing.Tuple[numpy.ndarray, metadata_module.DataMetadata]:
        assert not data_resource['isCollection']

        data = None
        column_names = None
        data_path = os.path.join(dataset_path, data_resource['resPath'])

        expected_names = None
        if data_resource.get('columns', None):
            expected_names = []
            for i, column in enumerate(data_resource['columns']):
                assert i == column['colIndex'], (i, column['colIndex'])
                expected_names.append(column['colName'])

        if data_resource['resFormat'] == ['text/csv']:
            for extension in ('', '.gz', '.bz2', '.zip', 'xz'):
                if os.path.exists(data_path + extension):
                    data_path += extension
                    pandas_data = pandas.read_csv(
                        data_path,
                        usecols=expected_names,
                        # We do not want to do any conversion of values at this point.
                        # This should be done by primitives later on.
                        dtype=str,
                        # We always expect one row header.
                        header=0,
                        # We want empty strings and not NaNs.
                        na_filter=False,
                        encoding='utf8',
                        low_memory=False,
                        memory_map=True,
                    )

                    column_names = list(pandas_data.columns)
                    data = pandas_data.values

                    if expected_names is not None and expected_names != column_names:
                        raise ValueError("Mismatch between column names in data {column_names} and expected names {expected_names}.".format(
                            column_names=column_names,
                            expected_names=expected_names,
                        ))

                    break

        else:
            raise NotImplementedError("Resource format '{resource_format}' for table '{resource_path}' is not supported.".format(
                resource_format=data_resource['resFormat'],
                resource_path=data_resource['resPath']
            ))

        if data is None:
            raise FileNotFoundError("Data file for table '{resource_path}' cannot be found.".format(
                resource_path=data_resource['resPath']
            ))

        assert column_names is not None

        metadata = metadata.update((data_resource['resID'],), {
            'structural_type': type(data),
            'semantic_types': [SEMANTIC_TYPES[data_resource['resType']]],
            'dimension': {
                'name': 'rows',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularRow'],
                'length': len(data),
            },
        })

        metadata = metadata.update((data_resource['resID'], metadata_module.ALL_ELEMENTS), {
            'dimension': {
                'name': 'columns',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularColumn'],
                'length': len(column_names),
            },
        })

        for i, column_name in enumerate(column_names):
            metadata = metadata.update((data_resource['resID'], metadata_module.ALL_ELEMENTS, i), {
                'name': column_name,
                'structural_type': str,
            })

        if expected_names is not None:
            REFERENCE_MAP = {
                'node': 'NODE',
                'nodeAttribute': 'NODE_ATTRIBUTE',
                'edge': 'EDGE',
                'edgeAttribute': 'EDGE_ATTRIBUTE',
            }

            for i, column in enumerate(data_resource['columns']):
                semantic_types = [SEMANTIC_TYPES[column['colType']]]

                # TODO: We ignore isIgnore. Ignored columns should just have empty roles.
                #       See: https://gitlab.datadrivendiscovery.org/MIT-LL/d3m_data_supply/issues/48
                for role in column['role']:
                    semantic_types.append(SEMANTIC_TYPES[role])

                column_metadata: typing.Dict[str, typing.Any] = {
                    'semantic_types': semantic_types,
                }

                if column.get('refersTo', None):
                    if isinstance(column['refersTo']['resObject'], str):
                        if column['refersTo']['resObject'] == 'item':
                            # We represent collections as a table with one column of filenames.
                            column_metadata['foreign_key'] = {
                                'type': 'COLUMN',
                                'resource_id': column['refersTo']['resID'],
                                'column_index': 0,
                            }
                        elif column['refersTo']['resObject'] in REFERENCE_MAP.keys():
                            column_metadata['foreign_key'] = {
                                'type': REFERENCE_MAP[column['refersTo']['resObject']],
                                'resource_id': column['refersTo']['resID'],
                            }
                        else:
                            raise ValueError("Unknown \"resObject\" value: {resource_object}".format(resource_object=column['refersTo']['resObject']))
                    else:
                        if 'columnIndex' in column['refersTo']['resObject']:
                            column_metadata['foreign_key'] = {
                                'type': 'COLUMN',
                                'resource_id': column['refersTo']['resID'],
                                'column_index': column['refersTo']['resObject']['columnIndex'],
                            }
                        elif 'columnName' in column['refersTo']['resObject']:
                            column_metadata['foreign_key'] = {
                                'type': 'COLUMN',
                                'resource_id': column['refersTo']['resID'],
                                'column_name': column['refersTo']['resObject']['columnName'],
                            }
                        else:
                            raise ValueError("Unknown \"resObject\" value: {resource_object}".format(resource_object=column['refersTo']['resObject']))

                metadata = metadata.update((data_resource['resID'], metadata_module.ALL_ELEMENTS, i), column_metadata)

        return data, metadata

    def _load_resource_type_timeseries(self, dataset_path: str, data_resource: typing.Dict, metadata: metadata_module.DataMetadata) -> typing.Tuple[numpy.ndarray, metadata_module.DataMetadata]:
        assert not data_resource['isCollection']

        return self._load_resource_type_table(dataset_path, data_resource, metadata)

    def _load_resource_type_graph(self, dataset_path: str, data_resource: typing.Dict, metadata: metadata_module.DataMetadata) -> \
            typing.Tuple[typing.Union[networkx.classes.graph.Graph, networkx.classes.digraph.DiGraph, networkx.classes.multigraph.MultiGraph,
                                      networkx.classes.multidigraph.MultiDiGraph], metadata_module.DataMetadata]:

        assert not data_resource['isCollection']

        data = None
        data_path = os.path.join(dataset_path, data_resource['resPath'])

        if data_resource['resFormat'] == ['text/gml']:
            for extension in ('', '.gz', '.bz2', '.gzip'):
                if os.path.exists(data_path + extension):
                    data_path += extension
                    data = networkx.read_gml(data_path, label='id')

                    break

        else:
            raise NotImplementedError("Resource format '{resource_format}' for graph '{resource_path}' is not supported.".format(
                resource_format=data_resource['resFormat'],
                resource_path=data_resource['resPath']
            ))

        if data is None:
            raise FileNotFoundError("Data file for graph '{resource_path}' cannot be found.".format(
                resource_path=data_resource['resPath']
            ))

        metadata = metadata.update((data_resource['resID'],), {
            'structural_type': type(data),
            'semantic_types': [SEMANTIC_TYPES[data_resource['resType']]],
            'dimension': {
                'name': 'nodes',
                'length': len(data),
            },
        })

        return data, metadata


class CSVLoader(Loader):
    """
    A class for loading a dataset from a CSV file.

    Loader supports both loading a dataset from a local file system or remote locations.
    URI should point to a file with ``.csv`` file extension.
    """

    def can_load(self, dataset_uri: str) -> bool:
        try:
            parsed_uri = url_parse.urlparse(dataset_uri)
        except Exception:
            return False

        if parsed_uri.scheme not in pandas_io_common._VALID_URLS:
            return False

        if parsed_uri.scheme == 'file':
            if parsed_uri.netloc not in ['', 'localhost']:
                return False

            if not parsed_uri.path.startswith('/'):
                return False

        for extension in ('', '.gz', '.bz2', '.zip', 'xz'):
            if parsed_uri.path.endswith('.csv' + extension):
                return True

        return False

    def load(self, dataset_uri: str, *, dataset_id: str = None, dataset_version: str = None, dataset_name: str = None) -> 'Dataset':
        assert self.can_load(dataset_uri)

        parsed_uri = url_parse.urlparse(dataset_uri)

        # Pandas requires a host for "file" URIs.
        if parsed_uri.scheme == 'file' and parsed_uri.netloc == '':
            parsed_uri = parsed_uri._replace(netloc='localhost')
            dataset_uri = url_parse.urlunparse(parsed_uri)

        # We read URI into a buffer manually to be able to compute a hash on the content.
        compression = pandas_io_common._infer_compression(dataset_uri, 'infer')
        buffer, _, compression = pandas_io_common.get_filepath_or_buffer(dataset_uri, 'utf8', compression)

        pandas_data = pandas.read_csv(
            buffer,
            # We do not want to do any conversion of values at this point.
            # This should be done by primitives later on.
            dtype=str,
            # We always expect one row header.
            header=0,
            # We want empty strings and not NaNs.
            na_filter=False,
            compression=compression,
            encoding='utf8',
            low_memory=False,
        )

        column_names = list(pandas_data.columns)
        data = pandas_data.values

        resources = {
            '0': data,
        }
        metadata = metadata_module.DataMetadata()

        metadata = metadata.update(('0',), {
            'structural_type': type(data),
            'semantic_types': ['https://metadata.datadrivendiscovery.org/types/Table'],
            'dimension': {
                'name': 'rows',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularRow'],
                'length': len(data),
            },
        })

        metadata = metadata.update(('0', metadata_module.ALL_ELEMENTS), {
            'dimension': {
                'name': 'columns',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularColumn'],
                'length': len(column_names),
            },
        })

        for i, column_name in enumerate(column_names):
            metadata = metadata.update(('0', metadata_module.ALL_ELEMENTS, i), {
                'name': column_name,
                'structural_type': str,
            })

        buffer_value = buffer.getvalue()

        dataset_metadata = {
            'schema': metadata_module.CONTAINER_SCHEMA_VERSION,
            'structural_type': Dataset,
            'id': dataset_id or dataset_uri,
            'version': dataset_version or hashlib.sha256(buffer_value).hexdigest(),
            'name': dataset_name or os.path.basename(parsed_uri.path),
            'location_uris': [
                dataset_uri,
            ],
            'stored_size': len(buffer_value),
            'dimension': {
                'name': 'resources',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/DatasetResource'],
                'length': len(resources),
            },
        }

        metadata = metadata.update((), dataset_metadata)

        return Dataset(resources, metadata)


class SklearnExampleLoader(Loader):
    """
    A class for loading example scikit-learn datasets.

    URI should be of the form ``sklearn://<name of the dataset>``, where names come from
    ``sklearn.datasets.load_*`` function names.
    """

    def can_load(self, dataset_uri: str) -> bool:
        if dataset_uri.startswith('sklearn://'):
            return True

        return False

    def load(self, dataset_uri: str, *, dataset_id: str = None, dataset_version: str = None, dataset_name: str = None) -> 'Dataset':
        assert self.can_load(dataset_uri)

        dataset_path = dataset_uri[len('sklearn://'):]

        if not hasattr(datasets, 'load_{dataset_path}'.format(dataset_path=dataset_path)):
            raise ValueError("Unknown sklearn dataset '{dataset_path}'.".format(dataset_path=dataset_path))

        bunch = getattr(datasets, 'load_{dataset_path}'.format(dataset_path=dataset_path))()

        bunch_data = bunch['data']
        bunch_target = bunch['target']

        if len(bunch_data.shape) == 1:
            bunch_data = bunch_data.reshape((bunch_data.shape[0], 1))
        if len(bunch_target.shape) == 1:
            bunch_target = bunch_target.reshape((bunch_target.shape[0], 1))

        column_names = []
        target_values = None

        if 'feature_names' in bunch:
            for feature_name in bunch['feature_names']:
                column_names.append(str(feature_name))

        if 'target_names' in bunch:
            if len(bunch['target_names']) == bunch_target.shape[1]:
                for target_name in bunch['target_names']:
                    column_names.append(str(target_name))
            else:
                target_values = [str(target_value) for target_value in bunch['target_names']]

        if target_values is not None:
            converted_target = numpy.empty(bunch_target.shape, dtype=object)

            for i, row in enumerate(bunch_target):
                for j, column in enumerate(row):
                    converted_target[i, j] = target_values[column]
        else:
            converted_target = bunch_target

        data = numpy.concatenate((bunch_data, converted_target), axis=1)

        resources = {
            '0': data,
        }
        metadata = metadata_module.DataMetadata()

        metadata = metadata.update(('0',), {
            'structural_type': type(data),
            'semantic_types': ['https://metadata.datadrivendiscovery.org/types/Table'],
            'dimension': {
                'name': 'rows',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularRow'],
                'length': len(data),
            },
        })

        metadata = metadata.update(('0', metadata_module.ALL_ELEMENTS), {
            'dimension': {
                'name': 'columns',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/TabularColumn'],
                'length': len(data[0]),
            },
        })

        for column_index in range(bunch_data.shape[1]):
            column_metadata: typing.Dict[str, typing.Any] = {
                'structural_type': bunch_data.dtype.type,
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/Attribute'],
            }

            if column_index < len(column_names):
                column_metadata['name'] = column_names[column_index]

            metadata = metadata.update(('0', metadata_module.ALL_ELEMENTS, column_index), column_metadata)

        for i in range(bunch_target.shape[1]):
            column_index = bunch_data.shape[1] + i

            column_metadata = {
                'structural_type': str if target_values is not None else bunch_target.dtype.type,
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/SuggestedTarget'],
            }

            if column_index < len(column_names):
                column_metadata['name'] = column_names[column_index]

            if target_values is not None:
                column_metadata['semantic_types'].append('https://metadata.datadrivendiscovery.org/types/CategoricalData')

            metadata = metadata.update(('0', metadata_module.ALL_ELEMENTS, column_index), column_metadata)

        hash = hashlib.sha256()

        hash.update(bunch['data'].tobytes())
        hash.update(bunch['target'].tobytes())

        if 'feature_names' in bunch:
            if isinstance(bunch['feature_names'], list):
                for feature_name in bunch['feature_names']:
                    hash.update(feature_name.encode('utf8'))
            else:
                hash.update(bunch['feature_names'].tobytes())

        if 'target_names' in bunch:
            if isinstance(bunch['target_names'], list):
                for target_name in bunch['target_names']:
                    hash.update(target_name.encode('utf8'))
            else:
                hash.update(bunch['target_names'].tobytes())

        if 'DESCR' in bunch:
            hash.update(bunch['DESCR'].encode('utf8'))

        dataset_metadata = {
            'schema': metadata_module.CONTAINER_SCHEMA_VERSION,
            'structural_type': Dataset,
            'id': dataset_id or dataset_uri,
            'version': dataset_version or hash.hexdigest(),
            'name': dataset_name or dataset_path,
            'location_uris': [
                dataset_uri,
            ],
            'dimension': {
                'name': 'resources',
                'semantic_types': ['https://metadata.datadrivendiscovery.org/types/DatasetResource'],
                'length': len(resources),
            },
        }

        if bunch.get('DESCR', None):
            dataset_metadata['description'] = bunch['DESCR']

        metadata = metadata.update((), dataset_metadata)

        return Dataset(resources, metadata)


# TODO: It should be probably immutable.
class Dataset(dict):
    """
    A class representing a dataset.

    Internally, it is a dictionary containing multiple resources (e.g., tables).

    Parameters
    ----------
    resources : Mapping
        A map from resource IDs to resources.
    metadata : DataMetadata
        Metadata associated with the ``data``.
    """

    metadata: metadata_module.DataMetadata = None
    loaders: typing.List[Loader] = [
        D3MDatasetLoader(),
        CSVLoader(),
        SklearnExampleLoader(),
    ]

    def __init__(self, resources: typing.Mapping, metadata: metadata_module.DataMetadata) -> None:
        super().__init__(resources)

        self.metadata = metadata

    @classmethod
    def load(cls, dataset_uri: str, *, dataset_id: str = None, dataset_version: str = None, dataset_name: str = None) -> 'Dataset':
        """
        Tries to load dataset from ``dataset_uri`` using all registered dataset loaders.

        Parameters
        ----------
        dataset_uri : str
            A datset URI to load.
        dataset_id : str
            Override dataset ID determined by the loader.
        dataset_version : str
            Override dataset version determined by the loader.
        dataset_name : str
            Override dataset name determined by the loader.

        Returns
        -------
        Dataset
            A loaded dataset.
        """

        for loader in cls.loaders:
            if loader.can_load(dataset_uri):
                return loader.load(dataset_uri, dataset_id=dataset_id, dataset_version=dataset_version, dataset_name=dataset_name)

        raise NotImplementedError("No known loader could load dataset '{dataset_uri}'.".format(dataset_uri=dataset_uri))

    # TODO: Allow one to specify priority which would then insert loader at a different place and not at the end?
    @classmethod
    def register_loader(cls, loader: Loader) -> None:
        """
        Registers a new datset loader.

        Parameters
        ----------
        loader : Loader
            An instance of the loader class implementing a new loader.
        """

        cls.loaders.append(loader)


if __name__ == '__main__':
    import pprint
    import sys

    for dataset_file_path in sys.argv[1:]:
        try:
            dataset = Dataset.load('file://{dataset_doc_path}'.format(dataset_doc_path=os.path.abspath(dataset_file_path)))
            pprint.pprint(dataset)
            dataset.metadata.pretty_print()
        except Exception as error:
            raise Exception("Unable to load dataset: {dataset_doc_path}".format(dataset_doc_path=dataset_file_path)) from error
