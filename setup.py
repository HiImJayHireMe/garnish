from distutils.core import setup
from setuptools import find_packages

setup(
    name='garnish-py',
    version='0.0.1',
    packages=find_packages(where='./garnish_py'),
    url='https://github.com/HiImJayHireMe/garnish/',
    license='MIT License',
    author='jay',
    author_email='jjtolton@gmail.com',
    description='Functional Flask microframework'
)
