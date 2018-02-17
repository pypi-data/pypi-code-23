#!/usr/bin/env python3
# -*- coding:utf8 -*-

import os
import subprocess
import getopt
import sys
from graphviz import Digraph


class portgraph:
    def __init__(self, graph, port, localbase, flavor=None,
                 with_pkg=False, verbose=False, recursion=-1, url=False,
                 build=True, run=False):
        self.graph = graph
        self.localbase = localbase
        self.flavor = flavor
        self.port = port
        self.with_pkg = with_pkg
        self.verbose = verbose
        self.recursion = recursion
        self.url = url
        self.www = "https://www.freshports.org/"
        self.all_ports = []
        self.PKG = "ports-mgmt/pkg"
        self.build = build
        self.run = run
        self.graph.attr('node', style='filled',
                        fillcolor='#E1E1E1', fontcolor='#737373')

    def __fullname2port(self, name):
        """ Return the name of the port. """
        return name[len(self.localbase)+1:]

    def __flavorname2port(self, flavorname):
        """ Return a name without the @flavor """
        supFlavor = flavorname.rfind('@')
        if supFlavor == -1:
            supFlavor = len(flavorname)

        return flavorname[:supFlavor]

    def buildGraph(self):
        if self.flavor:
            self.port = self.port + '@' + self.flavor
        if self.url:
            portwithoutflavor = self.__flavorname2port(self.port)
            self.graph.node(self.port,
                            URL=self.www+portwithoutflavor)
        if self.build:
            self.__recurseports(os.path.join(self.localbase, self.port),
                                self.flavor,
                                ['build', '#009999'],
                                self.recursion)
        if self.run:
            self.__recurseports(os.path.join(self.localbase, self.port),
                                self.flavor,
                                ['run', '#990000'],
                                self.recursion)

    def __recurseports(self, ports, flavor, depends_args, maxRecurse=-1):
        if maxRecurse == 0:
            return

        if self.verbose:
            print(ports)

        portname = self.__flavorname2port(ports)

        proc = subprocess.Popen(['make', '-C',
                                 portname,
                                 depends_args[0] + '-depends-list',
                                 '-DDEPENDS_SHOW_FLAVOR'] +
                                (['FLAVOR='+flavor] if flavor else []),
                                stdout=subprocess.PIPE)
        while True:
            line = proc.stdout.readline().decode('utf-8')
            if line != '':
                dep_port = line.rstrip()
                self.all_ports.append(ports)
                portname = self.__fullname2port(ports)
                depportname = self.__fullname2port(dep_port)

                if (depportname != self.PKG) or \
                   ((depportname == self.PKG) and
                   self.with_pkg):
                    if self.url:
                        depwithoutflavor = self.__flavorname2port(depportname)
                        self.graph.node(depportname,
                                        URL=self.www+depwithoutflavor)
                    self.graph.edge(portname, depportname,
                                    color=depends_args[1])
                if dep_port not in self.all_ports:
                    self.all_ports.append(dep_port)
                    self.__recurseports(dep_port, flavor, depends_args,
                                        maxRecurse - 1)
            else:
                break


def usage(name):
    print("{} produces a graph representing the ".format(name) +
          "dependencies needed for a given port")
    print("Options are:")
    print("-h or --help: Show this help")
    print("-l my_dir or --localbase my_dir: Sets my_dir as the directory" +
          " where ports are located (/usr/ports by default)")
    print("-p my_port or --port my_port: Sets my_port as the port to produce" +
          " the graph\n(ports-mgmt/py-portgraph by default).")
    print("-b or --build: build-depends-list " +
          "(if -b or -r is not present, -b is actived by default).")
    print("-r or --run: run-depends-list " +
          "(if -b or -r is not present, -b is actived by default).")
    print("-f my_flavor or --flavor my_flavor: Sets the flavor for the port.")
    print("-c or --recursion: Sets the maximum recursion.")
    print("-u or --url: Adds a link to freshports.")
    print("-w or --with-pkg: Since pkg is always required, this is disabled " +
          " by default. You can enable it with this option.")
    print("-a or --all: Build a graph for each port")


def graph4allports(localbase, flavor, with_pkg, verbose, recursion, url,
                   build, run):
    for cat in [rec for rec in os.scandir(localbase)
                if rec.is_dir()
                # Maybe use $LOCALBASE$ SUBDIR instead?
                and rec.name not in ['Mk', 'distfiles',
                                     'Tools', 'Templates',
                                     'Keywords', 'base']]:
        for port in [rec for rec in os.scandir(os.path.join(localbase, cat))
                     if rec.is_dir()]:
            graph4port(os.path.join(cat.name, port.name), localbase, flavor,
                       with_pkg, verbose, recursion, url, build, run)


def graph4port(port, localbase, flavor, with_pkg, verbose, recursion, url,
               build, run):
        name = port[port.find('/')+1:]
        if flavor:
            name = name + '@' + flavor
        g = Digraph(name, filename=name, format='svg')
        g.graph_attr['rankdir'] = 'LR'
        pg = portgraph(g, port, localbase, flavor, with_pkg,
                       verbose, recursion, url, build, run)
        pg.buildGraph()
        g.render(name)


def main():
    port = "ports-mgmt/py-portgraph"
    localbase = "/usr/ports"
    with_pkg = False
    verbose = False
    flavor = None
    url = False
    allports = False
    build = False
    run = False
    recursion = -1
    try:
        opts, args = getopt.getopt(sys.argv[1:],
                                   "hl:p:f:c:uvwabr",
                                   ["help", "localbase=",
                                    "port=", "flavor=", "recursion=", "url"
                                    "verbose",
                                    "with-pkg",
                                    "all",
                                    "build", "run"])
    except getopt.GetoptError as err:
        print(str(err))
        usage(sys.argv[0])
        sys.exit(2)

    for o, a in opts:
        if o == "-v":
            verbose = True
        elif o in ("-h", "--help"):
            usage(sys.argv[0])
            sys.exit()
        elif o in ("-l", "--localbase"):
            localbase = a.rstrip(os.sep)
        elif o in ("-p", "--port"):
            port = a
        elif o in ("-f", "--flavor"):
            flavor = a
        elif o in ("-c", "--recursion"):
            recursion = int(a)
        elif o in ("-u", "--url"):
            url = True
        elif o in ("-w", "--with-pkg"):
            with_pkg = True
        elif o in ("-a", "--all"):
            allports = True
        elif o in ("-b", "--build"):
            build = True
        elif o in ("-r", "--run"):
            run = True

    if build is False and run is False:
        build = True

    if allports:
        graph4allports(localbase, flavor, with_pkg, verbose, recursion, url,
                       build, run)
    else:
        graph4port(port, localbase, flavor, with_pkg, verbose, recursion, url,
                   build, run)


if __name__ == "__main__":
    main()
