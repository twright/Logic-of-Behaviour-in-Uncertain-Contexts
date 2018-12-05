#!/usr/bin/env python2

from distutils.core import setup
from Cython.Build import cythonize
from Cython.Distutils import build_ext
from distutils.extension import Extension
from distutils.cmd import Command
# from Cython.Distutils import build_ext
import subprocess
import os

import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

LIB_DIRS = ['.', './flowstar/', './flowstar/flowstar-2.1.0']
LIBS = ['flowstar', 'mpfr', 'gmp', 'gsl', 'gslcblas', 'm', 'glpk']
COMPILE_ARGS = ['-O3', '-std=c++17', '-Wno-register']
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
        name='flowstar.flowroots',
        sources=['flowstar/flowroots.pyx'],
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

    flowstar_link_path = 'flowstar/flowstar-2.1.0'

    def initialize_options(self):
        self.mode = 'debug'

    def finalize_options(self):
        if self.mode == 'upstream':
            self.flowstar_dir = os.path.join(os.getcwd(), 'flowstar',
                                             'flowstar-2.1.0-clean')
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
        subprocess.call(['make', 'clean'], cwd='flowstar/flowstar-2.1.0')


class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.announce('Testing...')
        subprocess.call(['pytest', '--doctest-cython'])


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


setup(package_dir={'flowstar': 'flowstar'},
      packages=['flowstar'],
      cmdclass={'choose_flowstar': ChooseFlowstarCommand,
                'clean_flowstar': CleanFlowstarCommand,
                'build_flowstar': BuildFlowstarCommand,
                'test': TestCommand,
                'build_ext': BuildAllCommand},
      ext_modules=cythonize(extensions, gdb_debug=True,
                            annotate=True, nthreads=4))
