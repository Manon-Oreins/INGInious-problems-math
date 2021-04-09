import os
import re
import json
import math

from sympy.core import Number
from sympy.parsing.latex import parse_latex
from sympy.printing.latex import latex
from sympy import simplify, sympify, N, E, pi, I, Equality, Unequality, StrictLessThan, LessThan, StrictGreaterThan, GreaterThan
from inginious.common.tasks_problems import Problem
from inginious.frontend.task_problems import DisplayableProblem
from inginious.frontend.parsable_text import ParsableText

PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))
PATH_TO_TEMPLATES = os.path.join(PATH_TO_PLUGIN, "templates")
__version__ = "0.1.dev0"
math_format = "expression: 5x+3  equation: x=y+3"
problem_type = "math"
math_problem_info = "This problem type is designed to allow many types \n" \
                    "of mathematical answers format. Including: \n" \
                    "Mathematical expressions: 5x+3 \n" \
                    "Mumerical values with tolerance: 88.91 \n" \
                    "Equations: y=3x\n" \
                    "Inequalities: x<5+y \n" \
                    "If you want to encode a vector, a matrix, \n" \
                    "or some intervals, please refer to other \n" \
                    "problem types.\n" \
                    "Note: If you use tolerance, it is expressed as \n" \
                    "absolute value, not relative."

general_remark = "e always represents the basis of natural logarithms \n" \
                "i always represents the imaginary constant \n" \
                "Do not use these letters to represent variables \n" \
                "log means log base 10 \n" \
                "ln means natural logarithm \n" \
                "log_a means log with base a \n" \
                ". represents the decimal and , represents a separation\n" \
                "When a letter is followed by an opening parenthesis,\n" \
                "it is interpreted as \"function of...\" \n" \
                "For example, x(2y+3) means x evaluted at 2y+3 \n" \
                "If you want a multiplication instead, use x*(2y+3)\n" \
                "or (2y+3)x. \n" \
                "This helps differentiate variables and functions."

class MathProblem(Problem):
    """Display an input box and check that the content is correct"""

    def __init__(self, problemid, content, translations, taskfs):
        Problem.__init__(self, problemid, content, translations, taskfs)
        self._header = content['header'] if "header" in content else ""
        self._answers = list(content.get("answers", [])) or ([content.get("answer", "")] if content.get("answer", "") else []) # retrocompat
        self._tolerance = content.get("tolerance", None)
        self._hints = content.get("hints", None)
        self._error_message = content.get("error_message", None)
        self._success_message = content.get("success_message", None)
        self._choices = content.get("choices", [])

    @classmethod
    def get_type(cls):
        return problem_type

    def input_is_consistent(self, task_input, default_allowed_extension, default_max_size):
        return self.get_id() in task_input

    def input_type(self):
        return list

    def check_answer(self, task_input, language):
        try:
            state = json.loads(task_input.get("@state", "{}"))
            state = state.get(self.get_id(), "")
        except:
            state = ""

        if not isinstance(self._answers, list):
            return None, None, None, 0, state
        try:
            student_answers = [self.parse_equation(eq) for eq in task_input[self.get_id()]]
            correct_answers = [self.parse_equation(eq) for eq in self._answers]
            unexpec_answers = [self.parse_equation(choice["answer"]) for choice in self._choices]
        except Exception as e:
            return False, None, ["_wrong_answer", "Parsing error: \n\n .. code-block:: \n\n\t" + str(e).replace("\n", "\n\t")], 1, state

        # Sort both student and correct answers array per their string representation
        # Equal equations should have the same string representation
        student_answers = self.sort(student_answers)
        correct_answers = self.sort(correct_answers)

        # Check for correct amount of answers
        checker = self.check_len(student_answers, correct_answers)
        if not checker[0]:
            return False, None, [checker[1]], 0, state

        state = json.dumps([latex(answer) for answer in student_answers])

        # Check if an unexpected answer has been given
        for i in range(0, len(self._choices)):
            unexpec_answer = unexpec_answers[i]
            for student_answer in student_answers:
                if self.is_equal(student_answer, unexpec_answer):
                    msg = self.gettext(language, self._choices[i]["feedback"])
                    return False, None, [msg], 0, state

        for i in range(0, len(correct_answers)):
            if not self.is_equal(student_answers[i], correct_answers[i]):
                msg = [self.gettext(language, self._error_message) or "_wrong_answer"]
                msg += ["Not correct : :math:`{}`".format(latex(student_answers[i]))]
                return False, None, msg, 0, state

        msg = self.gettext(language, self._success_message) or "_correct_answer"
        return True, None, [msg], 0, state

    def check_len(self, student_anwer, correct_answer):
        """ Verify the number of answers"""
        correct_len = len(correct_answer) == len(student_anwer)
        message = "Expected {} answer(s)".format(len(correct_answer))
        return [correct_len, message]


    def sort(self, answers):
        """Sort the answers based on alphabetical order"""
        return sorted(answers, key=lambda eq: str(eq))

    def parse_equation(cls, latex_str):
        # The \left and \right prefix are not supported by sympy (and useless for treatment)
        latex_str = re.sub("(\\\left|\\\right)", "", latex_str)
        latex_str = re.sub("(\\\log_)(\w)(\(|\^)", "\\\log_{\\2}\\3", latex_str)
        latex_str = re.sub("(\\\log_)(\w)(\w+)", "\\\log_{\\2}(\\3)", latex_str)
        latex_str = re.sub(r'(\w)_(\w)(\w+)', r'\1_{\2}\3', latex_str) #x_ab means x_{a}b but x_{ab} correclty means x_{ab}
        #general constants: always use i for imaginary constant, e for natural logarithm basis and \pi (or the symbol from toolbox) for pi
        eq = parse_latex(latex_str).subs([("e", E), ("i", I), ("pi", pi)])
        return sympify(eq)

    def is_equal(self, eq1, eq2):
        """Compare answers"""
        #answer=eq1, solution=eq2
        equation_types = [Equality, Unequality, StrictLessThan, LessThan, StrictGreaterThan, GreaterThan]

        if self._tolerance:
            eq1 = eq1.subs([(E, math.e), (pi, math.pi)])
            eq2 = eq2.subs([(E, math.e), (pi, math.pi)])
        #Numbers
        if (isinstance(eq1, Number) and isinstance(eq2, Number)) or self._tolerance:
            return round(float(abs(N(eq1 - eq2))), 10) <= round(float(self._tolerance), 10) if self._tolerance else abs(N(eq1 - eq2)) == 0
        #Numerical Evaluation
        if not type(eq1) == type(eq2):
            return N(eq1) == N(eq2)
        #Equality and inequalities
        if type(eq1) in equation_types:
            return eq1 == eq2 or simplify(eq1) == simplify(eq2)
        #Direct match
        if eq1 == eq2 or simplify(eq1) == simplify(eq2):
            return True
        #Uncaught
        return abs(N(eq1 - eq2)) == 0

    @classmethod
    def parse_problem(cls, problem_content):
        problem_content = Problem.parse_problem(problem_content)

        if "tolerance" in problem_content:
            if problem_content["tolerance"]:
                problem_content["tolerance"] = float(problem_content["tolerance"])
            else:
                del problem_content["tolerance"]

        if "choices" in problem_content:
            problem_content["choices"] = [val for _, val in
                                          sorted(iter(problem_content["choices"].items()), key=lambda x: int(x[0]))
                                          if val["feedback"].strip()]
        if "answers" in problem_content:
            problem_content["answers"] = [val for _, val in problem_content["answers"].items()]

        for message in ["error_message", "success_message"]:
            if message in problem_content and problem_content[message].strip() == "":
                del problem_content[message]

        return problem_content

    @classmethod
    def get_text_fields(cls):
        return Problem.get_text_fields()

class DisplayableMathProblem(MathProblem, DisplayableProblem):
    """ A displayable match problem """

    def __init__(self, problemid, content, translations, taskfs):
        MathProblem.__init__(self, problemid, content, translations, taskfs)

    @classmethod
    def get_type_name(self, language):
        return problem_type

    def show_input(self, template_helper, language, seed, format=math_format):
        """ Show MatchProblem """
        header = ParsableText(self.gettext(language, self._header), "rst",
                              translation=self.get_translation_obj(language))
        return template_helper.render("math.html", template_folder=PATH_TO_TEMPLATES, inputId=self.get_id(),
                                      header=header, hints=self._hints, format=format)

    @classmethod
    def show_editbox(cls, template_helper, key, language, problem_type="math", problem_type_info=math_problem_info):
        return template_helper.render("math_edit.html", template_folder=PATH_TO_TEMPLATES, key=key, problem_type_info=problem_type_info, problem_type=problem_type, general_remark=general_remark)

    @classmethod
    def show_editbox_templates(cls, template_helper, key, language, format=math_format):
        return template_helper.render("math_edit_templates.html", template_folder=PATH_TO_TEMPLATES, key=key, format=format)
