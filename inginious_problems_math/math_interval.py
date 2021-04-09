import os
import sys


from inginious.frontend.task_problems import DisplayableProblem
from inginious_problems_math.math_problem import MathProblem, DisplayableMathProblem

from sympy import simplify, sympify, N, E, pi, I, Union, Interval, FiniteSet, EmptySet

PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))
__version__ = "0.1.dev0"
math_format = "[0,2]∪[5,∞)"
problem_type = "math_interval"
math_problem_info = "This problem type is designed for intervals such as \n"\
                    + math_format + ".If you want an equation or a matrix..\n" \
                    "Please refer to other problem types. \n" \
                    "Note: the [] symbols represent inclusion and ()\n" \
                    "symbols represent exclusion.\n" \
                    "Including or excluding infinity is the same.\n" \
                    "It is advised to only ask for a single answer for this\n" \
                    "problem type. If you want, for example, 2 domains for 2\n" \
                    "different functions, please create two subproblems.\n"

class MathIntervalProblem(MathProblem):

    @classmethod
    def get_type(cls):
        return problem_type

    def parse_equation(cls, latex_str):
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

    def parse_interval(cls, latex_interval):
        """parse a single interval such as, for example (a,b] 
        into a Sympy Interval object"""
        borders, left_open, right_open = cls.clear_interval(latex_interval)
        borders = borders.split(',')
        if len(borders) == 1 and left_open == right_open and not left_open: #Consider single element interval such as [5]
            unique_element = cls.parse_element(borders[0])
            return Interval(unique_element,unique_element)
        if len(borders) != 2:
            return EmptySet
        left_element = borders[0]
        right_element = borders[1]
        leftBorder = cls.parse_element(left_element)
        rightBorder = cls.parse_element(right_element)
        return Interval(leftBorder, rightBorder, left_open, right_open)

    def clear_interval(cls, latex_interval):
        """Takes an interval formated such as (a,b] and computes information on
        inclusion exclusions then removes the ( and [ symbols """
        left_open = latex_interval.startswith("\\left(") or latex_interval.startswith('(')
        right_open = latex_interval.endswith("\\right)") or latex_interval.endswith(')')
        if latex_interval.startswith("\\left(") or latex_interval.startswith("\\left["):
            latex_interval = latex_interval[6:]
        elif latex_interval.startswith('(') or latex_interval.startswith('['):
            latex_interval = latex_interval[1:]
        if latex_interval.endswith("\\right)") or latex_interval.endswith("\\right]"):
            latex_interval=latex_interval[:-7]
        elif latex_interval.endswith(')') or latex_interval.endswith(']'):
            latex_interval = latex_interval[:-1]
        return [latex_interval, left_open, right_open]

    def parse_element(cls, element):
        """Parse a single element and returns it as a Sympy expression
        Called on every intervals borders"""
        element = element.replace("∞", str(sys.maxsize))
        element = element.replace("\\infty", str(sys.maxsize))
        return MathProblem.parse_equation(cls, element)


    def is_equal(self, eq1, eq2):
        """Redfines the is_equal to only accept Intervals and Unions"""
        #Intervals
        if type(eq1) in [Interval, Union, FiniteSet, EmptySet] and type(eq2) in [Interval, Union, FiniteSet, EmptySet]:
            return eq1 == eq2 or simplify(eq1) == simplify(eq2)
        return False

class DisplayableMathIntervalProblem(MathIntervalProblem, DisplayableProblem):
    """ A displayable math problem """

    def __init__(self, problemid, content, translations, taskfs):
        MathIntervalProblem.__init__(self, problemid, content, translations, taskfs)

    @classmethod
    def get_type_name(self, language):
        return problem_type

    def show_input(self, template_helper, language, seed):
        return DisplayableMathProblem.show_input(self, template_helper, language, seed, format=math_format)

    @classmethod
    def show_editbox(cls, template_helper, key, language):
        return DisplayableMathProblem.show_editbox(template_helper, key, language, problem_type=problem_type, problem_type_info=math_problem_info)

    @classmethod
    def show_editbox_templates(cls, template_helper, key, language):
        return DisplayableMathProblem.show_editbox_templates(template_helper, key, language, format=math_format)
