from json import loads as json_loads
from subprocess import run
from logging import (
    Logger,
    getLogger
)
from networkx import (
    DiGraph
)
from networkx.readwrite import json_graph

from .args import DEFAULT_ARGS


def conda_list(environment: str, logger: Logger = getLogger(__name__)) -> str:
    '''List all the packages in the given environment

    Parameters
    ----------
    environment: str
        Name of the environment
    logger: Logger
        Logger to use

    Returns
    -------
    stdout: str
        Output of the conda list command
    '''
    proc = run(["conda", "list", "--json", "--name", environment],
               text=True, capture_output=True)
    return json_loads(proc.stdout)


def conda_install(
    environment: str,
    package: str,
    logger: Logger = getLogger(__name__)
) -> str:
    '''Install a package in the given environment

    Parameters
    ----------
    environment: str
        Name of the environment
    package: str
        Name of the package to install
    logger: Logger
        Logger to use

    Returns
    -------
    stdout: str
        Output of the conda install command
    '''
    run(
        ["conda", "install", "--quiet",
            "--yes", "--name", environment, package],
        text=True, capture_output=True
    )
    # return json_loads(proc.stdout)


def conda_list_deps(
    package: str,
    environment: str = DEFAULT_ARGS['ENVIRONMENT'],
    recursive: bool = DEFAULT_ARGS['RECURSIVE'],
    deps_graph: DiGraph = DiGraph(),
    pkg_lst: dict = {},
    logger: Logger = getLogger(__name__)
):
    '''List all the dependencies of the given package in the given environment

    Parameters
    ----------
    environment: str
        Name of the environment
    package: str
        Name of the package
    recursive: bool
        Whether to list the dependencies of the dependencies
    deps_dict: dict
        Dictionary of dependencies
    pkg_lst: dict
        List of packages in the environment
    logger: Logger
        Logger to use

    Returns
    -------
    list
        List of dependencies of the package
    '''
    logger.debug(f"Package: {package}")
    logger.debug(f"Environment: {environment}")
    logger.debug(f"Recursive: {recursive}")
    logger.debug(
        f"Dependencies graph: {json_graph.node_link_data(deps_graph)}"
    )
    # logger.debug(f"Package list: {pkg_lst}")

    logger.info(
        f"Getting dependencies for package {package} "
        f"in '{environment}' environment..."
    )

    try:
        if 'license' in deps_graph.nodes[package]:
            logger.warning(f"Package {package} already in dependencies graph")
            return deps_graph
    except KeyError:
        pass

    proc = run(["conda", "tree", "-n", environment, "depends", package],
               text=True, capture_output=True)
    depends = proc.stdout.splitlines()

    if not pkg_lst:
        logger.info(f"Getting package list in '{environment}' environment...")
        pkg_lst = conda_list(environment, logger)

    try:
        ver = [pkg['version'] for pkg in pkg_lst if pkg['name'] == package][0]
    except IndexError:
        logger.warning(
            f"Package {package} not found in '{environment}' environment"
        )
        return deps_graph

    deps_graph.add_node(
        package,
        version=ver,
        license=conda_licence(package, ver)
    )
    for dep in depends:
        deps_graph.add_edge(package, dep)

    logger.debug(f'{package}: {deps_graph.nodes[package]}')

    if recursive:
        for dep in deps_graph.neighbors(package):
            logger.debug(f"processing {dep} (dependency of {package})")
            deps_graph = conda_list_deps(
                package=dep,
                environment=environment,
                recursive=recursive,
                deps_graph=deps_graph,
                pkg_lst=pkg_lst,
                logger=logger
            )

    return deps_graph


def conda_licence(
    package: str,
    version: str,
    logger: Logger = getLogger(__name__)
) -> str:
    '''Get the license of the given package

    Parameters
    ----------
    package: str
        Name of the package
    version: str
        Version of the package
    logger: Logger
        Logger to use

    Returns
    -------
    str
        License of the package
    '''
    proc = run(["conda", "search", "--json", package],
               text=True, capture_output=True)
    logger.debug(json_loads(proc.stdout))
    try:
        return [
            pkg_ver['license']
            for pkg_ver in json_loads(proc.stdout)[package]
            if pkg_ver['version'] == version
        ][0]
    except KeyError:
        return 'Unknown'


def conda_get_infos(
    package: str,
    ver: str = 'latest',
    logger: Logger = getLogger(__name__)
):
    '''Get the license and the dependencies of the given package

    Parameters
    ----------
    package: str
        Name of the package
    logger: Logger
        Logger to use

    Returns
    -------
    dict
        Dictionary of the license and the dependencies
    '''
    proc = run(["conda", "search", "--json", package],
               text=True, capture_output=True)
    pkg_ver_lst = json_loads(proc.stdout)[package]
    if ver == 'latest':
        return pkg_ver_lst[-1]
    elif ver:
        return list(
            filter(
                lambda pkg_ver_lst: pkg_ver_lst['version'] == ver,
                pkg_ver_lst
            )
        )
    return pkg_ver_lst


def conda_get_deps(
        package: str,
        ver: str = 'latest',
        recursive: bool = False,
        deps_dict: dict = {},
        logger: Logger = getLogger(__name__)
):
    '''Get the dependencies of the given package

    Parameters
    ----------
    package: str
        Name of the package
    logger: Logger
        Logger to use

    Returns
    -------
    list
        List of dependencies
    '''
    infos = conda_get_infos(package, ver)
    logger.debug(package, ver, infos)
    deps_dict[package] = conda_list_deps(package, recursive=False)
    print(deps_dict)
    # deps_dict[package] = {
    #     k: v
    #     for k, v in infos.items()
    #     if k in ['depends', 'license']
    # }
    # Remove pinned version from dependencies
    # deps_dict[package]['depends'] = [
    #     dep.split(' ')[0]
    #     for dep in deps_dict[package]['depends']
    # ]
    logger.debug(package, deps_dict[package])
    # if recursive:
    #     for dep in deps_dict[package]['depends']:
    #         if dep not in deps_dict:
    #             deps_dict[dep] = conda_get_deps(
    #                 dep,
    #                 recursive=recursive,
    #                 deps_dict=deps_dict,
    #                 logger=logger
    #             )
    return deps_dict
