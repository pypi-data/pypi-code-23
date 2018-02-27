import json
import subprocess

_BACKEND_WEIGHTS_ANNOTATION = 'zalando.org/backend-weights'


def backend_names(ingress):
    """Return the names of all services of an ingress."""

    result = []

    default_backend = ingress['spec'].get('backend')
    if default_backend:
        result.append(default_backend['serviceName'])

    rules = ingress['spec'].get('rules', [])
    for rule in rules:
        for path in rule.get('http', {}).get('paths', []):
            for backend in path.values():
                result.append(backend['serviceName'])

    return frozenset(result)


def backend_weights(ingress):
    """Return a dict containing all services of an ingress with their traffic weights as values.

    The backend weights will be extracted from the zalando.org/backend-weights annotation, if it's present. Unknown
    backends will default to a weight of 0, and backends removed from the ingress will be ignored. If the annotation
    is not present, all backends will get the same weight. Backends with negative weight will be ignored as well."""

    all_backends = frozenset(backend_names(ingress))

    raw_weights = ingress['metadata'].get('annotations', {}).get(_BACKEND_WEIGHTS_ANNOTATION)
    if raw_weights:
        weights = {backend: weight for backend, weight in json.loads(raw_weights).items()}
    else:
        # No backend weights defined, distribute evenly
        weights = {backend: 1 for backend in all_backends}

    return {backend: max(0.0, weights.get(backend, 0.0)) for backend in all_backends}


def rescale_weights(weights):
    """Rescale backend weights from a provided dict so that they sum up to 1.0. Always returns a new dict."""

    total_weight = float(sum(weights.values()))
    if total_weight == 0:
        return weights.copy()
    else:
        return {backend: weight / total_weight for backend, weight in weights.items()}


def get_ingress_info(kubectl, namespace, ingress):
    """Fetch the backends weights from a Kubernetes Ingress using kubectl."""

    cmdline = [kubectl, "get", "ingress", ingress, "-o", "json"]

    if namespace:
        cmdline += ("-n", namespace)

    data = subprocess.run(cmdline, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8").stdout

    return backend_weights(json.loads(data))


def print_weights_table(weights):
    """Print the backends and their weights in a user-friendly way."""

    service_len = max(max(len(elem) for elem in weights.keys()),
                      len("SERVICE"))

    print("{service:<{service_length}}   {weight}".format(service="SERVICE",
                                                          weight="WEIGHT",
                                                          service_length=service_len))

    for backend, weight in sorted(rescale_weights(weights).items()):
        print("{service:<{service_length}}   {weight:.1%}".format(service=backend,
                                                                  weight=weight,
                                                                  service_length=service_len))


def set_ingress_weights(kubectl, namespace, ingress, weights):
    """Update the backend weights on a Kubernetes Ingress using kubectl."""

    cmdline = [kubectl, "annotate", "ingress", ingress, "--overwrite"]

    if namespace:
        cmdline += ("-n", namespace)

    cmdline.append("{}={}".format(_BACKEND_WEIGHTS_ANNOTATION, json.dumps(weights)))
    subprocess.run(cmdline, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, encoding="utf-8")


def with_weight(current_weights, changed_backend, new_weight):
    """Update the weight of one backend in a provided dict and redistribute the rest proportionally. Always returns
    a new dict.

    The new weight must be between 0.0 and 1.0."""

    if not 0.0 <= new_weight <= 1.0:
        raise ValueError("Invalid weight: {}".format(new_weight))

    new_weights = {changed_backend: new_weight}

    # Redistribute the remaining weights
    remaining_weight = 1.0 - new_weight
    total_remaining_weight = sum(weight for backend, weight in current_weights.items() if backend != changed_backend)

    if total_remaining_weight == 0 and new_weight not in (0, 1.0):
        errmsg = "The only active backend {} cannot get partial traffic, must be either 0 or 100."
        raise ValueError(errmsg.format(changed_backend))

    for backend, weight in current_weights.items():
        if backend != changed_backend:
            new_weights[backend] = 0 if weight == 0 else weight * remaining_weight / total_remaining_weight

    return new_weights
