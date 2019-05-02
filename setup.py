from setuptools import setup, find_packages

from version import __version__


setup(
    name='reportportal-behave-client',
    packages=find_packages(exclude=[""]),
    package_data={'': ['']},
    version=__version__,
    description='ReportPortal integration client lib',
    author='Adrian Tamas',
    author_email='adi.tamas@outlook.com',
    license='MIT',
    python_requires='>=3'
)
