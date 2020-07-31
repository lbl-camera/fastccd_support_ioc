from caproto.server import PVGroup, pvproperty
from caproto import ChannelType
from . import utils


class FCCDSupport(PVGroup):
    """
    An IOC with three uncoupled read/writable PVs

    Scalar PVs
    ----------
    A (int)
    B (float)

    Vectors PVs
    -----------
    C (vector of int)
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

    initialize = pvproperty(value=0, dtype=int)
    shutdown = pvproperty(value=0, dtype=int, put=fccd_shutdown)
