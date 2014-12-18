import re
from setuptools import setup


version = re.search("__version__ = '([^']+)'",
                    open('blockext/__init__.py').read()).group(1)


setup(name = 'blockext',
      version = version,
      author = 'Tim Radvan, Connor Hudson',
      author_email = 'blob8108@gmail.com',
      url = 'https://github.com/blockext/blockext',
      description = 'Module for writing Scratch 2.0 and Snap! extensions',
      license = 'MIT',
      packages = ['blockext'],
      install_requires = [
          'future >= 0.12',
      ],
      classifiers = [
        "Programming Language :: Python",
      ],
)
 
