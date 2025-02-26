from setuptools import setup
#from setuptools.extension import Extension
from Cython.Build import cythonize
from Cython.Distutils import build_ext
from Cython.Distutils.extension import Extension
# setup(
#     name = 'Speedy_Compiled',
#     ext_modules = cythonize(
#         [
#             Extension("Speedy_Compiled", 
#                 ["Speedy_Compiled.pyx"],
#                 extra_compile_args=['/openmp'],
#                 extra_link_args=['/openmp'],
#             ),
#         ],
#         build_dir="build_cythonize",
#         compiler_directives={
#             'language_level' : "3",
#             'always_allow_keywords': True,
#         }
#     ),
#     cmdclass=dict(
#         build_ext=build_ext
#     ),
# )
setup(
    name = '__init__',
    ext_modules = cythonize(
        [
            Extension("Plugins.__init__", 
                ["Plugins/__init__.py"],
                
            ),
        ],
        build_dir="build_cythonize",
        compiler_directives={
            'language_level' : "3",
            'always_allow_keywords': True,
        }
    ),
    cmdclass=dict(
        build_ext=build_ext
    ),
)