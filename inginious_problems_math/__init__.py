# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import os
import re
import web
import json

from sympy.core import Number
from sympy.parsing.latex import parse_latex
from sympy.printing.latex import latex
from sympy import simplify, sympify, N, E, Equality

from inginious.common.tasks_problems import Problem
from inginious.frontend.task_problems import DisplayableProblem
from inginious.frontend.parsable_text import ParsableText

from inginious_problems_math.pages.hint import HintPage
from inginious_problems_math.pages.answers import AnswersPage

__version__ = "0.1.dev0"

PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))


class StaticMockPage(object):
    # TODO: Replace by shared static middleware and let webserver serve the files
    def GET(self, path):
        if not os.path.abspath(PATH_TO_PLUGIN) in os.path.abspath(os.path.join(PATH_TO_PLUGIN, path)):
            raise web.notfound()

        try:
            with open(os.path.join(PATH_TO_PLUGIN, "static", path), 'rb') as file:
                return file.read()
        except:
            raise web.notfound()

    def POST(self, path):
        return self.GET(path)


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
        return "math"

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
            student_answers = [MathProblem.parse_equation(eq) for eq in task_input[self.get_id()]]
            correct_answers = [MathProblem.parse_equation(eq) for eq in self._answers]
            unexpec_answers = [MathProblem.parse_equation(choice["answer"]) for choice in self._choices]
        except Exception as e:
            return False, None, ["_wrong_answer", "Parsing error: \n\n .. code-block:: \n\n\t" + str(e).replace("\n", "\n\t")], 1, state

        # Check for correct amount of answers
        if not len(student_answers) == len(correct_answers):
            msg = self.gettext(language, "Expected {} answer(s).".format(len(correct_answers)))
            return False, None, [msg], 0, state

        # Sort both student and correct answers array per their string representation
        # Equal equations should have the same string representation
        student_answers = sorted(student_answers, key=lambda eq: str(eq))
        correct_answers = sorted(correct_answers, key=lambda eq: str(eq))

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

    @classmethod
    def parse_equation(cls, latex_str):
        # The \left and \right prefix are not supported by sympy (and useless for treatment)
        latex_str = re.sub("(\\\left|\\\\right)", "", latex_str)
        latex_str = re.sub("(\\\log_)(\w)(\()", "\\\log_{\\2}(", latex_str)
        latex_str = re.sub("(\\\log_)(\w)(\w+)", "\\\log_{\\2}(\\3)", latex_str)
        # We parse LaTeX one time, and then reparse to evaluate constants correctly
        eq = parse_latex(latex_str)
        # Here we add an alias "e" as the E=2.71...
        return sympify(str(eq), locals={"e": E})

    def is_equal(self, eq1, eq2):
        if isinstance(eq1, Number) and isinstance(eq2, Number):
            return abs(N(eq1 - eq2)) < self._tolerance if self._tolerance else abs(N(eq1 - eq2)) == 0
        if not type(eq1) == type(eq2):
            return False
        elif type(eq1) == Equality:
            return eq1 == eq2 or simplify(eq1) == simplify(eq2)
        elif eq1 == eq2 or simplify(eq1) == simplify(eq2) or not simplify(eq1-eq2):
            return True
        elif self._tolerance:
            return abs(N(eq1 - eq2)) < self._tolerance
        else:
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
        return "math"

    @classmethod
    def get_renderer(cls, template_helper):
        """ Get the renderer for this class problem """
        return template_helper.get_custom_renderer(os.path.join(PATH_TO_PLUGIN, "templates"), False)

    def show_input(self, template_helper, language, seed):
        """ Show MatchProblem """
        header = ParsableText(self.gettext(language, self._header), "rst",
                              translation=self.get_translation_obj(language))
        return str(DisplayableMathProblem.get_renderer(template_helper).math(self.get_id(), header, self._hints))

    @classmethod
    def show_editbox(cls, template_helper, key, language):
        return DisplayableMathProblem.get_renderer(template_helper).math_edit(key)

    @classmethod
    def show_editbox_templates(cls, template_helper, key, language):
        return DisplayableMathProblem.get_renderer(template_helper).math_edit_templates(key)


def add_admin_menu(course): # pylint: disable=unused-argument
    return 'math-answers', '<i class="fa fa-calculator fa-fw"></i>&nbsp; Math answers'


def init(plugin_manager, course_factory, client, plugin_config):
    # TODO: Replace by shared static middleware and let webserver serve the files
    plugin_manager.add_page('/plugins/math/static/(.+)', StaticMockPage)
    plugin_manager.add_page('/plugins/math/hint', HintPage)
    plugin_manager.add_page('/admin/([^/]+)/math-answers', AnswersPage)
    plugin_manager.add_hook("css", lambda: "/plugins/math/static/mathquill.css")
    plugin_manager.add_hook("css", lambda: "/plugins/math/static/matheditor.css")
    plugin_manager.add_hook("javascript_header", lambda: "/plugins/math/static/mathquill.min.js")
    plugin_manager.add_hook("javascript_header", lambda: "/plugins/math/static/math.js")
    plugin_manager.add_hook("javascript_header", lambda: "/plugins/math/static/matheditor.js")
    plugin_manager.add_hook('course_admin_menu', add_admin_menu)
    course_factory.get_task_factory().add_problem_type(DisplayableMathProblem)
