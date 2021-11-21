#!/usr/bin/env python

import logging
from ina219 import INA219, SmbusI2cDevice, Smbus2I2cDevice, AdafruitI2cDevice

SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 0.2


def read():

    i2c_addr = INA219.i2c_addr()
    i2c_addr = INA219.I2C_ADDR_DEFAULT

    i2c_device = SmbusI2cDevice(interface=1, address=i2c_addr)
    i2c_device = Smbus2I2cDevice(interface=1, address=i2c_addr)
    i2c_device = AdafruitI2cDevice(interface=1, address=i2c_addr)

    ina = INA219(i2c_device, SHUNT_OHMS, MAX_EXPECTED_AMPS,
                 log_level=logging.INFO)
    ina.configure(ina.RANGE_16V, ina.GAIN_AUTO)

    print("Bus Voltage    : %.3f V" % ina.voltage())
    print("Bus Current    : %.3f mA" % ina.current())
    print("Supply Voltage : %.3f V" % ina.supply_voltage())
    print("Shunt voltage  : %.3f mV" % ina.shunt_voltage())
    print("Power          : %.3f mW" % ina.power())


if __name__ == "__main__":
    read()
