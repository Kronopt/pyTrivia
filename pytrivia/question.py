#!python
# coding: utf-8

"""
Question class - Represents a question retrieved from OpenTriviaDB
"""

import html


class Question:
    """
    Represents one OpenTriviaDB question.
    Question should have been retrieved in the default encoding, as per the OpenTriviaDB API documentation.

    Attributes
    ----------
    category : str
        Question Category.
    type : str
        Question type (usually 'multiple' or 'boolean').
    difficulty : str
        Question difficulty (usually 'easy', 'medium' or 'hard').
    question : str
        Actual question.
    correct_answer : str
        Correct answer to question.
    incorrect_answers : list
        Incorrect answers to question.
    """

    def __init__(self, category, type, difficulty, question, correct_answer, incorrect_answers):
        """
        Initializes a question from OpenTriviaDB.
        Assumes question was retrieved with default encoding, as specified in the OpenTriviaDB API documentation.

        This class can be easily initialized by passing to it any dictionary contained in the 'results' list of the
        json OpenTriviaDB response.
        ex: Question(**results[0])

        Parameters
        ----------
        category : str
            Question Category.
        type : str
            Question type (usually 'multiple' or 'boolean').
        difficulty : str
            Question difficulty (usually 'easy', 'medium' or 'hard').
        question : str
            Actual question.
        correct_answer : str
            Correct answer to question.
        incorrect_answers : list
            Incorrect answers to question.
        """
        self.category = category
        self.type = type.capitalize()
        self.difficulty = difficulty.capitalize()
        self.question = html.unescape(question)
        self.correct_answer = html.unescape(correct_answer)
        self.incorrect_answers = [html.unescape(incorrect_answer) for incorrect_answer in incorrect_answers]
