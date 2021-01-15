from fastccd_support_ioc.utils import cin_functions

cin_functions.WriteReg("8204", "0001", 1)
cin_functions.WriteReg("8205", "0009", 1)
