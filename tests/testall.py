import sys
import logging
import unittest
from mock import Mock, call
from ina219 import INA219

logger = logging.getLogger()
logger.level = logging.ERROR
logger.addHandler(logging.StreamHandler(sys.stdout))


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        self.ina = INA219(0.1, 0.4)
        self.ina._i2c.writeList = Mock()

    def test_16v_40mv(self):
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_1_40MV)
        calls = [call(0x05, [0x50, 0x00]), call(0x00, [0x01, 0x9f])]
        self.ina._i2c.writeList.assert_has_calls(calls)

    def test_32v_40mv(self):
        self.ina.configure(self.ina.RANGE_32V, self.ina.GAIN_1_40MV)
        calls = [call(0x05, [0x50, 0x00]), call(0x00, [0x21, 0x9f])]
        self.ina._i2c.writeList.assert_has_calls(calls)

    def test_32v_80mv(self):
        self.ina.configure(self.ina.RANGE_32V, self.ina.GAIN_2_80MV)
        calls = [call(0x05, [0x50, 0x00]), call(0x00, [0x29, 0x9f])]
        self.ina._i2c.writeList.assert_has_calls(calls)

    def test_32v_160mv(self):
        self.ina.configure(self.ina.RANGE_32V, self.ina.GAIN_4_160MV)
        calls = [call(0x05, [0x50, 0x00]), call(0x00, [0x31, 0x9f])]
        self.ina._i2c.writeList.assert_has_calls(calls)

    def test_32v_320mv(self):
        self.ina.configure(self.ina.RANGE_32V, self.ina.GAIN_8_320MV)
        calls = [call(0x05, [0x50, 0x00]), call(0x00, [0x39, 0x9f])]
        self.ina._i2c.writeList.assert_has_calls(calls)

    def test_32v_40mv_9bit(self):
        self.ina.configure(
            self.ina.RANGE_32V, self.ina.GAIN_1_40MV,
            self.ina.ADC_9BIT, self.ina.ADC_9BIT)
        calls = [call(0x05, [0x50, 0x00]), call(0x00, [0x20, 0x07])]
        self.ina._i2c.writeList.assert_has_calls(calls)

    def test_32v_40mv_10_bit_11_bit(self):
        self.ina.configure(
            self.ina.RANGE_32V, self.ina.GAIN_1_40MV,
            self.ina.ADC_10BIT, self.ina.ADC_11BIT)
        calls = [call(0x05, [0x50, 0x00]), call(0x00, [0x20, 0x97])]
        self.ina._i2c.writeList.assert_has_calls(calls)

    def test_32v_40mv_2_samples_128_samples(self):
        self.ina.configure(
            self.ina.RANGE_32V, self.ina.GAIN_1_40MV,
            self.ina.ADC_2SAMP, self.ina.ADC_128SAMP)
        calls = [call(0x05, [0x50, 0x00]), call(0x00, [0x24, 0xff])]
        self.ina._i2c.writeList.assert_has_calls(calls)

    def test_32v_40mv_4_samples_8_samples(self):
        self.ina.configure(
            self.ina.RANGE_32V, self.ina.GAIN_1_40MV,
            self.ina.ADC_4SAMP, self.ina.ADC_8SAMP)
        calls = [call(0x05, [0x50, 0x00]), call(0x00, [0x25, 0x5f])]
        self.ina._i2c.writeList.assert_has_calls(calls)

    def test_32v_40mv_8_samples_16_samples(self):
        self.ina.configure(
            self.ina.RANGE_32V, self.ina.GAIN_1_40MV,
            self.ina.ADC_8SAMP, self.ina.ADC_16SAMP)
        calls = [call(0x05, [0x50, 0x00]), call(0x00, [0x25, 0xe7])]
        self.ina._i2c.writeList.assert_has_calls(calls)

    def test_32v_40mv_32_samples_64_samples(self):
        self.ina.configure(
            self.ina.RANGE_32V, self.ina.GAIN_1_40MV,
            self.ina.ADC_32SAMP, self.ina.ADC_64SAMP)
        calls = [call(0x05, [0x50, 0x00]), call(0x00, [0x26, 0xf7])]
        self.ina._i2c.writeList.assert_has_calls(calls)

    def test_invalid_voltage_range(self):
        with self.assertRaisesRegexp(ValueError, "Invalid voltage range"):
            self.ina.configure(64, self.ina.GAIN_1_40MV)

    def test_max_current_exceeded(self):
        ina = INA219(0.1, 0.5)
        with self.assertRaisesRegexp(ValueError, "Expected current"):
            ina.configure(ina.RANGE_32V, ina.GAIN_1_40MV)

    def test_powerdown(self):
        self.ina.powerdown()
        self.ina._i2c.writeList.assert_called_with(0x00, [0x00, 0x00])

    def test_reset(self):
        self.ina.reset()
        self.ina._i2c.writeList.assert_called_with(0x00, [0x80, 0x00])


class TestRead(unittest.TestCase):

    def setUp(self):
        self.ina = INA219(0.1, 0.4)

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

    def test_read_20ua(self):
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_1_40MV)
        self.ina._i2c.readS16BE = Mock(return_value=1)
        self.assertEqual(self.ina.current(), 0.02)

    def test_read_0ma(self):
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_1_40MV)
        self.ina._i2c.readS16BE = Mock(return_value=0)
        self.assertEqual(self.ina.current(), 0)

    def test_read_negative_ma(self):
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_1_40MV)
        self.ina._i2c.readS16BE = Mock(return_value=-19795)
        self.assertAlmostEqual(self.ina.current(), -395.9, 2)

    def test_read_0mw(self):
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_1_40MV)
        self.ina._i2c.readU16BE = Mock(return_value=0)
        self.assertEqual(self.ina.power(), 0)

    def test_read_1914mw(self):
        self.ina.configure(self.ina.RANGE_16V, self.ina.GAIN_1_40MV)
        self.ina._i2c.readU16BE = Mock(return_value=4785)
        self.assertAlmostEqual(self.ina.power(), 1914.0, 2)

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

if __name__ == '__main__':
    unittest.main()
