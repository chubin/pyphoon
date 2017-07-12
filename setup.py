from setuptools import setup, find_packages
from pyphoon import __VERSION__
def install_requires():
    with open('requirements') as reqs:
        install_req = [
            line for line in reqs.read().split('\n')
        ]
    return install_req


def readme():
    with open("README.md") as f:
        return f.read()


setup(
    name="pyphoon",
    url="https://github.com/chubin/pyphoon",
    version=__VERSION__,
    description="ASCII Art Phase of the Moon (Python version)",
    long_description=readme(),
    keywords="pyphoon",
    author="chubin",
    packages=find_packages(),
    install_requires=install_requires(),
    scripts=['bin/pyphoon'],
    include_package_data=True
)