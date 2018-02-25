class Skeletonizer:
  def __init__(self, network, verbose=True):
    self.network = network
    self.verbose = verbose

    # TODO split in low level function and high level wrapper with named
    # arguments instead of a lambda function as argument

    # Low-level functions
    def _parallel_r(func, **kwargs):
        candidates = [(a, b) for a, b in network.get_pipe_pairs() if network.is_parallel(a, b)]

        for a, b in candidates:
            if func(a, b, **kwargs):
                network.merge_parallel(a, b)
                network.delete_pipe(b)

    def _branch_r(func, **kwargs):
        candidates = []

        for n in network.get_nodes():
            if len(n.get_pipes()) == 1 and network.can_remove_node(n):
                candidates.append(n)

        for n in candidates:
            p = n.get_pipes()[0]  # Only one pipe connected

            if func(n, p, **kwargs):
                p.get_other_node(n).merge(n)
                network.delete_pipe(p)

    def _serial_r(func, **kwargs):
        candidates = []

        for a, b in network.get_pipe_pairs():
            n = a.get_common_node(b)
            if network.can_remove_node(n) and network.is_serial(a, b):
                candidates.append((a, b))

        for a, b in candidates:
            # We might have removed one of the candidates already, so check again for their existence
            if a not in network.get_pipes() or b not in network.get_pipes():
                continue

            if func(a, b, **kwargs):
                network.merge_serial(a, b)
                network.delete_pipe(b)

    # Convenient wrappers for common skeletonization operations
    def short_pipe_removal(length=10.0):
        def func(a, b, **kwargs):
            if a.length < length or b.length < length:
                return True
            else:
                return False

        self._serial_r(func)

    def serial_pipe_removal(diameter_f=0.2, diameter_min=100.0, length=300.0, common_demand=1.5, elevation_diff=5.0):
        def func(a, b, **kwargs):
            node_common = a.get_common_node(b)
            node_a = a.get_other_node(node_common)
            node_b = b.get_other_node(node_common)

            if (((a.diameter - b.diameter)/a.diameter < diameter_f or
                   (a.diameter < diameter_min or b.diameter < diameter_min)) and
                (a.length < length or b.length < length) and
                (node_common.demand < common_demand) and
                (max(abs(node_a.elevation - common_node.elevation),
                     abs(node_a.elevation - common_node.elevation)) < elevation_diff)):
                return True
             else:
                return False

        self._serial_r(func)

