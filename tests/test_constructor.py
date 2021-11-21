import sys
import logging
import unittest
from mock import Mock
from ina219 import INA219, I2cDevice

logger = logging.getLogger()
logger.level = logging.ERROR
logger.addHandler(logging.StreamHandler(sys.stdout))


class TestConstructor(unittest.TestCase):

    def setUp(self):
        I2cDevice.register(Mock)  # make "Mock" a subclass of "I2cDevice"
        self.device = Mock()

    def test_default(self):
        self.ina = INA219(self.device, 0.1)
        self.assertEqual(self.ina._shunt_ohms, 0.1)
        self.assertIsNone(self.ina._max_expected_amps)
        self.assertIsNone(self.ina._gain)
        self.assertFalse(self.ina._auto_gain_enabled)
        self.assertAlmostEqual(self.ina._min_device_current_lsb, 6.25e-6, 2)

    def test_with_max_expected_amps(self):
        self.ina = INA219(self.device, 0.1, 0.4)
        self.assertEqual(self.ina._shunt_ohms, 0.1)
        self.assertEqual(self.ina._max_expected_amps, 0.4)

    def test_with_invalid_i2c_device_class(self):
        non_i2c_driver_instance = object()
        exp_exc_msg = 'I2C device class must be a subclass of I2cDevice'
        with self.assertRaisesRegexp(AssertionError, exp_exc_msg):
            self.ina = INA219(non_i2c_driver_instance, 0)
