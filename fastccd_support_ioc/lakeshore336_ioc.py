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
    """
    IOC for Lakeshore Model 336 IOC for Temperture Control
    """

    TemperatureCelsius = pvproperty(dtype=float, doc="Temperature in Celsius")
    TemperatureKelvin = pvproperty(dtype=float, doc="Temperature in Kelvin")
    HeaterOutput = pvproperty(dtype=float, doc="Heater Power")

    TemperatureLimit = pvproperty_with_rbv(dtype=float, doc="Temperature Limit (input A) in Kelvin for which to shut down"
                                                     "all control outputs when exceeded. A temperature limit of "
                                                     "zero turns the Temperature limit feature off for the given "
                                                     "sensor input.")
    SetPoint = pvproperty_with_rbv(dtype=float, doc="Set Point", value=-20.0)


    @TemperatureCelsius.readback.getter
    async def TemperatureCelsius(obj, instance):
        return float(lakeshore336.query('CRDG?'))

    @TemperatureCelsius.readback.scan(period=1)
    async def TemperatureCelsius(obj, instance, async_lib):
        await instance.write(float(lakeshore336.query('KRDG?')))

    @TemperatureKelvin.readback.getter
    async def TemperatureKelvin(obj, instance):
        return float(lakeshore336.query('KRDG?'))

    @TemperatureKelvin.readback.scan(period=1)
    async def TemperatureKelvin(obj, instance, async_lib):
        await instance.write(float(lakeshore336.query('KRDG?')))

    #TODO check which input channel is required?
    @TemperatureLimit.readback.getter
    async def TemperatureLimit(obj, instance):
        return float(lakeshore336.query('TLIMIT? A'))

    @TemperatureLimit.setpoint.putter
    async def TemperatureLimit(obj, instance, value):
        lakeshore336.query(f'TLIMIT A, {value}')

    @HeaterOutput.readback.getter
    async def HeaterOutput(obj, instance):
        return float(lakeshore336.query('HTR? 1'))

    @SetPoint.readback.getter
    async def SetPoint(obj, instance):
        return float(lakeshore336.query('SETP? 1'))

    @SetPoint.setpoint.putter
    async def SetPoint(obj, instance, value):
        lakeshore336.query(f'SETP 1, {value}')





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
