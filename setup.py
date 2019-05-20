from setuptools import setup, find_packages

from version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='reportportal-behave-client',
    packages=find_packages(exclude=[""]),
    package_data={'': ['']},
    version=__version__,
    description='ReportPortal integration client lib',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Adrian Tamas',
    author_email='adi.tamas@outlook.com',
    license='MIT',
    python_requires='>=3',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    url="https://github.com/Adrian-Tamas/reportportal-behave-integration-client-lib",
)
