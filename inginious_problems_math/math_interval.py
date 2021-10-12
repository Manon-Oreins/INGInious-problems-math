import os
import sys

from inginious.frontend.task_problems import DisplayableProblem
from inginious_problems_math.math_problem import MathProblem, DisplayableMathProblem

from sympy import simplify, sympify, N, E, pi, I, Union, Interval, FiniteSet, EmptySet

PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))
PATH_TO_TEMPLATES = os.path.join(PATH_TO_PLUGIN, "templates")
math_format = "[0,2]∪[5,∞)"
problem_type = "math_interval"


class MathIntervalProblem(MathProblem):

    @classmethod
    def get_type(cls):
        return problem_type

    @classmethod
    def parse_answer(cls, latex_str):
        """Returns the given input in the form of a Sympy Union object
        it starts by clearing the inputs then converting each subinterval
        before joining them together based on unions"""
        wrong_domain_intervals = latex_str.split('\\cup')
        correct_domain_intervals = []
        for wrong_format_interval in wrong_domain_intervals:
            correct_domain_interval = cls.parse_interval(wrong_format_interval)
            correct_domain_intervals.append(correct_domain_interval)
        domain = EmptySet
        for interval in correct_domain_intervals:
            domain = Union(domain, interval)
        return domain

    @classmethod
    def parse_interval(cls, latex_interval):
        """parse a single interval such as, for example (a,b] 
        into a Sympy Interval object"""
        borders, left_open, right_open = cls.sanitize_interval_input(latex_interval)
        borders = borders.split(',')
        if len(borders) == 1 and left_open == right_open and not left_open: #Consider single element interval such as [5]
            unique_element = cls.parse_element(borders[0])
            return Interval(unique_element, unique_element)
        if len(borders) != 2:
            raise ValueError("Correct intervals should contain 2 borders")
        left_element = borders[0]
        right_element = borders[1]
        leftBorder = cls.parse_element(left_element)
        rightBorder = cls.parse_element(right_element)
        return Interval(leftBorder, rightBorder, left_open, right_open)

    @classmethod
    def sanitize_interval_input(cls, latex_input):
        """Takes an interval formated such as (a,b] and computes information on
        inclusion exclusions then removes the ( and [ symbols """
        left_open = latex_input.startswith("\\left(") or latex_input.startswith('(')
        right_open = latex_input.endswith("\\right)") or latex_input.endswith(')')
        if latex_input.startswith("\\left(") or latex_input.startswith("\\left["):
            latex_input = latex_input[6:]
        elif latex_input.startswith('(') or latex_input.startswith('['):
            latex_input = latex_input[1:]
        if latex_input.endswith("\\right)") or latex_input.endswith("\\right]"):
            latex_input=latex_input[:-7]
        elif latex_input.endswith(')') or latex_input.endswith(']'):
            latex_input= latex_input[:-1]
        return [latex_input, left_open, right_open]

    @classmethod
    def parse_element(cls, element):
        """Parse a single element and returns it as a Sympy expression
        Called on every intervals borders"""
        element = element.replace("∞", str(sys.maxsize))
        element = element.replace("\\infty", str(sys.maxsize))
        element = element.replace("\\infinity", str(sys.maxsize))
        return MathProblem.parse_answer(element)

    def is_equal(self, eq1, eq2):
        """Redfines the is_equal to only accept Intervals and Unions"""
        #Intervals
        if type(eq1) in [Interval, Union, FiniteSet, EmptySet] and type(eq2) in [Interval, Union, FiniteSet, EmptySet]:
            return eq1 == eq2 or simplify(eq1) == simplify(eq2)
        elif eq1 == EmptySet and eq2 == EmptySet:
            return True
        return False

class DisplayableMathIntervalProblem(MathIntervalProblem, DisplayableProblem):
    """ A displayable math problem """

    # Some class attributes
    html_file = "math_edit.html"

    def __init__(self, problemid, content, translations, taskfs):
        MathIntervalProblem.__init__(self, problemid, content, translations, taskfs)

    @classmethod
    def get_type_name(self, language):
        return "math-interval"

    def show_input(self, template_helper, language, seed):
        return DisplayableMathProblem.show_input(self, template_helper, language, seed, format=math_format)

    @classmethod
    def show_editbox(cls, template_helper, key, language):
        return template_helper.render(cls.html_file, template_folder=PATH_TO_TEMPLATES, key=key,
                                      problem_type=problem_type, friendly_type=cls.get_type_name(language))
    @classmethod
    def show_editbox_templates(cls, template_helper, key, language):
        return DisplayableMathProblem.show_editbox_templates(template_helper, key, language, format=math_format)
