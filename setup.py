from setuptools import setup, find_packages

# Read the contents of your requirements file
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='coingeckoapi',
    version='1.0.0',
    author='Nathan Ramos, CFA',
    author_email='nathan.ramos.github@gmail.com',
    description='A Python wrapper for the CoinGecko API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nathanramoscfa/coingeckoapi',
    packages=find_packages(),
    install_requires=required,  # Use the read requirements
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
