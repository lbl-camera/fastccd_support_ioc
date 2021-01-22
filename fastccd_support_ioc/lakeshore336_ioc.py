from caproto.server import PVGroup, get_pv_pair_wrapper, conversion, pvproperty, ioc_arg_parser, run
from lakeshore import Model336

import sys
from textwrap import dedent
import logging
logger = logging.getLogger('caproto')

pvproperty_with_rbv = get_pv_pair_wrapper(setpoint_suffix='',
                                          readback_suffix='_RBV')


lakeshore336 = Model336(ip_address='192.168.10.3') #TODO catch time out and try to reconnect

class LakeshoreModel336(PVGroup):

    Temperature = pvproperty_with_rbv
    SetPoint = pvproperty_with_rbv
    HeaterPower = pvproperty_with_rbv
    HeaterSetup = pvproperty_with_rbv

    @Temperature.readback.getter
    async def Temperature(obj, instance):
        lakeshore336.query('CRDG?')

    @SetPoint.readback.getter
    async def SetPoint(obj, instance, n):
        lakeshore336.query(f'SETP? {n}')

    @SetPoint.setpoint.putter
    async def SetPoint(obj, instance, n, value):
        lakeshore336.query(f'SETP? {n}, {value}')

    @HeaterPower.readback.getter
    async def HeaterPower(obj, instance, n):
        lakeshore336.query(f'MOUT? {n}')

    @HeaterSetup.readback.getter
    async def HeaterSetup(obj, instance, n):
        lakeshore336.query(f'HTRSET? {n}')



def main():
    """Console script for lakeshore336_ioc."""

    ioc_options, run_options = ioc_arg_parser(
        default_prefix='ES7011:LakeShore336:',
        desc=dedent(LakeshoreModel336.__doc__))
    ioc = LakeshoreModel336(**ioc_options)
    run(ioc.pvdb, **run_options)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
