"""
AlgoInvar root package bridge.
Maps 'algoinvar' module namespace to '01_algoinvar_n4_hardware_baseline'.
"""
import importlib
import sys

_mod = importlib.import_module("01_algoinvar_n4_hardware_baseline")
sys.modules[__name__] = _mod
