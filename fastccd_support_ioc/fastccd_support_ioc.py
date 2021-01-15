import subprocess
from caproto.server import PVGroup, pvproperty, get_pv_pair_wrapper
from caproto import ChannelType
from fastccd_support_ioc.utils.protection_checks import check_FOPS

from . import utils
from textwrap import dedent
import sys
from caproto.server import ioc_arg_parser, run
from caproto.sync.client import write, read
from caproto.asyncio.client import Context
from caproto._utils import CaprotoTimeoutError

pvproperty_with_rbv = get_pv_pair_wrapper(setpoint_suffix='',
                                          readback_suffix='_RBV')

DEFAULT_ACQUIRETIME = 1
DEFAULT_ACQUIREPERIOD = 1.1


class FCCDSupport(PVGroup):
    """
    A support IOC to initialize, shutdown, and configure the ALS FastCCD; complements ADFastCCD
    """

    # ACQUIRE_POLL_PERIOD = 0.1

    def __init__(self, *args, camera_prefix, shutter_prefix, hdf5_prefix, **kwargs):
        self.camera_prefix = camera_prefix
        self.shutter_prefix = shutter_prefix
        self.hdf5_prefix = hdf5_prefix
        self._capture_goal = 0
        self._active_subprocess = None
        self._subprocess_completion_state = None
        super(FCCDSupport, self).__init__(*args, **kwargs)

    async def fccd_shutdown(self, instance, value):
        # Note: all the fccd scripts are injected into the utils module; you can call them like so:

        print("shutting down")
        await self.State.write("Shutting Down...")

    async def fccd_initialize(self, instance, value):
        print("initializing")
        await self.State.write("Initializing...")

    async def _fccd_initialize(self, instance, value):
        # utils.scripts.fccd_auto_start()
        if self._active_subprocess:
            raise RuntimeError('Another background process is still running.')
        self._active_subprocess = utils.scripts.cosmic_fccd_auto_start()
        self._subprocess_completion_state = "Initialized"

    async def _fccd_shutdown(self, instance, value):
        if self._active_subprocess:
            raise RuntimeError('Another background process is still running.')
        self._active_subprocess = utils.scripts.auto_power_down_script()
        self._subprocess_completion_state = "Off"

    State = pvproperty(dtype=ChannelType.ENUM,
                       enum_strings=["Unknown", "Initialized", "Initializing...", "Shutting Down...", "Off", ],
                       value="Unknown")

    @State.startup
    async def State(self, instance, async_lib):

        self._context = Context()

        self.pv, = await self._context.get_pvs(self.hdf5_prefix + 'NumCaptured_RBV')

        self.sub = self.pv.subscribe(data_type=ChannelType.INT)

        self.sub.add_callback(self.check_finished)

    async def check_finished(self, pv, response):
        # todo: make sure this is a falling edge
        print('data:', response.data[0])

        if response.data[0] == self._capture_goal:
            print('finished!')
            await self.AdjustedAcquire.write(0)

    @State.getter
    async def State(self, instance):
        return instance.value

    @State.putter
    async def State(self, instance, value):
        # if value != instance.value:
        #     print("setting state:", value)

        if value == "Initializing...":
            await self._fccd_initialize(None, None)

        elif value == "Shutting Down...":
            await self._fccd_shutdown(None, None)

        return value

    #
    # @State.scan(period=1)
    # async def State(self, instance, async_lib):
    #     if not check_FOPS() and instance.value == "Initialized": # we can check any state here; if any of them go down during init, all of them go down
    #         await instance.write("Off")

    Initialize = pvproperty(value=0, dtype=int, put=fccd_initialize)
    Shutdown = pvproperty(value=0, dtype=int, put=fccd_shutdown)

    AdjustedAcquireTime = pvproperty_with_rbv(value=DEFAULT_ACQUIRETIME, dtype=float,
                                              cls_kwargs={'precision': 3, 'units': 's'})
    AdjustedAcquirePeriod = pvproperty_with_rbv(value=DEFAULT_ACQUIREPERIOD, dtype=float,
                                                cls_kwargs={'precision': 3, 'units': 's'})
    AdjustedAcquire = pvproperty(value=0, dtype=int)

    @AdjustedAcquire.startup
    async def AdjustedAcquire(self, instance, async_lib):
        # write to Acquire to start the camera up in tv mode
        write(self.camera_prefix + 'Acquire', [1])

    @AdjustedAcquire.putter
    async def AdjustedAcquire(self, instance, value):
        self._capture_goal = read(self.hdf5_prefix + 'NumCapture').data
        # write(self.shutter_prefix + 'TriggerEnabled', [int(value)])
        # write(self.hdf5_prefix + 'Capture', [value])
        print(f'comparing: {value} {instance.value}')
        if value != instance.value:
            write(self.camera_prefix + 'Acquire', [0])
            # import time
            # time.sleep(1)
            write(self.camera_prefix + 'Acquire', [1])
            # time.sleep(1)
        return value

    @AdjustedAcquireTime.setpoint.putter
    async def AdjustedAcquireTime(self, instance, value):
        open_delay = read(self.parent.shutter_prefix + 'ShutterOpenDelay_RBV').data
        close_delay = read(self.parent.shutter_prefix + 'ShutterCloseDelay_RBV').data

        if not open_delay + value + close_delay <= self.parent.AdjustedAcquirePeriod.readback.value:
            await self.parent.AdjustedAcquirePeriod.setpoint.write(open_delay + value + close_delay)

        write(self.parent.camera_prefix + 'AcquireTime', value + close_delay + open_delay)
        write(self.parent.shutter_prefix + 'ShutterTime', value + open_delay)

        await self.readback.write(value)
        return value

    @AdjustedAcquirePeriod.setpoint.putter
    async def AdjustedAcquirePeriod(self, instance, value):
        readout_time = self.parent.ReadoutTime.value
        open_delay = read(self.parent.shutter_prefix + 'ShutterOpenDelay_RBV').data
        close_delay = read(self.parent.shutter_prefix + 'ShutterCloseDelay_RBV').data

        if not value - open_delay - close_delay >= self.parent.AdjustedAcquireTime.readback.value:
            await self.parent.AdjustedAcquireTime.setpoint.write(value - open_delay - close_delay)

        write(self.parent.camera_prefix + 'AcquirePeriod', value)
        write(self.parent.shutter_prefix + 'TriggerRate', 1. / value)

        await self.readback.write(value)
        return value

    @Initialize.scan(period=1)
    async def Initialize(self, instance, async_lib):
        if self._active_subprocess:
            print(f'checking subprocess: {self._active_subprocess}')
            return_code = self._active_subprocess.poll()
            if return_code is not None:
                self._active_subprocess = None
                completion_state = self._subprocess_completion_state
                self._subprocess_completion_state = None
                if return_code == 0:
                    print('Successful background process')
                    await self.State.write(completion_state)
                    await self.State.startup(None, None)
                elif return_code > 0:
                    await self.State.write('Off')

    ReadoutTime = pvproperty(dtype=float, value=.080)


def main():
    """Console script for fastccd_support_ioc."""

    ioc_options, run_options = ioc_arg_parser(
        default_prefix='ES7011:FastCCD:cam1:',
        desc=dedent(FCCDSupport.__doc__))
    ioc = FCCDSupport(camera_prefix='ES7011:FastCCD:cam1:',
                      shutter_prefix='ES7011:ShutterDelayGenerator:',
                      hdf5_prefix='ES7011:FastCCD:HDF1:',
                      **ioc_options)
    run(ioc.pvdb, **run_options)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
