from caproto.server import PVGroup, get_pv_pair_wrapper, conversion, pvproperty
import subprocess
from textwrap import dedent
import sys
from caproto.server import ioc_arg_parser, run


def ibterm(command, caster=None):
    command = f'/bin/bash -c "ibterm -d 15 <<< \\\"{command}\\\""'
    stdout = subprocess.check_output(command, shell=True)
    if caster:
        try:
            return caster(stdout.decode().split("\n")[2].strip("ibterm>"))
        except ValueError:
            return caster(stdout.decode().split("\n")[2].strip("ibterm>").split(",")[-1])
        # except ValueError:
        #     return caster(stdout.decode().split("\n")[2].strip("ibterm>2,"))

pvproperty_with_rbv = get_pv_pair_wrapper(setpoint_suffix='',
                                          readback_suffix='_RBV')


class DelayGenerator(PVGroup):
    """
    An IOC for the [something something] delay generator.
    """

    trigger_rate = pvproperty_with_rbv(dtype=float, doc="TriggerRate")
    # trigger_on_off = pvproperty_with_rbv(dtype=bool, doc="TriggerOnOFF")
    # delay_time = pvproperty_with_rbv(dtype=float, doc="DelayTime")
    # shutter_time =  pvproperty_with_rbv(dtype=float, doc="ShutterTime")

    #additional PVs only used for setup
    # setup = pvproperty(dtype=float, doc="Setup")
    #output_offset = pvproperty_with_rbv(dtype=int, doc="OutputOffset")


    # @setup.setpoint.putter
    # async def setup(obj, instance):
    #     ibterm(f"CL; DT 2,1,1E-3; DT 3,2,140E-3; TZ 1,1; TZ 4,1; OM 4,0; OM 1,3; OA 1,3.3; OO 1,0; TR 0,5")


    @trigger_rate.setpoint.putter
    async def trigger_rate(obj, instance, rate):
        ibterm(f"tr 0,{rate}")
        # await obj.readback.write(value)

    @trigger_rate.readback.getter
    async def trigger_rate(obj, instance):
        return ibterm(f"tr 0", float)

    # @trigger_on_off.setpoint.putter
    # async def trigger_on_off(obj, instance, boolean):
    #     if boolean == 0:
    #         ibterm(f"tm 2")
    #     if boolean == 1:
    #         ibterm(f"tm 0")
    #     # await obj.readback.write(value)
    #
    # @trigger_on_off.readback.getter
    # async def trigger_on_off(obj, instance):
    #     return ibterm(f"tm", int)
    #
    # @delay_time.setpoint.putter
    # async def delay_time(obj, instance, rate):
    #     ibterm(f"dt 2,1,{rate}")
    #     # await obj.readback.write(value)
    #
    # @delay_time.readback.getter
    # async def delay_time(obj, instance):
    #     return ibterm(f"dt 2", float)
    #
    # @shutter_time.setpoint.putter
    # async def shutter_time(obj, instance, rate):
    #     ibterm(f"dt 3,2,{rate}")
    #     # await obj.readback.write(value)
    #
    # @shutter_time.readback.getter
    # async def shutter_time(obj, instance):
    #     return ibterm(f"dt 3", float)


    #additional PVs only used for setup
    # @output_offset.setpoint.putter
    # async def output_offset(obj, instance, offset):
    #     ibterm(f"oo 1,{offset}")
    #     # await obj.readback.write(value)
    #
    # @output_offset.readback.getter
    # async def output_offset(obj, instance):
    #     return ibterm(f"oo 1", int)



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
