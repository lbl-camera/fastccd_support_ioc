from caproto.server import PVGroup, pvproperty
from caproto import ChannelType
from . import utils
from textwrap import dedent
import sys
from caproto.server import ioc_arg_parser, run


class FCCDSupport(PVGroup):
    """
    A support IOC to initialize, shutdown, and configure the ALS FastCCD; complements ADFastCCD
    """

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


def main():
    """Console script for fastccd_support_ioc."""

    ioc_options, run_options = ioc_arg_parser(
        default_prefix='XF:7011:',
        desc=dedent(FCCDSupport.__doc__))
    ioc = FCCDSupport(**ioc_options)
    run(ioc.pvdb, **run_options)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
