#!/usr/bin/env python

"""
conda-deps command line interface.

"""
from colorlog import ColoredFormatter
from logging import (
    Logger,
    getLogger,
    StreamHandler
)
from json import (
    dumps as json_dumps,
    loads as json_loads
)
from networkx import (
    DiGraph,
    compose_all as nx_compose_all,
    bfs_successors as nx_bfs_successors,
)
from networkx.readwrite import json_graph

from conda_deps._version import __version__
from conda_deps.args import build_args_parser
from conda_deps.conda import conda_list_deps


def create_logger(
    name: str = __name__,
    log_level: str = 'def_info'
) -> Logger:
    """
    Create a logger with name and log_level.

    Parameters
    ----------
    name : str
        A string containing the name that the logger will print out

    log_level : str
        A string containing the verbosity of the logger

    Returns
    -------
    Logger
        The logger object.

    """
    logger = getLogger(name)
    handler = StreamHandler()

    if log_level.startswith('def_'):
        log_format = '%(log_color)s%(message)s%(reset)s'
        log_level = log_level[4:]
    else:
        log_format = '%(log_color)s%(levelname)-8s | ' \
            + '%(asctime)s.%(msecs)03d %(module)s - ' \
            + '%(funcName)s(): %(message)s%(reset)s'

    formatter = ColoredFormatter(log_format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(log_level.upper())

    return logger


def entry_point():
    """
    Entry point for the rrparser command line interface.
    """
    parser = build_args_parser(
        prog='conda-deps',
        description='Package to list conda dependencies'
    )
    args = parser.parse_args()

    # Create logger
    logger = create_logger(parser.prog, args.log)

    logger.info(
        '\n{prog} {version}\n'.format(
            prog=logger.name,
            version=__version__
        )
    )
    logger.debug(args)

    # Load dependencies graph
    if args.deps_graphs is not None:
        # Join all the graphs
        deps_graph = nx_compose_all(
            [
                json_graph.node_link_graph(json_loads(open(f).read()))
                for f in args.deps_graphs
            ]
        )
    else:
        deps_graph = DiGraph()

    # Get all the dependencies
    res_deps_graph = DiGraph()
    logger.info("")
    for package in args.packages:
        deps_graph = conda_list_deps(
            package=package,
            environment=args.env,
            recursive=args.recursive,
            deps_graph=deps_graph,
            logger=logger
        )
        dependencies = sum(
            [succ[1] for succ in nx_bfs_successors(deps_graph, package)],
            []
        )
        res_deps_graph.update(deps_graph.subgraph([package] + dependencies))
        print(
            f"Package '{package}' has the following dependencies: "
            f"{', '.join(dependencies)}"
        )

    if args.outfile is None:
        # Print the dependencies graph
        print('The dependencies graph is: ')
        print(json_dumps(json_graph.node_link_data(res_deps_graph), indent=4))
    else:
        # Write the dependencies graph to a file
        print(f'Writing the dependencies graph to the file {args.outfile}...')
        with open(args.outfile, 'w') as f:
            f.write(
                json_dumps(
                    json_graph.node_link_data(res_deps_graph),
                    indent=4
                )
            )


if __name__ == '__main__':
    entry_point()
