"""Top-level package for FastCCD Support IOC."""

__author__ = """Ronald J Pandolfi"""
__email__ = 'ronpandolfi@lbl.gov'
__version__ = '0.1.0'

from . import utils
from caproto.server import PVGroup, get_pv_pair_wrapper
from caproto.server.autosave import autosaved, AutosaveHelper


pvproperty_with_rbv = get_pv_pair_wrapper(setpoint_suffix='',
                                          readback_suffix='_RBV')


class FastAutosaveHelper(AutosaveHelper):
    period = 1


def wrap_autosave(pvgroup: PVGroup):
    pvgroup.readback = autosaved(pvgroup.readback)
    pvgroup.setpoint = autosaved(pvgroup.setpoint)
    return pvgroup
