# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import json
import os
from operator import itemgetter

from inginious.frontend.pages.course_admin.utils import INGIniousAdminPage
from inginious.frontend.parsable_text import ParsableText
import inginious_problems_math

PATH_TO_PLUGIN = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir)
PATH_TO_TEMPLATES = os.path.join(PATH_TO_PLUGIN, "templates")


class AnswersPage(INGIniousAdminPage):
    def GET_AUTH(self, courseid):  # pylint: disable=arguments-differ
        course, __ = self.get_course_and_check_rights(courseid, allow_all_staff=False)
        data = {}
        tasks = course.get_tasks(True)
        for taskid, task in tasks.items():
            problems = task.get_problems()
            for problem in problems:
                if isinstance(problem, inginious_problems_math.MathProblem):
                    data.setdefault(taskid, {})["task"] = task
                    data[taskid].setdefault("pid", {})[problem.get_id()] = problem

        # Fetch user tasks
        for taskid, item in data.items():
            states = self.database.user_tasks.aggregate([
                {"$match" : {"courseid": courseid, "taskid": taskid}},
                {"$group": {"_id": "$state"}}
            ])
            # Parse the task state for each user
            states = [json.loads(state["_id"]) if state["_id"] else {} for state in states]

            for pid in data[taskid]["pid"].keys():
                task_ans = data[taskid].setdefault("answers", {})
                for state in states:
                    if state:
                        p_ans = task_ans.setdefault(pid, {})
                        p_ans[state.get(pid)] = p_ans.get(state.get(pid), 0) + 1
                task_ans[pid] = sorted([(json.loads(ans), count) for ans, count in task_ans.get(pid, {}).items() if ans],
                                       key=itemgetter(1), reverse=True)

        return self.template_helper.render("answers.html", template_folder=PATH_TO_TEMPLATES, course=course,
                                           data=data, ParsableText=ParsableText)
