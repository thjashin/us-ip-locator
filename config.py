#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# @file: config.py

import os


DEBUG = True

# LOG_FILE defines the main log file for the website
LOG_FILE = os.path.join(os.path.dirname(__file__), 'website.log')

# WEBSITE_LOGGING configures the logging facility of Python for the website.
WEBSITE_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        },
    },
    'handlers': {
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'verbose',
            'filename': LOG_FILE,
            'maxBytes': 204800,
            'backupCount': 3,
        },
    },
    'loggers': {
        '': {
            'handlers': ['default'],
            'level': 'WARNING',
        },
    }
}
