try:
    # Try using ez_setup to install setuptools if not already installed.
    from ez_setup import use_setuptools
    use_setuptools()
except ImportError:
    # Ignore import error and assume Python 3 which already has setuptools.
    pass

from setuptools import setup, find_packages

import sys

# Define required packages.
requires = ['Adafruit_GPIO', 'mock']
# Assume spidev is required on non-windows & non-mac platforms (i.e. linux).
if sys.platform != 'win32' and sys.platform != 'darwin':
    requires.append('spidev')

setup(name              = 'pi-ina219',
      version           = '1.0.0',
      author            = 'Chris Borrill',
      author_email      = 'chris.borrill@gmail.com',
      description       = 'Library that supports the INA219 current and power monitor from Texas Instruments.',
      license           = 'MIT',
      url               = 'https://github.com/chrisb/pi-ina219/',
      install_requires  = requires,
      test_suite        = 'tests',
      packages          = find_packages())
