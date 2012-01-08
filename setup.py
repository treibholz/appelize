#!/usr/bin/env python
from distutils import setup

if __name__ == '__main__':
    setup(
        name = 'appelize',
        version = '0.3',
        description = 'This program "appelizes" your music into a separate directory.',
        author = 'Klaus Umbach',
        author_email = '',
        url = 'klaus-github@uxix.de',
        scripts = [
            'appelize',
        ],
    )
