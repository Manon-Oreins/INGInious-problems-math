# -*- coding: utf-8 -*-
#
# This file is part of INGInious. See the LICENSE and the COPYRIGHTS files for
# more information about the licensing of this file.

import json
import web

from inginious.frontend.pages.utils import INGIniousAuthPage
from inginious.frontend.pages.course import handle_course_unavailable
from inginious.frontend.parsable_text import ParsableText

class HintPage(INGIniousAuthPage):
    def is_lti_page(self):
        return self.user_manager.session_lti_info() is not None

    def POST_AUTH(self):
        data = web.input()
        username = self.user_manager.session_username()
        language = self.user_manager.session_language()
        courseid = data.get("courseid", None)
        taskid = data.get("taskid", None)

        course = self.course_factory.get_course(courseid)
        if not self.user_manager.course_is_open_to_user(course, username, self.is_lti_page()):
            return handle_course_unavailable(self.cp.app.get_homepath(), self.template_helper, self.user_manager, course)

        task = course.get_task(taskid)
        if not self.user_manager.task_can_user_submit(task, username, None, self.is_lti_page()):
            return self.template_helper.get_renderer().task_unavailable()

        problemid = data.get("problemid", "")
        problems = task.get_problems()
        hints = ""
        for problem in problems:
            if problem.get_id() == problemid:
                hints = ParsableText(problem.gettext(language, problem._hints), "rst",
                                    translation=problem.get_translation_obj(language))

        if hints:
            user_tasks = self.database.user_tasks.find_one({"username": username, "courseid": courseid,
                                                            "taskid": taskid})
            try:
                state = json.loads(user_tasks.get("state", "{}"))
            except:
                state = {}

            state.setdefault("hints", {})[problemid] = True
            self.database.user_tasks.update_one({"username": username, "courseid": courseid,
                                                 "taskid": taskid}, {"$set": {"state": json.dumps(state)}})

        return hints