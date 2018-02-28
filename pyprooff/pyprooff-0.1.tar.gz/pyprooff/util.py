#!/usr/bin/python


def expose_variables(variables, to_stdout=True):
    """
    Given one or a list of strings corresponding to variable names, prints
    or returns variable names, types (prettified) and values.

    Args:
        variables: str or list of str. Will be eval()'d.
        to_stdout: boolean; if True, prints result; if False, returns list
                   of 3-tuples

    Returns:
        None or list of (variable name[str], type[str], value)
    """
    if type(variables) != list:
        variables = [variables]
    result = []
    for variable in variables:
        result.append((variable, str(type(variable)).
                       replace("<type '", "").
                       replace("'>", ""), eval(variable)))
    if to_stdout:
        for item in result:
            print('{} {} {}'.format(item[0], item[1], item[2]))
    else:
        return result


def expose_values(labels, values, use_repr=False, to_stdout=True):
    """
    Given a (zippable) list or one string for each of args labels and values,
    prints or returns them for nice interactive data manipulation/debugging.

    Args:
        labels: string or list of strings
                just used to identify values
        values: expressions
        use_repr: boolean; if True, will apply repr() to each value
        to_stdout: boolean; if True, prints result; if False, returns list
                   of 2-tuples

    Returns:
        list of 2-tuples or None, according to ``to_stdout``.

    :todo: is use_repr ever useful?
    """
    if type(labels) != list:
        labels = [labels]
        values = [values]
    assert len(labels) == len(values)
    result = []
    for label, value in zip(labels, values):
        if use_repr:
            result.append((label, repr(value)))
        else:
            result.append((label, value))
    if to_stdout:
        for item in result:
            print('{}: {}'.format(item[0], item[1]))
    else:
        return result


def os_walk_to_csv(rootdir):
    """
    Creates a csv of the directory structure of rootdir, with columns
    corresponding to folder structure, file names and attributes.
    """
    import os
    assert os.path.isdir(rootdir)
    import pandas as pd
    import datetime

    def epoch_to_str(epoch):
        return datetime.datetime.strftime(datetime.datetime.\
                            fromtimestamp(epoch), '%Y-%m-%dT%H:%M:%S')

    results = []
    max_depth = 0

    for root, _, files in os.walk(rootdir, topdown=False):
        for fn in files:
            fp = os.path.join(root, fn)
            dirs = root.split('/')[1:]
            max_depth = max(max_depth, len(dirs))
            fnroot, ext = os.path.splitext(fn)
            try:
                ext = ext[1:]
            except:
                pass
            timea = os.path.getatime(fp)
            timec = os.path.getctime(fp)
            timem = os.path.getmtime(fp)
            daysm2c = (timec - timem) / (60*60*24)
            daysm2a = (timea - timem) / (60*60*24)
            daysc2a = (timea - timec) / (60*60*24)
            hidden = (fn[0] == '.' or ext.find('~') != -1)
            d = {'full_path': fp,
                 'root': root,
                'filename': fn,
                'filename_noext': fnroot,
                'ext': ext,
                'size_MB': os.path.getsize(fp) / (1024**2),
                'timea': epoch_to_str(timea),
                'timec': epoch_to_str(timec),
                'timem': epoch_to_str(timem),
                'daysm2c': daysm2c,
                'daysm2a': daysm2a,
                'daysc2a': daysc2a}
            for i, dirname in enumerate(dirs[::-1]):
                d['dir_r{}'.format(i+1)] = dirname
                if dirname[0] == '.':
                    hidden = True
                if dirname[:2] == dirname[-2:] == '__':
                    hidden = True
            for i, dirname in enumerate(dirs):
                d['dir_f{}'.format(i)] = dirname
            d['hidden'] = hidden
            results.append(d)

    colorder = ['full_path', 'root', 'filename', 'filename_noext', 'ext', 'size_MB', 'timec', 'timem', 'timea',
               'daysm2c', 'daysm2a', 'daysc2a', 'hidden']
    for i in range(max_depth):
        colorder.append('dir_f{}'.format(i))
    for i in range(max_depth):
        colorder.append('dir_r{}'.format(i+1))

    df = pd.DataFrame(results)

    assert set(colorder) == set(list(df.columns))

    df = df[colorder]

    df.to_csv(rootdir+'.csv', encoding='latin-1')
