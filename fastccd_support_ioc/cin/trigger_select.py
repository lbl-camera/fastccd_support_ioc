import cin_functions
import cin_register_map


def enable_shutter_trigger_output(channel=2):
    # Get Value from Trigger Select Register
    reg_val = cin_functions.ReadReg(cin_register_map.REG_TRIGGERSELECT_REG)
    # print reg_val
    # print reg_val[7:]
    # print reg_val[6:7]
    # print reg_val[5:6]
    # print reg_val[4:5]
    # Oct 2022 John J confirms that E puts the shutter signal in the output connector
    # The F in the last (LSB) nibble is for routing Exposure to TriggerOutOutput1 in hardware
    str_val = reg_val[4:5] + reg_val[5:6] + "EF"
    # print str_val
    cin_functions.WriteReg(cin_register_map.REG_TRIGGERSELECT_REG, str_val, 1)
