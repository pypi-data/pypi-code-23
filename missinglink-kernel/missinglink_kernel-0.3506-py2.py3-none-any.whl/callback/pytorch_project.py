import copy

from .base_callback import BaseCallback, WEIGHTS_HASH_PREFIX, BaseContextValidator, Context
from .exceptions import MissingLinkException
from .interfaces import ModelHashInterface
from .settings import HyperParamTypes
from contextlib import contextmanager
from .utilities.utils import ZeroIndexedGenerators, get_nested_attribute_if_exists, prefix_metric_name
import numpy as np


class PyTorchProject(BaseCallback, ModelHashInterface):
    def __init__(self, owner_id, project_token, host=None):
        super(PyTorchProject, self).__init__(owner_id, project_token, host=host, framework='pytorch')
        self._context_validator = ContextValidator(self.logger)

    def _hyperparams_from_optimizer(self, optimizer):
        optimizer_to_attrs = {
            'Adadelta': ['rho', 'eps', 'lr', 'weight_decay'],
            'Adagrad': ['lr', 'lr_decay', 'weight_decay'],
            'Adam': ['lr', 'beta_1', 'beta_2', 'eps', 'weight_decay'],
            'Adamax': ['lr', 'beta_1', 'beta_2', 'eps', 'weight_decay'],
            'ASGD': ['lr', 'lambd', 'alpha', 't0', 'weight_decay'],
            'LBFGS': ['lr', 'max_iter', 'max_eval', 'tolerance_grad', 'tolerance_change', 'history_size'],
            'RMSprop': ['lr', 'alpha', 'eps', 'weight_decay'],
            'Rprop': ['lr', 'etaminus', 'etaplus', 'minimum_step_size', 'maximum_step_size'],
            'SGD': ['lr', 'dampening', 'weight_decay'],
        }
        attr_to_hyperparam = {
            'lr': 'learning_rate',
            'lr_decay': 'learning_rate_decay',
            'eps': 'epsilon',
            'lambd': 'lambda',
            'max_iter': 'max_iteration',
            'max_eval': 'max_evaluation',
            'tolerance_grad': 'tolerance_gradient',
        }

        optimizer_type = optimizer.__class__.__name__
        params_groups = optimizer.param_groups

        if len(params_groups) < 1:
            return

        hyperparams = copy.copy(params_groups[0])

        expansions = {
            'betas': ['beta_1', 'beta_2'],
            'etas': ['etaminus', 'etaplus'],
            'step_sizes': ['minimum_step_size', 'maximum_step_size']
        }

        for name, names in expansions.items():
            values = hyperparams.get(name)
            if values is not None and len(values) == len(names):
                for key, val in zip(names, values):
                    hyperparams[key] = val

        self.set_hyperparams(optimizer_algorithm=optimizer_type)
        self._extract_hyperparams(HyperParamTypes.OPTIMIZER, hyperparams, optimizer_to_attrs,
                                  attr_to_hyperparam, object_type=optimizer_type)

    def _hyperparams_from_data_object(self, data_object):
        iterator_attributes = ['train', 'repeat', 'shuffle', 'sort', 'sort_within_batch', 'device']
        object_to_attributes = {
            'DataLoader': ['num_workers', 'pin_memory', 'drop_last'],
            'Iterator': iterator_attributes,
            'BucketIterator': iterator_attributes,
            'BPTTIterator': iterator_attributes,
        }

        object_type = data_object.__class__.__name__
        if object_type not in object_to_attributes:
            return

        attribute_to_hyperparam = {}  # hyperparams will have the same names as the attributes

        self._extract_hyperparams(HyperParamTypes.CUSTOM, data_object, object_to_attributes, attribute_to_hyperparam)

        hyperparams = {'data_object': object_type}

        # maps hyperparams names to the attribute that holds their value
        extraction_map = {
            'dataset': ['dataset', '__class__', '__name__'],
            'batch_size': ['batch_size']
        }

        if object_type == 'DataLoader':
            extraction_map['collate_function'] = ['collate_fn', '__name__']
            extraction_map['sampler'] = ['sampler', '__class__', '__name__']

        elif object_type in object_to_attributes:
            extraction_map['batch_size_function'] = ['batch_size_fn', '__name__']

        for hyperparam_name, attributes_path in extraction_map.items():
            hyperparam_value = get_nested_attribute_if_exists(data_object, attributes_path)
            if hyperparam_value is not None:
                hyperparams[hyperparam_name] = hyperparam_value

        if hasattr(data_object, '__len__'):
            hyperparams['epoch_size'] = len(data_object)

        try:
            hyperparams['samples_count'] = len(data_object.dataset)
        except (TypeError, AttributeError):
            pass

        self.set_hyperparams(**hyperparams)

    def _begin_experiment(self, experiment):
        structure_hash = self._get_structure_hash(experiment.model)
        self.train_begin({}, structure_hash=structure_hash)

    def _end_experiment(self, experiment):
        self._train_end(iterations=experiment._iteration, metricData=self._latest_metrics)

    @contextmanager
    def create_experiment(self, model,
                          display_name=None,
                          description=None,
                          class_mapping=None,
                          optimizer=None,
                          train_data_object=None,
                          hyperparams=None,
                          metrics=None,
                          stopped_callback=None):
        if metrics is None:
            metrics = {}
        self.set_properties(display_name=display_name, description=description, class_mapping=class_mapping)
        if optimizer:
            self._hyperparams_from_optimizer(optimizer)

        if train_data_object:
            self._hyperparams_from_data_object(train_data_object)

        if hyperparams is not None:
            self.set_hyperparams(**hyperparams)
        self.stopped_callback = stopped_callback

        try:
            experiment = PyTorchExperiment(self, model, metrics)

            self._context_validator.enter(Context.EXPERIMENT)
            self._begin_experiment(experiment)

            yield experiment

            self._end_experiment(experiment)
            self._context_validator.exit(Context.EXPERIMENT)

        except Exception:
            self.logger.exception('Training has failed')
            raise

    def _get_structure_hash(self, net):
        layers = []
        for m in net.modules():
            layers.append(str(m))
        layers = tuple(layers)
        hash_string = self._hash(layers)
        return hash_string

    def get_weights_hash(self, net):
        from missinglink_kernel.callback.utilities.utils import hasharray, hashcombine

        hashes = list()
        for m in net.modules():
            layer_hashes = [hasharray(i.data.cpu().numpy()) for i in m.parameters()]
            hashes.extend(layer_hashes)

        hash_key = hashcombine(*hashes)
        return WEIGHTS_HASH_PREFIX + hash_key

    def calculate_weights_hash(self, net):
        return self.get_weights_hash(net)


class PyTorchExperiment(object):
    def __init__(self, project, model, metrics):
        self._callback = project
        self._logger = self._callback.logger
        self._context_validator = self._callback._context_validator

        self._latest_results = {}
        self._validation_metric_data = {}
        self._validation_iteration_count = {}
        self._is_iteration_with_validation = False

        self._iteration = 0
        self._batch = 0
        self._epoch = 0
        self._epochs = None

        self.metrics = {}
        self.wrap_metrics(metrics)
        self.model = model

    @property
    def in_validation_context(self):
        return self._context_validator.last_context == Context.VALIDATION

    @property
    def in_test_context(self):
        return self._context_validator.last_context == Context.TEST

    def _update_metric_data(self, metric_name, metric_data):
        metric_data_dict = self._validation_metric_data if self.in_validation_context else self._latest_results

        if not self.in_validation_context:
            metric_data_dict[metric_name] = metric_data
        else:
            metric_data_dict.setdefault(metric_name, 0)
            metric_data_dict[metric_name] += metric_data
            self._validation_iteration_count.setdefault(metric_name, 0)
            self._validation_iteration_count[metric_name] += 1

    def _wrap(self, base, key):
        def wrapped(*args, **kwargs):
            result = base(*args, **kwargs)

            # Do not monitor metrics if inside test context
            if self.in_test_context:
                return result

            is_custom_metric = not (hasattr(result, 'data') and hasattr(result.data, '__getitem__'))

            metric_data = result if is_custom_metric else result.data[0]

            prefixed_key = prefix_metric_name(key, self.in_validation_context, is_custom_metric)

            self._update_metric_data(prefixed_key, metric_data)

            return result

        return wrapped

    def wrap_metrics(self, metrics):
        """
        :param metrics: Single, list or dictionary of pytorch functionals
        """
        if isinstance(metrics, dict):
            wrapped = copy.copy(metrics)

            for key in wrapped.keys():
                base = metrics[key]

                wrapped[key] = self._wrap(base, key)

            self.metrics.update(wrapped)

        elif isinstance(metrics, (list, tuple)):
            wrapped = []

            for i in range(len(metrics)):
                base = metrics[i]

                key = base.__name__
                wrapped_function = self._wrap(base, key)

                wrapped.append(wrapped_function)
                self.metrics[key] = wrapped_function

        else:
            base = metrics

            key = base.__name__
            wrapped = self._wrap(base, key)
            self.metrics[key] = wrapped

        return wrapped

    @staticmethod
    def _total_epochs(max_iterations, epoch_size):
        if not max_iterations or not epoch_size:
            return None

        return max_iterations // epoch_size

    @staticmethod
    def _is_epoch_iteration(iteration, epoch_size):
        """
        Used to determine if the current iteration is the end of an epoch in loop with epoch_size.
        :param iteration: A 0-based iteration index.
        :param epoch_size: Number of iterations in every epoch.
        :return: True if the iteration is the end of an epoch, False otherwise. False if epoch_size is 0 or None.
        """
        if not epoch_size:
            return False

        return (iteration + 1) % epoch_size == 0

    def _assert_single_argument(self, args, error_message=''):
        # count arguments
        args_count = len([arg for arg in args if arg is not None])

        if args_count != 1:
            raise MissingLinkException('Bad Arguments: ' + error_message, self._logger)

    @staticmethod
    def _epoch_batch_loop_total_iterations(iterations, iterable):
        # This function is called by:
        #   `epoch_loop` to calculate the number of total epochs
        #   `batch_loop` to calculate the epoch size (= batches per epoch)
        if iterable is None:
            return iterations

        if hasattr(iterable, '__len__'):
            return len(iterable)

        return None

    @staticmethod
    def _batch_loop_max_iterations(epochs, epoch_size):
        try:
            return epochs * epoch_size
        except TypeError:
            return None

    @staticmethod
    def _choose_generator(iterations, condition, iterable):
        if iterations is not None:
            return ZeroIndexedGenerators.range_generator(iterations)

        if condition is not None:
            return ZeroIndexedGenerators.condition_generator(condition)

        if iterable is not None:
            return ZeroIndexedGenerators.iterable_generator(iterable)

        return None

    def loop(self, max_iterations=None, condition=None, iterable=None, epoch_size=None):
        """Provides a training loop generator.

        This generator allows the MissingLinkAI SDK to correctly track each training iteration and its
        corresponding metrics.

        You would normally write the training loop as
        ```python
            for step in range(1000):
                # Perform a training step
        ```

        This can be converted to
        ```python
            for step in experiment.loop(max_iterations=1000):
                # Perform a training step
        ```

        If you wants to run the training steps while a condition is satisfied, a while loop is preferred.
        ```python
            threshold = 10
            step = 0
            while loss > threshold:
                # Perform a training step
                step += 1
        ```

        This can be converted to
        ```python
            threshold = 10
            for step in experiment.loop(condition=lambda _: loss > threshold):
                # Perform a training step
        ```

        If you want to iterate over an iterable (a list, a file, etc.):
        ```python
            for sample in data:
                # Perform a training step
        ```

        This can be converted to
        ```python
            for step, sample in experiment.loop(iterable=data):
                # Perform a training step
        ```

        If you want to collect and analyze metrics with respect to epochs, specify the `epoch_size` param with
        the number of iterations per epoch.

        # Arguments:
            max_iterations: The maximum number of training iterations to be run. Cannot be provided
                together with `condition` or `iterable`.
            condition: The condition function to run the training steps. Once the condition fails, the
                training will terminate immediately. This function takes 1 parameter: a 0-based index
                indicating how many iterations have been run.
                Cannot be provided together with `max_iterations` or `iterable`.
            iterable: The iterable to iterate over in the loop, such as a list, a file, a generator function, etc.
                Cannot be provided together with `max_iterations` or `condition`.
            epoch_size: (Optional.) The number of iterations per epoch.

        # Yields:
            A 0-based index, if provided with `max_iterations` or with `condition`.
            A tuple of 0-based index and a sample, if provided with `iterable`.
        """
        message = '`loop` should be called with one of max_iterations, condition, or iterable.' \
                  ' Called with: max_iterations=%s, condition=%s, iterable=%s instead.' % \
                  (max_iterations, condition, iterable)
        self._assert_single_argument((max_iterations, condition, iterable), message)

        self._context_validator.enter(Context.LOOP)

        self._callback.set_hyperparams(max_iterations=max_iterations, epoch_size=epoch_size,
                                       total_epochs=self._total_epochs(max_iterations, epoch_size))
        if iterable is not None:
            self._callback._hyperparams_from_data_object(iterable)

        # In the case of multiple loops on the same experiment,
        # you might expect index to start at `self._iteration - 1`,
        # so the index of the loops keeps incrementing from loop to loop.
        # However, we decided to keep it this way, to keep on consistency with the `range` function.
        generator = self._choose_generator(max_iterations, condition, iterable)

        if generator is None:
            raise MissingLinkException('Provide max_iteration, condition or iterable to loop.', self._logger)

        should_increment_epoch = True
        for result in generator:
            self._iteration += 1
            self._batch += 1
            self._latest_results = {}
            self._is_iteration_with_validation = False

            if should_increment_epoch:
                self._epoch += 1
                self._batch = 1
                should_increment_epoch = False

            yield result

            try:
                i = result[0]
            except TypeError:
                i = result

            is_epoch_iteration = self._is_epoch_iteration(i, epoch_size)

            weights_hash = self._callback.get_weights_hash(self.model) \
                if self._is_iteration_with_validation or is_epoch_iteration else None

            batch_weights_hash = weights_hash if self._is_iteration_with_validation else None

            self._callback.batch_end(self._batch, self._epoch, self._latest_results, iteration=self._iteration,
                                     weights_hash=batch_weights_hash, is_test=self._is_iteration_with_validation)

            if is_epoch_iteration:
                should_increment_epoch = True

                self._callback.epoch_end(self._epoch, self._latest_results, weights_hash=weights_hash)

        self._context_validator.exit(Context.LOOP)

    def batch_loop(self, batches=None, condition=None, iterable=None):
        """Provides a batch loop generator.

        This generator should be nested in a `epoch_loop` generator. Please see `epoch_loop` for more details.

        This generator can be used like the `range` function:
        ```python
        for batch_index in experiment.batch_loop(batches):
            # Preform training on a single batch
        ```

        Also, this generator can be used to iterate over an iterable, like so:
        ```python
        for batch_index, batch_data in experiment.bath_loop(iterable=data):
            # Preform training on a single batch
        ```

        # Arguments:
            batches: The total number of batches. Cannot be provided with `iterable`.
            iterable: The iterable to iterate over in the batch loop, such as a list, a file, a generator function, etc.
                Cannot be provided together with `batches`.
        # Yields:
            A 0-based index, if provided with `batches`.
            A tuple of 0-based index and the next member in the `iterable`, if provided with `iterable`.
        """
        message = '`batch_loop` should be called with one of batches, condition, or iterable.' \
                  ' Called with: batches=%s, condition=%s, iterable=%s instead.' % \
                  (batches, condition, iterable)
        self._assert_single_argument((batches, condition, iterable), message)

        self._context_validator.enter(Context.BATCH_LOOP)

        epoch_size = self._epoch_batch_loop_total_iterations(batches, iterable)
        max_iterations = self._batch_loop_max_iterations(self._epochs, epoch_size)
        self._callback.set_hyperparams(epoch_size=epoch_size, max_iterations=max_iterations)
        if iterable is not None:
            self._callback._hyperparams_from_data_object(iterable)

        generator = self._choose_generator(batches, condition, iterable)

        if generator is None:
            raise MissingLinkException('Provide batches, condition or iterable to batch_loop.', self._logger)

        for result in generator:
            self._iteration += 1
            self._batch += 1
            self._latest_results = {}
            self._is_iteration_with_validation = False

            yield result

            weights_hash = self._callback.get_weights_hash(self.model) if self._is_iteration_with_validation else None

            self._callback.batch_end(self._batch, self._epoch, self._latest_results, iteration=self._iteration,
                                     weights_hash=weights_hash, is_test=self._is_iteration_with_validation)

        self._context_validator.exit(Context.BATCH_LOOP)

    def epoch_loop(self, epochs=None, condition=None, iterable=None):
        """Provides a epoch loop generator.

        This generator is used together with the `batch_loop` generator to run your training with
        epochs and batches using nested loops.

        You would normally write your training loops as
        ```python
        for epoch in range(epochs):
            for batch in range(batches):
                # Perform a training step on a batch of data
        ```

        This can be converted to
        ```python
        for epoch in experiment.epoch_loop(epochs):
            for batch in experiment.batch_loop(batches):
                # Perform a training step on a batch of data
        ```

        If you want to iterate over an iterable (a list, a file, etc.):
        ```python
            for epoch_data in data:
                # Perform an epoch
        ```

        This can be converted to
        ```python
            for step, epoch_data in experiment.epoch_loop(iterable=data):
                for batch in experiment.batch_loop(batches):
                    # Perform a training step on a batch of data
        ```

        # Arguments:
            epochs: The total number of epochs
            iterable: The iterable to iterate over in the epoch loop, such as a list, a file, a generator function, etc.
                Cannot be provided together with `epochs`.
        # Yields:
            A 0-based index, if provided with `epochs`.
            A tuple of 0-based index and the next member in the `iterable`, if provided with `iterable`.
        """
        message = '`epoch_loop` should be called with one of epochs, condition, or iterable.' \
                  ' Called with: epochs=%s, condition=%s, iterable=%s instead.' % \
                  (epochs, condition, iterable)
        self._assert_single_argument((epochs, condition, iterable), message)

        self._context_validator.enter(Context.EPOCH_LOOP)

        self._epochs = self._epoch_batch_loop_total_iterations(epochs, iterable)
        self._callback.set_hyperparams(total_epochs=self._epochs)
        if iterable is not None:
            self._callback._hyperparams_from_data_object(iterable)

        generator = self._choose_generator(epochs, condition, iterable)

        if generator is None:
            raise MissingLinkException('Provide epochs, condition or iterable to epoch_loop.', self._logger)

        for result in generator:
            self._epoch += 1
            self._batch = 0

            yield result

            weights_hash = self._callback.get_weights_hash(self.model)

            self._callback.epoch_end(self._epoch, self._latest_results, weights_hash=weights_hash)

        self._context_validator.exit(Context.EPOCH_LOOP)

    @contextmanager
    def train(self):
        self._context_validator.enter(Context.TRAIN)
        yield
        self._context_validator.exit(Context.TRAIN)

    @contextmanager
    def validation(self):
        self._context_validator.enter(Context.VALIDATION)

        self._validation_metric_data = {}
        self._validation_iteration_count = {}

        yield

        for metric_name in self._validation_metric_data:
            self._validation_metric_data[metric_name] /= self._validation_iteration_count[metric_name]

        self._latest_results.update(self._validation_metric_data)
        self._is_iteration_with_validation = True

        self._context_validator.exit(Context.VALIDATION)

    @contextmanager
    def test(self, model=None, test_data_object=None, target_attribute_name='label', test_iterations=None):
        """
        `test` context for generating a confusion matrix.

        if you use a `DataLoader`, use like so:

            with test(model, test_data_object=test_loader):
                # test code

        if you use a `Iterator`, a `BucketIterator`, or a `BPTTIterator`, use like so:

            with test(model, test_data_object=test_iterator, target_attribute_name='label'):
                # test code

        Otherwise, test manually, like so:

            with test(model, test_iterations=1000):
                # call here `test_iterations` times to `confusion_matrix`

        :param model: The tested model. If not specified, defaults to the experiment's model.
        :param test_data_object: A `DataLoader` or a `Iterator` that provides the test data.
        :param target_attribute_name: The attribute name of the target of every batch,
            so that `batch.target_attribute_name` is the target. Defaults to 'label'.
        :param test_iterations: For manual test. number of test iterations.
            Should be equal to the amount of times `confusion_matrix` will be called.
        :return: None
        """
        self._context_validator.enter(Context.TEST)

        if model is None:
            model = self.model

        if test_data_object:
            with self._test_with_patched_object(model, test_data_object, target_attribute_name) as result:
                yield result

        elif test_iterations:
            with self._test_manually(model, test_iterations) as result:
                yield result

        else:
            self._logger.warning("Failed to test: Not provided `test_data_object` nor with `test_iterations`")
            yield

        self._context_validator.exit(Context.TEST)

    @contextmanager
    def _test_with_patched_object(self, model, object_to_patch, target_attribute_name=None):
        map_type_to_patch_function = {
            'Iterator': self._patch_torchtext_iterator,
            'BPTTIterator': self._patch_torchtext_iterator,
            'BucketIterator': self._patch_torchtext_iterator,
            'DataLoader': self._patch_data_loader,
        }
        object_type = type(object_to_patch).__name__

        try:
            patch_function = map_type_to_patch_function[object_type]

        except KeyError:
            message = "TypeError: object of type %s is not supported for test. Please use manual test."
            self._logger.warning(message)
            yield

        else:
            weights_hash = self._callback.get_weights_hash(model)
            test_iterations = len(object_to_patch)

            # noinspection PyProtectedMember
            self._callback._test_begin(test_iter=test_iterations, weights_hash=weights_hash)

            # this is just to access the variables from the inner scopes
            # noinspection PyClassHasNoInit
            class OuterScope:
                target = []

            map_patch_function_to_arguments = {
                self._patch_torchtext_iterator: [object_to_patch, target_attribute_name, OuterScope, self._logger],
                self._patch_data_loader: [object_to_patch, OuterScope]
            }

            patch_function_args = map_patch_function_to_arguments[patch_function]
            unpatch_function = patch_function(*patch_function_args)

            def hook(_module, _input, output):
                # this is invoked after the model is forwarded
                self.confusion_matrix(output, OuterScope.target)

            handle = model.register_forward_hook(hook)

            yield

            handle.remove()
            unpatch_function()

    @staticmethod
    def _patch_data_loader(data_loader, outer_scope):
        base_iter = type(data_loader).__iter__

        def patched_iter(*args, **kwargs):
            data_loader_iter = base_iter(*args, **kwargs)
            base_next = type(data_loader_iter).__next__

            outer_scope.data_loader_iter = data_loader_iter
            outer_scope.base_next = base_next

            def patched_next(*args_, **kwargs_):
                outer_scope.data, outer_scope.target = base_next(*args_, **kwargs_)

                return outer_scope.data, outer_scope.target

            type(data_loader_iter).__next__ = type(data_loader_iter).next = patched_next

            return data_loader_iter

        type(data_loader).__iter__ = patched_iter

        def unpatch():
            type(data_loader).__iter__ = base_iter
            type(outer_scope.data_loader_iter).__next__ = type(
                outer_scope.data_loader_iter).next = outer_scope.base_next

        return unpatch

    @staticmethod
    def _patch_torchtext_iterator(iterator, target_attribute_name, outer_scope, logger):
        base_iter = type(iterator).__iter__

        def patched_iter(*args, **kwargs):
            for batch in base_iter(*args, **kwargs):
                outer_scope.target = getattr(batch, target_attribute_name, None)

                if outer_scope.target is None:
                    outer_scope.target = []
                    logger.warning(
                        "Could not find %s in batch. Make sure target_attribute_name is correct" % target_attribute_name
                    )

                yield batch

        type(iterator).__iter__ = patched_iter

        def unpatch():
            type(iterator).__iter__ = base_iter

        return unpatch

    @contextmanager
    def _test_manually(self, model, test_iterations):
        weights_hash = self._callback.get_weights_hash(model)

        # noinspection PyProtectedMember
        self._callback._test_begin(test_iter=test_iterations, weights_hash=weights_hash)

        yield

        if self._callback._has_test_context:
            # In case `confusion_matrix` was called less times than expected, end the test.
            self._logger.warning("`confusion_matrix` was called less times than expected")
            self._callback._send_test_iteration_end(
                expected=[], predictions=[], probabilities=[],
                partial_class_mapping={}, partial_found_classes=[], is_finished=True
            )
            self._callback._test_end()

    def confusion_matrix(self, output, target):
        """
        Explicit function to generate a confusion matrix. Call only inside a `test` context.
        :param output: A 2D `torch.autograd.Variable`. The output of the model for a single batch.
        :param target: A 1D `torch.autograd.Variable` or Array-Like. The targets (labels) of a single batch.
        :return: None
        """
        if not self.in_test_context:
            self._logger.warning("Failed to generate confusion matrix: Not in `test` context")
            return

        if not self._callback._has_test_context:
            self._logger.warning(
                "`confusion_matrix` was called more times than expected. Future calls in this same test will be ignored"
            )
            return

        try:
            target = target.data if type(target).__name__ == 'Variable' else target
            expected = [int(x) for x in target]

        except (ValueError, TypeError) as e:
            self._logger.warning("Failed to generate confusion matrix: `target` is not good: %s" % str(e))
            return

        try:
            output_numpy = output.data.numpy()
            predictions = np.argmax(output_numpy, axis=1).tolist() if len(output_numpy) > 0 else []
            probabilities = np.max(output_numpy, axis=1).tolist() if len(output_numpy) > 0 else []

        except (AttributeError, np.AxisError, TypeError) as e:
            self._logger.warning("Failed to generate confusion matrix: `output` is not good: %s" % str(e))
            return

        # noinspection PyProtectedMember
        self._callback._test_iteration_end(expected, predictions, probabilities)


class ContextValidator(BaseContextValidator):
    """
    This class validates if we can enter or exit a context.
    """
    def __init__(self, logger):
        super(ContextValidator, self).__init__(logger)

    def _validate_test_context(self):
        message = '`test` context cannot be inside `test` context or inside `validation` context, ' \
                  'and must be inside an `experiment` context. This context is ignored.'
        self._exclude_from_contexts([Context.VALIDATION, Context.TEST], message)

    def _validate_validation_context(self):
        message = '`validation` context cannot be inside `validation` context or inside `test` context, ' \
                  'and must be inside an `experiment` context. This context is ignored.'
        self._exclude_from_contexts([Context.VALIDATION, Context.TEST], message)

    def _validate_train_context(self):
        # Train context does nothing, so the user can do whatever he wants with it
        pass

    def _exclude_from_contexts(self, excluded, error_message=''):
        if not self._contexts or self.last_context in excluded:
            # Do not raise exception because we don't want to halt the experiment halfway
            self._logger.error(error_message)
