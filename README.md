# Raspberry Pi Python Library for Voltage and Current Sensors Using the INA219

This Python library supports the [INA219](http://www.ti.com/lit/ds/symlink/ina219.pdf) 
current and power monitor from Texas Instruments.

The library currently only supports _continuous_ reads of voltage and 
power, but not _triggered_ reads.

The low power mode of the INA219 is supported, so if only occasional 
reads are being made in a battery based system, current consumption can 
be minimised.

The library has been tested with the 
[Adafruit INA219 Breakout](https://www.adafruit.com/products/904).

## Prerequisites

This library and its dependencies 
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
0.1&Omega; shunt resistor and a maximum expected current of _400mA_. 
The address of the sensor in this case is the default of _0x40_.

Note that the bus voltage is that on the load side of the shunt resister, 
if you want the voltage on the supply side then you should add the bus
voltage and shunt voltage together, or use the *supply_voltage()* 
function.

```python
#!/usr/bin/env python
from ina219 import INA219

SHUNT_OHMS = 0.1
MAX_EXPECTED_AMPS = 0.4


def read():
    ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS)
    ina.configure(ina.RANGE_16V, ina.GAIN_1_40MV)

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
while True:
    ina.configure(ina.RANGE_16V, ina.GAIN_1_40MV)
    print "Voltage : %.3f V" % ina.voltage()
    ina.powerdown()
    time.sleep(300)
```

## Functions

* `INA219()` constructs the class.
The arguments, are:
    * shunt_ohms: The value of the shunt resistor in Ohms (mandatory).
    * max_expected_amps: The maximum expected current in Amps (mandatory).
    * address: The I2C address of the INA219, defaults to *0x40*.
    * log_level: Set to _logging.DEBUG_ to see the detailed calibration calculations (optional).
* `configure()` configures and calibrates how the INA219 will take measurements.
The arguments, which are all optional, are:
    * voltage_range: The full scale voltage range, this is either 16V or 32V, 
    represented by one of the following constants.
        * RANGE_16V: Range 0-16 volts
        * RANGE_32V: Range 0-32 volts (**default**). **Device only supports upto 26V.**
    * gain: The gain, which controls the maximum range of the shunt voltage, represented by one of the following constants. 
        * GAIN_1_40MV: Maximum shunt voltage 40mV
        * GAIN_2_80MV: Maximum shunt voltage 80mV
        * GAIN_4_160MV: Maximum shunt voltage 160mV
        * GAIN_8_320MV: Maximum shunt voltage 320mV (**default**)
    * bus_adc: The bus ADC resolution (9-, 10-, 11-, or 12-bit), or
        set the number of samples used when averaging results, represented by
        one of the following constants.
        * ADC_9BIT: 9 bit, conversion time 84us.
        * ADC_10BIT: 10 bit, conversion time 148us.
        * ADC_11BIT: 11 bit, conversion time 276us.
        * ADC_12BIT: 12 bit conversion time 532us (**default**).
        * ADC_2SAMP: 2 samples at 12 bit, conversion time 1.06ms.
        * ADC_4SAMP: 4 samples at 12 bit, conversion time 2.13ms.
        * ADC_8SAMP: 8 samples at 12 bit, conversion time 4.26ms.
        * ADC_16SAMP: 16 samples at 12 bit, conversion time 8.51ms
        * ADC_32SAMP: 32 samples at 12 bit, conversion time 17.02ms.
        * ADC_64SAMP: 64 samples at 12 bit, conversion time 34.05ms.
        * ADC_128SAMP: 128 samples at 12 bit, conversion time 68.10ms.
    * shunt_adc: The shunt ADC resolution (9-, 10-, 11-, or 12-bit), or
        set the number of samples used when averaging results, represented by
        one of the following constants.
        * ADC_9BIT: 9 bit, conversion time 84us.
        * ADC_10BIT: 10 bit, conversion time 148us.
        * ADC_11BIT: 11 bit, conversion time 276us.
        * ADC_12BIT: 12 bit conversion time 532us (**default**).
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
* `powerdown()` Put the INA219 into power down mode.
* `reset()` Reset the INA219 to its default configuration.

## Performance

On a Raspberry Pi 2 Model B running Raspbian Jesse and reading a voltage 
(12-bit) in a loop and writing to file every 1000 reads, a read
occurred approximately every 10 milliSeconds.

## Debugging

To understand the calibration calculation results, debug output can be 
enabled with:

```python
    ina = INA219(SHUNT_OHMS, MAX_EXPECTED_AMPS, log_level=logging.DEBUG)
```

## Testing

The library comes with a full test suite which can be executed from the 
top level directory with:

```shell
 python -m unittest tests.testall
```

## Coding Standard

This library adheres to the *PEP8* standard and follows the *idiomatic* 
style described in the book *Writing Idiomatic Python* by *Jeff Knupp*.
