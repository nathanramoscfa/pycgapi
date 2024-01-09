from setuptools import setup, find_packages

# Read the contents of your requirements file
with open('requirements.txt', encoding='utf-8') as f:
    required = f.read().splitlines()

# Open and read the README file for the long description
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='cgapi',
    version='0.1.0',
    author='Nathan Ramos, CFA',
    author_email='nathan.ramos.github@gmail.com',
    description='A Python wrapper for the CoinGecko API',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nathanramoscfa/cgapi',
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
