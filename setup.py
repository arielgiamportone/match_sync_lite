from setuptools import setup, find_packages

setup(
    name="match_sync_lite",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'pandas',
        'numpy',
        'matplotlib',
        'faker'
    ],
)