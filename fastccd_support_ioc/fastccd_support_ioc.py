from caproto.server import PVGroup, pvproperty, SubGroup, get_pv_pair_wrapper
from caproto import ChannelType
from . import utils
import subprocess


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


class FCCDSupport(PVGroup):

    async def fccd_shutdown(self, instance, value):
        # Note: all the fccd scripts are injected into the utils module; you can call them like so:

        print("shutting down")
        utils.scripts.auto_power_down_script()

    async def fccd_initialize(self, instance, value):
        print("initializing")
        utils.scripts.fccd_auto_start()

    state = pvproperty(dtype=ChannelType.ENUM, enum_strings=["unknown", "initialized", "off", ])

    @state.getter
    async def state(self, instance):
        return instance.value

    @state.putter
    async def state(self, instance, value):
        if value != instance.value:
            print("setting state:", value)

            if value == "initialized":
                await self.fccd_initialize(None, None)

            elif value == "off":
                await self.fccd_shutdown(None, None)

        return value

    initialize = pvproperty(value=0, dtype=int, put=fccd_initialize)
    shutdown = pvproperty(value=0, dtype=int, put=fccd_shutdown)


class SupportIOC(PVGroup):
    """
    A support IOC for the LBL FastCCD, including options to configure a delay generator for shuttering
    """

    delay_generator = SubGroup(DelayGenerator, prefix='DelayGenerator:')
    fastccd_support = SubGroup(FCCDSupport, prefix='FastCCD:')
