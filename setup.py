import os
import re
from setuptools import setup, find_packages


# Function to extract the version from __version__.py
def get_version():
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, '__version__.py'), encoding='utf-8') as f:
        version_file_contents = f.read()
    # Use regular expression to extract version string
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file_contents, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


# Read the contents of your requirements file
with open('requirements.txt', encoding='utf-8') as f:
    required = f.read().splitlines()

# Open and read the README file for the long description
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='pycgapi',
    version=get_version(),
    author='Nathan Ramos, CFA',
    author_email='nathan.ramos.github@gmail.com',
    description='A Python wrapper for the CoinGecko API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nathanramoscfa/pycgapi',
    packages=find_packages(),
    install_requires=required,
    python_requires='>=3.11',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3 :: Only',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
