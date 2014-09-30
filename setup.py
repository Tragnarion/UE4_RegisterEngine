# Copyright (C) 2014 Tragnarion Studios
#
# UE4 engine registration helper.
#
# Author: Moritz Wundke

from setuptools import setup, find_packages

setup(
    name = 'ue4_registerengine',
    version = '0.1',
    description = 'UE4 engine registration helper',
    author = 'Moritz Wundke',
    packages = find_packages(),
    zip_safe = False,
)