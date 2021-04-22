# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import os

from flask import send_from_directory
from inginious.frontend.pages.utils import INGIniousPage

from inginious_problems_math.pages.hint import HintPage
from inginious_problems_math.pages.answers import AnswersPage
from inginious_problems_math.math_problem import DisplayableMathProblem
from inginious_problems_math.math_matrix import DisplayableMathMatrixProblem
from inginious_problems_math.math_interval import DisplayableMathIntervalProblem

__version__ = "0.1.dev0"

PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))
PATH_TO_TEMPLATES = os.path.join(PATH_TO_PLUGIN, "templates")

class StaticMockPage(INGIniousPage):
    def GET(self, path):
        return send_from_directory(os.path.join(PATH_TO_PLUGIN, "static"), path)

    def POST(self, path):
        return self.GET(path)

def add_admin_menu(course): # pylint: disable=unused-argument
    return 'math-answers', '<i class="fa fa-calculator fa-fw"></i>&nbsp; Math answers'

def init(plugin_manager, course_factory, client, plugin_config):
    # TODO: Replace by shared static middleware and let webserver serve the files
    plugin_manager.add_page('/plugins/math/static/<path:path>', StaticMockPage.as_view('mathstaticpage'))
    plugin_manager.add_page('/plugins/math/hint', HintPage.as_view('mathhintpage'))
    plugin_manager.add_page('/admin/<courseid>/math-answers', AnswersPage.as_view('mathanswerspage'))
    plugin_manager.add_hook("css", lambda: "/plugins/math/static/mathquill.css")
    plugin_manager.add_hook("css", lambda: "/plugins/math/static/matheditor.css")
    plugin_manager.add_hook("javascript_header", lambda: "/plugins/math/static/mathquill.min.js")
    plugin_manager.add_hook("javascript_header", lambda: "/plugins/math/static/math.js")
    plugin_manager.add_hook("javascript_header", lambda: "/plugins/math/static/matheditor.js")
    plugin_manager.add_hook('course_admin_menu', add_admin_menu)
    course_factory.get_task_factory().add_problem_type(DisplayableMathProblem)
    course_factory.get_task_factory().add_problem_type(DisplayableMathMatrixProblem)
    course_factory.get_task_factory().add_problem_type(DisplayableMathIntervalProblem)
