from collections import defaultdict
from six.moves.urllib.parse import quote
from typing import cast, Any, Dict, List, Sequence, Set, Text, Union  # NOQA
import collections
import datetime
import os
import re
import six
import sys
import time
import traceback
import warnings

from pandas import DataFrame  # type: ignore
# This is imported from `future` so its type checking is wonky
import html  # type: ignore
import pandas as pd  # type: ignore
import tqdm  # type: ignore

from .edpclient import NoSuchGeneratorError
from .edpclient import EdpClient, Visibility, CallableEndpoint
from .population_model import PopulationModel
from .population_schema import PopulationSchema  # NOQA

# Always refetch a population's schema if this duration has elapsed since the
# last fetch, to pick up changes made outside the edpanalyst session.
SCHEMA_INVALIDATION_SECS = 30

EPOCH = datetime.datetime(1970, 1, 1)


def _date_to_days(v, col_name):  # type: (Any, str) -> int
    """Converts a date-like object or str, `v`, to days since the epoch."""
    if isinstance(v, str):
        try:
            v = datetime.datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('value %r in column %r is not an ISO 8601 date' %
                             (v, col_name))
    elif (not isinstance(v, pd.Timestamp) and
          not isinstance(v, datetime.datetime) and
          not isinstance(v, datetime.date)):
        raise ValueError('value %r in column %r is not convertible to a date' %
                         (v, col_name))
    return (datetime.datetime(v.year, v.month, v.day) - EPOCH).days


class AmbiguityWarning(UserWarning):
    pass


class Session(object):

    def __init__(
            self,
            profile=None,  # type: str
            edp_url=None,  # type: str
            bearer_token=None,  # type: Text
            endpoint=None  # type: CallableEndpoint
    ):  # type: (...) -> None
        self._client = EdpClient(profile=profile, edp_url=edp_url,
                                 bearer_token=bearer_token)
        if endpoint is None:
            url = (self._client.config.edp_url + '/rpc')
            endpoint = CallableEndpoint(url, self._client._session)
        self._endpoint = endpoint
        # Try and list so we raise an error if you're not auth'd
        self.list_populations()

    def list(self, keyword=None):
        pops = self._endpoint.population.get().json()
        models = [m for pop in pops for m in pop['models']]
        models_df = DataFrame({
            'id': [pm['id'] for pm in models],
            'name': [pm['name'] for pm in models],
            'parent_id': [pm.get('parent_id') for pm in models],
            'creation_time':
            [pd.to_datetime(pm['creation_time'], unit='s') for pm in models],
            'status': [pm['build_progress']['status'] for pm in models],
        }, columns=['id', 'name', 'parent_id', 'creation_time', 'status'])
        return _filtered(models_df, keyword)

    def list_populations(self, keyword=None):
        pops = self._endpoint.population.get().json()
        pops_df = DataFrame({
            'id': [pop['id'] for pop in pops],
            'name': [pop['name'] for pop in pops],
            'creation_time':
            [pd.to_datetime(pop['creation_time'], unit='s') for pop in pops],
            'num_models': [len(pop['models']) for pop in pops]
        }, columns=['id', 'name', 'creation_time', 'num_models'])
        return _filtered(pops_df, keyword)

    def population(self, pid):  # type: (str) -> Population
        """Returns the Population corresponding to `pid`."""
        try:
            return Population(pid, self._client)
        except NoSuchGeneratorError:
            if pid.startswith('pm-'):
                raise NoSuchGeneratorError(
                    'You used a Population Model ID, '
                    'calling a population requires the Population ID.')
            else:
                raise NoSuchGeneratorError('Unknown Population ID')

    def popmod(self, pmid):  # type: (str) -> PopulationModel
        """Returns the PopulationModel corresponding to `pmid`."""
        try:
            return PopulationModel(pmid, self._client)
        except NoSuchGeneratorError:
            if pmid.startswith('p-'):
                raise NoSuchGeneratorError(
                    'You used a Population ID, '
                    'calling a population model requires the '
                    'Population Model ID.')
            else:
                raise NoSuchGeneratorError('Unknown Population Model ID')

    def upload(
            self,
            data,  # type: DataFrame
            name,  # type: str
            schema=None,  # type: PopulationSchema
            hints=None,  # type: Dict[str, Any]
            autobuild=True,  # type: bool
            random_seed=None,  # type: int
    ):  # type: (...) -> Population
        """Create a population in EDP from uploaded data.

        Args:
            data: The data to create a population from.
            name: The name of the newly created population.
            schema: The schema describing the data. If not provided the server
                will attempt to guess one for you.
            hints: Provide hints to the guesser if not providing a schema.
            autobuild: If true, a number of model builds will be started
                automatically after creating the population
            random_seed: A random seed to make the build deterministic. Only
                meaningful with autobuild=True.
        """
        # TODO(asilvers): We require you to upload strings for categoricals so
        # that there's no ambiguity as to the representation as there could be
        # if they were floats. But this auto-conversion doesn't really solve
        # that issue, it just hides it from you. These issues go away when we
        # upload raw data and do assembly server-side, since presumably at that
        # point you're uploading strings anyway (e.g. CSV from a file).
        # TODO(asilvers): Also consider not doing this for numeric columns.
        if schema and hints:
            raise ValueError('At most one of `schema` and `hints` '
                             'can be provided.')
        stringed_df = data.copy()
        for col in data.columns:
            stringed_df[col] = stringed_df[col].astype(six.text_type)
        nulled_df = stringed_df.where(pd.notnull(data), None)
        json_data = nulled_df.to_dict(orient='list')
        pid = self._client.upload_population(data=json_data, schema=schema,
                                             hints=hints, name=name)
        pop = Population(pid=pid, client=self._client)
        if autobuild:
            pop.build_model(name=name + ' (auto)', iterations=500,
                            ensemble_size=32, max_seconds=300,
                            random_seed=random_seed)
        return pop

    def upload_file(
            self,
            path,  # type: str
            name=None,  # type: str
            autobuild=True,  # type: bool
            random_seed=None,  # type: int
    ):  # type: (...) -> Population
        name = name if name is not None else os.path.basename(path)
        url = '%s/rpc/population/upload_raw_data' % (
            self._client.config.edp_url,)
        with open(path, 'rb') as f:
            resp = self._client._session.post(url, files={name: (name, f)})
        resp.raise_for_status()
        pid = resp.json()['id']
        pop = Population(pid=pid, client=self._client)
        if autobuild:
            pop.build_model(name=name + ' (auto)', iterations=500,
                            ensemble_size=32, max_seconds=300,
                            random_seed=random_seed)
        return pop

    def send_feedback(self, message, send_traceback=True):
        # type: (str, bool) -> None
        """Report feedback to Empirical's support team.

        Sends `message` along with the most recent exception (unless
        `send_traceback` is False).
        """
        req = {'message': message}
        if send_traceback and hasattr(sys, 'last_traceback'):
            req['traceback'] = ''.join(traceback.format_tb(sys.last_traceback))
        self._endpoint.feedback.post(json=req)


def _filtered(items, keyword):
    """Filter a data frame of population / population models."""
    if not keyword:
        return items

    idx = []
    for r in range(items.shape[0]):
        if (items.name[r].lower().find(keyword.lower()) != -1):
            idx.append(r)
    return items.loc[idx]


class Population(object):

    def __init__(
            self,
            pid,  # type: str
            client,  # type: EdpClient
            endpoint=None,  # type: CallableEndpoint
            time_fn=time.time):  # type: (...) -> None
        self._pid = pid
        self._client = client
        if endpoint is None:
            url = (self._client.config.edp_url +
                   '/rpc/population/%s' % quote(self._pid))
            endpoint = CallableEndpoint(url, self._client._session)
        self._endpoint = endpoint
        self.name  # Cause an error if this population doesn't exist
        self._schema = None  # type: PopulationSchema
        self._schema_fetch_time = None  # type: float
        self._time_fn = time_fn

    def __str__(self):  # type: () -> str
        return ('Population(id=%r, name=%r)' % (self._pid, self.name))

    def __repr__(self):  # type: () -> str
        return str(self)

    def _repr_html_(self):  # type: () -> str
        return (('<span>%s</span><br>' %
                 (html.escape(self.name),)) + '<span>Models:</span>'
                '<ul>' + ''.join([('<li>' + m._repr_html_() + '</li>')
                                  for m in self.models]) + '</ul>')

    def rename(self, name):  # type: (str) -> None
        """Rename this population."""
        self._endpoint.rename.post(json=name)

    def _metadata(self):  # type: () -> Dict[str, Any]
        # TODO(asilvers): Half of this metadata (e.g. creation_time) doesn't
        # ever change, so making a call for each access is unnecessary and
        # wasteful. But if it's causing problems we probably have bigger
        # problems. Think about this at some point.
        return self._endpoint.get().json()

    @property
    def id(self):  # type: () -> str
        return self._pid

    @property
    def name(self):  # type: () -> str
        return self._metadata()['name']

    @property
    def creation_time(self):  # type: () -> float
        return self._metadata()['creation_time']

    @property
    def user_metadata(self):  # type: () -> Dict[str, str]
        return self._metadata()['user_metadata']

    @property
    def models(self):  # type: () -> List[PopulationModel]
        return [
            PopulationModel(model['id'], self._client)
            for model in self._metadata()['models']
        ]

    @property
    def schema(self):  # type: () -> PopulationSchema
        if self._schema is None or self._time_fn(
        ) - self._schema_fetch_time > SCHEMA_INVALIDATION_SECS:
            resp = self._endpoint.schema.get()
            self._schema = PopulationSchema.from_json(resp.json())
            self._schema_fetch_time = self._time_fn()

        return self._schema

    def visibility(self):  # type: () -> Visibility
        """Fetches visibility for this population."""
        resp = self._endpoint.visibility.get()
        return Visibility.from_json(resp.json())

    def delete(self):  # type: () -> None
        """Delete this population.

        This Population object will become invalid after deletion.
        """
        self._endpoint.delete()

    def make_public(self):  # type: () -> Visibility
        """Make this population public.

        Returns the ACL for the population after the modification.
        """
        req = {'public': True}
        resp = self._endpoint.visibility.patch(json=req)
        return Visibility.from_json(resp.json())

    def add_reader(self, reader,
                   send_email=False):  # type: (str, bool) -> Visibility
        """Add `reader` to this population's reader list.

        Args:
            reader: The email of the user who should have read access to the
                population.
            send_email: Whether to send an email to the new reader.

        Returns the ACL for this model after the modification.
        """
        req = {'readers': [reader], 'send_email': send_email}
        resp = self._endpoint.visibility.patch(json=req)
        return Visibility.from_json(resp.json())

    def add_reader_domain(self, domain):  # type): (str) -> Visibility
        """Give all users on `domain` read access to this population.

        Args:
            domain: The domain to grant read access to. Must begin with '@'.

        Returns the ACL for this model after the modification.
        """
        req = {'reader_domain': domain}
        resp = self._endpoint.visibility.patch(json=req)
        return Visibility.from_json(resp.json())

    def remove_reader(self, reader):  # type: (str) -> Visibility
        """Remove `reader` from this population's reader list.

        Args:
            reader: The email of the user whose read access to remove.

        Returns the ACL for this model after the modification. If the given
        user does not already have read access, this method will return
        successfully but have no effect.
        """
        req = {'remove_readers': [reader]}
        resp = self._endpoint.visibility.patch(json=req)
        return Visibility.from_json(resp.json())

    def remove_reader_domain(self, domain):  # type: (str) -> Visibility
        """Remove domain-wide read access from `domain`.

        Users in `domain` whose emails were individually added will not have
        their read access removed.

        Args:
            reader: The domain to remove read access from. Must begin with '@'.

        Returns the ACL for this model after the modification. If the given
        domain does not already have read access, this method will return
        successfully but have no effect.
        """
        req = {'remove_reader_domain': domain}
        resp = self._endpoint.visibility.patch(json=req)
        return Visibility.from_json(resp.json())

    def _find_latest(self, models):
        """Return the latest built model, or None if none exist."""
        if len(models) == 0:
            # If no models are being built then it's probably silly to wait
            raise ValueError('This population has no models')

        built = [m for m in models if m['build_progress']['status'] == 'built']
        if len(built) > 0:
            # TODO(asilvers): This is actually looking at models' creation
            # times, not how recently they finished building. That's probably
            # not quite right.
            latest = max(built, key=lambda m: m['creation_time'])
            return PopulationModel(latest['id'], self._client)
        else:
            return None

    # Wait 70 seconds by default. 60 seconds for the 1 minute model build, and
    # an extra 10 for post-build finish-up stuff.
    def latest(self, wait=70):  # type: (int) -> PopulationModel
        """Returns this population's most recently built model.

        This will wait up to `wait` seconds for a model to finish building.

        Raises `ValueError` if `wait` is 0 (or falsey) and this model has no
        already-built models, or if `wait` seconds have elapsed and no models
        have finished.
        """
        timeout_time = time.time() + wait
        with tqdm.tqdm(unit='', leave=False) as progress_bar:
            current_pb_state = 0
            while True:
                models = self._metadata()['models']
                latest = self._find_latest(models)
                if latest:
                    return latest
                if time.time() > timeout_time:
                    break

                # TODO(asilvers): Just bail if we think we're not gonna make
                # it?
                build_progress = _min_seconds_remaining(models)
                if build_progress:
                    progress_bar.total = build_progress.total
                    # `tqdm.update` adds its argument to progress, not sets it,
                    # and doesn't provide a way to do so. Which means we need
                    # to do this silly runaround. Why not pick a different
                    # progress bar then? Because asilvers@ already wasted
                    # enough time on this.
                    to_add = build_progress.elapsed - current_pb_state
                    progress_bar.update(to_add)
                    current_pb_state = current_pb_state + to_add
                # TODO(asilvers): Am I going to regret the number of
                # metadata REST calls this puts out?
                time.sleep(1)
        # Don't mention timeouts if we didn't wait
        if not wait:
            raise ValueError('This population has no built models')
        raise ValueError('Timed out waiting for models to finish building')

    def build_model(
            self,
            name=None,  # type: str
            ensemble_size=16,  # type: int
            iterations=100,  # type: int
            max_seconds=None,  # type: int
            builder='lazy',  # type: str
            random_seed=None,  # type: int
            clusters=None,  # type: int
    ):  # type: (...) -> PopulationModel
        """Build a model from this population.

        Args:
            name: The name of the newly built model
            ensemble_size: How many sub-models to build in the model ensemble.
            iterations: The number of iterations to build for
            max_seconds: If set, the model build will attempt to take no longer
                than this many seconds to build. This is not a hard limit.
            builder: Which builder to use.
            random_seed: A random seed to make the build deterministic.
            clusters: Number of clusters when `builder` is "cv" (experimental).
        """
        name = name or self.name
        req = {
            'name': name,
            'build_def': {
                'num_models': ensemble_size,
                'builder': builder,
                'duration': {
                    'iterations': iterations
                }
            }
        }  # type: Dict[str, Any]
        if random_seed is not None:
            req['build_def']['random_seed'] = random_seed
        if max_seconds is not None:
            req['build_def']['duration']['max_seconds'] = max_seconds
        if clusters is not None:
            req['build_def']['clusters'] = clusters
        resp = self._endpoint.build.post(json=req)
        return PopulationModel(resp.json()['id'], self._client)

    def clone_data(self, name=None, schema=None, hints=None):
        # type(str, PopulationSchema, Dict) -> None
        """Create a new population with the same data as this one, and possibly
        a new schema.
        """
        endpoint = CallableEndpoint('%s/clone_data' % (self._endpoint.url,),
                                    self._client._session)
        req = {}
        if name:
            req['name'] = name
        if schema:
            req['schema'] = schema
        if hints:
            req['hints'] = hints

        resp = endpoint.post(json=req)
        return Population(resp.json()['id'], self._client)

    def set_column_display_name(self, column,
                                display_name):  # type(str, str) -> None
        """Sets the display name for a column.

        Passing None or an empty string removes a previously set display name.
        """
        display_name = display_name or ''
        # URL path components need to be escaped twice in order for embedded
        # slashes to be handled correctly.
        endpoint = CallableEndpoint(
            '%s/column/%s/display_name' % (self._endpoint.url,
                                           _double_encode(column)),
            self._client._session)
        endpoint.post(json=display_name)
        # Clear cached schema so we pick up the new value.
        self._schema = None

    def set_column_description(self, column,
                               description):  # type(str, str) -> None
        """Sets the description for a column.

        Passing None or an empty string removes a previously set description.
        """
        description = description or ''
        endpoint = CallableEndpoint(
            '%s/column/%s/description' % (self._endpoint.url,
                                          _double_encode(column)),
            self._client._session)
        endpoint.post(json=description)
        self._schema = None

    def set_categorical_display_value(
            self, column, categorical_value,
            display_value):  # type(str, str, str) -> None
        """Sets the display value for a value of a categorical column.

        Passing None or an empty string removes a previously set display value.
        """
        display_value = display_value or ''
        endpoint = CallableEndpoint(
            '%s/column/%s/values/%s/display_value' %
            (self._endpoint.url, _double_encode(column),
             _double_encode(categorical_value)), self._client._session)
        endpoint.post(json=display_value)
        self._schema = None

    def set_categorical_value_description(
            self, column, categorical_value,
            description):  # type(str, str, str) -> None
        """Sets the description for a value of a categorical column.

        Passing None or an empty string removes a previously set description.
        """
        description = description or ''
        endpoint = CallableEndpoint(
            '%s/column/%s/values/%s/description' %
            (self._endpoint.url, _double_encode(column),
             _double_encode(categorical_value)), self._client._session)
        endpoint.post(json=description)
        self._schema = None

    def column_groups(self):  # type () -> Dict[str, Set[str]]
        """Returns a dict describing the population's column groups.

        Column groups are defined by including an identifier starting with a
        '#' character in the descriptions of all columns in the group. The
        keys of the returned dict are the group identifiers and the values
        are sets of column names in that group.
        """
        s = self.schema
        groups = defaultdict(set)  # type: Dict[str, Set[str]]
        group_id_regex = re.compile(r'#\w+')
        for col in s.columns():
            desc = s[col].description
            if desc:
                for group_id in group_id_regex.findall(desc):
                    groups[group_id].add(col)
        return groups

    def select(
            self,
            targets=None,  # type: List[str]
            where=None,  # type: Dict[str, Union[str, int, float]]
            rowids=None,  # type: List[int]
            limit=None,  # type: int
            random_seed=None,  # type: int
    ):  # type: (...) -> DataFrame
        """Return a subset of a population's data.

        The response DataFrame's index corresponds to the population's rowids.

        Args:
            targets: The list of columns to select. If not specified, returns
                all columns.
            where: Limit the results to those rows where the values of the
                specified columns match the values in `where`. If not
                specified, `select` returns all rows.
            rowids: The rowids to restrict results to. If not specified
                returns all rows.
            limit: Return at most `limit` rows. If this would otherwise return
                more than that, the rows to return are chosen randomly.
            random_seed: Optional random seed between 0 and 2**32; only
                meaningful if `limit` is specified.
        """
        targets = self._columns_from_arg(targets)
        req = {'target': targets}  # type: Dict[str, Any]
        if rowids is not None:
            req['rowids'] = rowids_from_arg(rowids)
        if where:
            req['where'] = where
        if limit is not None:
            req['limit'] = int(limit)
        if random_seed is not None:
            req['random_seed'] = random_seed
        resp = self._endpoint.select.post(json=req)
        respjson = resp.json()
        return DataFrame(respjson['columns'], columns=targets,
                         index=respjson['rowids'])

    def add_derived_column(self, column, dependencies, script, stat_type,
                           categorical_values=None):
        """Define a derived column whose value is computed from other columns.

        Args:
            column: Name of the derived column. This may be an existing derived
                column, in which case it will be updated. It may not be an
                existing non-derived column.
            dependencies: List of columns whose values may be used in the
                computation of the derived column.
            script: Lua source code to compute the value of the derived column.
            stat_type: Stat type of the derived column.
            categorical_values: For categorical derived columns, the possible
                string values the column may have.
        """
        endpoint = CallableEndpoint('%s/derived_column/%s' %
                                    (self._endpoint.url,
                                     _double_encode(column)),
                                    self._client._session)
        req = {
            'value_script': script,
            'stat_type': stat_type,
            'dependencies': dependencies,
            'categorical_values': categorical_values or [],
        }
        endpoint.post(json=req)
        self._schema = None

    def remove_derived_column(self, column):
        """Remove a previously defined derived column.

        Args:
            column: Name of the derived column to remove.
        """
        endpoint = CallableEndpoint('%s/derived_column/%s' %
                                    (self._endpoint.url,
                                     _double_encode(column)),
                                    self._client._session)
        endpoint.delete()
        self._schema = None

    def _columns_from_arg(self, columns):
        """Given a columns argument, return a list of column names. Handles
        None and non-list sequences, and expands column group identifiers."""
        self._check_column_list(columns)
        if columns is None:
            return list(self._modeled_columns())
        # Check if there are possible column group identifiers.
        if not any(c.startswith('#') for c in columns):
            return list(columns)
        # Expand column group identifiers to the corresponding column names.
        column_groups = self.column_groups()
        all_columns = self.schema.columns()
        expanded_columns = []  # type: List[str]
        for c in columns:
            if c in column_groups:
                if c in all_columns:
                    warnings.warn(
                        '"%s" is both a column name and a column group '
                        'identifier. Using the single column' % (c,),
                        AmbiguityWarning)
                    expanded_columns.append(c)
                else:
                    expanded_columns.extend(column_groups[c])
            else:
                expanded_columns.append(c)
        return list(expanded_columns)

    def _check_column_list(self, columns):
        """Make sure someone didn't accidentally pass a string as a list."""
        if isinstance(columns, six.string_types):
            raise ValueError('`columns` takes a sequence, not a single string')
        return columns

    def _modeled_columns(self):
        return [
            cname for cname in self.schema.columns()
            if self.schema[cname].stat_type != 'void'
        ]

    def _serializable_value(self, v, col_name):  # type: (Any, str) -> Any
        """Converts a data frame element to one that can be JSON-serialized."""
        desc = self.schema[col_name]
        if v is None:
            return None
        elif desc.stat_type == 'date':
            return _date_to_days(v, col_name)
        else:
            return v

    def _serializable_value_dict(self, d):
        # type: (Dict[str, Any]) -> Dict[str, Any]
        """Converts a key-value dict to one that can be JSON-serialized.

        `d` is a dict of the sort usually passed as `given_values`. The
        returned dict is the same, but with all the values who are not directly
        representable in JSON replaced with ones that are. Right now, that
        means dates are converted to days since the epoch.
        """
        self._check_column_list(d.keys())
        r = {}
        for c, v in six.iteritems(d):
            r[c] = self._serializable_value(v, c)
        return r

    def _serializable_column_dict(self, d):
        # type: (Dict[str, List[Any]]) -> Dict[str, List[Any]]
        """Converts a key-to-list dict to one that can be JSON-serialized.

        Similar to `_serializable_value_dict`, but `d` is a map to lists of
        values, not values. This can be applied to the return value of
        `DataFrame.to_dict(orient='list')`.
        """
        self._check_column_list(d.keys())
        r = {}
        for c in d:
            r[c] = [self._serializable_value(v, c) for v in d[c]]
        return r

    def _deserialize_column(self, col_name, values):
        # type: (str, List[Any]) -> List[Any]
        """Converts a column returned in JSON to a Python representation.

        This is the inverse of what `_serializable_column_dict` does to each
        column.
        """
        if self.schema[col_name].stat_type == 'date':
            return pd.to_datetime(values, unit='D')  # "D" means "days"
        else:
            return values


def rowids_from_arg(rowids):
    # type: (List[int]) -> Union[str, List[int]]
    """Return `rowids` if non-None or the 'all' selector if None."""
    # Ask yourself, is `pd.Index([97, 108, 108]) == 'all'`? That is why we call
    # `isinstance`.
    if rowids is None or (isinstance(rowids, str) and rowids == 'all'):
        return 'all'
    else:
        return _ensure_rowids_are_real_ints(rowids)


def _ensure_rowids_are_real_ints(rowids):
    # numpy int64s aren't JSON serializable, even though they look like
    # ints in pretty much every other way. Convert them. Yes, this also
    # casts strings, but if they successfully cast, so be it.
    return [int(r) for r in rowids]


def _double_encode(val):
    return quote(quote(val))


def _min_seconds_remaining(models):
    # Find the model we think is closest to being done, then return the number
    # of seconds left in its build.
    min_seconds = None  # type: BuildProgress
    for m in models:
        # TODO(asilvers): Rather than forcing clients to write this themselves
        # (edpclient.js also has this code) we should probably compute this
        # server-side.
        progress = m['build_progress']
        if progress['status'] == 'in_progress':
            start_time = progress['start_time']
            now = time.time()
            elapsed_seconds = now - start_time
            fraction_done = progress.get('fraction_done', 0)
            if fraction_done > .01:
                expected_total_seconds = elapsed_seconds / fraction_done
                remaining_seconds = expected_total_seconds - elapsed_seconds
                if (min_seconds is None or
                        remaining_seconds < min_seconds.remaining):
                    min_seconds = BuildProgress(
                        int(elapsed_seconds), int(expected_total_seconds))

    return min_seconds


class BuildProgress(
        collections.namedtuple('BuildProgress', ['elapsed', 'total'])):

    @property
    def remaining(self):
        return self.total - self.elapsed
