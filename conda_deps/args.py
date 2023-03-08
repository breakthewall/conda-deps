from os import environ as os_environ
from argparse import ArgumentParser
from conda_deps._version import __version__
from typing import (
    Callable,
)


DEFAULT_ARGS = {
    'RECURSIVE': False,
    'ENVIRONMENT': os_environ['CONDA_DEFAULT_ENV'],
    'OUTPUT_FORMAT': 'json'
}


def build_args_parser(
    prog: str,
    description: str = '',
    epilog: str = '',
    m_add_args: Callable = None,
) -> ArgumentParser:

    parser = ArgumentParser(
        prog=prog,
        description=description,
        epilog=epilog
    )

    # Build Parser with rptools common arguments
    parser = _add_arguments(parser)

    # Add module specific arguments
    if m_add_args is not None:
        parser = m_add_args(parser)

    return parser


def add_logger_args(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument(
        '--log', '-l',
        metavar='ARG',
        type=str,
        choices=[
            'debug', 'info', 'warning', 'error', 'critical', 'silent', 'quiet',
            'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL', 'SILENT', 'QUIET'
        ],
        default='def_info',
        help='Adds a console logger for the specified level (default: error)'
    )
    parser.add_argument(
        '--silent', '-s',
        action='store_true',
        default=False,
        help='run %(prog)s silently'
    )
    return parser


def _add_arguments(parser: ArgumentParser) -> ArgumentParser:
    # Add arguments related to the logger
    parser = add_logger_args(parser)

    parser.add_argument(
        '--packages',
        nargs='+',
        required=True,
        type=str,
        help="Name of the packages to list dependencies"
    )

    parser.add_argument(
        '--env',
        type=str,
        default=DEFAULT_ARGS['ENVIRONMENT'],
        help="Environment where to list dependencies. "
        + "If not provided, the current environment is used."
    )

    parser.add_argument(
        '--recursive',
        action='store_true',
        default=DEFAULT_ARGS['RECURSIVE'],
        help="List all dependencies recursively "
        + f"(default: {DEFAULT_ARGS['RECURSIVE']})"
    )

    parser.add_argument(
        '--outfile',
        type=str,
        default=None,
        help="Output file where to save the dependencies"
    )

    parser.add_argument(
        '--deps-graphs',
        nargs='+',
        type=str,
        default=None,
        help="Dependencies graph file where to load dependencies"
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s {}'.format(__version__),
        help='show the version number and exit'
    )

    return parser
