from caproto.server import PVGroup, get_pv_pair_wrapper, conversion
import subprocess
from textwrap import dedent
import sys
from caproto.server import ioc_arg_parser, run


def ibterm(command, caster=None):
    command = f'/bin/bash -c "ibterm -d 15 <<< \\\"{command}\\\""'
    stdout = subprocess.check_output(command, shell=True)
    if caster:
        return caster(stdout.decode().split("\n")[2].strip("ibterm>"))


pvproperty_with_rbv = get_pv_pair_wrapper(setpoint_suffix='',
                                          readback_suffix='_RBV')


class DelayGenerator(PVGroup):
    """
    An IOC for the [something something] delay generator.
    """

    trigger_rate = pvproperty_with_rbv(dtype=float, doc="TriggerRate")
    trigger_mode = pvproperty_with_rbv(dtype=int, doc="TriggerMode")
    delay_time = pvproperty_with_rbv(type=float, doc="DelayTime")
    shutter_time =  pvproperty_with_rbv(type=float, doc="ShutterTime")

    # trigger_mode = pvproperty_with_rbv("TriggerMode")
    # trigger_enabled = pvproperty_with_rbv("TriggerEnabled")

    @trigger_rate.setpoint.putter
    async def trigger_rate(obj, instance, rate):
        ibterm(f"tr 0,{rate}")
        # await obj.readback.write(value)

    @trigger_rate.readback.getter
    async def trigger_rate(obj, instance):
        return ibterm(f"tr 0", float)

    @trigger_mode.setpoint.putter
    async def trigger_mode(obj, instance, mode):
        "TriggerMode = 0 is int, TriggerMode 2 is SS = Single-Shot trigger"
        ibterm(f"tm ,{mode}")

    @trigger_mode.setpoint.getter
    async def trigger_mode(obj, instance):
        ibterm(f"tm")

    @delay_time.setpoint.putter
    async def delay_time(obj, instance, sec ):
        ibterm(f"dt 2,1,{sec}")

    @delay_time.setpoint.getter
    async def delay_time(obj, instance):
        ibterm(f"dt 2")

    @shutter_time.setpoint.putter
    async def shutter_time(obj, instance, sec ):
        ibterm(f"dt 3,2,{sec}")

    @shutter_time.setpoint.getter
    async def shutter_time(obj, instance):
        ibterm(f"dt 2")


def main():
    """Console script for fastccd_support_ioc."""

    ioc_options, run_options = ioc_arg_parser(
        default_prefix='XF:7011:',
        desc=dedent(DelayGenerator.__doc__))
    ioc = DelayGenerator(**ioc_options)

    print("#" * 80, conversion.group_to_device(ioc), "#" * 80, sep='\n')

    run(ioc.pvdb, **run_options)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
