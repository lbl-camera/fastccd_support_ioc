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

    # trigger_mode = pvproperty_with_rbv("TriggerMode")
    # trigger_enabled = pvproperty_with_rbv("TriggerEnabled")

    @trigger_rate.setpoint.putter
    async def trigger_rate(obj, instance, value):
        ibterm(f"tr 0,{value}")
        # await obj.readback.write(value)

    @trigger_rate.readback.getter
    async def trigger_rate(obj, instance):
        return ibterm(f"tr 0", float)


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
