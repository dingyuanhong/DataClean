#!/usr/bin/env


from setuptools import find_packages, setup

fp_requires = open('requirements.txt');
requires = [];
try:
    line = fp_requires.readline();
    requires.append(line);
finally:


setup(
    name = 'dataclean',
    description = "",
    long_description = "",
    platforms = "any",
    author="",
    author_email="dingyuanhong.2008@163.com",
    url="https://www.baidu.com/",
    license = "MIT",
    packages=find_packages(),
    install_requires = requires
)