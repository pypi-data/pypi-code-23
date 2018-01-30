#!/usr/env/bin python
# author: WU Dingcheng
from .l1tool import l1filter, cvx
from .reader import reader
import argparse


def app(filename,
        output='components.dat',
        lam=1000,
        rho=80,
        periods=(365.25, 186.725),
        verbose=True,
        solver=cvx.MOSEK):
    """
    :param filename: str, file input
    :param output: str, file output
    :param lam: int, lambda parameter in L1 Regularize
    :param rho: int, rho parameter in L1 Regularize
    :param periods: list, periods for seasonal
    :param verbose: bool, show verbose or not
    :param solver: cvx.solver
    :return: df, pandas dataframe
    """
    try:
        df = reader(filename)
    except Exception as ex:
        print(ex)
        print("Error file format! Please refer to the mannual!")
        return
    components = l1filter(df['t'].values,
                          df['component'].values,
                          periods=periods,
                          lam=lam,
                          rho=rho,
                          verbose=verbose,
                          solver=solver)
    df['trends'] = components[0]
    df['level'] = components[1]
    if periods is not None:
        df['seasonal'] = components[2]
    df.pop('t')
    df.to_csv(output, float_format='%.2f', sep=' ')
    print("The estimated components have been written in {}".format(output))
    return df


def main():
    import sys
    args = sys.argv[1:]
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file",
                        type=str,
                        required=True,
                        help="input time series file")
    parser.add_argument('-l', '--lam',
                        default=1200,
                        type=float,
                        help='lambda parameter')
    parser.add_argument('-r', '--rho',
                        default=80,
                        type=float,
                        help='rho parameter'),
    parser.add_argument('-p', '--periods',
                        type=str,
                        default='386.25,186.725',
                        help='periods, with , spearate each period')
    parser.add_argument('-o', '--out',
                        type=str,
                        default='components.dat',
                        help='output filename')
    parser.add_argument('-v', '--verbose',
                        action="store_true",
                        help='cvx verbose')
    parser.add_argument('-s', '--solver',
                        type=str,
                        default='mosek',
                        help='cvx solver')
    args = parser.parse_args(args)
    filename = args.file
    lam = args.lam
    rho = args.rho
    periods = list(map(float, args.periods.split(',')))
    output = args.out
    solver_dicts = {'cvxopt': cvx.CVXOPT,
                    'mosek': cvx.MOSEK}
    solver = solver_dicts.get(args.solver, None)
    if solver is None:
        print("Error solver, cvxopt and mosek are supported!")
        return
    verbose = True if args.verbose else False
    app(filename, output=output, lam=lam,
        rho=rho, periods=periods, verbose=verbose)
