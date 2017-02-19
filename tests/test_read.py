import sys
import logging
import unittest
from mock import Mock, patch
from ina219 import INA219

logger = logging.getLogger()
logger.level = logging.ERROR
logger.addHandler(logging.StreamHandler(sys.stdout))


class TestRead(unittest.TestCase):

    @patch('Adafruit_GPIO.I2C.get_i2c_device')
    def setUp(self, device):
        device.return_value = Mock()
        self.ina = INA219(0.1, 0.4)
        self.ina._i2c.writeList = Mock()

    def test_read_32v(self):
        self.ina._i2c.readU16BE = Mock(return_value=64000)
        self.assertEqual(self.ina.voltage(), 32)

    def test_read_16v(self):
        self.ina._i2c.readU16BE = Mock(return_value=32000)
        self.assertEqual(self.ina.voltage(), 16)

    def test_read_4_808v(self):
        self.ina._i2c.readU16BE = Mock(return_value=9618)
        self.assertEqual(self.ina.voltage(), 4.808)

    def test_read_4mv(self):
        self.ina._i2c.readU16BE = Mock(return_value=8)
        self.assertEqual(self.ina.voltage(), 0.004)

    def test_read_supply_voltage(self):
        self.ina.voltage = Mock(return_value=2.504)
        self.ina.shunt_voltage = Mock(return_value=35.000)
        self.assertEqual(self.ina.supply_voltage(), 2.539)

    def test_read_0v(self):
        self.ina._i2c.readU16BE = Mock(return_value=0)
        self.assertEqual(self.ina.voltage(), 0)

    def test_read_12ua(self):
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_1_40MV)
        self.ina._i2c.readS16BE = Mock(return_value=1)
        self.assertAlmostEqual(self.ina.current(), 0.012, 3)

    def test_read_0ma(self):
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_1_40MV)
        self.ina._i2c.readS16BE = Mock(return_value=0)
        self.assertEqual(self.ina.current(), 0)

    def test_read_negative_ma(self):
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_1_40MV)
        self.ina._i2c.readS16BE = Mock(return_value=-19795)
        self.assertAlmostEqual(self.ina.current(), -236.9, 1)

    def test_read_0mw(self):
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_1_40MV)
        self.ina._i2c.readU16BE = Mock(return_value=0)
        self.assertEqual(self.ina.power(), 0)

    def test_read_1914mw(self):
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_1_40MV)
        self.ina._i2c.readU16BE = Mock(return_value=7997)
        self.assertAlmostEqual(self.ina.power(), 1914.0, 0)

    def test_read_shunt_20mv(self):
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_1_40MV)
        self.ina._i2c.readS16BE = Mock(return_value=2000)
        self.assertEqual(self.ina.shunt_voltage(), 20.0)

    def test_read_shunt_0mv(self):
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_1_40MV)
        self.ina._i2c.readS16BE = Mock(return_value=0)
        self.assertEqual(self.ina.shunt_voltage(), 0)

    def test_read_shunt_negative_40mv(self):
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_1_40MV)
        self.ina._i2c.readS16BE = Mock(return_value=-4000)
        self.assertEqual(self.ina.shunt_voltage(), -40.0)

    def test_current_overflow_valid(self):
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_2_80MV)
        self.ina._i2c.readU16BE = Mock(return_value=4001)
        self.assertEqual(self.ina.voltage(), 2.0)
        self.assertTrue(self.ina.current_overflow())
