# Raspberry Pi Python Library for Voltage and Current Sensors Using the INA219

[![Build Status](https://travis-ci.org/chrisb2/pi_ina219.svg?branch=master)](https://travis-ci.org/chrisb2/pi_ina219)
[![codecov](https://codecov.io/gh/chrisb2/pi_ina219/branch/master/graph/badge.svg)](https://codecov.io/gh/chrisb2/pi_ina219)
[![PyPI version](https://badge.fury.io/py/pi-ina219.svg)](https://badge.fury.io/py/pi-ina219)

This Python library supports the [INA219](http://www.ti.com/lit/ds/symlink/ina219.pdf) 
voltage, current and power monitor sensor from Texas Instruments. The intent of the library 
is to make it easy to use the quite complex functionality of this sensor.  

The library currently only supports _continuous_ reads of voltage and 
power, but not _triggered_ reads.

The library supports the detection of _overflow_ in the current/power 
calculations which results in meaningless values for these readings.

The low power mode of the INA219 is supported, so if only occasional 
reads are being made in a battery based system, current consumption can 
be minimised.

The library has been tested with the 
[Adafruit INA219 Breakout](https://www.adafruit.com/products/904).

## Installation and Upgrade

This library and its dependency 
([Adafruit GPIO library](https://github.com/adafruit/Adafruit_Python_GPIO)) 
can be installed from PyPI by executing:

```shell
sudo pip install pi-ina219
```
To upgrade from a previous version install direct from Github execute:

```shell
sudo pip uninstall pi-ina219
sudo pip install pi-ina219
```

The Adafruit library supports the I2C protocol on all versions of the 
Raspberry Pi. Remember to enable the I2C bus under the *Advanced Options* 
of *raspi-config*.

## Usage

The address of the sensor unless otherwise specified is the default 
of _0x40_.

Note that the bus voltage is that on the load side of the shunt resister, 
if you want the voltage on the supply side then you should add the bus
voltage and shunt voltage together, or use the *supply_voltage()* 
function.

### Simple - Auto Gain

This mode is great for getting started, as it will provide valid readings 
until the device current capability is exceeded for the value of the 
shunt resistor connected (3.2A for 0.1&Omega; shunt resistor). It does this by
automatically adjusting the gain as required until the maximum is reached,
when a _DeviceRangeError_ exception is thrown to avoid invalid readings being taken.

The downside of this approach is reduced current and power resolution.


```python
#!/usr/bin/env python
from ina219 import INA219
from ina219 import DeviceRangeError

SHUNT_OHMS = 0.1


def read():
    ina = INA219(SHUNT_OHMS)
    ina.configure()

    print "Bus Voltage: %.3f V" % ina.voltage()
    try:
        print "Bus Current: %.3f mA" % ina.current()
        print "Power: %.3f mW" % ina.power()
        print "Shunt voltage: %.3f mV" % ina.shunt_voltage()
    except DeviceRangeError as e:
        # Current out of device range with specified shunt resister
        print e


if __name__ == "__main__":
    read()
```

### Advance - Auto Gain, High Resolution

In this mode by understanding the maximum current expected in your system
and specifying this in the script you can achieve the best possible current
and power resolution. The library will calculate the best gain to achieve
the highest resolution based on the maximum expected current.

In this mode if the current exceeds the maximum specified, the gain will 
be automatically increased, so a valid reading will still result, but at 
a lower resolution.

As above when the maximum gain is reached, an exception is thrown to 
avoid invalid readings being taken.

```python
#!/usr/bin/env python
from ina219 import INA219
from ina219 import DeviceRangeError

SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 0.2


def read():
    ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS)
    ina.configure(ina.RANGE_16V)

    print "Bus Voltage: %.3f V" % ina.voltage()
    try:
        print "Bus Current: %.3f mA" % ina.current()
        print "Power: %.3f mW" % ina.power()
        print "Shunt voltage: %.3f mV" % ina.shunt_voltage()
    except DeviceRangeError as e:
        # Current out of device range with specified shunt resister
        print e


if __name__ == "__main__":
    read()
```

### Advance - Manual Gain, High Resolution

In this mode by understanding the maximum current expected in your system
and specifying this and the gain in the script you can always achieve the 
best possible current and power resolution, at the price of missing current
and power values if a current overflow occurs.

```python
#!/usr/bin/env python
from ina219 import INA219
from ina219 import DeviceRangeError

SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 0.2


def read():
    ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS)
    ina.configure(ina.RANGE_16V, ina.GAIN_1_40MV)

    print "Bus Voltage: %.3f V" % ina.voltage()
    try:
        print "Bus Current: %.3f mA" % ina.current()
        print "Power: %.3f mW" % ina.power()
        print "Shunt voltage: %.3f mV" % ina.shunt_voltage()
    except DeviceRangeError as e:
        print "Current overflow"


if __name__ == "__main__":
    read()
```

### Sensor Address

The sensor address may be altered as follows:

```python
ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, address=0x41)
```

### Low Power Mode

The sensor may be put in low power mode between reads as follows:

```python
ina.configure(ina.RANGE_16V)
while True:
    print "Voltage : %.3f V" % ina.voltage()
    ina.sleep()
    time.sleep(60)
    ina.wake();
```

Note that if you do not wake the device after sleeping, the value 
returned from a read will be the previous value taken before sleeping.

## Functions

* `INA219()` constructs the class.
The arguments, are:
    * shunt_ohms: The value of the shunt resistor in Ohms (mandatory).
    * max_expected_amps: The maximum expected current in Amps (optional).
    * address: The I2C address of the INA219, defaults to *0x40* (optional).
    * log_level: Set to _logging.INFO_ to see the detailed calibration 
    calculations and _logging.DEBUG_ to see register operations (optional).
* `configure()` configures and calibrates how the INA219 will take measurements.
The arguments, which are all optional, are:
    * voltage_range: The full scale voltage range, this is either 16V or 32V, 
    represented by one of the following constants (optional).
        * RANGE_16V: Range zero to 16 volts
        * RANGE_32V: Range zero to 32 volts (**default**). **Device only supports upto 26V.**
    * gain: The gain, which controls the maximum range of the shunt voltage, 
        represented by one of the following constants (optional). 
        * GAIN_1_40MV: Maximum shunt voltage 40mV
        * GAIN_2_80MV: Maximum shunt voltage 80mV
        * GAIN_4_160MV: Maximum shunt voltage 160mV
        * GAIN_8_320MV: Maximum shunt voltage 320mV
        * GAIN_AUTO: Automatically calculate the gain (**default**)
    * bus_adc: The bus ADC resolution (9, 10, 11, or 12-bit), or
        set the number of samples used when averaging results, represented by
        one of the following constants (optional).
        * ADC_9BIT: 9 bit, conversion time 84us.
        * ADC_10BIT: 10 bit, conversion time 148us.
        * ADC_11BIT: 11 bit, conversion time 276us.
        * ADC_12BIT: 12 bit, conversion time 532us (**default**).
        * ADC_2SAMP: 2 samples at 12 bit, conversion time 1.06ms.
        * ADC_4SAMP: 4 samples at 12 bit, conversion time 2.13ms.
        * ADC_8SAMP: 8 samples at 12 bit, conversion time 4.26ms.
        * ADC_16SAMP: 16 samples at 12 bit, conversion time 8.51ms
        * ADC_32SAMP: 32 samples at 12 bit, conversion time 17.02ms.
        * ADC_64SAMP: 64 samples at 12 bit, conversion time 34.05ms.
        * ADC_128SAMP: 128 samples at 12 bit, conversion time 68.10ms.
    * shunt_adc: The shunt ADC resolution (9, 10, 11, or 12-bit), or
        set the number of samples used when averaging results, represented by
        one of the following constants (optional).
        * ADC_9BIT: 9 bit, conversion time 84us.
        * ADC_10BIT: 10 bit, conversion time 148us.
        * ADC_11BIT: 11 bit, conversion time 276us.
        * ADC_12BIT: 12 bit, conversion time 532us (**default**).
        * ADC_2SAMP: 2 samples at 12 bit, conversion time 1.06ms.
        * ADC_4SAMP: 4 samples at 12 bit, conversion time 2.13ms.
        * ADC_8SAMP: 8 samples at 12 bit, conversion time 4.26ms.
        * ADC_16SAMP: 16 samples at 12 bit, conversion time 8.51ms
        * ADC_32SAMP: 32 samples at 12 bit, conversion time 17.02ms.
        * ADC_64SAMP: 64 samples at 12 bit, conversion time 34.05ms.
        * ADC_128SAMP: 128 samples at 12 bit, conversion time 68.10ms.
* `voltage()` Returns the bus voltage in volts (V).
* `supply_voltage()` Returns the bus supply voltage in volts (V). This 
    is the sum of the bus voltage and shunt voltage. A _DeviceRangeError_ 
    exception is thrown if current overflow occurs.
* `current()` Returns the bus current in milliamps (mA). 
	A _DeviceRangeError_ exception is thrown if current overflow occurs.
* `power()` Returns the bus power consumption in milliwatts (mW). 
	A _DeviceRangeError_ exception is thrown if current overflow occurs.
* `shunt_voltage()` Returns the shunt voltage in millivolts (mV). 
	A _DeviceRangeError_ exception is thrown if current overflow occurs.
* `current_overflow()` Returns 'True' if an overflow has 
	occured. Alternatively handle the _DeviceRangeError_ exception
	as shown in the examples above.
* `sleep()` Put the INA219 into power down mode.
* `wake()` Wake the INA219 from power down mode.
* `reset()` Reset the INA219 to its default configuration.

## Performance

On a Raspberry Pi 2 Model B running Raspbian Jesse and reading a 12-bit
voltage in a loop, a read occurred approximately every 10 milliSeconds.

## Debugging

To understand the calibration calculation results and automatic gain
increases, informational output can be enabled with:

```python
    ina = INA219(SHUNT_OHMS, log_level=logging.INFO)
```

Detailed logging of device register operations can be enabled with:

```python
    ina = INA219(SHUNT_OHMS, log_level=logging.DEBUG)
```

## Testing

Install the library as described above, this will install all the
dependencies required for the unit tests, as well as the library 
itself. Clone the library source from Github then execute the test suite
from the top level directory with:

```shell
python -m unittest discover -s tests -p 'test_*.py'
```

A single unit test class may be run as follows:

```shell
python -m unittest tests.test_configuration.TestConfiguration
```

Code coverage metrics may be generated and viewed with:

```shell
coverage run --branch --source=ina219 -m unittest discover -s tests -p 'test_*.py'
coverage report -m
```

## Coding Standard

This library adheres to the *PEP8* standard and follows the *idiomatic* 
style described in the book *Writing Idiomatic Python* by *Jeff Knupp*.
