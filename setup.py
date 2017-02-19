try:
    # Try using ez_setup to install setuptools if not already installed.
    from ez_setup import use_setuptools
    use_setuptools()
except ImportError:
    # Ignore import error and assume Python 3 which already has setuptools.
    pass

from setuptools import setup

DESC = ('Library that supports the INA219 current and '
        'power monitor from Texas Instruments.')

# Define required packages.
requires = ['Adafruit_GPIO', 'mock']

setup(name='pi-ina219',
      version='1.1.0',
      author='Chris Borrill',
      author_email='chris.borrill@gmail.com',
      description=DESC,
      license='MIT',
      url='https://github.com/chrisb/pi_ina219/',
      install_requires=requires,
      test_suite='tests',
      py_modules=['ina219'])
