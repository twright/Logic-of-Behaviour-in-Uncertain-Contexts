from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension
# from Cython.Distutils import build_ext

import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

LIB_DIRS = ['.', 'flowstar-2.1.0']
LIBS = ['flowstar', 'mpfr', 'gmp', 'gsl', 'gslcblas', 'm', 'glpk']
COMPILE_ARGS = ['-O0', '-std=c++17', '-Wno-register']
LINK_ARGS = ['-std=c++17']

extensions = [
    Extension(
        name='interval',
        sources=['interval.pyx'],
        libraries=LIBS,
        language='c++',
        extra_compile_args=COMPILE_ARGS,
        extra_link_args=LINK_ARGS,
        library_dirs=LIB_DIRS,
        include_dirs=LIB_DIRS,
    ),
    # Extension(
    #     name='modelParser',
    #     sources=['modelParser.pyx'],
    #     libraries=LIBS,
    #     language='c++',
    #     extra_compile_args=COMPILE_ARGS,
    #     extra_link_args=LINK_ARGS,
    #     library_dirs=LIB_DIRS,
    #     include_dirs=LIB_DIRS,
    # ),
    Extension(
        name='reachability',
        sources=['reachability.pyx'],
        libraries=LIBS,
        language='c++',
        extra_compile_args=COMPILE_ARGS,
        extra_link_args=LINK_ARGS,
        library_dirs=LIB_DIRS,
        include_dirs=LIB_DIRS,
    ),
    Extension(
        name='flowroots',
        sources=['flowroots.pyx'],
        libraries=LIBS,
        language='c++',
        extra_compile_args=COMPILE_ARGS,
        extra_link_args=LINK_ARGS,
        library_dirs=LIB_DIRS,
        include_dirs=LIB_DIRS,
    ),
    Extension(
        name='flowinttests',
        sources=['flowinttests.pyx'],
        libraries=LIBS,
        language='c++',
        extra_compile_args=COMPILE_ARGS,
        extra_link_args=LINK_ARGS,
        library_dirs=LIB_DIRS,
        include_dirs=LIB_DIRS,
        setup_requires=['pytest-runner'],
        tests_require=['pytest']
    ),
    # Extension(
    #     name='flowtest',
    #     sources=['flowtest.pyx'],
    #     libraries=LIBS,
    #     language='c++',
    #     extra_compile_args=COMPILE_ARGS,
    #     extra_link_args=LINK_ARGS,
    #     library_dirs=LIB_DIRS,
    #     include_dirs=LIB_DIRS,
    # ),
]

setup(ext_modules=cythonize(extensions, gdb_debug=True, annotate=True))
