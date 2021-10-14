import sys
import string
import time
import socket

from fastccd_support_ioc.utils.cin_functions import WriteReg, ReadReg
from fastccd_support_ioc.utils.cin_register_map import REG_COMMAND, REG_READ_ADDRESS, \
    REG_BIASANDCLOCKREGISTERADDRESS_REG, REG_BIASREGISTERDATAOUT_REG
from caproto.sync.client import read


def temp_check():
    if read('ES7011:FastCCD:TemperatureCelsiusA').data[0] > 0. or read('ES7011:FastCCD:TemperatureCelsiusB').data[
        0] > 0.:
        raise AssertionError('Camera is not cold enough to power on completely (< 0 C)')


def check_FOPS(VOLTAGE_MARGIN=.2) -> bool:
    # ============================================================================
    #               System Constants
    # ============================================================================
    E36102A_IP = "192.168.1.3"
    E36102A_PORT = 5025

    try:

        # Create a socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(3)
        s.connect((E36102A_IP, E36102A_PORT))

        # Clear Communications
        s.sendall(b'*CLS\r\n')
        # Wait at least 50ms before sending next command
        time.sleep(0.1)

        # print "FastCCD FO Power Supply Monitor"
        s.sendall(b'MEAS:VOLT?')
        v = s.recv(16)
        s.sendall(b'MEAS:CURR?')
        i = s.recv(16)
        # print v
        voltage = float(v)
        if (voltage < 0.01): voltage = 0.000

        # print i
        current = float(i)
        if (current < 0.01): current = 0.000

        if not _within_range(voltage, 4.5):
            return False

    except Exception as ex:
        print(ex)
        return False

    return True


def check_camera_power(VOLTAGE_MARGIN=.2) -> bool:
    import sys
    import socket
    import string
    import time

    # ============================================================================
    #               System Constants
    # ============================================================================
    # Setup the Keithley 2701 DMM
    DMM2701_IP = "192.168.1.47"
    DMM2701_PORT = 1394

    # Create a socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(3)
    s.connect((DMM2701_IP, DMM2701_PORT))

    # Configure DMM
    # s.sendall("RST;FORM:ELEM READ\r\n")
    # Setup Channel List (@101:106) Voltage Chans, (@109:114) Current Chans
    # Scan & Readout Channels one at a time

    # print("\nFastCCD Power Monitor")

    s.sendall(b'MEAS:VOLT? (@101)\r\n')
    v = s.recv(1024).decode()
    tv = float(v[0] + v[1] + v[2] + v[3] + v[4] + v[5] + v[11] + v[12] + v[13] + v[14])
    s.sendall(b'MEAS:VOLT? (@109)\r\n')
    a = s.recv(1024).decode()
    ta = float(a[1] + a[2] + a[3] + a[4] + a[10] + a[11] + a[12] + a[13] + a[14]) * 100
    if (tv < 0.05): tv = 0
    if (ta < 0.001): ta = 0
    # print("A04V : " + str(tv) + "V @ " + str(ta)[:6] + "A")
    if not _within_range(tv, 4):
        return False

    s.sendall(b'MEAS:VOLT? (@103)\r\n')
    v = s.recv(1024).decode()
    tv = float(v[0] + v[1] + v[2] + v[3] + v[4] + v[5] + v[11] + v[12] + v[13] + v[14])
    s.sendall(b'MEAS:VOLT? (@111)\r\n')
    a = s.recv(1024).decode()
    ta = float(a[1] + a[2] + a[3] + a[4] + a[10] + a[11] + a[12] + a[13] + a[14]) * 100
    if (tv < 0.05): tv = 0
    if (ta < 0.001): ta = 0
    # print("A15V : " + str(tv) + "V @ " + str(ta)[:6] + "A")
    if not _within_range(tv, 15):
        return False

    s.sendall(b'MEAS:VOLT? (@104)\r\n')
    v = s.recv(1024).decode()
    tv = float(v[0] + v[1] + v[2] + v[3] + v[4] + v[5] + v[11] + v[12] + v[13] + v[14])
    s.sendall(b'MEAS:VOLT? (@112)\r\n')
    a = s.recv(1024).decode()
    ta = float(a[1] + a[2] + a[3] + a[4] + a[10] + a[11] + a[12] + a[13] + a[14]) * 100
    if (tv < 0.05): tv = 0
    if (ta < 0.001): ta = 0
    # print("B15V : " + str(tv) + "V @ " + str(ta)[:6] + "A")
    if not _within_range(tv, 15):
        return False

    s.sendall(b'MEAS:VOLT? (@105)\r\n')
    v = s.recv(1024).decode()
    tv = float(v[0] + v[1] + v[2] + v[3] + v[4] + v[5] + v[11] + v[12] + v[13] + v[14])
    s.sendall(b'MEAS:VOLT? (@113)\r\n')
    a = s.recv(1024).decode()
    ta = float(a[1] + a[2] + a[3] + a[4] + a[10] + a[11] + a[12] + a[13] + a[14]) * 100
    if (tv < 0.05): tv = 0
    if (ta < 0.001): ta = 0
    # print("A30V : " + str(tv) + "V @ " + str(ta)[:6] + "A")
    if not _within_range(tv, 30):
        return False

    s.sendall(b'MEAS:VOLT? (@106)\r\n')
    v = s.recv(1024).decode()
    tv = float(v[0] + v[1] + v[2] + v[3] + v[4] + v[5] + v[11] + v[12] + v[13] + v[14])
    s.sendall(b'MEAS:VOLT? (@114)\r\n')
    a = s.recv(1024).decode()
    ta = float(a[1] + a[2] + a[3] + a[4] + a[10] + a[11] + a[12] + a[13] + a[14]) * 100
    if (tv < 0.05): tv = 0
    if (ta < 0.001): ta = 0
    # print("B30V : " + str(tv) + "V @ " + str(ta)[:6] + "A")
    if not _within_range(tv, 30):
        return False

    # print()

    s.close()
    return True


BIAS_AND_VOLTAGE_RANGES = [9.,
                           -9.,
                           9.,
                           -9.,
                           9.,
                           -9.,
                           9.,
                           -9.,
                           9.,
                           -9.,
                           9.,
                           -9.,
                           99.,
                           5.,
                           -15.,
                           -25.,
                           -10.,
                           -5.1,
                           0.,
                           0.]


def check_bias_clocks(margin=.2):
    values = []
    for i in range(len(BIAS_AND_VOLTAGE_RANGES)):
        values.append(_read_register_through_mailbox(i))
    return list(enumerate(values))


def _read_register_through_mailbox(register_index: int):
    # construct a register string i.e. "0032"
    register = "00" + hex(0x30 + (2 * register_index))[2:]

    # Write read target address to REG_BIASANDCLOCKREGISTERADDRESS_REG
    WriteReg(REG_BIASANDCLOCKREGISTERADDRESS_REG, str(register), 1)

    # Write REG_READ_ADDRESS to REG_BIASREGISTERDATAOUT_REG
    WriteReg(REG_BIASREGISTERDATAOUT_REG, REG_READ_ADDRESS, 1)

    # Trigger Command
    WriteReg(REG_COMMAND, REG_COMMAND, 1)

    # Read result from REG_READ_ADDRESS
    result = ReadReg(REG_READ_ADDRESS)

    # linearize return value
    return ((int(result, 16) & 0x3fff) * BIAS_AND_VOLTAGE_RANGES[register_index]) / 4096.


def _within_range(value, target, margin=None, percent=.05):
    if margin:
        within_range = target - margin < value < target + margin

    else:
        within_range = target * (1 - percent) < value < target * (1 + percent)

    if not within_range:
        print(f'Value {value} outside range {margin}/{percent} of target {target}')

    return within_range
