#!/usr/bin/env python3

from setuptools import setup, find_packages

with open("requirements.txt", "r") as reqs:
    requirements = reqs.readlines()

setup(
    name="scuffed-bot",
    version="0.1.2-alpha",
    description="scuffed-cloud discord server bot",
    author="Philip Bove",
    install_requires=requirements,
    author_email="phil@bove.online",
    packages=find_packages(),
    scripts=["bin/scuffed-bot"],
)
