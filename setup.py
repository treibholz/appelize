#!/usr/bin/env python

from distutils.core import setup as _setup

if __name__ == '__main__':
    _setup(
        name = 'appelize',
        version = '0.3.2',
        description = 'This program "appelizes" your music into a separate directory.',
        author = 'Klaus Umbach',
        author_email = 'klaus-github@uxix.de',
        url = 'https://github.com/treibholz/appelize',
        scripts = [
            'appelize',
        ],
    )

# vim:foldmethod=marker:tabstop=4:autoindent:shiftwidth=4:expandtab:smarttab:softtabstop=4
