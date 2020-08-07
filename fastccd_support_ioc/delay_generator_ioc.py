from caproto.server import PVGroup, get_pv_pair_wrapper, conversion, pvproperty
import subprocess
from textwrap import dedent
import sys
from caproto.server import ioc_arg_parser, run
from caproto import ChannelType
import logging

logger = logging.getLogger('caproto')


# TODO: rename PVs to compliant convention
# TODO: decide on PV naming convention
# TODO: add docs to PVs
# TODO: Should ibterm only ever return one value, or would we ever want multiple values back from a command?


def ibterm(command, caster=None):
    command = f'/bin/bash -c "ibterm -d 15 <<< \\\"{command}\\\""'
    logger.debug('exec:', command)
    stdout = subprocess.check_output(command, shell=True)
    if caster:
        return caster(stdout.decode().split("\n")[2].strip("ibterm>").split(",")[-1])


pvproperty_with_rbv = get_pv_pair_wrapper(setpoint_suffix='',
                                          readback_suffix='_RBV')


class DelayGenerator(PVGroup):
    """
    An IOC for the [something something] delay generator.
    """

    trigger_rate = pvproperty_with_rbv(dtype=float, doc="TriggerRate")
    trigger_on_off = pvproperty_with_rbv(dtype=bool, doc="TriggerOnOFF")
    delay_time = pvproperty_with_rbv(dtype=float, doc="DelayTime")
    shutter_time = pvproperty_with_rbv(dtype=float, doc="ShutterTime")

    @trigger_rate.setpoint.putter
    async def trigger_rate(obj, instance, value):
        ibterm(f"tr 0,{value}")

    @trigger_rate.readback.getter
    async def trigger_rate(obj, instance):
        return ibterm(f"tr 0", float)

    @trigger_on_off.setpoint.putter
    async def trigger_on_off(obj, instance, on):
        logger.debug('setting triggering:', on)
        if on:
            ibterm(f"tm 0")
        else:
            ibterm(f"tm 2")

    @trigger_on_off.readback.getter
    async def trigger_on_off(obj, instance):
        return ibterm(f"tm", bool)

    @delay_time.setpoint.putter
    async def delay_time(obj, instance, delay):
        ibterm(f"dt 2,1,{delay}")

    @delay_time.readback.getter
    async def delay_time(obj, instance):
        return ibterm(f"dt 2", float)

    @shutter_time.setpoint.putter
    async def shutter_time(obj, instance, shutter_time):
        ibterm(f"dt 3,2,{shutter_time}")

    @shutter_time.readback.getter
    async def shutter_time(obj, instance):
        return ibterm(f"dt 3", float)

    state = pvproperty(dtype=ChannelType.ENUM, enum_strings=["unknown", "initialized", "off", ])

    async def _initialize(self, instance, value):
        # clear and setup various parameters
        ibterm(f"CL; DT 2,1,1E-3; DT 3,2,140E-3; TZ 1,1; TZ 4,1; OM 4,0; OM 1,3; OA 1,3.3; OO 1,0; TR 0,5")

    async def _shutdown(self, instance, value):
        # only clear device
        ibterm(f"CL")

    @state.getter
    async def state(self, instance):
        return instance.value

    @state.putter
    async def state(self, instance, value):
        if value != instance.value:
            logger.debug("setting state:", value)

            if value == "initialized":
                await self.initialize(None, None)

            elif value == "off":
                await self.shutdown(None, None)

        return value

    initialize = pvproperty(value=0, dtype=int, put=_initialize)
    shutdown = pvproperty(value=0, dtype=int, put=_shutdown)

    @state.startup
    async def state(self, instance, async_lib):
        await self._initialize(None, None)

    @state.shutdown
    async def state(self, instance, async_lib):
        await self._shutdown(None, None)


def main():
    """Console script for fastccd_support_ioc."""

    ioc_options, run_options = ioc_arg_parser(
        default_prefix='XF:7011:ShutterDelayGenerator:',
        desc=dedent(DelayGenerator.__doc__))
    ioc = DelayGenerator(**ioc_options)

    logger.info("\nAuto-generated Ophyd device for this PVGroup",
                "#" * 80,
                conversion.group_to_device(ioc),
                "#" * 80,
                sep='\n')

    run(ioc.pvdb, **run_options)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
