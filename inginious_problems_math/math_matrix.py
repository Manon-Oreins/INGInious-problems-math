import os

from inginious.frontend.task_problems import DisplayableProblem
from inginious_problems_math.math_problem import MathProblem, DisplayableMathProblem

from sympy import Matrix

PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))
__version__ = "0.1.dev0"
problem_type = "math_matrix"
math_format = "matrix: a,b:c,d  vector: a,b,c"
math_problem_info = "This problem type is designed for matrix such as \n"\
                    "[a,b:c,d] and vectors such as [a,b,c].\n" \
                    "Elements must be mathematical\n" \
                    "expressions or numerical values. \n" \
                    "If you want an equation or intervals...\n" \
                    "Please refer to other problem types.\n" \
                    "Note: Simply use : to design a matrix or don't \n" \
                    "if you want to design a vector.\n" \
                    "[] symbols can be added or removed around \n" \
                    "the entire matrix or vector, such as [a,b:c,d] \n" \
                    "or a,b:c,d without impact.\n" \
                    "Vectors of size 2 such as [a,b] are perfect \n" \
                    "for cartesian points and size 3 such as [a,b,c]\n" \
                    "for spatial points."

class MathMatrixProblem(MathProblem):

    @classmethod
    def get_type(cls):
        return problem_type

    def parse_equation(cls, latex_str):
        """Redefines the parse_equation to parse each element of each line"""
        latex_str = latex_str.replace('\\left[', '')
        latex_str = latex_str.replace('\\right]', '')
        latex_str_tab = latex_str.split(':')
        return Matrix(list(map(cls.parse_line,latex_str_tab)))

    def parse_line(cls, latex_str):
        """Parse each element of a line"""
        latex_str_tab = latex_str.split(',')
        return list(map(cls.parse_element,latex_str_tab))

    def parse_element(cls, latex_str):
        """Parse a single element"""
        return MathProblem.parse_equation(cls, latex_str)

    def is_equal(self, matrix1, matrix2):
        """Refefines the is_equal method to compare two matrix by comparing lines one by one"""
        return matrix1 == matrix2

    def check_len(self, student_answer, correct_answer):
        """Check if the number of answers (matrix) is correct. Also checks if the matrix sizes are correct."""
        if len(correct_answer) != len(student_answer):
            message = "Expected {} answers".format(len(correct_answer))
            return [False, message]
        for i in range(0, len(correct_answer)):
            if student_answer[i].shape != correct_answer[i].shape:
                sizes = list(map(lambda o: o.shape, correct_answer))
                message = "Expected " + str(len(correct_answer)) + " answers of size " + str(sizes)
                return [False, message]
        return [True, "ok"]

    def sort(self, answers):
        """Redefines the sorting method to sort matrix in case of multiple matrix asked"""
        return sorted(answers, key=lambda x: self.compare(x))

    def compare(self, answer):
        """Compare matrix based on their int representations for ordering. This is only useful if multiple answers (matrix) are asked"""
        int_representation = [ord(c) for c in str(answer)]
        s = [str(i) for i in int_representation]
        res = int("".join(s))
        return float(str(len(answer)) + "." + str(res))


class DisplayableMathMatrixProblem(MathMatrixProblem, DisplayableProblem):
    """ A displayable math problem """

    def __init__(self, problemid, content, translations, taskfs):
        MathMatrixProblem.__init__(self, problemid, content, translations, taskfs)

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
