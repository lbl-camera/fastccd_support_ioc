from caproto.server import PVGroup, get_pv_pair_wrapper, conversion, pvproperty
from lakeshore import Model336

import logging
logger = logging.getLogger('caproto')

lakeshore336 = Model336(ip_address='192.168.10.3') #TODO catch time out and try to reconnect

