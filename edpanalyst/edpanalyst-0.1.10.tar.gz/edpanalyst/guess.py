from __future__ import division

from typing import Any, Dict, Iterable, Iterator, List, Optional, Tuple  # NOQA
import datetime
import re
import six

from natsort import humansorted  # type: ignore
import numpy as np  # type: ignore
import pandas as pd  # type: ignore # NOQA

from .population_schema import PopulationSchema, ColumnDefinition

# How small a number of values guarantees categorical
_CATEGORICAL_THRESHOLD = 20

# How many values should cover what fraction of the space to accept
# categorical?
_CATEGORICAL_COVERAGE_COUNT = 10
_CATEGORICAL_COVERAGE_RATIO = 0.6


class HintValueError(ValueError):
    pass


def guess_schema(df):  # type: (pd.DataFrame) -> PopulationSchema
    """Guesses a schema for a data frame."""
    coldefs = {col: _guess_given_vals(col, df[col]) for col in df.columns}
    return PopulationSchema(coldefs, order=df.columns)


def _guess_given_vals(col_name, data):
    # type: (str, pd.Series) -> ColumnDefinition
    """Returns a guess as to the definition of a column given its data.

    These heuristics are utterly unprincipled and simply seem to work well on a
    minimal set of test datasets. They should be improved as failures crop up.
    """
    if len(data.dropna()) == 0:
        return ColumnDefinition(col_name, 'void', 'Column is empty')

    try:
        unique_vals = data.dropna().unique()
    except TypeError:
        # If the values are non-hashable, give up.
        return ColumnDefinition(col_name, 'void', 'Column is not scalars')

    cardinality = len(unique_vals)
    if cardinality == 1:
        return ColumnDefinition(col_name, 'void', 'Column is constant')

    if all(_is_date(v) for v in data):
        return ColumnDefinition(col_name, 'date')

    # Use categorical for anything with less than 20 values, even numbers.
    if cardinality < _CATEGORICAL_THRESHOLD:
        return ColumnDefinition(col_name,
                                _possibly_ordered_categorical(unique_vals),
                                'Only %d distinct values' % cardinality,
                                values=_infer_categorical_values(data))

    non_num_vals = [v for v in unique_vals if not _numbery(v)]
    if len(non_num_vals) == 0:
        numeric_vals = data.astype(float)
        stat_type, reason = _guess_real_stat_type_and_reason(numeric_vals)
        precision = _guess_precision(numeric_vals)
        return ColumnDefinition(col_name, stat_type,
                                'Contains only numbers (%d of them, %s)' %
                                (cardinality, reason), precision=precision)

    if cardinality == len(data):
        return ColumnDefinition(col_name, 'void',
                                'Non-numeric and all values unique')

    counts = data.dropna().value_counts()
    coverage = counts[:_CATEGORICAL_COVERAGE_COUNT].sum() / len(data.dropna())
    if coverage > _CATEGORICAL_COVERAGE_RATIO:
        reason = ('{} distinct values, {} non-numeric, '
                  'first {} cover {:.2%} of the space').format(
                      cardinality, len(non_num_vals),
                      _CATEGORICAL_COVERAGE_COUNT, coverage)
        return ColumnDefinition(col_name,
                                _possibly_ordered_categorical(unique_vals),
                                reason, values=_infer_categorical_values(data))

    # Ignore anything with more than 20 distinct non-numeric values
    # and poor coverage.
    nonnum_str = ", ".join(non_num_vals[:3])
    if len(non_num_vals) > 3:
        nonnum_str += ", ..."
    return ColumnDefinition(col_name, 'void',
                            '%d distinct values. %d are non-numeric (%s)' %
                            (cardinality, len(non_num_vals), nonnum_str))


def make_column_from_hint(col_name, data, hint, display_name=None):
    # type: (str, pd.Series, Dict[str, str], str) -> ColumnDefinition
    if 'stat_type' not in hint:
        raise HintValueError(
            'hint %s for column %s does not contain stat_type' % (hint,
                                                                  col_name))

    if hint['stat_type'] == 'void':
        return ColumnDefinition(col_name, 'void', 'Hinted',
                                display_name=display_name)

    elif hint['stat_type'] == 'categorical':
        return ColumnDefinition(col_name, 'categorical', 'Hinted',
                                values=_infer_categorical_values(data),
                                display_name=display_name)

    elif hint['stat_type'] in ('real', 'realAdditive', 'realMultiplicative',
                               'magnitude'):
        try:
            data = data.astype(float)
        except ValueError:
            # Provide a more explicit error message
            raise HintValueError('Numeric hint %s for column %s, but column '
                                 'contains non-numeric values' % (hint,
                                                                  col_name))

        if hint['stat_type'] == 'realMultiplicative' and (data <= 0).any():
            raise HintValueError(
                'Hinted realMultiplicative, but column contains '
                'non-positive values: %s' % hint)

        if hint['stat_type'] == 'magnitude' and (data < 0).any():
            raise HintValueError(
                'Hinted magnitude, but column contains negative '
                'values: %s' % hint)

        if hint['stat_type'] == 'real':
            stat_type, _ = _guess_real_stat_type_and_reason(data)
        else:
            stat_type = hint['stat_type']

        return ColumnDefinition(col_name, stat_type, 'Hinted',
                                precision=_guess_precision(data),
                                display_name=display_name)
    else:
        raise HintValueError('invalid stat_type hint %s for column %s' %
                             (hint, col_name))


def _infer_categorical_values(data):  # type: (np.ndarray) -> List[str]
    # TODO(asilvers): Categoricals have to be strings, but auto-converting
    # still allows ambiguity in representations of floats. This probably
    # doesn't get solved until guess is done on the server.
    return humansorted(data.dropna().unique().astype(six.text_type))


def _guess_real_stat_type_and_reason(data):
    # type: (pd.Series) -> Tuple[str, str]
    """Guesses a stat type for `data`."""
    vals = data.dropna().sort_values()
    if (vals < 0).any():
        # In theory there are cases where we want to guess magnitude here,
        # where both the positive and negative halves look log-scaled, but punt
        # on that for now.
        return 'realAdditive', 'not all values are positive'
    if (vals > 0).all():
        # If they're all positive, it makes no sense to be a magnitude
        loggy, reason = _looks_loggy(vals)
        return ('realMultiplicative' if loggy else 'realAdditive'), reason
    else:
        # If they're all non-negative but include 0s, it can't be
        # realMultiplicative, but it might make sense to be a magnitude if the
        # non-zeros look log-scale.
        pos_vals = vals[vals > 0]
        loggy, reason = _looks_loggy(pos_vals)
        return ('magnitude' if loggy else 'realAdditive'), reason


def _looks_loggy(vals):  # type: (List[float]) -> Tuple[bool, str]
    # Compute the correlation of the column's values and their logs with
    # uniform quantiles.
    quantiles = np.linspace(1, len(vals), num=len(vals)) / (len(vals) + 1)
    quantiles_cor = np.corrcoef(quantiles, vals)[0, 1]
    log_quantiles_cor = np.corrcoef(quantiles, np.log(vals))[0, 1]
    if np.isnan(quantiles_cor) or np.isnan(log_quantiles_cor):
        # Should never happen, since we're guaranteed two distinct values.
        raise ValueError('could not infer type for %r' % (vals,))
    # If both uniform and log-uniform quantiles match the distribution of the
    # values well, return realAdditive. Otherwise, pick realMultiplicative if
    # log-uniform quantiles match better, and realAdditive if uniform quantiles
    # match better.
    reason = 'uniform cor. %.3f, log-uniform cor. %.3f' % (quantiles_cor,
                                                           log_quantiles_cor)
    return (log_quantiles_cor > quantiles_cor and quantiles_cor < 0.95), reason


def _guess_precision(vals):  # type: (np.ndarray) -> Tuple[int, int]
    """Returns a (n, d) tuple such that `vals` are measured to only n/d.

    For example, if all values are multiples of 1000, returns (1000, 1).
    Returns None if it looks like `vals` use all of the bits available.
    Currently only guesses decimal precision.
    """
    abs_max = np.max(np.abs(vals))
    # Try units of 1,000,000 down to 0.000001, counting down so that we take
    # the coarsest one possible.
    for places in range(-6, 7):
        # If places is 2, `max_normalized_err` is 0.7 on `vals` of
        # [0.01, 0.027, 0.04].
        z = vals * 10**places
        max_normalized_err = np.max(np.abs(np.round(z) - z))
        # If we have at least six places of accuracy, we've found a precision.
        # Except, check `abs_max` so we don't accept either 1e-30 as being even
        # units of 1e-6 since it rounds to zero with 30 places of accuracy, and
        # we don't accept 1e+30 even though it's an exact multiple of 1e+6.
        if (max_normalized_err < 1e-6 and
                10**(-places) <= abs_max < 10**(9 - places)):
            if places < 0:
                return (10**-places, 1)
            else:
                return (1, 10**places)
    return None


def _numbery(val):
    """Returns True if a value looks like a number."""
    try:
        float(val)
        return True
    except (ValueError, TypeError):
        return False


# Return the kind of categorical we should use given that a column contains
# `unique_vals`. This is basically whether we're confident that our ordering is
# sensible.
def _possibly_ordered_categorical(unique_vals):
    # asilvers@ says "this file is called guess.py", and oh boy is this
    # regex a guess. Right now it should just be things that start with numbers
    # or ranges (like 1-3).
    ordery_regex = re.compile('^\d+\.?\d*(-\d+)?($| )')
    ordered = all(re.search(ordery_regex, str(v)) for v in unique_vals)
    return 'orderedCategorical' if ordered else 'categorical'


def _is_date(val):
    """Returns true if `val` is a date or can be parsed as one."""
    if isinstance(val, datetime.date):
        try:
            return (val.hour == 0 and val.minute == 0 and  # type: ignore
                    val.second == 0)  # type: ignore
        except AttributeError:
            # `pd.Timestamp` and `datetime.datetime` subclass `datetime.date`,
            # but are not "dates." So, if the `hour`, `minute`, or `second`
            # attribute is missing, we know we have a real date.
            return True
    else:
        try:
            datetime.datetime.strptime(val, '%Y-%m-%d')
            return True
        except (TypeError, ValueError):
            return False
