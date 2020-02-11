#!python
# coding: utf-8

"""
pyTrivia

Python wrapper for OpenTriviaDB (https://opentdb.com/)
"""

__author__ = 'Pedro HC David, https://github.com/Kronopt'
__credits__ = ['Pedro HC David']
__version__ = '1.0a'
__license__ = 'GPLv3'


from .client import Client
from .question import Question
from .exceptions import NoResults, InvalidParameter, TokenNotFound, TokenEmpty, UnexpectedResponseCode, HttpError
