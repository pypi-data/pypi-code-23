import abc
import collections
import numbers
import sys
import typing

import numpy  # type: ignore
import typing_inspect  # type: ignore
from pytypes import type_util  # type: ignore
from sklearn.utils import validation as sklearn_validation  # type: ignore

from . import metadata, utils

__all__ = (
    'Hyperparameter', 'Enumeration', 'UniformInt', 'Uniform', 'LogUniform', 'Normal', 'LogNormal',
    'Hyperparams',
)

RandomState = typing.Union[numbers.Integral, numpy.integer, numpy.random.RandomState]


T = typing.TypeVar('T')


def _get_structural_type_argument(obj: typing.Any) -> type:
    cls = typing_inspect.get_generic_type(obj)

    return utils.get_type_arguments(cls)[T]


class Hyperparameter(typing.Generic[T], abc.ABC):
    """
    A base class for hyper-parameter descriptions.

    A base hyper-parameter does not give any information about the space of the hyper-parameter,
    besides a default value.

    Type variable ``T`` is optional and if not provided an attempt to automatically infer
    it from ``default`` will be made. Attribute ``structural_type`` exposes this type.

    Attributes
    ----------
    name : str
        A name of this hyper-parameter in the configuration of all hyper-parameters.
    default : Any
        A default value for this hyper-parameter.
    structural_type : type
        A Python type of this hyper-parameter. All values of the hyper-parameter, including the default value,
        should be of this type.
    semantic_types : Sequence[str]
        A list of URIs providing semantic meaning of the hyper-parameter. The idea is that this can help
        express how the hyper-parameter is being used, e.g., as a learning rate or as kernel parameter.
    description : str
        An optional natural language description of the hyper-parameter.
    """

    def __init__(self, default: T, *, semantic_types: typing.Sequence[str] = None, description: str = None, _structural_type: type = None) -> None:
        if _structural_type is not None:
            structural_type = _structural_type
        else:
            structural_type = _get_structural_type_argument(self)

            if structural_type == typing.Any:
                structural_type = type_util.deep_type(default, depth=1)

        if not utils.is_instance(default, structural_type):
            raise TypeError("Default value '{default}' is not an instance of the structural type: {structural_type}".format(default=default, structural_type=structural_type))

        if semantic_types is None:
            semantic_types = ()

        self.name: str = None
        self.default = default
        self.structural_type = structural_type
        self.semantic_types = semantic_types
        self.description = description

    def contribute_to_class(self, name: str) -> None:
        if self.name is not None:
            raise ValueError("Name is already set to '{name}'.".format(name=self.name))

        self.name = name

    def validate(self, value: T) -> None:
        """
        Validates that a given ``value`` belongs to the space of the hyper-parameter.

        If not, it throws an exception.

        Parameters
        ----------
        value : Any
            Value to validate.
        """

        if not utils.is_instance(value, self.structural_type):
            raise TypeError("Value '{value}' for hyper-parameter '{name}' does not match its type '{type}'.".format(value=value, name=self.name, type=self.structural_type))

    def sample(self, random_state: RandomState = None) -> T:
        """
        Samples a random value from the hyper-parameter search space.

        For the base class it always returns a ``default`` value because the space
        is unknown.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Any
            A sampled value.
        """

        sklearn_validation.check_random_state(random_state)

        return self.default

    def __repr__(self) -> str:
        return '{class_name}(default={default})'.format(
            class_name=type(self).__name__,
            default=self.default,
        )

    def to_json(self) -> typing.Dict:
        """
        Converts the hyper-parameter to a JSON-compatible structure.

        Returns
        -------
        Dict
            A JSON-compatible dict.
        """

        result = {
            'type': type(self),
            'default': utils.to_json_value(self.default),
            'structural_type': self.structural_type,
            'semantic_types': self.semantic_types,
        }

        if self.description is not None:
            result['description'] = self.description

        return result


class Bounded(Hyperparameter[T]):
    """
    A bounded hyper-parameter with lower and upper bounds, but no other
    information about the distribution of the space of the hyper-parameter,
    besides a default value.

    Both lower and upper bounds are inclusive. Each bound can be also ``None``
    to signal that the hyper-parameter is unbounded for that bound. Both
    bounds cannot be ``None`` because then this is the same as
    ``Hyperparameter`` class, so you can use that one directly.

    Type variable ``T`` is optional and if not provided an attempt to
    automatically infer it from bounds and ``default`` will be made.

    Attributes
    ----------
    lower : Any
        A lower bound.
    upper : Any
        An upper bound.
    """

    def __init__(self, lower: T, upper: T, default: T, *, semantic_types: typing.Sequence[str] = None, description: str = None, _structural_type: type = None) -> None:
        if lower is None and upper is None:
            raise ValueError("Lower and upper bounds cannot both be None.")

        if _structural_type is not None:
            structural_type = _structural_type
            maybe_optional_structural_type = structural_type
        else:
            structural_type = _get_structural_type_argument(self)

            if structural_type == typing.Any:
                structural_types = list(type_util.deep_type(value, depth=1) for value in [lower, upper, default] if value is not None)
                type_util.simplify_for_Union(structural_types)
                structural_type = typing.Union[tuple(structural_types)]  # type: ignore

            if lower is None or upper is None:
                maybe_optional_structural_type = typing.Optional[structural_type]  # type: ignore
            else:
                maybe_optional_structural_type = structural_type

        if not utils.is_instance(lower, maybe_optional_structural_type):
            raise TypeError("Lower bound '{lower}' is not an instance of the structural type: {structural_type}".format(lower=lower, structural_type=structural_type))

        if not utils.is_instance(upper, maybe_optional_structural_type):
            raise TypeError("Upper bound '{upper}' is not an instance of the structural type: {structural_type}".format(upper=upper, structural_type=structural_type))

        # We pass structural type maybe wrapped into Optional to allow default value to be None, which
        # could trigger a type-check exception otherwise because None might not match the strict structural type.
        super().__init__(default, semantic_types=semantic_types, description=description, _structural_type=maybe_optional_structural_type)

        # We restore the attribute to the strict structural type.
        self.structural_type = structural_type

        self.lower = lower
        self.upper = upper

        self._check_bounds(default, "Default value")

    def _check_bounds(self, value: T, value_name: str) -> None:
        # This my throw an exception if default is not comparable, but this is on purpose.
        if self.lower is None:
            if not (value is None or value <= self.upper):  # type: ignore
                raise ValueError("{value_name} '{value}' is outside of range ({lower}, {upper}].".format(value_name=value_name, value=value, lower=self.lower, upper=self.upper))
        elif self.upper is None:
            if not (value is None or self.lower <= value):  # type: ignore
                raise ValueError("{value_name} '{value}' is outside of range [{lower}, {upper}).".format(value_name=value_name, value=value, lower=self.lower, upper=self.upper))
        else:
            if not (self.lower <= value <= self.upper):  # type: ignore
                raise ValueError("{value_name} '{value}' is outside of range [{lower}, {upper}].".format(value_name=value_name, value=value, lower=self.lower, upper=self.upper))

    def validate(self, value: T) -> None:
        """
        Validates that a given ``value`` belongs to the space of the hyper-parameter.

        If not, it throws an exception.

        Parameters
        ----------
        value : Any
            Value to validate.
        """

        super().validate(value)

        self._check_bounds(value, "Value")

    def sample(self, random_state: RandomState = None) -> T:
        """
        Samples a random value from the hyper-parameter search space.

        Tt always returns a ``default`` value because the distribution of
        the space is unknown.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Any
            A sampled value.
        """

        sklearn_validation.check_random_state(random_state)

        return self.default

    def __repr__(self) -> str:
        return '{class_name}(lower={lower}, upper={upper}, default={default})'.format(
            class_name=type(self).__name__,
            lower=self.lower,
            upper=self.upper,
            default=self.default,
        )

    def to_json(self) -> typing.Dict:
        """
        Converts the hyper-parameter to a JSON-compatible structure.

        Returns
        -------
        Dict
            A JSON-compatible dict.
        """

        json = super().to_json()
        json.update({
            'lower': utils.to_json_value(self.lower),
            'upper': utils.to_json_value(self.upper),
        })
        return json


class Enumeration(Hyperparameter[T]):
    """
    An enumeration hyper-parameter with a value drawn uniformly from a list of values.

    If ``None`` is a valid choice, it should be listed among ``values``.

    Type variable ``T`` is optional and if not provided an attempt to
    automatically infer it from ``values`` will be made.

    Attributes
    ----------
    values : Sequence[Any]
        A list of choice values.
    """

    def __init__(self, values: typing.Sequence[T], default: T, *, semantic_types: typing.Sequence[str] = None, description: str = None, _structural_type: type = None) -> None:
        if _structural_type is not None:
            structural_type = _structural_type
        else:
            structural_type = _get_structural_type_argument(self)

            if structural_type == typing.Any:
                structural_types = list(type_util.deep_type(value, depth=1) for value in values)
                type_util.simplify_for_Union(structural_types)
                structural_type = typing.Union[tuple(structural_types)]  # type: ignore

        for value in values:
            if not utils.is_instance(value, structural_type):
                raise TypeError("Value '{value}' is not an instance of the structural type: {structural_type}".format(value=value, structural_type=structural_type))

        if default not in values:
            raise ValueError("Default value '{default}' is not among values.".format(default=default))

        super().__init__(default, semantic_types=semantic_types, description=description, _structural_type=structural_type)

        self.values = values

    def validate(self, value: T) -> None:
        """
        Validates that a given ``value`` belongs to the space of the hyper-parameter.

        If not, it throws an exception.

        Parameters
        ----------
        value : Any
            Value to validate.
        """

        if value not in self.values:
            raise ValueError("Value '{value}' for hyper-parameter '{name}' is not among values.".format(value=value, name=self.name))

    def sample(self, random_state: RandomState = None) -> T:
        """
        Samples a random value from the hyper-parameter search space, i.e., samples
        a value from ``values``.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Any
            A sampled value.
        """

        random_state = sklearn_validation.check_random_state(random_state)

        return random_state.choice(self.values)

    def __repr__(self) -> str:
        return '{class_name}(values={values}, default={default})'.format(
            class_name=type(self).__name__,
            values=self.values,
            default=self.default,
        )

    def to_json(self) -> typing.Dict:
        """
        Converts the hyper-parameter to a JSON-compatible structure.

        Returns
        -------
        Dict
            A JSON-compatible dict.
        """

        json = super().to_json()
        json.update({
            'values': [utils.to_json_value(value) for value in self.values],
        })
        return json


class UniformInt(Hyperparameter[int]):
    """
    An int hyper-parameter with a value drawn uniformly from ``[lower, upper)``,
    or from `[lower, upper]``, if the upper bound is inclusive.

    Attributes
    ----------
    lower : int
        A lower bound.
    upper : int
        An upper bound.
    upper_inclusive : bool
        Is the upper bound inclusive?
    """

    def __init__(self, lower: int, upper: int, default: int, *, upper_inclusive: bool = False, semantic_types: typing.Sequence[str] = None, description: str = None) -> None:
        if upper_inclusive:
            if not lower <= default <= upper:
                raise ValueError("Default value '{default}' is outside of range [{lower}, {upper}].".format(default=default, lower=lower, upper=upper))
        else:
            if not lower <= default < upper:
                raise ValueError("Default value '{default}' is outside of range [{lower}, {upper}).".format(default=default, lower=lower, upper=upper))

        super().__init__(default, semantic_types=semantic_types, description=description)

        self.lower = lower
        self.upper = upper
        self.upper_inclusive = upper_inclusive

    def validate(self, value: int) -> None:
        """
        Validates that a given ``value`` belongs to the space of the hyper-parameter.

        If not, it throws an exception.

        Parameters
        ----------
        value : int
            Value to validate.
        """

        super().validate(value)

        if self.upper_inclusive:
            if not self.lower <= value <= self.upper:
                raise ValueError("Value '{value}' for hyper-parameter '{name}' is outside of range [{lower}, {upper}].".format(value=value, name=self.name, lower=self.lower, upper=self.upper))
        else:
            if not self.lower <= value < self.upper:
                raise ValueError("Value '{value}' for hyper-parameter '{name}' is outside of range [{lower}, {upper}).".format(value=value, name=self.name, lower=self.lower, upper=self.upper))

    def sample(self, random_state: RandomState = None) -> int:
        """
        Samples a random value from the hyper-parameter search space.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        int
            A sampled value.
        """

        random_state = sklearn_validation.check_random_state(random_state)

        if self.upper_inclusive:
            return random_state.randint(self.lower, self.upper + 1)
        else:
            return random_state.randint(self.lower, self.upper)

    def __repr__(self) -> str:
        return '{class_name}(lower={lower}, upper={upper}, default={default}, upper_inclusive={upper_inclusive})'.format(
            class_name=type(self).__name__,
            lower=self.lower,
            upper=self.upper,
            default=self.default,
            upper_inclusive=self.upper_inclusive,
        )

    def to_json(self) -> typing.Dict:
        """
        Converts the hyper-parameter to a JSON-compatible structure.

        Returns
        -------
        Dict
            A JSON-compatible dict.
        """

        json = super().to_json()
        json.update({
            'lower': self.lower,
            'upper': self.upper,
            'upper_inclusive': self.upper_inclusive,
        })
        return json


class Uniform(Hyperparameter[float]):
    """
    A float hyper-parameter with a value drawn uniformly from ``[lower, upper)``,
    or from `[lower, upper]``, if the upper bound is inclusive.

    If ``q`` is provided, then the value is drawn according to ``round(uniform(lower, upper) / q) * q``.

    Attributes
    ----------
    lower : float
        A lower bound.
    upper : float
        An upper bound.
    q : float
        An optional quantization factor.
    upper_inclusive : bool
        Is the upper bound inclusive?
    """

    def __init__(self, lower: float, upper: float, default: float, q: float = None, *, upper_inclusive: bool = False, semantic_types: typing.Sequence[str] = None, description: str = None) -> None:
        if upper_inclusive:
            if not lower <= default <= upper:
                raise ValueError("Default value '{default}' is outside of range [{lower}, {upper}].".format(default=default, lower=lower, upper=upper))
        else:
            if not lower <= default < upper:
                raise ValueError("Default value '{default}' is outside of range [{lower}, {upper}).".format(default=default, lower=lower, upper=upper))

        super().__init__(default, semantic_types=semantic_types, description=description)

        self.lower = lower
        self.upper = upper
        self.q = q
        self.upper_inclusive = upper_inclusive

    def validate(self, value: float) -> None:
        """
        Validates that a given ``value`` belongs to the space of the hyper-parameter.

        If not, it throws an exception.

        Parameters
        ----------
        value : float
            Value to validate.
        """

        super().validate(value)

        if self.upper_inclusive:
            if not self.lower <= value <= self.upper:
                raise ValueError("Value '{value}' for hyper-parameter '{name}' is outside of range [{lower}, {upper}].".format(value=value, name=self.name, lower=self.lower, upper=self.upper))
        else:
            if not self.lower <= value < self.upper:
                raise ValueError("Value '{value}' for hyper-parameter '{name}' is outside of range [{lower}, {upper}).".format(value=value, name=self.name, lower=self.lower, upper=self.upper))

    def sample(self, random_state: RandomState = None) -> float:
        """
        Samples a random value from the hyper-parameter search space.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        float
            A sampled value.
        """

        random_state = sklearn_validation.check_random_state(random_state)

        if self.upper_inclusive:
            # TODO: Is there a better way to get a random sample from an inclusive range?
            value = random_state.uniform(self.lower, self.upper + sys.float_info.epsilon)
        else:
            value = random_state.uniform(self.lower, self.upper)

        if self.q is None:
            return value
        else:
            return numpy.round(value / self.q) * self.q

    def __repr__(self) -> str:
        return '{class_name}(lower={lower}, upper={upper}, q={q}, default={default}, upper_inclusive={upper_inclusive})'.format(
            class_name=type(self).__name__,
            lower=self.lower,
            upper=self.upper,
            q=self.q,
            default=self.default,
            upper_inclusive=self.upper_inclusive,
        )

    def to_json(self) -> typing.Dict:
        """
        Converts the hyper-parameter to a JSON-compatible structure.

        Returns
        -------
        Dict
            A JSON-compatible dict.
        """

        json = super().to_json()

        json.update({
            'lower': self.lower,
            'upper': self.upper,
            'upper_inclusive': self.upper_inclusive,
        })

        if self.q is not None:
            json['q'] = self.q

        return json


class LogUniform(Hyperparameter[float]):
    """
    A float hyper-parameter with a value drawn from ``[lower, upper)`` according to ``exp(uniform(lower, upper))``
    so that the logarithm of the value is uniformly distributed,
    or from `[lower, upper]``, if the upper bound is inclusive.

    If ``q`` is provided, then the value is drawn according to ``round(exp(uniform(lower, upper)) / q) * q``.

    Attributes
    ----------
    lower : float
        A lower bound.
    upper : float
        An upper bound.
    q : float
        An optional quantization factor.
    upper_inclusive : bool
        Is the upper bound inclusive?
    """

    def __init__(self, lower: float, upper: float, default: float, q: float = None, *, upper_inclusive: bool = False, semantic_types: typing.Sequence[str] = None, description: str = None) -> None:
        if upper_inclusive:
            if not lower <= default <= upper:
                raise ValueError("Default value '{default}' is outside of range [{lower}, {upper}].".format(default=default, lower=lower, upper=upper))
        else:
            if not lower <= default < upper:
                raise ValueError("Default value '{default}' is outside of range [{lower}, {upper}).".format(default=default, lower=lower, upper=upper))

        super().__init__(default, semantic_types=semantic_types, description=description)

        self.lower = lower
        self.upper = upper
        self.q = q
        self.upper_inclusive = upper_inclusive

    def validate(self, value: float) -> None:
        """
        Validates that a given ``value`` belongs to the space of the hyper-parameter.

        If not, it throws an exception.

        Parameters
        ----------
        value : float
            Value to validate.
        """

        super().validate(value)

        if self.upper_inclusive:
            if not self.lower <= value <= self.upper:
                raise ValueError("Value '{value}' for hyper-parameter '{name}' is outside of range [{lower}, {upper}].".format(value=value, name=self.name, lower=self.lower, upper=self.upper))
        else:
            if not self.lower <= value < self.upper:
                raise ValueError("Value '{value}' for hyper-parameter '{name}' is outside of range [{lower}, {upper}).".format(value=value, name=self.name, lower=self.lower, upper=self.upper))

    def sample(self, random_state: RandomState = None) -> float:
        """
        Samples a random value from the hyper-parameter search space.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        float
            A sampled value.
        """

        random_state = sklearn_validation.check_random_state(random_state)

        if self.upper_inclusive:
            # TODO: Is there a better way to get a random sample from an inclusive range?
            value = numpy.exp(random_state.uniform(self.lower, self.upper + sys.float_info.epsilon))
        else:
            value = numpy.exp(random_state.uniform(self.lower, self.upper))

        if self.q is None:
            return value
        else:
            return numpy.round(value / self.q) * self.q

    def __repr__(self) -> str:
        return '{class_name}(lower={lower}, upper={upper}, q={q}, default={default}, upper_inclusive={upper_inclusive})'.format(
            class_name=type(self).__name__,
            lower=self.lower,
            upper=self.upper,
            q=self.q,
            default=self.default,
            upper_inclusive=self.upper_inclusive,
        )

    def to_json(self) -> typing.Dict:
        """
        Converts the hyper-parameter to a JSON-compatible structure.

        Returns
        -------
        Dict
            A JSON-compatible dict.
        """

        json = super().to_json()

        json.update({
            'lower': self.lower,
            'upper': self.upper,
            'upper_inclusive': self.upper_inclusive,
        })

        if self.q is not None:
            json['q'] = self.q

        return json


class Normal(Hyperparameter[float]):
    """
    A float hyper-parameter with a value drawn normally distributed according to ``mu`` and ``sigma``.

    If ``q`` is provided, then the value is drawn according to ``round(normal(mu, sigma) / q) * q``.

    Attributes
    ----------
    mu : float
        A mean of normal distribution.
    sigma : float
        A standard deviation of normal distribution.
    q : float
        An optional quantization factor.
    """

    def __init__(self, mu: float, sigma: float, default: float, q: float = None, *, semantic_types: typing.Sequence[str] = None, description: str = None) -> None:
        super().__init__(default, semantic_types=semantic_types, description=description)

        self.mu = mu
        self.sigma = sigma
        self.q = q

    def sample(self, random_state: RandomState = None) -> float:
        """
        Samples a random value from the hyper-parameter search space.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        float
            A sampled value.
        """

        random_state = sklearn_validation.check_random_state(random_state)

        value = random_state.normal(self.mu, self.sigma)

        if self.q is None:
            return value
        else:
            return numpy.round(value / self.q) * self.q

    def __repr__(self) -> str:
        return '{class_name}(mu={mu}, sigma={sigma}, q={q}, default={default})'.format(
            class_name=type(self).__name__,
            mu=self.mu,
            sigma=self.sigma,
            q=self.q,
            default=self.default,
        )

    def to_json(self) -> typing.Dict:
        """
        Converts the hyper-parameter to a JSON-compatible structure.

        Returns
        -------
        Dict
            A JSON-compatible dict.
        """

        json = super().to_json()

        json.update({
            'mu': self.mu,
            'sigma': self.sigma,
        })

        if self.q is not None:
            json['q'] = self.q

        return json


class LogNormal(Hyperparameter[float]):
    """
    A float hyper-parameter with a value drawn according to ``exp(normal(mu, sigma))`` so that the logarithm of the value is
    normally distributed.

    If ``q`` is provided, then the value is drawn according to ``round(exp(normal(mu, sigma)) / q) * q``.

    Attributes
    ----------
    mu : float
        A mean of normal distribution.
    sigma : float
        A standard deviation of normal distribution.
    q : float
        An optional quantization factor.
    """

    def __init__(self, mu: float, sigma: float, default: float, q: float = None, *, semantic_types: typing.Sequence[str] = None, description: str = None) -> None:
        super().__init__(default, semantic_types=semantic_types, description=description)

        self.mu = mu
        self.sigma = sigma
        self.q = q

    def sample(self, random_state: RandomState = None) -> float:
        """
        Samples a random value from the hyper-parameter search space.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        float
            A sampled value.
        """

        random_state = sklearn_validation.check_random_state(random_state)

        value = numpy.exp(random_state.normal(self.mu, self.sigma))

        if self.q is None:
            return value
        else:
            return numpy.round(value / self.q) * self.q

    def __repr__(self) -> str:
        return '{class_name}(mu={mu}, sigma={sigma}, q={q}, default={default})'.format(
            class_name=type(self).__name__,
            mu=self.mu,
            sigma=self.sigma,
            q=self.q,
            default=self.default,
        )

    def to_json(self) -> typing.Dict:
        """
        Converts the hyper-parameter to a JSON-compatible structure.

        Returns
        -------
        Dict
            A JSON-compatible dict.
        """

        json = super().to_json()

        json.update({
            'mu': self.mu,
            'sigma': self.sigma,
        })

        if self.q is not None:
            json['q'] = self.q

        return json


class Union(Hyperparameter[T]):
    """
    An union hyper-parameter which combines multiple other hyper-parameters.

    This is useful when a hyper-parameter has multiple modalities and each modality
    can be described with a different hyper-parameter.

    No relation or probability distribution between modalities is prescribed.

    Type variable ``T`` does not have to be specified because the structural type
    can be automatically inferred as an union of all hyper-parameters in configuration.

    Attributes
    ----------
    configuration : OrderedDict[str, Hyperparameter]
        A configuration of hyper-parameters to combine into one. It is important
        that configuration uses an ordered dict so that order is reproducible
        (default dict has unspecified order).
    """

    def __init__(self, configuration: 'collections.OrderedDict[str, Hyperparameter]', default: str, *, semantic_types: typing.Sequence[str] = None,
                 description: str = None, _structural_type: type = None) -> None:
        for name, hyperparameter in configuration.items():
            if not isinstance(name, str):
                raise TypeError("Hyper-parameter name is not a string: {name}".format(name=name))
            if not isinstance(hyperparameter, Hyperparameter):
                raise TypeError("Hyper-parameter description is not an instance of the Hyperparameter class: {name}".format(name=name))

            hyperparameter.contribute_to_class(name)

        if default not in configuration:
            raise ValueError("Default value '{value}' is not in configuration.")

        if _structural_type is not None:
            structural_type = _structural_type
        else:
            structural_type = _get_structural_type_argument(self)

            if structural_type == typing.Any:
                structural_type = typing.Union[tuple(hyperparameter.structural_type for hyperparameter in configuration.values())]  # type: ignore

        for name, hyperparameter in configuration.items():
            if not utils.is_subclass(hyperparameter.structural_type, structural_type):
                raise TypeError("Hyper-parameter '{name}' is not a subclass of the structural type: {structural_type}".format(name=name, structural_type=structural_type))

        super().__init__(configuration[default].default, semantic_types=semantic_types, description=description, _structural_type=structural_type)

        self.default_hyperparameter = configuration[default]
        self.configuration = configuration

    def validate(self, value: T) -> None:
        """
        Validates that a given ``value`` belongs to the space of the hyper-parameter.

        If not, it throws an exception.

        Parameters
        ----------
        value : Any
            Value to validate.
        """

        # Check that value belongs to a structural type.
        super().validate(value)

        for name, hyperparameter in self.configuration.items():
            # We know that value has to match at least one structural type of configured hyper-parameters.
            if utils.is_instance(value, hyperparameter.structural_type):
                try:
                    hyperparameter.validate(value)
                    # Value validated with at least one hyper-parameter, we can return.
                    return
                except Exception:
                    pass

        raise ValueError("Value '{value}' for hyper-parameter '{name}' has not validated with any of configured hyper-parameters.".format(value=value, name=self.name))

    def sample(self, random_state: RandomState = None) -> T:
        """
        Samples a random value from the hyper-parameter search space.

        It first chooses a hyper-parameter from its configuration and then
        samples it.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Any
            A sampled value.
        """

        random_state = sklearn_validation.check_random_state(random_state)

        hyperparameter = random_state.choice(list(self.configuration.values()))

        return hyperparameter.sample(random_state)

    def __repr__(self) -> str:
        return '{class_name}(configuration={{{configuration}}}, default={default})'.format(
            class_name=type(self).__name__,
            configuration=', '.join('{name}: {hyperparameter}'.format(name=name, hyperparameter=hyperparameter) for name, hyperparameter in self.configuration.items()),
            default=self.default,
        )

    def to_json(self) -> typing.Dict:
        """
        Converts the hyper-parameter to a JSON-compatible structure.

        Returns
        -------
        Dict
            A JSON-compatible dict.
        """

        json = super().to_json()
        json.update({
            'configuration': {name: hyperparameter.to_json() for name, hyperparameter in self.configuration.items()}
        })
        return json


class HyperparamsMeta(abc.ABCMeta):
    """
    A metaclass which provides the hyper-parameter description its name.
    """

    def __new__(mcls, class_name, bases, namespace, **kwargs):  # type: ignore
        # This should run only on subclasses of the "Hyperparams" class.
        if bases != (dict,):
            configuration = collections.OrderedDict()

            for name, value in namespace.items():
                if name.startswith('_'):
                    continue

                if isinstance(value, Hyperparameter):
                    if name in metadata.STANDARD_PIPELINE_ARGUMENTS or name in metadata.STANDARD_RUNTIME_ARGUMENTS:
                        raise ValueError("Hyper-parameter name '{name}' is reserved because it is used as an argument in primitive interfaces.".format(
                            name=name,
                        ))

                    value.contribute_to_class(name)
                    configuration[name] = value

            for name in configuration.keys():
                del namespace[name]

            namespace['configuration'] = configuration

        return super().__new__(mcls, class_name, bases, namespace, **kwargs)

    def __repr__(self):  # type: ignore
        return '<class \'{module}.{class_name}\' configuration={{{configuration}}}>'.format(
            module=self.__module__,
            class_name=self.__name__,
            configuration=', '.join('{name}: {hyperparameter}'.format(name=name, hyperparameter=hyperparameter) for name, hyperparameter in self.configuration.items()),
        )


# A special Python method which is stored efficiently
# when pickled. See PEP 307 for more details.
def __newobj__(cls: type, *args: typing.Any) -> typing.Any:
    return cls.__new__(cls, *args)


H = typing.TypeVar('H', bound='Hyperparams')


class Hyperparams(dict, metaclass=HyperparamsMeta):
    """
    A base class to be subclassed and used as a type for ``Hyperparams``
    type argument in primitive interfaces. An instance of this subclass
    is passed as a ``hyperparams`` argument to primitive's constructor.

    You should subclass the class and configure class attributes to
    hyper-parameters you want. They will be extracted out and put into
    the ``configuration`` attribute. They have to be an instance of the
    `Hyperparameter` class for this to happen.

    You can define additional methods and attributes on the class.
    Prefix them with `_` to not conflict with future standard ones.

    When creating an instance of the class, all hyper-parameters have
    to be provided. Default values have to be explicitly passed.

    Attributes
    ----------
    configuration : OrderedDict[str, Hyperparameter]
        A hyper-parameters space.
    """

    configuration: 'collections.OrderedDict[str, Hyperparameter]' = collections.OrderedDict()

    def __init__(self, other: typing.Dict[str, typing.Any] = None, **values: typing.Any) -> None:
        if other is None:
            other = {}

        values = dict(other, **values)

        configuration_keys = set(self.configuration.keys())
        values_keys = set(values.keys())

        missing = configuration_keys - values_keys
        if len(missing):
            raise ValueError("Not all hyper-parameters are specified: {missing}".format(missing=missing))

        extra = values_keys - configuration_keys
        if len(extra):
            raise ValueError("Additional hyper-parameters are specified: {extra}".format(extra=extra))

        for name, value in values.items():
            self.configuration[name].validate(value)

        super().__init__(values)

    @classmethod
    def sample(cls: typing.Type[H], random_state: RandomState = None) -> H:
        """
        Returns a hyper-space sample with all values sampled from their hyper-parameter's space.

        Parameters
        ----------
        random_state : Union[Integral, integer, RandomState]
            A random seed or state to be used when sampling.

        Returns
        -------
        Hyperparams
            An instance of hyper-parameters.
        """
        random_state = sklearn_validation.check_random_state(random_state)

        values = {}

        for name, hyperparameter in cls.configuration.items():
            values[name] = hyperparameter.sample(random_state)

        return cls(values)

    @classmethod
    def defaults(cls: typing.Type[H]) -> H:
        """
        Returns a hyper-space sample with all values set to defaults.

        Returns
        -------
        Hyperparams
            An instance of hyper-parameters.
        """

        values = {}

        for name, hyperparameter in cls.configuration.items():
            values[name] = hyperparameter.default

        return cls(values)

    def __setitem__(self, key, value):  # type: ignore
        raise AttributeError("Hyper-parameters are immutable.")

    def __delitem__(self, key):  # type: ignore
        raise AttributeError("Hyper-parameters are immutable.")

    def clear(self):  # type: ignore
        raise AttributeError("Hyper-parameters are immutable.")

    def pop(self, key, default=None):  # type: ignore
        raise AttributeError("Hyper-parameters are immutable.")

    def popitem(self):  # type: ignore
        raise AttributeError("Hyper-parameters are immutable.")

    def setdefault(self, key, default=None):  # type: ignore
        raise AttributeError("Hyper-parameters are immutable.")

    def update(self, *args, **kwargs):  # type: ignore
        raise AttributeError("Hyper-parameters are immutable.")

    def __repr__(self) -> str:
        return '{class_name}({super})'.format(class_name=type(self).__name__, super=super().__repr__())

    @classmethod
    def to_json(cls) -> typing.Dict[str, typing.Dict]:
        """
        Converts the hyper-parameter configuration to a JSON-compatible structure.

        Returns
        -------
        Dict
            A JSON-compatible dict.
        """

        return {name: hyperparameter.to_json() for name, hyperparameter in cls.configuration.items()}

    def __getstate__(self) -> dict:
        return dict(self)

    def __setstate__(self, state: dict) -> None:
        self.__init__(state)  # type: ignore

    # We have to implement our own __reduce__ method because dict is otherwise pickled
    # using a built-in implementation which does not call "__getstate__".
    def __reduce__(self) -> typing.Tuple[typing.Callable, typing.Tuple, dict]:
        return (__newobj__, (self.__class__,), self.__getstate__())
