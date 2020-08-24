from caproto.server import PVGroup, pvproperty
from caproto import ChannelType
from . import utils
from textwrap import dedent
import sys
from caproto.server import ioc_arg_parser, run
from caproto.sync.client import write, read


class FCCDSupport(PVGroup):
    """
    A support IOC to initialize, shutdown, and configure the ALS FastCCD; complements ADFastCCD
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

    State = pvproperty(dtype=ChannelType.ENUM, enum_strings=["unknown", "initialized", "off", ])

    @State.getter
    async def State(self, instance):
        return instance.value

    @State.putter
    async def State(self, instance, value):
        if value != instance.value:
            print("setting state:", value)

            if value == "initialized":
                await self.fccd_initialize(None, None)

            elif value == "off":
                await self.fccd_shutdown(None, None)

        return value

    Initialize = pvproperty(value=0, dtype=int, put=fccd_initialize)
    Shutdown = pvproperty(value=0, dtype=int, put=fccd_shutdown)

    AcquireTime = pvproperty(value=0, dtype=int)
    AcquirePeriod = pvproperty(value=0, dtype=int)

    @AcquireTime.putter
    async def AcquireTime(self, instance, value):
        open_delay = read(self.shutter_prefix + 'ShutterOpenDelay_RBV').data
        close_delay = read(self.shutter_prefix + 'ShutterCloseDelay_RBV').data

        assert open_delay + value + close_delay <= self.AcquirePeriod.value

        write(self.camera_prefix + 'cam1:AcquireTime', value + open_delay + close_delay)
        write(self.shutter_prefix + 'ShutterTime', value + open_delay)
        return value

    @AcquirePeriod.putter
    async def AcquirePeriod(self, instance, value):
        readout_time = self.readout_time.value

        assert value + readout_time >= self.AcquireTime.value

        write(self.camera_prefix + 'cam1:AcquirePeriod', value)
        write(self.shutter_prefix + 'TriggerRate', value)
        return value

    ReadoutTime = pvproperty(dtype=float, value=.080)


def main():
    """Console script for fastccd_support_ioc."""

    ioc_options, run_options = ioc_arg_parser(
        default_prefix='ES7011:FastCCD',
        desc=dedent(FCCDSupport.__doc__))
    ioc = FCCDSupport(camera_prefix='ES7011:FastCCD', shutter_prefix='ES7011:ShutterDelayGenerator:', **ioc_options)
    run(ioc.pvdb, **run_options)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
