# Raspberry Pi Python Library for Voltage and Current Sensors Using the INA219

[![Build Status](https://travis-ci.org/chrisb2/pi_ina219.svg?branch=master)](https://travis-ci.org/chrisb2/pi_ina219)

This Python library supports the [INA219](http://www.ti.com/lit/ds/symlink/ina219.pdf) 
current and power monitor from Texas Instruments.

The library currently only supports _continuous_ reads of voltage and 
power, but not _triggered_ reads.

The library supports the detection of _overflow_ in the current/power 
calculations which results in meaningless values for current and power. 
This support depends on the calibration of the device. If the device 
calibration does not allow overflow detection then a warning is written 
to the console. This warning may be ignored if you are confident that 
overflow cannot occur in your system. To avoid the warning and allow 
overflow detection increase the gain.

The low power mode of the INA219 is supported, so if only occasional 
reads are being made in a battery based system, current consumption can 
be minimised.

The library has been tested with the 
[Adafruit INA219 Breakout](https://www.adafruit.com/products/904).

## Prerequisites

This library and its dependency 
([Adafruit GPIO library](https://github.com/adafruit/Adafruit_Python_GPIO)) 
can be installed by executing:

```shell
sudo pip install git+git://github.com/chrisb2/pi_ina219.git
```

The Adafruit library supports the I2C protocol on all versions of the 
Raspberry Pi. Remember to enable the I2C bus under the *Advanced Options* 
of *raspi-config*.

## Usage

The following code demonstrates basic usage of this library with a 
0.1&Omega; shunt resistor and a maximum expected current of _200mA_. 
The address of the sensor in this case is the default of _0x40_.

Note that the bus voltage is that on the load side of the shunt resister, 
if you want the voltage on the supply side then you should add the bus
voltage and shunt voltage together, or use the *supply_voltage()* 
function.

The gain is automatically calculated to maximise the resolution.

```python
#!/usr/bin/env python
from ina219 import INA219

SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 0.2


def read():
    ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS)
    ina.configure(ina.RANGE_16V)

    print "Bus Voltage: %.3f V" % ina.voltage()
    print "Bus Current: %.3f mA" % ina.current()
    print "Power: %.3f mW" % ina.power()
    print "Shunt voltage: %.3f mV" % ina.shunt_voltage()

if __name__ == "__main__":
    read()
```

The sensor address may be altered as follows:

```python
ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, address=0x41)
```

The sensor may be put in low power mode between reads as follows:

```python
ina.configure(ina.RANGE_16V, ina.GAIN_1_40MV)
while True:
    print "Voltage : %.3f V" % ina.voltage()
    ina.sleep()
    time.sleep(60)
    ina.wake();
```

Note that if you do not wake the device after sleeping, the value 
returned from a read will be the previous value taken before sleeping.

Current overflow can be detected and meaningless values for current and 
power can be avoided as follows:

```python
print "Bus Voltage    : %.3f V" % ina.voltage()
if ina.current_overflow():
    print "Current overflow"
else:
    print "Bus Current    : %.3f mA" % ina.current()
```

## Functions

* `INA219()` constructs the class.
The arguments, are:
    * shunt_ohms: The value of the shunt resistor in Ohms (mandatory).
    * max_expected_amps: The maximum expected current in Amps (mandatory).
    * address: The I2C address of the INA219, defaults to *0x40* (optional).
    * log_level: Set to _logging.INFO_ to see the detailed calibration 
    calculations and _logging.DEBUG_ to see register operations (optional).
* `configure()` configures and calibrates how the INA219 will take measurements.
The arguments, which are all optional, are:
    * voltage_range: The full scale voltage range, this is either 16V or 32V, 
    represented by one of the following constants.
        * RANGE_16V: Range zero to 16 volts
        * RANGE_32V: Range zero to 32 volts (**default**). **Device only supports upto 26V.**
    * gain: The gain, which controls the maximum range of the shunt voltage, represented by one of the following constants. 
        * GAIN_1_40MV: Maximum shunt voltage 40mV
        * GAIN_2_80MV: Maximum shunt voltage 80mV
        * GAIN_4_160MV: Maximum shunt voltage 160mV
        * GAIN_8_320MV: Maximum shunt voltage 320mV
        * GAIN_AUTO: Automatically calculate the gain (**default**)
    * bus_adc: The bus ADC resolution (9, 10, 11, or 12-bit), or
        set the number of samples used when averaging results, represented by
        one of the following constants.
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
        one of the following constants.
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
    is the sum of the bus voltage and shunt voltage.
* `current()` Returns the bus current in milliamps (mA).
* `power()` Returns the bus power consumption in milliwatts (mW).
* `shunt_voltage()` Returns the shunt voltage in millivolts (mV).
* `current_overflow()` If the device is configured such that current
overflows can be detected, then this method returns 'True' if an overflow
has occured. If the configuration cannot detect overflows a
_RuntimeException_ is thrown.
* `sleep()` Put the INA219 into power down mode.
* `wake()` Wake the INA219 from power down mode.
* `reset()` Reset the INA219 to its default configuration.

## Performance

On a Raspberry Pi 2 Model B running Raspbian Jesse and reading a 12-bit
voltage in a loop, a read occurred approximately every 10 milliSeconds.

## Debugging

To understand the calibration calculation results, informational output
can be enabled with:

```python
    ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, log_level=logging.INFO)
```

## Testing

Install the library as described above, this will install all the
dependencies required for the unit tests, as well as the library 
itself. Clone the library source from Github then execute the test suite
from the top level directory with:

```shell
python -m unittest tests.testall
```

## Coding Standard

This library adheres to the *PEP8* standard and follows the *idiomatic* 
style described in the book *Writing Idiomatic Python* by *Jeff Knupp*.
