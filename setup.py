#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pathlib

import setuptools

from xappt.utilities import git_tools, setup_helpers

PROJECT_PATH = pathlib.Path(__file__).absolute().parent
VERSION_PATH = PROJECT_PATH.joinpath("xappt_qt", "__version__.py")
README_PATH = PROJECT_PATH.joinpath("README.md")

os.chdir(PROJECT_PATH)


def main():
    if git_tools.is_dirty(PROJECT_PATH):
        print("Local repository is not clean")
        if not setup_helpers.ask("Proceed anyway?"):
            return

    if not setup_helpers.cleanup_build_files(PROJECT_PATH):
        return

    install_requires = list(setup_helpers.requirements(PROJECT_PATH))

    setup_dict = {
        'name': 'xappt_qt',
        'version': setup_helpers.get_version(VERSION_PATH),
        'author': 'Christopher Montesano',
        'author_email': 'cmdev.00+xappt@gmail.com',
        'url': 'https://github.com/cmontesano/xappt_qt',
        'description': 'Qt/PyQt5 interface plugin for xappt.',
        'long_description': README_PATH.read_text("utf8"),
        'long_description_content_type': 'text/markdown',
        'packages': setup_helpers.build_package_list('xappt_qt'),
        'include_package_data': True,
        'zip_safe': False,
        'license': 'MIT',
        'platforms': 'any',
        'python_requires': '>=3.7, <4',
        'install_requires': install_requires,
        'classifiers': [
            'Topic :: Utilities',
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
        ],
        'entry_points': {
            'console_scripts': [
                'xappt-qt=xappt_qt.main:main',
            ],
        },
    }

    commit_id = git_tools.commit_id(PROJECT_PATH, short=True)
    setup_helpers.update_build(VERSION_PATH, commit_id)
    setuptools.setup(**setup_dict)
    setup_helpers.update_build(VERSION_PATH, "dev")


if __name__ == '__main__':
    main()
