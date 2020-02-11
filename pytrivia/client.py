#!python
# coding: utf-8

"""
Client - Communicates with OpenTriviaDB API.
"""

import requests
from .question import Question
from .exceptions import NoResults, InvalidParameter, TokenNotFound, TokenEmpty, UnexpectedResponseCode, HttpError
from . import __version__


class Client:
    """
    pyTrivia client.
    Handles all the communication with the OpenTriviaDB API, including token management.

    Attributes
    ----------
    MAIN_URL : str
        OpenTriviaDB domain.
    API_URL : str
        Base OpenTriviaDB API url.
    TOKEN_URL : str
        Base OpenTriviaDB token handler url.
    ALL_CATEGORIES_URL : str
        Category lookup url.
    CATEGORIES_COUNT_URL : str
        Question count lookup url.
    ALL_CATEGORIES_COUNTS_URL : str
        Total question count lookup url.
    HTTP_HEADER : dict
        HTTP header sent with every request.
    token : str
        Token in use.
    categories : dict
        Categories and respective ids.
    """

    MAIN_URL = 'https://opentdb.com/'
    API_URL = MAIN_URL + 'api.php'
    TOKEN_URL = MAIN_URL + 'api_token.php'
    ALL_CATEGORIES_URL = MAIN_URL + 'api_category.php'
    CATEGORIES_COUNT_URL = MAIN_URL + 'api_count.php'
    ALL_CATEGORIES_COUNTS_URL = MAIN_URL + 'api_count_global.php'

    HTTP_HEADER = {
        'User-Agent': 'pyTrivia/' + __version__,
        'Content-Type': 'application/json'
    }

    def __init__(self):
        """
        Initializes the pyTrivia client.
        Performs 2 requests to the OpenTriviaDB API:
            - Token request
            - Categories request

        Raises
        ------
        ValueError
            If the HTTP response body does not contain valid json (request.json error).
        HttpError
            If the HTTP code is not 200 OK.
        NoResults, InvalidParameter, TokenNotFound, TokenEmpty, UnexpectedResponseCode
            If the OpenTriviaDB response code is not 0.
        """
        self.token = self._get_token()
        self.categories = self._get_categories()

    def _get_token(self, reset=False):
        """
        Retrieves an OpenTriviaDB session token.

        Parameters
        ----------
        reset : bool, optional
            Token is reset if True, a new token is retrieved otherwise.

        Returns
        -------
        str
            OpenTriviaDB session token.

        Raises
        ------
        ValueError
            If the HTTP response body does not contain valid json (request.json error).
        HttpError
            If the HTTP code is not 200 OK.
        NoResults, InvalidParameter, TokenNotFound, TokenEmpty, UnexpectedResponseCode
            If the OpenTriviaDB response code is not 0.
        """
        if reset:
            token_url = '%s?command=reset&token=%s' % (self.TOKEN_URL, self.token)
        else:
            token_url = '%s?command=request' % self.TOKEN_URL
        json = self._request_resource(token_url)
        return json['token']

    def _get_categories(self):
        """
        Retrieves all OpenTriviaDB categories and respective ids.

        Raises
        ------
        ValueError
            If the HTTP response body does not contain valid json (request.json error).
        HttpError
            If the HTTP code is not 200 OK.
        NoResults, InvalidParameter, TokenNotFound, TokenEmpty, UnexpectedResponseCode
            If the OpenTriviaDB response code is not 0.

        Returns
        -------
        dict
            OpenTriviaDB categories (keys) and ids (values).

        Raises
        ------
        ValueError
            If the HTTP response body does not contain valid json (request.json error).
        HttpError
            If the HTTP code is not 200 OK.
        NoResults, InvalidParameter, TokenNotFound, TokenEmpty, UnexpectedResponseCode
            If the OpenTriviaDB response code is not 0.
        """
        json = self._request_resource(self.ALL_CATEGORIES_URL)
        # Assumes json is structured as per the OpenTriviaDB documentation.
        # Any error that arises from "wrong" dictionary keys is because json response was
        # altered by OpenTriviaDB in the meanwhile.
        categories = {category['name']: category['id'] for category in json['trivia_categories']}
        return categories

    def _request_resource(self, url):
        """
        Performs an HTTP request to an OpenTriviaDB url and retrieves the json response.

        Parameters
        ----------
        url : str
            The HTTP request will be made to this url.

        Returns
        -------
        dict
            Parsed json response.

        Raises
        ------
        ValueError
            If the HTTP response body does not contain valid json (request.json error).
        HttpError
            If the HTTP code is not 200 OK.
        NoResults, InvalidParameter, TokenNotFound, TokenEmpty, UnexpectedResponseCode
            If the OpenTriviaDB response code is not 0.
        """
        response = requests.get(url, headers=self.HTTP_HEADER)
        if response.status_code != 200:
            raise HttpError(response.status_code, response.reason)
        json = response.json()
        # Assumes json is structured as per the OpenTriviaDB documentation.
        # Any error that arises from "wrong" dictionary keys is because json response was
        # altered by OpenTriviaDB in the meanwhile.
        response_code = json['response_code']
        if response_code == 1:
            raise NoResults()
        elif response_code == 2:
            raise InvalidParameter()
        elif response_code == 3:
            raise TokenNotFound()
        elif response_code == 4:
            raise TokenEmpty()
        elif response_code != 0:
            raise UnexpectedResponseCode(str(response_code))
        return json
