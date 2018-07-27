# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

#with open('docs/requirements.txt') as f:
#    required = f.read().splitlines()

setup(
    name='activity-monitor',
    version='0.13.4',
    author=u'Tim Baxter',
    author_email='mail.baxter@gmail.com',
    url='http://github.com/tBaxter/activity-monitor',
    license='MIT',
    description='A sort of tumblelog-y thing heavily based on code I got somewhere.',
    long_description=open('README.md').read(),
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
)
