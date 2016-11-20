""" This library supports the INA219 current and power monitor
from Texas Instruments with a Raspberry Pi using the I2C bus."""
import logging
from math import log10, floor, ceil, trunc
import Adafruit_GPIO.I2C as I2C


class INA219:

    RANGE_16V = 0  # Range 0-16 volts
    RANGE_32V = 1  # Range 0-32 volts

    GAIN_1_40MV = 0  # Maximum shut voltage 40mV
    GAIN_2_80MV = 1  # Maximum shut voltage 80mV
    GAIN_4_160MV = 2  # Maximum shut voltage 160mV
    GAIN_8_320MV = 3  # Maximum shut voltage 320mV

    ADC_9BIT = 0  # 9bit conversion time  84us.
    ADC_10BIT = 1  # 10bit conversion time 148us.
    ADC_11BIT = 2  # 11bit conversion time 2766us.
    ADC_12BIT = 3  # 12bit conversion time 532us.
    ADC_2SAMP = 9  # 2 samples at 12bit, conversion time 1.06ms.
    ADC_4SAMP = 10  # 4 samples at 12bit, conversion time 2.13ms.
    ADC_8SAMP = 11  # 8 samples at 12bit, conversion time 4.26ms.
    ADC_16SAMP = 12  # 16 samples at 12bit,conversion time 8.51ms
    ADC_32SAMP = 13  # 32 samples at 12bit, conversion time 17.02ms.
    ADC_64SAMP = 14  # 64 samples at 12bit, conversion time 34.05ms.
    ADC_128SAMP = 15  # 128 samples at 12bit, conversion time 68.10ms.

    __ADDRESS = 0x40

    __REG_CONFIG = 0x00
    __REG_SHUNTVOLTAGE = 0x01
    __REG_BUSVOLTAGE = 0x02
    __REG_POWER = 0x03
    __REG_CURRENT = 0x04
    __REG_CALIBRATION = 0x05

    __RST = 15
    __BRNG = 13
    __PG1 = 12
    __PG0 = 11
    __BADC4 = 10
    __BADC3 = 9
    __BADC2 = 8
    __BADC1 = 7
    __SADC4 = 6
    __SADC3 = 5
    __SADC2 = 4
    __SADC1 = 3
    __MODE3 = 2
    __MODE2 = 1
    __MODE1 = 0

    __OVF = 1

    __BUS_RANGE = [16, 32]
    __GAIN_VOLTS = [0.04, 0.08, 0.16, 0.32]

    __PWR_DOWN = 0
    __CONT_SH_BUS = 7

    __LSB_ERR_MSG = ('Calibration error, current lsb %.3e must be '
                     'between min lsb %.3e and max lsb %.3e')
    __AMP_ERR_MSG = ('Expected current %.3fA is greater '
                     'than max possible current %.3fA')
    __OVF_WRN_MSH = ('Current overflow detection is not operative, invalid '
                     'current/power readings are possible, '
                     'the current_overflow() method cannot be used')

    __LOG_FORMAT = '%(asctime)s - %(levelname)s - INA219 %(message)s'
    __LOG_MSG_1 = ('shunt ohms: %.3f, bus max volts: %d, '
                   'shunt volts max: %.2f, max expected amps: %.3f, '
                   'bus ADC: %d, shunt ADC: %d')

    __SHUNT_MILLIVOLTS_LSB = 0.01  # 10uV
    __BUS_MILLIVOLTS_LSB = 4  # 4mV

    def __init__(self, shunt_ohms, max_expected_amps, address=__ADDRESS,
                 log_level=logging.ERROR):
        """ Construct the class passing in the resistance of the shunt
        resistor and the maximum expected current flowing through it in
        your system.

        Arguments:
        shunt_ohms -- value of shunt resistor in Ohms (mandatory).
        max_expected_amps -- the maximum expected current in Amps (mandatory).
        address -- the I2C address of the INA219, defaults to *0x40*.
        log_level -- set to logging.DEBUG to see detailed calibration
            calculations (optional).
        """
        logging.basicConfig(level=log_level, format=self.__LOG_FORMAT)
        self._i2c = I2C.get_i2c_device(address)
        self._shunt_ohms = shunt_ohms
        self._max_expected_amps = max_expected_amps
        self._current_overflow = 0
        self._overflow_operative = True

    def configure(self, voltage_range=RANGE_32V, gain=GAIN_8_320MV,
                  bus_adc=ADC_12BIT, shunt_adc=ADC_12BIT):
        """ Configures and calibrates how the INA219 will take measurements.

        Arguments:
        voltage_range -- The full scale voltage range, this is either 16V
            or 32V represented by one of the following constants;
            RANGE_16V, RANGE_32V (default).
        gain -- The gain which controls the maximum range of the shunt
            voltage represented by one of the following constants;
            GAIN_1_40MV, GAIN_2_80MV, GAIN_4_160MV,
            GAIN_8_320MV (default).
        bus_adc -- The bus ADC resolution (9, 10, 11, or 12-bit) or
            set the number of samples used when averaging results
            represent by one of the following constants; ADC_9BIT,
            ADC_10BIT, ADC_11BIT, ADC_12BIT (default),
            ADC_2SAMP, ADC_4SAMP, ADC_8SAMP, ADC_16SAMP,
            ADC_32SAMP, ADC_64SAMP, ADC_128SAMP
        shunt_adc -- The shunt ADC resolution (9, 10, 11, or 12-bit) or
            set the number of samples used when averaging results
            represent by one of the following constants; ADC_9BIT,
            ADC_10BIT, ADC_11BIT, ADC_12BIT (default),
            ADC_2SAMP, ADC_4SAMP, ADC_8SAMP, ADC_16SAMP,
            ADC_32SAMP, ADC_64SAMP, ADC_128SAMP
        """
        self.__validate_voltage_range(voltage_range)
        logging.debug(
            self.__LOG_MSG_1 %
            (self._shunt_ohms, self.__BUS_RANGE[voltage_range],
             self.__GAIN_VOLTS[gain], self._max_expected_amps,
             bus_adc, shunt_adc))
        self._calibrate(
            self.__BUS_RANGE[voltage_range], self.__GAIN_VOLTS[gain],
            self._max_expected_amps)
        self._configure(voltage_range, gain, bus_adc, shunt_adc)

    def voltage(self):
        """ Returns the bus voltage in volts. """
        value = self._voltage_register()
        return float(value) * self.__BUS_MILLIVOLTS_LSB / 1000

    def supply_voltage(self):
        """ Returns the bus supply voltage in volts. This is the sum of
        the bus voltage and shunt voltage."""
        return self.voltage() + (float(self.shunt_voltage()) / 1000)

    def current(self):
        """ Returns the bus current in milliamps. """
        return self._current_register() * self._current_lsb * 1000

    def power(self):
        """ Returns the bus power consumption in milliwatts. """
        return self._power_register() * self._power_lsb * 1000

    def shunt_voltage(self):
        """ Returns the shunt voltage in millivolts. """
        return self._shunt_voltage_register() * self.__SHUNT_MILLIVOLTS_LSB

    def powerdown(self):
        """ Put the INA219 into power down mode. """
        self._configuration_register(self.__PWR_DOWN)

    def current_overflow(self):
        """ Returns true if the sensor has detect current overflow. In
        this case the current and power values are invalid."""
        if self._overflow_operative:
            return self._current_overflow
        else:
            raise RuntimeError('Current overflows cannot be detected')

    def reset(self):
        """ Reset the INA219 to its default configuration. """
        self._configuration_register(1 << self.__RST)

    def _configure(self, voltage_range, gain, bus_adc, shunt_adc):
        configuration = (
            voltage_range << self.__BRNG | gain << self.__PG0 |
            bus_adc << self.__BADC1 | shunt_adc << self.__SADC1 |
            self.__CONT_SH_BUS)
        self._configuration_register(configuration)

    def _calibrate(self, bus_volts_max, shunt_volts_max, max_expected_amps):
        max_possible_amps = shunt_volts_max / self._shunt_ohms
        if max_expected_amps > round(max_possible_amps, 3):
            raise ValueError(self.__AMP_ERR_MSG %
                             (max_expected_amps, max_possible_amps))

        logging.info("max possible current: %.3fA" %
                     max_possible_amps)
        logging.info("max expected current: %.3fA" %
                     max_expected_amps)

        min_current_lsb = float(max_expected_amps) / 32767
        max_current_lsb = float(max_expected_amps) / 4096

        self._current_lsb = self.__select_min_rounded_lsb(min_current_lsb)
        logging.info("min current LSB: %.3e A/bit" % min_current_lsb)
        logging.info("max current LSB: %.3e A/bit" % max_current_lsb)
        logging.info("chosen current LSB: %.3e A/bit" % self._current_lsb)

        if self._current_lsb > max_current_lsb:
            raise ValueError(
                self.__LSB_ERR_MSG %
                (self._current_lsb, min_current_lsb, max_current_lsb))

        self._power_lsb = self._current_lsb * 20
        logging.info("power LSB: %.3e W/bit" % self._power_lsb)

        max_current = self._current_lsb * 32767
        if max_current >= max_possible_amps:
            max_current_before_overflow = max_possible_amps
        else:
            max_current_before_overflow = max_current
        logging.info("max current before overflow: %.3fA" %
                     max_current_before_overflow)

        max_shunt_voltage = max_current_before_overflow * self._shunt_ohms
        if max_shunt_voltage >= shunt_volts_max:
            max_shunt_voltage_before_overflow = shunt_volts_max
            self._overflow_operative = False
            logging.warn(self.__OVF_WRN_MSH)
        else:
            max_shunt_voltage_before_overflow = max_shunt_voltage
        logging.info("max shunt voltage before overflow: %.3fV" %
                     max_shunt_voltage_before_overflow)

        calibration = trunc(0.04096 / (self._current_lsb * self._shunt_ohms))
        logging.info("calibration: %d" % calibration)
        self._calibration_register(calibration)

    def _configuration_register(self, register_value):
        logging.debug("configuration: 0x%04x" % register_value)
        self.__write_register(self.__REG_CONFIG, register_value)

    def _calibration_register(self, register_value):
        logging.debug("calibration: 0x%04x" % register_value)
        self.__write_register(self.__REG_CALIBRATION, register_value)

    def _voltage_register(self):
        register_value = self.__read_register(self.__REG_BUSVOLTAGE)
        self._current_overflow = register_value & self.__OVF
        return register_value >> 3

    def _current_register(self):
        return self.__read_register(self.__REG_CURRENT, True)

    def _shunt_voltage_register(self):
        return self.__read_register(self.__REG_SHUNTVOLTAGE, True)

    def _power_register(self):
        return self.__read_register(self.__REG_POWER)

    def __validate_voltage_range(self, voltage_range):
        if voltage_range > len(self.__BUS_RANGE) - 1:
            raise ValueError("Invalid voltage range")

    def __select_min_rounded_lsb(self, x):
        if not x:
            return 0
        power = -int(floor(log10(abs(x))))
        factor = (10 ** power)
        return ceil(x * factor) / factor

    def __write_register(self, register, register_value):
        register_bytes = self.__to_bytes(register_value)
        logging.debug(
            "write register 0x%02x: 0x%04x 0b%s" %
            (register, register_value,
             self.__binary_as_string(register_value)))
        self._i2c.writeList(register, register_bytes)

    def __read_register(self, register, negative_value_supported=False):
        if negative_value_supported:
            register_value = self._i2c.readS16BE(register)
        else:
            register_value = self._i2c.readU16BE(register)
        logging.debug(
            "read register 0x%02x: %d" % (register, register_value))
        return register_value

    def __to_bytes(self, register_value):
        return [(register_value >> 8) & 0xFF, register_value & 0xFF]

    def __binary_as_string(self, register_value):
        return bin(register_value)[2:].zfill(16)
