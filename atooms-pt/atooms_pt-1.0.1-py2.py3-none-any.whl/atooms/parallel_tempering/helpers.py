"""Helper functions."""

from atooms.core.utils import rank, comm


def sync(var, other):
    if rank < other:
        comm.send(var, dest=other, tag=12)
    else:
        var = comm.recv(source=other, tag=12)
    return var


def exchange(var, other):
    if rank < other:
        comm.send(var, dest=other, tag=10)
        new_var = comm.recv(source=other, tag=11)
    else:
        new_var = comm.recv(source=other, tag=10)
        comm.send(var, dest=other, tag=11)
    return new_var
