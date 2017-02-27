import sys
import logging
import unittest
from mock import Mock, patch
from ina219 import INA219

logger = logging.getLogger()
logger.level = logging.ERROR
logger.addHandler(logging.StreamHandler(sys.stdout))


class TestConstructor(unittest.TestCase):

    @patch('Adafruit_GPIO.I2C.get_i2c_device')
    def test_default(self, device):
        device.return_value = Mock()
        self.ina = INA219(0.1)
        self.assertEqual(self.ina._shunt_ohms, 0.1)
        self.assertIsNone(self.ina._max_expected_amps)
        self.assertIsNone(self.ina._gain)
        self.assertFalse(self.ina._auto_gain_enabled)
        self.assertAlmostEqual(self.ina._min_device_current_lsb, 6.25e-6, 2)

    @patch('Adafruit_GPIO.I2C.get_i2c_device')
    def test_with_max_expected_amps(self, device):
        device.return_value = Mock()
        self.ina = INA219(0.1, 0.4)
        self.assertEqual(self.ina._shunt_ohms, 0.1)
        self.assertEqual(self.ina._max_expected_amps, 0.4)
