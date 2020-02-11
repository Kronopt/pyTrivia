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
    categories : tuple
        All available question categories.
    difficulties : tuple
        All available question difficulties.
    types : tuple
        All available question types.

    Methods
    -------
    get_questions(number=1, category=None, difficulty=None, _type=None)
        Retrieves questions from the OpenTriviaDB API.

    Raises
    ------
    TypeError
        When calling get_questions, if number is not and int between 1 and 50.
        When calling get_questions, if category is not a str in self.categories.
        When calling get_questions, if difficulty is not a str in self.difficulties.
        When calling get_questions, if _type is not a str in self.types.
    ValueError
        When calling __init__, get_questions, if the HTTP response body does not contain valid json
        (request.json error).
    HttpError
        When calling __init__, get_questions, if the HTTP code is not 200 OK.
    NoResults, InvalidParameter, TokenNotFound, TokenEmpty, UnexpectedResponseCode
        When calling __init__, get_questions, if the OpenTriviaDB response code is not 0.
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
            - Available categories request

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
        self._categories_and_ids = self._get_categories()
        self._difficulties = ('easy', 'medium', 'hard')
        self._types = ('multiple', 'boolean')

    @property
    def categories(self):
        """
        Shows all available categories.

        Returns
        -------
        tuple
            Tuple of all valid categories.
        """
        return tuple(self._categories_and_ids)  # keys only, which are the category names

    @property
    def difficulties(self):
        """Returns _difficulties. All available difficulties."""
        return self._difficulties

    @property
    def types(self):
        """Returns _types. All available types."""
        return self._types

    def get_questions(self, number=1, category=None, difficulty=None, _type=None):
        """
        Retrieves questions from OpenTriviaDB.

        Parameters
        ----------
        number : int, optional
            Number of questions to retrieve (0 < number <= 50).
        category : str or None, optional
            Question category. One of self.categories.
        difficulty : str or None, optional
            Question difficulty. One of self._difficulties
        _type : str or None, optional
            Type of question. One of self._types

        Returns
        -------
        list(Question)

        Raises
        ------
        TypeError
            If number is not and int between 1 and 50.
            If category is not a str in self.categories.
            If difficulty is not a str in self._difficulties.
            If _type is not a str in self._types.
        ValueError
            If the HTTP response body does not contain valid json (request.json error).
        HttpError
            If the HTTP code is not 200 OK.
        NoResults, InvalidParameter, TokenNotFound, TokenEmpty, UnexpectedResponseCode
            If the OpenTriviaDB response code is not 0.
        """
        # number
        if not (isinstance(number, int) and (0 < number <= 50)):
            raise TypeError('Parameter \'number\' must be an int between 1 and 50')
        # category
        if category is None:
            category = ''
        elif category in self._categories_and_ids:
            category = '&category=%i' % self._categories_and_ids[category]
        else:
            raise TypeError('Parameter \'category\' must be an existing category. '
                            'Call Client.category to check available categories.')
        # difficulty
        if difficulty is None:
            difficulty = ''
        elif difficulty in self._difficulties:
            difficulty = '&difficulty=%s' % difficulty
        else:
            raise TypeError('Parameter \'difficulty\' must be one of: %s' % ', '.join(self._difficulties))
        # _type
        if _type is None:
            _type = ''
        elif _type in self._types:
            _type = '&type=%s' % _type
        else:
            raise TypeError('Parameter \'_type\' must be one of: %s' % ', '.join(self._types))

        api_url = '%s?amount=%i%s%s%s&token=' % (self.API_URL, number, category, difficulty, _type)

        # handle token
        try:
            json = self._request_resource(api_url + self.token)
        except TokenNotFound:  # get a new token
            self.token = self._get_token()
            # if this throws another TokenNotFound, something is up with the API...
            json = self._request_resource(api_url + self.token)
        except TokenEmpty:  # reset token
            self.token = self._get_token(reset=True)
            # if this throws another TokenEmpty, something is up with the API...
            json = self._request_resource(api_url + self.token)
        return [Question(**question) for question in json['results']]

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
        json = self._request_resource(self.ALL_CATEGORIES_URL, response_code=False)
        # Assumes json is structured as per the OpenTriviaDB documentation.
        # Any error that arises from "wrong" dictionary keys is because json response was
        # altered by OpenTriviaDB in the meanwhile.
        categories = {category['name']: category['id'] for category in json['trivia_categories']}
        return categories

    def _request_resource(self, url, response_code=True):
        """
        Performs an HTTP request to an OpenTriviaDB url and retrieves the json response.

        Parameters
        ----------
        url : str
            The HTTP request will be made to this url.
        response_code : bool
            Whether to check for response_code or not

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
        if response_code:
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
