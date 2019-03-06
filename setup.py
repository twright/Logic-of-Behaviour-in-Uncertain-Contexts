#!/usr/bin/env python2

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
# from distutils.core import setup
# from setuptools import find_packages

Cython.Compiler.Options.annotate = True
Cython.Compiler.Options.fast_fail = True

LIB_DIRS = ['.', './flowstar/', './ulbc/', './flowstar/flowstar-2.1.0',
            '/usr/include/boost']
LIBS = ['flowstar', 'mpfr', 'gmp', 'gsl', 'gslcblas', 'm', 'glpk']
COMPILE_ARGS = ['-O3', '-std=c++17', '-Wno-register', '-march=native']
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
        os.unlink(self.flowstar_link_path)
        os.symlink(self.flowstar_dir, self.flowstar_link_path)
        self.run_command('clean_flowstar')


class CleanFlowstarCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.announce('Cleaning flowstar...')
        try:
            subprocess.call('make clean', cwd='flowstar/flowstar-2.1.0',
                            shell=True)
        except:
            pass
        try:
            subprocess.call('rm -f flowstar/*.so', shell=True)
        except:
            pass


class TestCommand(Command):
    user_options = [
        ('verbose-test', 'v', 'Verbose?'),
        ('all', 'a', 'Run all tests?'),
    ]

    def initialize_options(self):
        self.verbose_test = False
        self.all = False

    def finalize_options(self):
        self.verbose_test = bool(self.verbose_test)
        self.all = bool(self.all)

    def run(self):
        self.run_command('build_ext')
        # self.run_command('pytest')
        self.announce('Testing...')
        cmd = ['pytest']  # , '--doctest-cython']
        if self.verbose_test:
            cmd.append('-v')
        if self.all:
            cmd.append('-m "slow"')
        subprocess.call(cmd)


class BuildFlowstarCommand(Command):
    user_options = []

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
                          language_level=2))
