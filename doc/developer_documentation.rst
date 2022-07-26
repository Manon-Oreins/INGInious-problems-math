Developer's documentation
=========================


Code structure
--------------

Every subproblem type is managed by a python file : *math_interval.py*, *math_matrix.py* and *math_set.py* inherit from *math_problem.py* that inherits from the class *Problem* of Inginious.

*math.html* handle the display of a math problem when *math_edit.html* handle the display of the page allowing the administrator to modify a math problem.

These html files are managed by Javascript files such as *math.js*, and *matheditor.js* for the visual editor.

Useful functions
----------------

``check_answer`` : Check the state and the information submitted by the student and return the correct feedback.

``parse_answer`` : Take the student's answer, modify it and return a clean version ready to be passed in the *is_equal* function.

``is_equal`` : Compare the student answer and the expected answer using *sympy* functions and return *True* or *False* if the two are considered equal or not depending on the options checked by the admin.

``parse_problem`` : Remove/add or modify entries in the dictionary representing the content of the supbroblemn to prepare the treatment of these information.



