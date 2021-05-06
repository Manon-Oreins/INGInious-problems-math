import os
import re

from inginious.frontend.task_problems import DisplayableProblem
from inginious_problems_math.math_problem import MathProblem, DisplayableMathProblem

from sympy import simplify, sympify, N, E, pi, I, Union, Intersection, FiniteSet, EmptySet, ConditionSet, S

PATH_TO_PLUGIN = os.path.abspath(os.path.dirname(__file__))
PATH_TO_TEMPLATES = os.path.join(PATH_TO_PLUGIN, "templates")
math_format = "Explicit: {1,2,3}  Implicit: {x|x<4|N}"
problem_type = "math_set"

class MathSetProblem(MathProblem):


    def __init__(self, problemid, content, translations, taskfs):
        """Adds the set_type to the generic ProblemMath constructor"""
        super().__init__(problemid, content, translations, taskfs)
        self._set_type = content.get("set_type", None)

    @classmethod
    def get_type(cls):
        return problem_type

    @classmethod
    def parse_answer(cls, latex_str):
        eq = latex_str.replace("\\left\\{", "{")
        eq = eq.replace("\\right\\}", "}")
        if "|" in eq:
            return cls.parse_implicit_set(eq)
        else:
            return cls.parse_explicit_set(eq)

    @classmethod
    def parse_explicit_set(cls, eq):
        """Parses potentially multiple explicit sets with unions and intersections,
         eq is formatted such as {1,2,3}u{4,5,6}"""
        final_set_1 = S.UniversalSet
        tab_1 = eq.split('\\cap')  # Intersections
        for set_1 in tab_1:
            tab_2 = set_1.split('\\cup')  # Unions
            final_set_2 = EmptySet
            for set_2 in tab_2:
                sympy_set_2 = cls.parse_single_explicit_set(set_2)
                final_set_2 = Union(final_set_2, sympy_set_2)
            final_set_1 = Intersection(final_set_1, final_set_2)
        return simplify(final_set_1)

    @classmethod
    def parse_single_explicit_set(cls, eq):
        """Parses a single explicit set, formatted such as {1,2,3}"""
        eq = eq[1:-1]
        eq_tab = eq.split(',')
        expressions_tab = list(map(MathProblem.parse_answer, eq_tab))
        final_set = sympify({element for element in expressions_tab})
        return final_set

    @classmethod
    def parse_implicit_set(cls, eq):
        """Parses an implicit set, formatted such as {variable, condition, domain}
        For example, eq could be {x|(x²>25)&(x³<150)}"""
        eq = eq[1:-1]
        eq = eq.replace("\\left", "")
        eq = eq.replace("\\right", "")
        eq_tab = eq.split("|")
        if len(eq_tab)!=3:
            raise ValueError("For implicit set, please follow the format {variable|condition|domain}")
        target = MathProblem.parse_answer(eq_tab[0])
        condition = cls.parse_conditions(eq_tab[1])
        domain = cls.parse_domain(eq_tab[2])
        return simplify(ConditionSet(target, condition, domain))

    @classmethod
    def parse_domain(cls, domain):
        domain = domain.replace("N", "S.Naturals")
        domain = domain.replace("Z+", "S.Naturals0")
        domain = domain.replace("Z-", "S.Integers-S.Naturals")
        domain = domain.replace("Z", "S.Integers")
        domain = domain.replace("R", "S.Reals")
        domain = domain.replace("Q", "S.Rationals")
        return sympify(domain)

    @classmethod
    def parse_conditions(cls, conditions):
        conditions_tab = conditions.split("\\&")
        final_conditions = None
        for condition in conditions_tab:
            if condition.startswith("(") and condition.endswith(")"):  #MathProblem.parse_answer does not accept equation/inequation surrounded by parenthesis
                condition = condition[1:-1]
            condition = MathProblem.parse_answer(condition)
            if final_conditions is None:
                final_conditions = sympify(condition)
            else:
                final_conditions = sympify(condition & final_conditions)
        return simplify(final_conditions)

    def get_format(self):
        if self._set_type == "explicit":
            return "Explicit: {1,2,3}"
        elif self._set_type == "implicit":
            return "Implicit: {x|x<4|N}"
        return math_format

    def is_equal(self, eq1, eq2):
        """Redfines the is_equal to only accept Intervals and Unions"""
        #Sets
        if type(eq1) in [Intersection, Union, FiniteSet, ConditionSet] and type(eq2) in [Intersection, Union, FiniteSet, ConditionSet]:
            return eq1 == eq2 or simplify(eq1) == simplify(eq2)
        elif eq1 == EmptySet and eq2 == EmptySet:
            return True
        return False

class DisplayableMathSetProblem(MathSetProblem, DisplayableProblem):
    """ A displayable math problem """

    # Some class attributes
    html_file = "math_set_edit.html"

    def __init__(self, problemid, content, translations, taskfs):
        MathSetProblem.__init__(self, problemid, content, translations, taskfs)

    @classmethod
    def get_type_name(self, language):
        return "math-set"

    def show_input(self, template_helper, language, seed):
        return DisplayableMathProblem.show_input(self, template_helper, language, seed, format=MathSetProblem.get_format(self))

    @classmethod
    def show_editbox(cls, template_helper, key, language):
        return template_helper.render(cls.html_file, template_folder=PATH_TO_TEMPLATES, key=key,
                                      problem_type=problem_type, friendly_type=cls.get_type_name(language))

    @classmethod
    def show_editbox_templates(cls, template_helper, key, language):
        return DisplayableMathProblem.show_editbox_templates(template_helper, key, language, format=math_format)
