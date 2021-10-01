#!/home/cosmic/anaconda3/envs/test/bin/python
from caproto.server import PVGroup, get_pv_pair_wrapper, conversion, pvproperty, ioc_arg_parser, run
from lakeshore import Model336

import sys
from textwrap import dedent
import logging
from . import pvproperty_with_rbv
logger = logging.getLogger('caproto')


lakeshore336 = Model336(ip_address='192.168.10.3') #TODO catch time out and try to reconnect

class LakeshoreModel336(PVGroup):
    """
    IOC for Lakeshore Model 336 IOC for Temperture Control
    see manual for commands:
    https://www.lakeshore.com/docs/default-source/product-downloads/336_manual.pdf?sfvrsn=fa4e3a80_5
    """

    TemperatureCelsiusA = pvproperty(dtype=float, doc="Temperature in Celsius", precision=2)
    TemperatureKelvinA = pvproperty(dtype=float, doc="Temperature in Kelvin", precision=2)
    TemperatureCelsiusB = pvproperty(dtype=float, doc="Temperature in Celsius", precision=2)
    TemperatureKelvinB = pvproperty(dtype=float, doc="Temperature in Kelvin", precision=2)
    HeaterOutput = pvproperty(dtype=float, doc="Heater output in %", precision=2)

    TemperatureLimitA = pvproperty_with_rbv(dtype=float,
                                            doc="Temperature Limit (input A) in Kelvin for which to shut down"
                                                "all control outputs when exceeded. A temperature limit of "
                                                "zero turns the Temperature limit feature off for the given "
                                                "sensor input.", precision=2)
    TemperatureLimitB = pvproperty_with_rbv(dtype=float,
                                            doc="Temperature Limit (input A) in Kelvin for which to shut down"
                                                "all control outputs when exceeded. A temperature limit of "
                                                "zero turns the Temperature limit feature off for the given "
                                                "sensor input.", precision=2)
    TemperatureSetPoint = pvproperty_with_rbv(dtype=float, doc="Temperature set point", value=-20.0, precision=2)

    @TemperatureCelsiusA.getter
    async def TemperatureCelsiusA(obj, instance):
        return float(lakeshore336.query('CRDG?'))

    @TemperatureCelsiusA.scan(period=1)
    async def TemperatureCelsiusA(obj, instance, async_lib):
        await instance.write(float(lakeshore336.query('CRDG?')))

    @TemperatureKelvinA.getter
    async def TemperatureKelvinA(obj, instance):
        return float(lakeshore336.query('KRDG?'))

    @TemperatureKelvinA.scan(period=1)
    async def TemperatureKelvinA(obj, instance, async_lib):
        await instance.write(float(lakeshore336.query('KRDG?')))

    @TemperatureLimitA.readback.getter
    async def TemperatureLimitA(obj, instance):
        return float(lakeshore336.query('TLIMIT? A'))

    @TemperatureLimitA.setpoint.putter
    async def TemperatureLimitA(obj, instance, value):
        lakeshore336.query(f'TLIMIT A, {value}')

    @TemperatureCelsiusB.getter
    async def TemperatureCelsiusB(obj, instance):
        return float(lakeshore336.query('CRDG? B'))

    @TemperatureCelsiusB.scan(period=1)
    async def TemperatureCelsiusB(obj, instance, async_lib):
        await instance.write(float(lakeshore336.query('CRDG? B')))

    @TemperatureKelvinB.getter
    async def TemperatureKelvinB(obj, instance):
        return float(lakeshore336.query('KRDG? B'))

    @TemperatureKelvinB.scan(period=1)
    async def TemperatureKelvinB(obj, instance, async_lib):
        await instance.write(float(lakeshore336.query('KRDG? B')))

    @TemperatureLimitB.readback.getter
    async def TemperatureLimitB(obj, instance):
        return float(lakeshore336.query('TLIMIT? B'))

    @TemperatureLimitB.setpoint.putter
    async def TemperatureLimitB(obj, instance, value):
        lakeshore336.query(f'TLIMIT B, {value}')

    @HeaterOutput.getter
    async def HeaterOutput(obj, instance):
        return float(lakeshore336.query('HTR? 1'))

    @HeaterOutput.scan(period=1)
    async def HeaterOutput(obj, instance, async_lib):
        await instance.write(float(lakeshore336.query('HTR? 1')))

    @TemperatureSetPoint.readback.getter
    async def TemperatureSetPoint(obj, instance):
        return float(lakeshore336.query('SETP? 1'))

    @TemperatureSetPoint.setpoint.putter
    async def TemperatureSetPoint(obj, instance, value):
        lakeshore336.query(f'SETP 1, {value}')





def main():
    """Console script for lakeshore336_ioc."""

    ioc_options, run_options = ioc_arg_parser(
        default_prefix='ES7011:FastCCD:',
        desc=dedent(LakeshoreModel336.__doc__))
    ioc = LakeshoreModel336(**ioc_options)
    run(ioc.pvdb, **run_options)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
