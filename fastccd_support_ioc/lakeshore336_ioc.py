#!/home/cosmic/anaconda3/envs/test/bin/python
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
    """ Lakeshore Model 336 IOC 
    """
    Temperature = pvproperty_with_rbv(dtype=float, doc="Temperature")
    SetPoint = pvproperty_with_rbv(dtype=float, doc="SetPoint", value=-20.0)
    HeaterPower = pvproperty_with_rbv(dtype=float, doc="HeaterPower")
    HeaterSetup = pvproperty_with_rbv(dtype=float, doc="HeaterSetup")

    @Temperature.readback.getter
    async def Temperature(obj, instance):
        print(lakeshore336.query('CRDG?'))
        return float(lakeshore336.query('CRDG?'))

    @Temperature.readback.scan(period=1)
    async def Temperature(obj, instance, async_lib):
        await instance.write(float(lakeshore336.query('CRDG?')))


    @SetPoint.readback.getter
    async def SetPoint(obj, instance):
        return float(lakeshore336.query('SETP? 1'))

    @SetPoint.setpoint.putter
    async def SetPoint(obj, instance, value):
        lakeshore336.query(f'SETP? 1, {value}')

    @HeaterPower.readback.getter
    async def HeaterPower(obj, instance):
        return float(lakeshore336.query(f'MOUT? 1'))

    @HeaterSetup.readback.getter
    async def HeaterSetup(obj, instance):
        return float(lakeshore336.query(f'HTRSET? 1'))



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
