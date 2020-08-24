from caproto.server import PVGroup, pvproperty
from caproto import ChannelType
from . import utils
from textwrap import dedent
import sys
from caproto.server import ioc_arg_parser, run
from caproto.sync.client import write, read


class FCCDSupport(PVGroup):
    """
    Support IOC for LBL FastCCD
    """

    def __init__(self, *args, camera_prefix, shutter_prefix, **kwargs):
        self.camera_prefix = camera_prefix
        self.shutter_prefix = shutter_prefix
        super(FCCDSupport, self).__init__(*args, **kwargs)

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

    acquire_time = pvproperty(value=0, dtype=int)
    acquire_period = pvproperty(value=0, dtype=int)

    @acquire_time.putter
    async def acquire_time(self, instance, value):
        open_delay = read(self.shutter_prefix + 'shutter_open_delay_RBV')
        close_delay = read(self.shutter_prefix + 'shutter_close_delay_RBV')
        write(self.camera_prefix + 'cam1:AcquireTime', value + open_delay + close_delay)
        write(self.shutter_prefix + 'shutter_time', value + open_delay)
        return value

    @acquire_period.putter
    async def acquire_period(self, instance, value):
        readout_time = self.readout_time.value

        assert value + readout_time >= self.acquire_time.value

        write(self.camera_prefix + 'cam1:AcquirePeriod', value)
        write(self.shutter_prefix + 'trigger_rate', value)
        return value

    readout_time = pvproperty(dtype=float, value=.080)


def main():
    """Console script for fastccd_support_ioc."""

    ioc_options, run_options = ioc_arg_parser(
        default_prefix='XF:7011:',
        desc=dedent(FCCDSupport.__doc__))
    ioc = FCCDSupport(camera_prefix='ALS:701:', shutter_prefix='XF:7011:ShutterDelayGenerator:', **ioc_options)
    run(ioc.pvdb, **run_options)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
