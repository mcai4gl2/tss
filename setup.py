import logging
import sys
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        logging.basicConfig(format='%(asctime)s %(levelname)s %(name)s %(message)s', level='DEBUG')

        # import here, cause outside the eggs aren't loaded
        import pytest

        args = [self.pytest_args] if isinstance(self.pytest_args, basestring) else list(self.pytest_args)
        args.extend(['--cov', 'tss',
                     '--cov-report', 'html',
                     '-x', 'tests'
                     ])
        errno = pytest.main(args) #@UndefinedVariable
        sys.exit(errno)

setup(
      name='tss',
      version='0.0.1',
      packages=find_packages(),
      cmdclass={'test': PyTest},
      setup_requires=[],
      install_requires=['numpy', 'pandas', 'pymongo'],
      tests_require=['pytest', 'mock', 'pytest-cov', 'mock', 'lettuce']
      )