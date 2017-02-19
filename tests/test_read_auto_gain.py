import sys
import logging
import unittest
from mock import Mock, call, patch
from ina219 import INA219

logger = logging.getLogger()
logger.level = logging.ERROR
logger.addHandler(logging.StreamHandler(sys.stdout))


class TestReadAutoGain(unittest.TestCase):

    GAIN_RANGE_MSG = 'Current out of device range \(overflow\)'

    @patch('Adafruit_GPIO.I2C.get_i2c_device')
    def setUp(self, device):
        device.return_value = Mock()

    def test_auto_gain(self):
        self.ina = INA219(0.1, 0.4)
        self.ina._i2c.writeList = Mock()
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_AUTO)

        self.ina._read_voltage_register = Mock()
        self.ina._read_voltage_register.side_effect = [4001, 4000]
        self.ina._read_configuration = Mock()
        self.ina._read_configuration.side_effect = [2463, 2463]
        self.ina._current_register = Mock(return_value=100)

        self.ina.voltage()
        self.assertAlmostEqual(self.ina.current(), 4.787, 3)

        calls = [call(0x05, [0x42, 0xd8]), call(0x00, [0x09, 0x9f]),
                 call(0x05, [0x21, 0x6c]), call(0x00, [0x11, 0x9f])]
        self.ina._i2c.writeList.assert_has_calls(calls)

    def test_auto_gain_out_of_range(self):
        self.ina = INA219(0.1, 3.0)
        self.ina._i2c.writeList = Mock()
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_AUTO)

        self.ina._read_voltage_register = Mock(return_value=4001)
        self.ina._read_configuration = Mock(return_value=6559)

        self.ina.voltage()
        with self.assertRaisesRegexp(RuntimeError, self.GAIN_RANGE_MSG):
            self.ina.current()
