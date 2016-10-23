#!/usr/bin/env python

import logging
from ina219 import INA219

SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 0.5


def read():
    ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, log_level=logging.INFO)
    ina.configure(ina.RANGE_16V, ina.GAIN_2_80MV)

    print "Voltage       : %.3f V" % ina.voltage()
    print "Current       : %.3f mA" % ina.current()
    print "Power         : %.3f mW" % ina.power()
    print "Shunt voltage : %.3f mV" % ina.shunt_voltage()

    ina.powerdown()

if __name__ == "__main__":
    read()
