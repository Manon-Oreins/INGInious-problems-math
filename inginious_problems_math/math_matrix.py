import os

from inginious.frontend.task_problems import DisplayableProblem
from inginious_problems_math.math_problem import MathProblem, DisplayableMathProblem

from sympy import Matrix
from sympy import simplify

PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))
PATH_TO_TEMPLATES = os.path.join(PATH_TO_PLUGIN, "templates")
problem_type = "math_matrix"
math_format = "matrix: a,b:c,d  vector: a,b,c"


class MathMatrixProblem(MathProblem):

    @classmethod
    def get_type(cls):
        return problem_type

    @classmethod
    def parse_answer(cls, latex_str):
        """Redefines the parse_answer to parse each element of each line"""
        latex_str = latex_str.replace('\\left[', '')
        latex_str = latex_str.replace('\\right]', '')
        latex_str_tab = latex_str.split(':')
        return Matrix(list(map(cls.parse_line,latex_str_tab)))

    @classmethod
    def parse_line(cls,latex_str):
        """Parse each element of a line"""
        latex_str_tab = latex_str.split(',')
        return list(map(cls.parse_element, latex_str_tab))

    @classmethod
    def parse_element(cls, latex_str):
        """Parse a single element"""
        # Needs simplify because the parser of MathProblem doesn't do any
        return simplify(MathProblem.parse_answer(latex_str))

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

    # Some class attributes
    html_file = "math_edit.html"

    def __init__(self, problemid, content, translations, taskfs):
        MathMatrixProblem.__init__(self, problemid, content, translations, taskfs)

    @classmethod
    def get_type_name(self, language):
        return "math-matrix"

    def show_input(self, template_helper, language, seed):
        return DisplayableMathProblem.show_input(self, template_helper, language, seed, format=math_format)

    @classmethod
    def show_editbox(cls, template_helper, key, language):
        return template_helper.render(cls.html_file, template_folder=PATH_TO_TEMPLATES, key=key,
                                      problem_type=problem_type, friendly_type=cls.get_type_name(language))

    @classmethod
    def show_editbox_templates(cls, template_helper, key, language):
        return DisplayableMathProblem.show_editbox_templates(template_helper, key, language, format=math_format)
