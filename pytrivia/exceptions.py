#!python
# coding: utf-8

"""
OpenTriviaDB related exceptions.
"""


class OpenTriviaDBException(Exception):
    """Base exception class."""

    def __str__(self):
        return '[Code %i] %s' % (self.code, self.message)


class NoResults(OpenTriviaDBException):
    """
    Could not return results.
    The OpenTriviaDB API doesn't have enough questions for your query.
    Ex: Asking for 50 Questions in a Category that only has 20.

    Attributes
    ----------
    code : int
        Exception code (as in OpenTriviaDB).
    message : str
        Exception message.
    """
    def __init__(self):
        self.code = 1
        self.message = 'Could not return results. The OpenTriviaDB API doesn\'t have enough questions for your query.'


class InvalidParameter(OpenTriviaDBException):
    """
    Contains an invalid parameter.
    Arguments passed in aren't valid.
    Ex: Amount = Five.

    Attributes
    ----------
    code : int
        Exception code (as in OpenTriviaDB).
    message : str
        Exception message.
    """
    def __init__(self):
        self.code = 2
        self.message = 'Contains an invalid parameter. Arguments passed in aren\'t valid.'


class TokenNotFound(OpenTriviaDBException):
    """
    Session Token does not exist.

    Attributes
    ----------
    code : int
        Exception code (as in OpenTriviaDB).
    message : str
        Exception message.
    """
    def __init__(self):
        self.code = 3
        self.message = 'Session Token does not exist.'


class TokenEmpty(OpenTriviaDBException):
    """
    Session Token has returned all possible questions for the specified query.
    Resetting the Token is necessary.

    Attributes
    ----------
    code : int
        Exception code (as in OpenTriviaDB).
    message : str
        Exception message.
    """
    def __init__(self):
        self.code = 4
        self.message = 'Session Token has returned all possible questions for the specified query. ' \
                       'Resetting the Token is necessary.'


class UnexpectedResponseCode(OpenTriviaDBException):
    """
    Unexpected OpenTriviaDB response code received (not defined in the OpenTriviaDB documentation).

    Attributes
    ----------
    code : str
        Exception code.
    message : str
        Exception message.
    """
    def __init__(self, code):
        self.code = code
        self.message = 'Unexpected OpenTriviaDB response code received: %s' % code

    def __str__(self):
        return self.message


class HttpError(OpenTriviaDBException):
    """
    HTTP status code received was not 200 OK.

    Attributes
    ----------
    status_code : int
        HTTP status code.
    message : str
        HTTP text corresponding to status code.
    """
    def __init__(self, status_code, message):
        self.status_code = status_code
        self.message = message

    def __str__(self):
        return 'Received HTTP status code %i: %s. Expected 200: OK' % (self.status_code, self.message)
