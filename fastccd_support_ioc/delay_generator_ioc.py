import subprocess
from textwrap import dedent
import sys
from caproto.server import PVGroup, conversion, pvproperty, SubGroup, ioc_arg_parser, run
from caproto import ChannelType
import logging

from . import wrap_autosave, pvproperty_with_rbv, FastAutosaveHelper

logger = logging.getLogger('caproto')

# TODO: rename PVs to compliant convention
# TODO: decide on PV naming convention
# TODO: add docs to PVs

shutter_states = {'TRIGGER': 0, 'OPEN': 1, 'CLOSED': 2}

ibterm_lock = None


async def ibterm_read(command, caster=None):
    command = f'/bin/bash -c "ibterm -d 15 <<< \\\"{command}\\\""'
    logger.debug(f'exec: {command}')
    print(f'exec: {command}')

    for i in range(100):
        try:
            async with ibterm_lock:
                stdout = subprocess.check_output(command, shell=True)
            if caster:
                value_string = stdout.decode().split("\n")[2].strip("ibterm>").split(",")[-1]
                logger.debug(f'casting value: {value_string}')
                print(f'casting value: {value_string}')
                return caster(value_string)
            else:
                break
        except ValueError:
            print(f'Failed to cast value using {caster}, retrying attempt {i}: {value_string}')
    else:
        raise ConnectionError('Failed to cast value 100 times.')


ibterm = ibterm_read


async def ibterm_write(command, value, caster=None, confirm=True):
    await ibterm_read(f'{command},{value}', caster)
    if not confirm:
        return
    for i in range(100):
        if value == await ibterm_read(f'{command}', caster or type(value)):
            break
    else:
        raise ConnectionError('Failed to cast value 100 times.')


INITIAL_TRIGGER_RATE = 5
SHUTTER_OUTPUT_AMPLITUDE = 3.3


class DelayGenerator(PVGroup):
    """
    An IOC for the [something something] delay generator.
    """

    autosave_helper = SubGroup(FastAutosaveHelper)

    TriggerRate = wrap_autosave(pvproperty_with_rbv(dtype=float, doc="TriggerRate", value=INITIAL_TRIGGER_RATE))
    TriggerEnabled = pvproperty_with_rbv(dtype=bool, doc="TriggerOnOFF", value=True)
    #ShutterEnabled = pvproperty_with_rbv(dtype=bool, doc="ShutterOnOFF", value=False)
    ShutterEnabled = pvproperty_with_rbv(dtype=ChannelType.ENUM, enum_strings=['TRIGGER', 'OPEN', 'CLOSED'], doc="ShutterState", value='TRIGGER')
    ShutterOpenDelay = wrap_autosave(pvproperty_with_rbv(dtype=float, doc="DelayTime", value=0.0035))
    ShutterTime = wrap_autosave(pvproperty_with_rbv(dtype=float, doc="ShutterTime"))

    @TriggerRate.setpoint.putter
    async def TriggerRate(obj, instance, value):
        await ibterm_write(f"tr 0", value)

    @TriggerRate.readback.getter
    async def TriggerRate(obj, instance):
        return ibterm_read(f"tr 0", float)

    @TriggerEnabled.setpoint.putter
    async def TriggerEnabled(obj, instance, on):
        logger.debug(f'setting triggering: {on}')
        if on=='On':
            await ibterm(f"tm 0")
        else:
            await ibterm(f"tm 2")

    @TriggerEnabled.readback.getter
    async def TriggerEnabled(obj, instance):
        return await ibterm_read(f"tm", bool)

    #@ShutterEnabled.setpoint.putter
    #async def ShutterEnabled(obj, instance, on):
        #logger.debug(f'setting triggering: {on}')
        #if on == 'On':
            #ibterm(f"OM 4,0; OA 4,.1")
        #else:
            #ibterm(f"OM 4,3")

    @ShutterEnabled.setpoint.putter
    async def ShutterEnabled(obj, instance, on):
        on = on.upper()
        print(f"Setting ShutterEnabled state: {on}")
        logger.debug(f'setting triggering: {on}')
        if on == 'TRIGGER':
            await ibterm_write('OM 4', 0)
            await ibterm_write('OA 4', SHUTTER_OUTPUT_AMPLITUDE)
            await ibterm_write('OO 4', 0)
        elif on == 'OPEN':
            await ibterm_write('OM 4', 3)
            await ibterm_write('OA 4', .1)
            await ibterm_write('OO 4', SHUTTER_OUTPUT_AMPLITUDE)
        elif on == 'CLOSED':
            await ibterm_write('OM 4', 3)
            await ibterm_write('OA 4', .1)
            await ibterm_write('OO 4', 0)
        else:
            msg = "Shutter state {on.upper()} not valid; use TRIGGER, OPEN, or CLOSED"
            #raise ValueError(msg)
            print(msg)
            logger.debug(msg)
        await obj.readback.write(shutter_states[on])

    @ShutterEnabled.readback.getter
    async def ShutterEnabled(obj, instance):
        mode = await ibterm_read(f"OM 4", float)
        amplitude = await ibterm_read(f"OA 4", float)
        offset = await ibterm_read(f"OO 4", float)

        print(mode, amplitude, offset)

        if mode == 0:
            return 0  # 'TRIGGER'
        elif mode == 3:
            if offset == 0:
                return 2  # 'CLOSED'
            else:
                return 1  # 'OPEN'
        else:
            raise ValueError("Invalid shutter state has been set.")

    #@ShutterEnabled.readback.getter
    #async def ShutterEnabled(obj, instance):
        #return ibterm(f"OM 4", float) == 0

    # @ShutterOpenDelay.setpoint.putter
    # async def ShutterOpenDelay(obj, instance, delay):
    #     ibterm(f"dt 2,1,{delay}")

    # @ShutterOpenDelay.readback.getter
    # async def ShutterOpenDelay(obj, instance):
    #     return ibterm(f"dt 2", float)

    @ShutterTime.setpoint.putter
    async def ShutterTime(obj, instance, shutter_time):
        if shutter_time < obj.parent.ShutterOpenDelay.readback.value + obj.parent.ShutterCloseDelay.readback.value:
            raise ValueError("Shutter time cannot be less than the time it takes to open AND close the shutter (less than 0 exposure time).")
        await ibterm(f"dt 3,1,{shutter_time}")

    @ShutterTime.readback.getter
    async def ShutterTime(obj, instance):
        return await ibterm(f"dt 3", float) - obj.ShutterCloseDelay.readback.value

    State = pvproperty(dtype=ChannelType.ENUM, enum_strings=["Unknown", "Initialized", "Uninitialized", ])

    async def initialize(self, instance, value):
        await self.State.write('Initialized')

    async def reset(self, instance, value):
        await self.State.write('Uninitialized')

    async def _initialize(self, instance, value):
        # Channels
        # 1 - T0 - (DEPRECATED, now timing only) Camera Trigger
        # 2 - A (for timing purposes)
        # 3 - B Shutter pulse
        # 4 - A & B - Shutter (physical connection)
        # 5 - A | B
        # 6 - C (?) Camera Trigger

        # clear and setup various parameters
        await ibterm('CL')  # Clear
        await ibterm('DT 2,1,0')  # Set 2 to trigger 1ms off of 1
        await ibterm('DT 3,2,140E-3')  # Set 3 to trigger 140ms off of 2
        await ibterm('TZ 1,1')  # Impedance
        await ibterm('TZ 4,1')  # Impedance
        await ibterm('OM 4,0')  # Set 4 to TTL
        await ibterm('OM 1,3')  # Set 1 to Variable
        await ibterm_write('OA 1', SHUTTER_OUTPUT_AMPLITUDE)  # Voltage
        await ibterm('OO 1,0')  # Offset
        await ibterm_write('TR 0', INITIAL_TRIGGER_RATE)  # Set trigger rate
        await ibterm('TM 0')

    async def _reset(self, instance, value):
        # only clear device
        await ibterm(f"CL")

    @State.startup
    async def State(self, instance, async_lib):
        global ibterm_lock
        ibterm_lock = async_lib.library.locks.Lock()
        await self.State.write('Initialized')

    @State.getter
    async def State(self, instance):
        return instance.value

    @State.putter
    async def State(self, instance, value):
        if value != instance.value:
            print("setting state:", value)
            logger.debug("setting state:", value)

            if value == "Initialized":
                await self._initialize(None, None)

            elif value == "Uninitialized":
                await self._reset(None, None)

        return value

    Initialize = pvproperty(value=0, dtype=int, put=initialize)
    Reset = pvproperty(value=0, dtype=int, put=reset)

    @State.shutdown
    async def State(self, instance, async_lib):
        await self.State.write('Uninitialized')

    ShutterCloseDelay = wrap_autosave(pvproperty_with_rbv(dtype=float, doc="Shutter Close Delay", value=0.004))


def main():
    """Console script for fastccd_support_ioc."""

    ioc_options, run_options = ioc_arg_parser(
        default_prefix='ES7011:ShutterDelayGenerator:',
        desc=dedent(DelayGenerator.__doc__))
    ioc = DelayGenerator(**ioc_options)

    logger.info('\n'.join(["\nAuto-generated Ophyd device for this PVGroup",
                "#" * 80,
                str(conversion.group_to_device(ioc)),
                "#" * 80]))

    run(ioc.pvdb, **run_options)

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover

