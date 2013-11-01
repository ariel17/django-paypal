#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Description: TODO
Source: http://stackoverflow.com/questions/3841725/how-to-launch-tests-for-django-reusable-app 
"""
__author__ = "Ariel Gerardo Rios (ariel.gerardo.rios@gmail.com)"


import os
import sys

from django.conf import settings
from django.test.simple import DjangoTestSuiteRunner


DIRNAME = os.path.dirname(__file__)

settings.configure(
    DEBUG=True,
    DATABASE_ENGINE='sqlite3',
    DATABASE_NAME=os.path.join(DIRNAME, 'database.db'),
    INSTALLED_APPS=(
        'paypal.pro',
        'paypal.standard',
        'paypal.standard.pdt',
        'paypal.standard.ipn',
    )
)


if __name__ == '__main__':
    test_runner = DjangoTestSuiteRunner(verbosity=1)
    failures = test_runner.run_tests(['myapp', ])
    if failures:
        sys.exit(failures)
