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


def ibterm(command, caster=None):
    command = f'/bin/bash -c "ibterm -d 15 <<< \\\"{command}\\\""'
    logger.debug(f'exec: {command}')
    print(f'exec: {command}')
    stdout = subprocess.check_output(command, shell=True)
    if caster:
        value_string = stdout.decode().split("\n")[2].strip("ibterm>").split(",")[-1]
        print('casting value:', value_string)
        return caster(value_string)


pvproperty_with_rbv = get_pv_pair_wrapper(setpoint_suffix='',
                                          readback_suffix='_RBV')


class DelayGenerator(PVGroup):
    """
    An IOC for the [something something] delay generator.
    """

    TriggerRate = pvproperty_with_rbv(dtype=float, doc="TriggerRate")
    TriggerEnabled = pvproperty_with_rbv(dtype=bool, doc="TriggerOnOFF")
    ShutterOpenDelay = pvproperty_with_rbv(dtype=float, doc="DelayTime", value=0.0035)
    ShutterTime = pvproperty_with_rbv(dtype=float, doc="ShutterTime")

    @TriggerRate.setpoint.putter
    async def TriggerRate(obj, instance, value):
        ibterm(f"tr 0,{value}")

    @TriggerRate.readback.getter
    async def TriggerRate(obj, instance):
        return ibterm(f"tr 0", float)

    @TriggerEnabled.setpoint.putter
    async def TriggerEnabled(obj, instance, on):
        logger.debug(f'setting triggering: {on}')
        if on=='On':
            ibterm(f"tm 0")
        else:
            ibterm(f"tm 2")

    @TriggerEnabled.readback.getter
    async def TriggerEnabled(obj, instance):
        return ibterm(f"tm", bool)

    @ShutterOpenDelay.setpoint.putter
    async def ShutterOpenDelay(obj, instance, delay):
        ibterm(f"dt 2,1,{delay}")

    @ShutterOpenDelay.readback.getter
    async def ShutterOpenDelay(obj, instance):
        return ibterm(f"dt 2", float)

    @ShutterTime.setpoint.putter
    async def ShutterTime(obj, instance, shutter_time):
        ibterm(f"dt 3,2,{shutter_time}")

    @ShutterTime.readback.getter
    async def ShutterTime(obj, instance):
        return ibterm(f"dt 3", float)

    State = pvproperty(dtype=ChannelType.ENUM, enum_strings=["unknown", "initialized", "uninitialized", ])

    async def _initialize(self, instance, value):
        # clear and setup various parameters
        ibterm(f"CL; DT 2,1,1E-3; DT 3,2,140E-3; TZ 1,1; TZ 4,1; OM 4,0; OM 1,3; OA 1,3.3; OO 1,0; TR 0,5")

    async def _reset(self, instance, value):
        # only clear device
        ibterm(f"CL")

    @State.getter
    async def State(self, instance):
        return instance.value

    @State.putter
    async def State(self, instance, value):
        if value != instance.value:
            logger.debug("setting state:", value)

            if value == "initialized":
                await self._initialize(None, None)

            elif value == "uninitialized":
                await self._reset(None, None)

        return value

    Initialize = pvproperty(value=0, dtype=int, put=_initialize)
    Reset = pvproperty(value=0, dtype=int, put=_reset)

    @State.startup
    async def State(self, instance, async_lib):
        await self._initialize(None, None)

    @State.shutdown
    async def State(self, instance, async_lib):
        await self._reset(None, None)

    ShutterCloseDelay = pvproperty_with_rbv(dtype=float, doc="Shutter Close Delay", value=0.004)


def main():
    """Console script for fastccd_support_ioc."""

    ioc_options, run_options = ioc_arg_parser(
        default_prefix='XF:7011:ShutterDelayGenerator:',
        desc=dedent(DelayGenerator.__doc__))
    ioc = DelayGenerator(**ioc_options)

    logger.info('\n'.join(["\nAuto-generated Ophyd device for this PVGroup",
                "#" * 80,
                str(conversion.group_to_device(ioc)),
                "#" * 80]))

    run(ioc.pvdb, **run_options)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
