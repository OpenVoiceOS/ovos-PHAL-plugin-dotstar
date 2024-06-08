#!/usr/bin/env python3
import os

from setuptools import setup

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


def required(requirements_file):
    """ Read requirements file and remove comments and empty lines. """
    with open(os.path.join(BASEDIR, requirements_file), 'r') as f:
        requirements = f.read().splitlines()
        if 'MYCROFT_LOOSE_REQUIREMENTS' in os.environ:
            print('USING LOOSE REQUIREMENTS!')
            requirements = [r.replace('==', '>=').replace(
                '~=', '>=') for r in requirements]
        return [pkg for pkg in requirements
                if pkg.strip() and not pkg.startswith("#")]


PLUGIN_ENTRY_POINT = 'ovos-PHAL-plugin-dotstar=ovos_PHAL_plugin_dotstar:DotStarLedControlPlugin'
setup(
    name='ovos-PHAL-plugin-dotstar',
    version='0.0.1',
    description='An OVOS PHAL plugin to control DotStar type LEDs',
    url='https://github.com/builderjer/ovos-PHAL-plugin-dotstar',
    author='builderjer',
    author_email='builderjer@gmail.com',
    license='MIT',
    packages=['ovos_PHAL_plugin_dotstar'],
    package_data={'': package_files('ovos_PHAL_plugin_dotstar')},
    install_requires=required("requirements.txt"),
    zip_safe=True,
    include_package_data=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Text Processing :: Linguistic',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11'
    ],
    entry_points={'ovos.plugin.phal': PLUGIN_ENTRY_POINT}
)
