from unittest import TestCase
from os import path as os_path
from subprocess import run
from random import randint
from json import loads as json_loads
from networkx.readwrite import json_graph

from conda_deps.conda import (
    conda_list,
    conda_install,
    conda_list_deps
)


class Test_conda(TestCase):

    DATA_FOLDER = os_path.join(
        os_path.dirname(os_path.realpath(__file__)),
        'data'
    )

    __pkg = 'tk'

    def setUp(self) -> None:
        self.__env = str(randint(0, 100000))
        self.__tk_deps = [Test_conda.__pkg, 'libzlib']
        run(["conda", "create", "-n", self.__env, Test_conda.__pkg, "-y"],
            text=True, capture_output=True)

    def tearDown(self) -> None:
        run(["conda", "remove", "-n", self.__env],
            text=True, capture_output=True)

    def test_conda_list(self):
        pkg_lst = conda_list(self.__env)
        self.assertSetEqual(
            set([pkg['name'] for pkg in pkg_lst]),
            set(self.__tk_deps)
        )

    def test_conda_install(self):
        conda_install(self.__env, "libiconv")
        pkg_lst = conda_list(self.__env)
        self.assertSetEqual(
            set([pkg['name'] for pkg in pkg_lst]),
            set(self.__tk_deps + ['libiconv'])
        )

    # python -m conda_deps --packages tk
    def test_conda_list_deps(self):
        deps_graph = conda_list_deps(Test_conda.__pkg, self.__env)
        self.assertDictEqual(
            json_graph.node_link_data(deps_graph),
            json_loads(open(f'{Test_conda.DATA_FOLDER}/tk.json').read())
        )

    # python -m conda_deps --packages tk --recursive
    def test_conda_list_deps_rec(self):
        deps_graph = conda_list_deps(
            package=Test_conda.__pkg,
            environment=self.__env,
            recursive=True
        )
        self.assertDictEqual(
            json_graph.node_link_data(deps_graph),
            json_loads(open(f'{Test_conda.DATA_FOLDER}/tk_rec.json').read())
        )
