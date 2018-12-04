from distutils.core import setup
from Cython.Build import cythonize
from distutils.extension import Extension
# from Cython.Distutils import build_ext

import Cython.Compiler.Options
Cython.Compiler.Options.annotate = True

LIB_DIRS = ['.', './flowstar/', './flowstar/flowstar-2.1.0']
LIBS = ['flowstar', 'mpfr', 'gmp', 'gsl', 'gslcblas', 'm', 'glpk']
COMPILE_ARGS = ['-O0', '-std=c++17', '-Wno-register']
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
        setup_requires=['pytest-runner'],
        tests_require=['pytest']
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

setup(package_dir={'flowstar': 'flowstar'},
      packages=['flowstar'],
      # package_data = {'': ['flowstar/*', '*.pyx', '*.pxd', '*.cpp', '*.h', 'flowstar/*.pxd'],
      #     'flowstar': ['flowstar/*.pxd'],
      #     'flowstar.poly': ['flowstar/*.pxd'],
      #     'flowstar.reachability': ['flowstar/*.pxd'],
      #     'flowstar.interval': ['flowstar/*.pxd'],
      # },
      ext_modules=cythonize(extensions, gdb_debug=True,
                            annotate=True, nthreads=4))
