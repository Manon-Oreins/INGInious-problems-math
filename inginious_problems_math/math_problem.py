import os
import re
import json
import math

from sympy.core import Number
from sympy.parsing.latex import parse_latex
from sympy.printing.latex import latex
from sympy import simplify, sympify, expand_log, expand_trig, factor, N, E, pi, I, Equality, Unequality, StrictLessThan, LessThan, StrictGreaterThan, GreaterThan
from inginious.common.tasks_problems import Problem
from inginious.frontend.task_problems import DisplayableProblem
from inginious.frontend.parsable_text import ParsableText

PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))
PATH_TO_TEMPLATES = os.path.join(PATH_TO_PLUGIN, "templates")
math_format = "expression: 5x+3  equation: x=y+3  inequation: x<2y+1"
problem_type = "math"


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
        self._comparison_type = content.get("comparison_type", "symbolic")
        self._use_log = content.get("use_log", False)
        self._use_trigo = content.get("use_trigo", False)
        self._use_complex = content.get("use_complex", False)

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
            student_answers = [self.parse_answer(eq) for eq in task_input[self.get_id()]]
            correct_answers = [self.parse_answer(eq) for eq in self._answers]
            unexpec_answers = [self.parse_answer(choice["answer"]) for choice in self._choices]
        except Exception as e:
            return False, None, ["_wrong_answer", "Parsing error: \n\n .. code-block:: \n\n\t" + str(e).replace("\n", "\n\t")], 0, state

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
                try:
                    if self.is_equal(student_answer, unexpec_answer):
                        msg = self.gettext(language, self._choices[i]["feedback"])
                        return False, None, [msg], 0, state
                except Exception as e:
                    return False, None, [str(e)], 0, state

        for i in range(0, len(correct_answers)):
            try:
                if not self.is_equal(student_answers[i], correct_answers[i]):
                    msg = [self.gettext(language, self._error_message) or "_wrong_answer"]
                    msg += ["Not correct : :math:`{}`".format(latex(student_answers[i]))]
                    return False, None, msg, 0, state
            except Exception as e:
                return False, None, [str(e)], 0, state


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

    @classmethod
    def parse_answer(cls, latex_str):

        # The \left and \right prefix are not supported by sympy (and useless for treatment)
        latex_str = re.sub("(\\\left|\\\right)", "", latex_str)
        latex_str = re.sub("(\\\log_)(\w)(\(|\^)", "\\\log_{\\2}\\3", latex_str)
        latex_str = re.sub("(\\\log_)(\w)(\w+)", "\\\log_{\\2}(\\3)", latex_str)
        latex_str = re.sub(r'(\w)_(\w)(\w+)', r'\1_{\2}\3', latex_str) #x_ab means x_{a}b but x_{ab} correclty means x_{ab}
        latex_str = latex_str.replace("\\ne", "\\neq")
        latex_str = latex_str.replace("\\right|", "|")
        latex_str = latex_str.replace("\\left|", "|")

        #general constants: always use i for imaginary constant, e for natural logarithm basis and \pi (or the symbol from toolbox) for pi
        eq = sympify(parse_latex(latex_str).subs([("e", E), ("i", I), ("pi", pi)]))
        # Do not simplify the answer to be able to check for perfect match if needed
        return eq

    def is_equal(self, eq1, eq2):
        """Compare answers"""
        #answer=eq1, solution=eq2
        equation_types = [Equality, Unequality, StrictLessThan, LessThan, StrictGreaterThan, GreaterThan]
        #Symbolic equality/Perfect match
        if self._comparison_type == "perfect_match":
            return eq1 == eq2
        eq1 = factor(simplify(eq1))    #simplify is mandatory to counter expand_trig and expand_log weaknesses
        eq2 = factor(simplify(eq2))
        #Trigonometric simplifications
        if self._use_trigo:
            eq1 = expand_trig(eq1)
            eq2 = expand_trig(eq2)
        #Logarithmic simplifications
        if self._use_log:
            if self._use_complex:
                eq1 = expand_log(eq1)
                eq2 = expand_log(eq2)
            else:
                eq1 = expand_log(eq1, force=True)
                eq2 = expand_log(eq2, force=True)
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
    """ A displayable math problem """

    # Some class attributes
    problem_type = "math"
    html_file = "math_edit.html"

    def __init__(self, problemid, content, translations, taskfs):
        MathProblem.__init__(self, problemid, content, translations, taskfs)


    @classmethod
    def get_type_name(self, language):
        return problem_type

    def show_input(self, template_helper, language, seed, format=math_format):
        """ Show MathProblem """
        header = ParsableText(self.gettext(language, self._header), "rst",
                              translation=self.get_translation_obj(language))
        return template_helper.render("math.html", template_folder=PATH_TO_TEMPLATES, inputId=self.get_id(),
                                      header=header, hints=self._hints, format=format)

    @classmethod
    def show_editbox(cls, template_helper, key, language):
        return template_helper.render(cls.html_file, template_folder=PATH_TO_TEMPLATES, key=key, problem_type=cls.problem_type, friendly_type=cls.get_type_name(language))

    @classmethod
    def show_editbox_templates(cls, template_helper, key, language, format=math_format):
        return template_helper.render("math_edit_templates.html", template_folder=PATH_TO_TEMPLATES, key=key, format=format)
