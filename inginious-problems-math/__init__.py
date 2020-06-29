# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import os
import re
import web

from sympy.parsing.latex import parse_latex
from sympy.parsing.latex.errors import LaTeXParsingError
from sympy import simplify, sympify, N

from inginious.common.tasks_problems import Problem
from inginious.frontend.task_problems import DisplayableProblem
from inginious.frontend.parsable_text import ParsableText
from inginious.frontend.pages.utils import INGIniousAuthPage
from inginious.frontend.pages.course import handle_course_unavailable

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


class HintPage(INGIniousAuthPage):
    def POST_AUTH(self):
        data = web.input()
        username = self.user_manager.session_username()
        language = self.user_manager.session_language()
        courseid = data.get("courseid", None)
        taskid = data.get("taskid", None)

        course = self.course_factory.get_course(courseid)
        if not self.user_manager.course_is_open_to_user(course, username):
            return handle_course_unavailable(self.cp.app.get_homepath(), self.template_helper, self.user_manager, course)

        task = course.get_task(taskid)
        if not self.user_manager.task_is_visible_by_user(task, username):
            return self.template_helper.get_renderer().task_unavailable()

        problemid = data.get("problemid", "")
        problems = task.get_problems()
        for problem in problems:
            if problem.get_id() == problemid:
                return ParsableText(problem.gettext(language, problem._hints), "rst",
                                    translation=problem.get_translation_obj(language))

        return ""

class MathProblem(Problem):
    """Display an input box and check that the content is correct"""

    def __init__(self, task, problemid, content):
        Problem.__init__(self, task, problemid, content)
        self._header = content['header'] if "header" in content else ""
        self._answer = str(content.get("answer", ""))
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
        return str

    def check_answer(self, task_input, language):
        if not self._answer:
            return None, None, None, 0

        if not task_input[self.get_id()]:
            return False, None, ["_wrong_answer"], 1

        try:
            student_answer = MathProblem.parse_equation(task_input[self.get_id()])
            correct_answer = MathProblem.parse_equation(self._answer)
        except LaTeXParsingError as e:
            return False, None, ["_wrong_answer", "Parsing error: " + str(e)], 1

        if self.is_equal(student_answer, correct_answer):
            msg = self.gettext(language, self._success_message) or "_correct_answer"
            return True, None, [msg], 0
        else:
            # Iterate on possibles student choices:
            for choice in self._choices:
                try:
                    choice_answer = MathProblem.parse_equation(choice_answer)
                    if self.is_equal(student_answer, choice_answer):
                        msg = self.gettext(language, choice["feedback"])
                        return False, None, [msg], 1
                except LaTeXParsingError as e:
                    return False, None, ["_wrong_answer", "Parsing error: " + str(e)], 1
            # If not among choices, return the default error message
            msg = self.gettext(language, self._error_message) or "_wrong_answer"
            return False, None, [msg], 1

    @classmethod
    def parse_equation(cls, latex_str):
        # The \left and \right prefix are not supported by sympy (and useless for treatment)
        latex_str = re.sub("(\\\left|\\\\right)", "", latex_str)
        return parse_latex(latex_str)

    def is_equal(self, eq1, eq2):
        if not simplify(eq1-eq2) or not simplify(sympify(str(eq1)) - sympify(str(eq2))):
            return True
        elif self._tolerance:
            return abs(N(sympify(str(eq1)) - sympify(str(eq2)))) < self._tolerance
        else:
            return abs(N(sympify(str(eq1)) - sympify(str(eq2)))) == 0

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

        for message in ["error_message", "success_message"]:
            if message in problem_content and problem_content[message].strip() == "":
                del problem_content[message]

        return problem_content

    @classmethod
    def get_text_fields(cls):
        return Problem.get_text_fields()


class DisplayableMathProblem(MathProblem, DisplayableProblem):
    """ A displayable match problem """

    def __init__(self, task, problemid, content):
        MathProblem.__init__(self, task, problemid, content)

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
        return str(DisplayableMathProblem.get_renderer(template_helper).math(self._task, self.get_id(), header, self._hints))

    @classmethod
    def show_editbox(cls, template_helper, key, language):
        return DisplayableMathProblem.get_renderer(template_helper).math_edit(key)

    @classmethod
    def show_editbox_templates(cls, template_helper, key, language):
        return DisplayableMathProblem.get_renderer(template_helper).math_edit_templates(key)


def init(plugin_manager, course_factory, client, plugin_config):
    # TODO: Replace by shared static middleware and let webserver serve the files
    plugin_manager.add_page('/plugins/math/static/(.+)', StaticMockPage)
    plugin_manager.add_page('/plugins/math/hint', HintPage)
    plugin_manager.add_hook("css", lambda: "/plugins/math/static/mathquill.css")
    plugin_manager.add_hook("css", lambda: "/plugins/math/static/matheditor.css")
    plugin_manager.add_hook("javascript_header", lambda: "/plugins/math/static/mathquill.min.js")
    plugin_manager.add_hook("javascript_header", lambda: "/plugins/math/static/math.js")
    plugin_manager.add_hook("javascript_header", lambda: "/plugins/math/static/matheditor.js")
    course_factory.get_task_factory().add_problem_type(DisplayableMathProblem)
