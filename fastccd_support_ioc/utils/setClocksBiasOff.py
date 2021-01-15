from fastccd_support_ioc.utils import cin_functions

cin_functions.WriteReg("8204", "0000", 1)
cin_functions.WriteReg("8205", "0008", 1)
