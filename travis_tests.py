import unittest

if __name__ == '__main__':
    import pynetworking
    from pynetworking.Logging import logger
    import sys

    logger.setLevel(40)
    test_loader = unittest.TestLoader()
    test_suite = test_loader.discover('pynetworking.tests', pattern='test_*.py')
    test_suite._tests.pop(1)    # Exclude Communication tests
    runner = unittest.TextTestRunner(stream=sys.stderr)
    runner.run(test_suite)
