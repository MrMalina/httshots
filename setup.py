#!/usr/bin/env python
#
# Copyright 2015-2025 MrMalina. Subject to the MIT license.
# See the included LICENSE file for more information.
#

import sys
import setuptools

import httshots

print(setuptools.find_packages(where='src'))

setuptools.setup(
    name='httshots',
    version=httshots.pkg_version,
    author='MrMalina',
    author_email='python.mr.malina@yandex.ru',
    url='https://github.com/MrMalina/httshots',
    description='Heroes of the Storm Twitch bot',
    packages = setuptools.find_packages(),
    include_package_data=True,
    package_data={
        "httshots": [
            "addons/*",
            "bot/*",
            "data/**/*",
            "config/**/*", 
            "files/**/*",
            "parser/*",
            "visual/*",
            "files/data/.placeholder",
            "readme.md",
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Games/Entertainment :: Real Time Strategy',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Archiving',
        'Topic :: Utilities',
    ],
    install_requires=['mpyq >= 0.2.5', 'six >= 1.14.0',
                      'configobj', 'imgurpython',
                      'Pillow', 'mpyq',
                      'twitchio[starlette]',
                      'asqlite @ git+https://github.com/Rapptz/asqlite.git',
                      'heroprotocol @ git+https://github.com/MrMalina/heroprotocol'
                     ],
    python_requires='>=3.12',
)