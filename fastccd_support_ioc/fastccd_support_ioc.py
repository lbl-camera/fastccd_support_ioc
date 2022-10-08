from caproto.server import PVGroup, SubGroup, pvproperty, get_pv_pair_wrapper
from caproto import ChannelType

from textwrap import dedent
import sys
from caproto.server import ioc_arg_parser, run
from caproto.sync.client import write, read
from caproto.asyncio.client import Context, PV
from pip._internal import main
main(['install', 'loguru'])
from loguru import logger

from . import utils, pvproperty_with_rbv, wrap_autosave, FastAutosaveHelper
from .utils.protection_checks import power_check_no_bias_clocks, power_check_with_bias_clocks
from .utils.cin_functions import ReadReg
from .cin.shutter import set_shutter_time_s

DEFAULT_ACQUIRETIME = 1
DEFAULT_ACQUIREPERIOD = 1.1

async def read(pv):
    if isinstance(pv, PV):
        return (await pv.read()).data[0]
    else:
        return (await pv.read(pv.pvspec.dtype))[1][0]


class FCCDSupport(PVGroup):
    """
    A support IOC to initialize, shutdown, and configure the ALS FastCCD; complements ADFastCCD
    """

    # ACQUIRE_POLL_PERIOD = 0.1

    def __init__(self, *args, camera_prefix, shutter_prefix, hdf5_prefix, **kwargs):
        self.camera_prefix = camera_prefix
        self.shutter_prefix = shutter_prefix
        self.hdf5_prefix = hdf5_prefix
        super(FCCDSupport, self).__init__(*args, **kwargs)

    @SubGroup(prefix='shutter:')
    class Shutter(PVGroup):
        shutter_enabled = pvproperty(name='shutter_enabled', dtype=ChannelType.ENUM, enum_strings=['TRIGGER', 'OPEN', 'CLOSED'], )

        @shutter_enabled.putter
        async def shutter_enabled(self, instance, value):
            value = value.upper()
            logger.debug(f'setting shutter_enabled state: {value}')
            if value == 'TRIGGER':
                await self.parent.Cam.adjusted_acquire_time.write(self.parent.Cam.adjusted_acquire_time.value)  # re-write current value to update shutter
            elif value == 'CLOSED':
                await self.parent.Cam.adjusted_acquire_time.write(self.parent.Cam.adjusted_acquire_time.value)  # re-write current value to update shutter
            elif value == 'OPEN':
                raise NotImplementedError()

    @SubGroup(prefix='cam1:')
    class Cam(PVGroup):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.capture_pv = None
            self.acquire_pv = None
            self.acquire_rbv_pv = None
            self._active_subprocess = None
            self._subprocess_completion_state = None
            self.A_temp_pv = None
            self.B_temp_pv = None

        startup = pvproperty(name='startup', dtype=ChannelType.INT)

        @startup.startup
        async def startup(self, instance, async_lib):
            self._context = Context()
            self.acquire_rbv_pv, = await self._context.get_pvs(self.prefix + 'Acquire_RBV')
            self.acquire_pv, = await self._context.get_pvs(self.prefix + 'Acquire')
            self.capture_pv, = await self._context.get_pvs(self.parent.prefix + 'HDF1:Capture_RBV')
            self.mode_pv, = await self._context.get_pvs(self.prefix + 'ImageMode')
            self.acquire_rbv_sub = self.acquire_rbv_pv.subscribe(data_type=ChannelType.INT)
            self.acquire_rbv_sub.add_callback(self.acquire_finished)
            self.A_temp_pv, = await self._context.get_pvs(self.parent.prefix + 'TemperatureCelsiusA')
            self.B_temp_pv, = await self._context.get_pvs(self.parent.prefix + 'TemperatureCelsiusB')


        async def fccd_shutdown(self, instance, value):
            # Note: all the fccd scripts are injected into the utils module; you can call them like so:

            logger.info("shutting down")
            await self.State.write("Shutting Down...")

        async def fccd_initialize(self, instance, value):
            logger.info("initializing")
            await self.State.write("Initializing...")

        async def _fccd_initialize(self, instance, value):
            # utils.scripts.fccd_auto_start()
            if self._active_subprocess:
                raise RuntimeError('Another background process is still running.')
            self._active_subprocess = utils.scripts.cosmic_fccd_auto_start(str(self.TestFrameMode.value))
            self._subprocess_completion_state = "Initialized"

        async def _fccd_shutdown(self, instance, value):
            if self._active_subprocess:
                raise RuntimeError('Another background process is still running.')
            self._active_subprocess = utils.scripts.auto_power_down_script()
            self._subprocess_completion_state = "Off"

        State = pvproperty(dtype=ChannelType.ENUM,
                           enum_strings=["Unknown", "Initialized", "Initializing...", "Shutting Down...", "Off", ],
                           value="Unknown")

        @State.getter
        async def State(self, instance):
            return instance.value

        @State.putter
        async def State(self, instance, value):
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

        autosave_helper = SubGroup(FastAutosaveHelper)

        Initialize = pvproperty(value=0, dtype=int, put=fccd_initialize)
        Shutdown = pvproperty(value=0, dtype=int, put=fccd_shutdown)

        adjusted_acquire_time = pvproperty(value=DEFAULT_ACQUIRETIME, dtype=float,
                                                  precision=3, units='s')
        adjusted_acquire_period = pvproperty(value=DEFAULT_ACQUIREPERIOD, dtype=float,
                                                    precision=3, units='s')

        adjusted_acquire = pvproperty_with_rbv(value=0, dtype=int)
        adjusted_num_images = pvproperty(value=0, dtype=int)

        TestFrameMode = pvproperty(value=False, dtype=bool)

        async def acquire_finished(self, pv, response):
            if response.data[0] == 0:
                await self.adjusted_acquire.readback.write(0)
                await self.adjusted_acquire.setpoint.write(0)

        @adjusted_acquire.setpoint.putter
        async def adjusted_acquire(self, instance, value):
            await self.parent.acquire_pv.write(0, wait=False)
            if value:
                logger.debug('switching to acquire mode')
                await self.parent.mode_pv.write(1)
            await self.parent.acquire_pv.write(value, wait=False)

        @adjusted_acquire.readback.getter
        async def adjusted_acquire(self, instance):
            return await read(self.parent.acquire_rbv_pv)

        # @adjusted_acquire.readback.scan(period=2)
        # async def adjusted_acquire(self, instance, async_lib):
        @Shutdown.scan(period=2)
        async def Shutdown(self, instance, async_lib):  # TODO: find out how to associate this with adjusted_acquire.readback
            # if not acquiring or capturing
            if self.capture_pv and self.acquire_rbv_pv:
                capture = await read(self.capture_pv)
                acquire = await read(self.acquire_rbv_pv)
                logger.debug(f'capture, acquire = {capture}, {acquire}')
                if not capture and not acquire:
                    logger.info('switching to tv mode')
                    await self.mode_pv.write(2)
                    await self.acquire_pv.write(1, wait=False)

        @adjusted_num_images.putter
        async def adjusted_num_images(self, instance, value):
            write(self.parent.prefix + 'HDF1:NumCapture', value)
            write(self.parent.camera_prefix + 'NumImages', value)

        @adjusted_acquire_time.putter
        async def adjusted_acquire_time(self, instance, value):
            readout_time = self.readout_time.value
            open_delay = self.open_delay.value
            close_delay = self.close_delay.value

            if not open_delay + value + readout_time <= self.adjusted_acquire_period.value:  # NOTE: close_delay is not included here because it is done during exposure
                await self.adjusted_acquire_period.write(open_delay + value + readout_time)

            write(self.parent.camera_prefix + 'AcquireTime', value)  # TODO: change to async write

            shutter_enabled = self.parent.Shutter.shutter_enabled.value
            if shutter_enabled == 0:  # Trigger
                set_shutter_time_s(open_delay + value - close_delay)
            elif shutter_enabled == 1: # Open
                ...#?
            elif shutter_enabled == 2:
                set_shutter_time_s(0)

            return value

        @adjusted_acquire_period.putter
        async def adjusted_acquire_period(self, instance, value):
            readout_time = self.readout_time.value
            open_delay = self.open_delay.value
            close_delay = self.close_delay.value

            if not value - open_delay - readout_time >= self.adjusted_acquire_time.value:
                await self.adjusted_acquire_time.write(value - open_delay - readout_time)

            write(self.parent.camera_prefix + 'AcquirePeriod', value)

            # await self.write(value)
            return value

        @Initialize.scan(period=1)
        async def Initialize(self, instance, async_lib):
            needs_shutdown = False

            if self.A_temp_pv and self.B_temp_pv:
                A_temp = (await self.A_temp_pv.read()).data[0]
                B_temp = (await self.B_temp_pv.read()).data[0]
            else:
                A_temp = 999
                B_temp = 999

            if self.AutoStart.value == 'On' \
                and self.State.value in ['Off', 'Unknown'] \
                and not self._active_subprocess \
                and (B_temp < 0) and (A_temp < 0):
                await self.fccd_initialize(None, None)
            elif self.State.value == 'Initialized' and not self._active_subprocess and ((B_temp > 2) or (A_temp > 2)):
                logger.critical(f'Temps above operational threshold (2 C): {A_temp}, {B_temp}')
                needs_shutdown = True

            if self._active_subprocess:
                logger.debug(f'checking subprocess: {" ".join(self._active_subprocess.args)}')
                return_code = self._active_subprocess.poll()
                if return_code is not None:
                    completion_state = self._subprocess_completion_state
                    if return_code == 0:
                        logger.info(f'Successful background process: {" ".join(self._active_subprocess.args)}')
                        await self.State.write(completion_state)
                    elif return_code > 0:
                        error = self._active_subprocess.stderr.read().decode()
                        logger.error(error)
                        await self.ErrorStatus.write(error)
                        await self.ErrorStatus.write('')
                        needs_shutdown = True
                    self._active_subprocess = None
                    self._subprocess_completion_state = None

            if needs_shutdown:
                self._active_subprocess = None  # force dumping any running subprocess
                self._subprocess_completion_state = None
                await self.fccd_shutdown(None, None)

        readout_time = pvproperty(dtype=float, value=.050)
        open_delay = pvproperty(dtype=float, value=0.0035)
        close_delay = pvproperty(dtype=float, value=0.0035)

        ErrorStatus = pvproperty(dtype=str, value="", read_only=True)
        AutoStart = pvproperty(dtype=bool, value='Off')  # value='On')

        BiasState = pvproperty(dtype=ChannelType.ENUM,
                           enum_strings=["Unknown", "On", "Powering On...", "Powering Off...", "Off", ],
                           value="Unknown")

        @BiasState.startup
        async def BiasState(self, instance, async_lib):
            global com_lock
            self.async_lib = async_lib
            com_lock = async_lib.library.locks.Lock()

        @BiasState.putter
        async def BiasState(self, instance, value):
            if value != instance.value:
                logger.info(f"setting bias state: {value}")

                if value == "Powering On...":
                    value = await self._power_on_bias(None, None)

                elif value == "Powering Off...":
                    value = await self._power_off_bias(None, None)

            return value

        async def _power_on_bias(self, instance, value):
            async with com_lock:
                power_check_no_bias_clocks()
                utils.scripts.setClocksBiasOn()
                # wait longer than 3s - psu ioc scans every 3 seconds
                await self.async_lib.library.sleep(4)
                power_check_with_bias_clocks()
                logger.info(f"Powered On")
                return "On"

        async def _power_off_bias(self, instance, value):
            async with com_lock:
                utils.scripts.setClocksBiasOff()
                logger.info(f"Powered Off")
                return "Off"

        async def power_on_bias(self, instance, value):
            await self.BiasState.write('Powering On...')

        async def power_off_bias(self, instance, value):
            await self.BiasState.write('Powering Off...')

        BiasOn = pvproperty(value=0, dtype=int, put=power_on_bias)
        BiasOff = pvproperty(value=0, dtype=int, put=power_off_bias)


def main():
    """Console script for fastccd_support_ioc."""

    ioc_options, run_options = ioc_arg_parser(
        default_prefix='ES7011:FastCCD:',
        desc=dedent(FCCDSupport.__doc__))
    ioc = FCCDSupport(camera_prefix='ES7011:FastCCD:cam1:',
                      shutter_prefix='ES7011:ShutterDelayGenerator:',
                      hdf5_prefix='ES7011:FastCCD:HDF1:',
                      **ioc_options)
    run(ioc.pvdb, **run_options)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
