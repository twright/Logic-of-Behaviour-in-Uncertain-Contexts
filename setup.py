#!/usr/bin/env python3

import os
# from Cython.Distutils import build_ext
import subprocess
# from distutils.extension import Extension

from setuptools import setup, find_packages
import Cython.Compiler.Options
from Cython.Build import cythonize
from Cython.Distutils import build_ext
from distutils.extension import Extension
from distutils.cmd import Command
from typing import *
# from distutils.core import setup
# from setuptools import find_packages

Cython.Compiler.Options.annotate = True
Cython.Compiler.Options.fast_fail = True

LIB_DIRS = ['.', './flowstar/', './ulbc/', './flowstar/flowstar-2.1.0',
            '/usr/include/boost']
LIBS = ['flowstar', 'mpfr', 'gmp', 'gsl', 'gslcblas', 'm', 'glpk']
COMPILE_ARGS = ['-O3', '-std=c++17', '-Wno-register', '-march=native',
                '-mtune=native']
LINK_ARGS = ['-std=c++17']

extensions = [
    Extension(
        name='flowstar.interval',
        sources=['flowstar/interval.pyx'],
        language='c++',
        libraries=LIBS,
        extra_compile_args=COMPILE_ARGS,
        extra_link_args=LINK_ARGS,
        library_dirs=LIB_DIRS,
        include_dirs=LIB_DIRS,
    ),
    Extension(
        name='flowstar.modelParser',
        sources=['flowstar/modelParser.pyx'],
        language='c++',
        libraries=LIBS,
        extra_compile_args=COMPILE_ARGS,
        extra_link_args=LINK_ARGS,
        library_dirs=LIB_DIRS,
        include_dirs=LIB_DIRS,
    ),
    Extension(
        name='flowstar.taylormodel',
        sources=['flowstar/taylormodel.pyx'],
        language='c++',
        libraries=LIBS,
        extra_compile_args=COMPILE_ARGS,
        extra_link_args=LINK_ARGS,
        library_dirs=LIB_DIRS,
        include_dirs=LIB_DIRS,
    ),
    Extension(
        name='flowstar.poly',
        sources=['flowstar/poly.pyx'],
        language='c++',
        libraries=LIBS,
        extra_compile_args=COMPILE_ARGS,
        extra_link_args=LINK_ARGS,
        library_dirs=LIB_DIRS,
        include_dirs=LIB_DIRS,
    ),
    Extension(
        name='flowstar.root_detection',
        sources=['flowstar/root_detection.pyx'],
        language='c++',
        libraries=LIBS,
        extra_compile_args=COMPILE_ARGS,
        extra_link_args=LINK_ARGS,
        library_dirs=LIB_DIRS,
        include_dirs=LIB_DIRS,
    ),
    Extension(
        name='flowstar.plotting',
        sources=['flowstar/plotting.pyx'],
        language='c++',
        libraries=LIBS,
        extra_compile_args=COMPILE_ARGS,
        extra_link_args=LINK_ARGS,
        library_dirs=LIB_DIRS,
        include_dirs=LIB_DIRS,
    ),
    Extension(
        name='flowstar.observable',
        sources=['flowstar/observable.pyx'],
        language='c++',
        libraries=LIBS,
        extra_compile_args=COMPILE_ARGS,
        extra_link_args=LINK_ARGS,
        library_dirs=LIB_DIRS,
        include_dirs=LIB_DIRS,
    ),
    Extension(
        name='flowstar.reachability',
        sources=['flowstar/reachability.pyx'],
        language='c++',
        libraries=LIBS,
        extra_compile_args=COMPILE_ARGS,
        extra_link_args=LINK_ARGS,
        library_dirs=LIB_DIRS,
        include_dirs=LIB_DIRS,
    ),
    Extension(
        name='flowstar.observers',
        sources=['flowstar/observers.pyx'],
        language='c++',
        libraries=LIBS,
        extra_compile_args=COMPILE_ARGS,
        extra_link_args=LINK_ARGS,
        library_dirs=LIB_DIRS,
        include_dirs=LIB_DIRS,
    ),
]


class ChooseFlowstarCommand(Command):
    user_options = [
        ('mode=', 'm', 'which version for flowstar to use? [upstream/debug]')
    ]

    flowstar_link_path = os.path.join(os.getcwd(), 'flowstar',
                                      'flowstar-2.1.0')

    def initialize_options(self):
        self.mode = 'debug'

    def finalize_options(self):
        if self.mode == 'upstream':
            self.flowstar_dir = os.path.join(os.getcwd(), 'flowstar',
                                             'flowstar-2.1.0-clean')
        elif self.mode == 'fastintervals':
            self.flowstar_dir = os.path.join(os.getcwd(), 'flowstar',
                                             'flowstar-2.1.0-fast-intervals')
        elif self.mode == 'debug':
            self.flowstar_dir = os.path.join(os.getcwd(), 'flowstar',
                                             'flowstar-2.1.0-debug')
        else:
            raise ValueError('mode must be upstream or debug!')

    def run(self):
        self.announce('Choosing flowstar {}...'.format(self.mode))
        try:
            os.unlink(self.flowstar_link_path)
        except os.error:
            pass
        os.symlink(self.flowstar_dir, self.flowstar_link_path)
        self.run_command('clean_flowstar')


class CleanFlowstarCommand(Command):
    user_options: List[Tuple[str, str, str]] = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.announce('Cleaning flowstar...')
        # try:
        subprocess.call('make clean', cwd='flowstar/flowstar-2.1.0',
                        shell=True)
        # except:
            # pass
        try:
            subprocess.call('rm -f flowstar/*.so', shell=True)
        except:
            pass


class TestCommand(Command):
    user_options = [
        ('verbose-test', 'v', 'Verbose?'),
        ('all', 'a', 'Run all tests?'),
        ('most', 'm', 'Run most tests (including slower ones)?'),
        ('failed', 'f', 'Run only tests which failed last time.'),
        ('fail-fast', 'x', 'Stop after the first test fails.'),
    ]

    def initialize_options(self):
        self.verbose_test = False
        self.all = False
        self.most = False
        self.failed = False
        self.fail_fast = False

    def finalize_options(self):
        self.verbose_test = bool(self.verbose_test)
        self.all = bool(self.all)
        self.most = bool(self.most)
        self.failed = bool(self.failed)
        self.fail_fast = bool(self.fail_fast)

    def run(self):
        # self.announce("anouncing", 1)
        self.run_command('build_ext')
        # self.run_command('pytest')
        self.announce('Testing...')
        cmd = ['/usr/bin/env', 'python3', '-m', 'pytest', '--disable-pytest-warnings']  # , '--doctest-cython']
        if self.verbose_test:
            cmd.append('-v')
        if self.all:
            self.announce("running all tests")
            # cmd.append('-m "slow or not slow or very_slow or not very_slow"')
            cmd.extend(['-m', 'very_slow or not very_slow'])
        elif self.most:
            self.announce("running *most* tests")
            cmd.extend(['-m', 'not very_slow'])
        else:
            self.announce("warning: excluding slow tests")
            cmd.extend(['-m', 'not slow and not very_slow'])
        if self.failed:
            cmd.extend(["--lf", "--lfnf=all"])
        if self.fail_fast:
            cmd.append("-x")

        print(f"cmd = {repr(cmd)}")
        subprocess.call(cmd)


class BuildFlowstarCommand(Command):
    user_options: List[Tuple[str, str, str]] = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.announce('Building flowstar...')
        subprocess.call(['make'], cwd='flowstar/flowstar-2.1.0')


class BuildAllCommand(build_ext, object):
    def initialize_options(self):
        super(BuildAllCommand, self).initialize_options()

    def build_extensions(self):
        self.run_command('build_flowstar')
        super(BuildAllCommand, self).build_extensions()


setup(
    packages=find_packages(),
    package_dir={'ulbc': 'ulbc', 'flowstar': 'flowstar'},
    py_modules=['flowstar', 'ulbc'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    cmdclass={'choose_flowstar': ChooseFlowstarCommand,
              'clean_flowstar': CleanFlowstarCommand,
              'build_flowstar': BuildFlowstarCommand,
              'test': TestCommand,
              'build_ext': BuildAllCommand},
    ext_modules=cythonize(extensions, gdb_debug=True,
                          annotate=True, nthreads=4,
                          language_level=3))
