# -*- coding: utf-8 -*-


def convert_to_relative_paths(struct, base):
    """Makes the given litezip `struct`'s `Path` objects relative to `base`.

    """
    def _rel(p):
        return p.relative_to(base)

    new_struct = []
    for obj in struct:
        new_obj = type(obj)(obj.id, _rel(obj.file),
                            tuple([_rel(y) for y in obj.resources]))
        new_struct.append(new_obj)
    return tuple(new_struct)
