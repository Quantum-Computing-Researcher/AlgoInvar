import os
import sys
from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext

class get_pybind_include:
    """Helper class to delay importing pybind11 until after it is installed."""
    def __str__(self):
        import pybind11
        return pybind11.get_include()

extra_compile_args = ["-O3", "-std=c++17"]
if sys.platform == "win32":
    extra_compile_args = ["/O2", "/std:c++17"]

ext_modules = [
    Extension(
        "algoinvar_core",
        [
            os.path.join("src", "algoinvar_fast.cpp"),
            os.path.join("bindings", "pybind_module.cpp"),
        ],
        include_dirs=[
            "include",
            get_pybind_include(),
        ],
        language="c++",
        extra_compile_args=extra_compile_args,
    ),
]

setup(
    name="algoinvar_core",
    version="1.0.0",
    author="Rehan Arqam",
    author_email="rarqam14@gmail.com",
    description="High-performance C++ backend for AlgoInvar quantum invariant verification",
    long_description="Native C++17 evaluation engine with hardware-accelerated bitwise POPCNT routines for utility-scale quantum processor bitstrings.",
    ext_modules=ext_modules,
    setup_requires=["pybind11>=2.6.0"],
    install_requires=["pybind11>=2.6.0"],
    zip_safe=False,
    python_requires=">=3.8",
)
