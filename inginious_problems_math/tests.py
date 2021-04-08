
import re
import unittest
import math
from sympy.core import Number
from sympy.parsing.latex import parse_latex
from sympy.printing.latex import latex
from sympy import simplify, sympify, N, E, pi, Equality
from inginious_problems_math.math_problem import MathProblem


class TestParseEquation(unittest.TestCase):


    def test_unique_expression(self):
        self.assertEqual((int(MathProblem.parse_equation(self, "x").subs("x",10))),10)
        self.assertEqual((int(MathProblem.parse_equation(self, "2x-x").subs("x",10))),10)
        self.assertEqual((int(MathProblem.parse_equation(self, "x2-x").subs("x",10))),10)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{5x}{5}").subs("x",10))),10)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{25x}{5}-4x").subs("x",10))),10)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{x}{1}").subs("x",10))),10)
        self.assertEqual((int(MathProblem.parse_equation(self, "1x").subs("x",10))),10)
        self.assertEqual((int(MathProblem.parse_equation(self, "1x^1-5+5").subs("x",10))),10)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{x^2}{x}").subs("x",10))),10)


    def test_simple_expression(self):
        self.assertEqual((int(MathProblem.parse_equation(self, "2x+1").subs("x",17))),35)
        self.assertEqual((int(MathProblem.parse_equation(self, "1+x2").subs("x",17))),35)
        self.assertEqual((int(MathProblem.parse_equation(self, "2x+2-1").subs("x",17))),35)
        self.assertEqual(int((MathProblem.parse_equation(self, "x+x+1").subs("x",17))),35)
        self.assertEqual((int(MathProblem.parse_equation(self, "2x+7-6").subs("x",17))),35)
        self.assertEqual((int(MathProblem.parse_equation(self, "x3+2-x-1").subs("x",17))),35)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{3xxx+2xx-xxx-1xx}{xx}").subs("x",17))),35)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{15xxx+10xx-5xxx-5xx}{5xx}").subs("x",17))),35)


    def test_simple_polynomial(self):
        self.assertEqual((int(MathProblem.parse_equation(self, "3x^2+2x+5").subs("x",18))),1013)
        self.assertEqual((int(MathProblem.parse_equation(self, "3x^2+2x+5+x^4-x^4").subs("x",18))),1013)
        self.assertEqual((int(MathProblem.parse_equation(self, "3x^2+5x+10-5-3x").subs("x",18))),1013)
        self.assertEqual((int(MathProblem.parse_equation(self, "3xx+2x+5").subs("x",18))),1013)
        self.assertEqual((int(MathProblem.parse_equation(self, "xx+2xx+2x+5").subs("x",18))),1013)
        self.assertEqual((int(MathProblem.parse_equation(self, "2+3x^2*2+x+x+3-3xx").subs("x",18))),1013)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{2x+3x^3*2+xx+xx+3x-3xxx}{x}").subs("x",18))),1013)


    def test_multivariable_polynomial(self):
        self.assertEqual((int(MathProblem.parse_equation(self, "3x^2+x+4y^2+2y+4").subs([("x",3), ("y", 4)]))),106)
        self.assertEqual((int(MathProblem.parse_equation(self, "4+3x^2+x+4y^2+2y+1-1").subs([("x",3), ("y", 4)]))),106)
        self.assertEqual((int(MathProblem.parse_equation(self, "3x^2+x+(2y+1)2y+4").subs([("x",3), ("y", 4)]))),106)
        self.assertEqual((int(MathProblem.parse_equation(self, "x*\\left(3x+1\\right)+4y^2+2y+4").subs([("x",3), ("y", 4)]))),106)
        self.assertEqual((int(MathProblem.parse_equation(self, "3x^2+x+2(2y^2)+2y+4").subs([("x",3), ("y", 4)]))),106)
        self.assertEqual((int(MathProblem.parse_equation(self, "3x^2+2x-x+4y^2+2y+4").subs([("x",3), ("y", 4)]))),106)
        self.assertEqual((int(MathProblem.parse_equation(self, "3x^2+x2-x+y^2*4+2y+4").subs([("x",3), ("y", 4)]))),106)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{3x^3+xx2-xx+y^2*4x+2yx+4x}{x}").subs([("x",3), ("y", 4)]))),106)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{3x^2y+xy2-xy+y^3*4+2yy+4y}{y}").subs([("x",3), ("y", 4)]))),106)


    def test_unique_exponent(self):
        self.assertEqual((int(MathProblem.parse_equation(self, "x^1").subs("x",10))),10)
        self.assertEqual((int(MathProblem.parse_equation(self, "x^2").subs("x",10))),100)
        self.assertEqual((int(MathProblem.parse_equation(self, "x^2x").subs("x",30))),27000)
        self.assertEqual((int(MathProblem.parse_equation(self, "x^3").subs("x",30))),27000)
        self.assertEqual((int(MathProblem.parse_equation(self, "x^x").subs("x",3))),27)
        self.assertEqual((int(MathProblem.parse_equation(self, "x^x2").subs("x",3))),54)
        self.assertEqual((int(MathProblem.parse_equation(self, "x^{x}").subs("x",3))),27)
        self.assertEqual((int(MathProblem.parse_equation(self, "x^{1x}").subs("x",3))),27)
        self.assertEqual((int(MathProblem.parse_equation(self, "x^{2x}").subs("x",3))),729)
        self.assertEqual((int(MathProblem.parse_equation(self, "x^{2x}2").subs("x",3))),1458)
        self.assertEqual((int(MathProblem.parse_equation(self, "x^{x2}2").subs("x",3))),1458)
        self.assertEqual((int(MathProblem.parse_equation(self, "2x^{x2}").subs("x",3))),1458)
        self.assertEqual((int(MathProblem.parse_equation(self, "xx^{2x}").subs("x",2))),32)
        self.assertEqual((int(MathProblem.parse_equation(self, "(3x)^{2x}").subs("x",2))),1296)
        self.assertEqual((int(MathProblem.parse_equation(self, "x^{2xx}").subs("x",2))),256)
        self.assertEqual((int(MathProblem.parse_equation(self, "x^{x2x}").subs("x",2))),256)
        self.assertEqual((int(MathProblem.parse_equation(self, "x^{2x^2}").subs("x",2))),256)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{x^{2x^2}}{1}").subs("x",2))),256)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{\\frac{x^{2x^2}}{1}}{1}").subs("x",2))),256)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{\\frac{2xx^{2x^2}}{1}}{2x}").subs("x",2))),256)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{2x^{2x^2}}{2}").subs("x",2))),256)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{2xx^{2x^2}}{2x}").subs("x",2))),256)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{4x^{2x^2}}{2x}").subs("x",2))),256)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{xxx^{2x^2}}{2x}").subs("x",2))),256)
        self.assertEqual((float(MathProblem.parse_equation(self, "\\frac{2x}{xxx^{2x^2}}").subs("x",2))),1/256)
        self.assertEqual((float(MathProblem.parse_equation(self, "\\sqrt{\\frac{2x}{xxx^{2x^2}}}").subs("x",2))),math.sqrt(1/256))


    def test_multiple_exponent(self):
        self.assertEqual((int(MathProblem.parse_equation(self, "x^2+y^2").subs([("x",2), ("y", 3)]))),13)
        self.assertEqual((int(MathProblem.parse_equation(self, "x^y+y^x").subs([("x",2), ("y", 3)]))),17)
        self.assertEqual((int(MathProblem.parse_equation(self, "2x^y+y^x").subs([("x",2), ("y", 3)]))),25)
        self.assertEqual((int(MathProblem.parse_equation(self, "x^y2+y^x").subs([("x",2), ("y", 3)]))),25)
        self.assertEqual((int(MathProblem.parse_equation(self, "2x^y+2y^x").subs([("x",2), ("y", 3)]))),34)
        self.assertEqual((int(MathProblem.parse_equation(self, "2x^2y+2y^x").subs([("x",2), ("y", 3)]))),42)
        self.assertEqual((int(MathProblem.parse_equation(self, "2x^{2y}+2y^x").subs([("x",2), ("y", 3)]))),146)
        self.assertEqual((int(MathProblem.parse_equation(self, "2x^{2y}+(2y)^x").subs([("x",2), ("y", 3)]))),164)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{6x^{2y+1}+(2y)^x3x}{3x}").subs([("x",2), ("y", 3)]))),164)
        self.assertEqual((int(MathProblem.parse_equation(self, "2x^{y^2}").subs([("x", 2), ("y",3)]))), 1024)
        self.assertEqual((float(MathProblem.parse_equation(self, "\\frac{x+x}{4xx^y+y^x2x}").subs([("x",2), ("y", 3)]))),1/25)
        self.assertEqual((float(MathProblem.parse_equation(self, "\\sqrt{2x^{2y}}").subs([("x", 2), ("y",3)]))), math.sqrt(128))


    def test_log(self):
        self.assertEqual((int(MathProblem.parse_equation(self, "\\log x").subs("x",10))),1)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\log10x").subs("x",10))),2)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\log10x+10").subs("x",10))),12)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\left(\\log x\\right)^2").subs("x",100))),4)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\log\\left(x+90\\right)").subs("x",10))),2)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\left(\\log x\\right)^{\\log1000}").subs("x",100))),8)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\log x^2").subs("x",10))),2)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\sqrt{\\log x^4}").subs("x",10))),2)
        self.assertEqual((float(MathProblem.parse_equation(self, "\\log x^y").subs([("x", 10), ("y",3)]))),3)
        self.assertEqual((float(MathProblem.parse_equation(self, "\\log 2x").subs("x",10))),float(math.log10(20)))
        self.assertEqual((float(MathProblem.parse_equation(self, "2\\log 2x").subs("x",10))),float(2*math.log10(20)))
        self.assertEqual((float(MathProblem.parse_equation(self, "\\log x^10").subs("x",2))),float(math.log10(1024)))
        self.assertEqual((float(MathProblem.parse_equation(self, "\\left(\\left(\\log x\\right)^{\\log100}\\right)^{2}").subs("x",100))),16)
        self.assertEqual((float(MathProblem.parse_equation(self, "\\frac{\\log1000x}{\\log10x}").subs("x",10))),2)
        self.assertEqual((float(MathProblem.parse_equation(self, "\\left(\\log x\\right)^y").subs([("x",100), ("y", 4)]))),16)
        self.assertEqual((float(MathProblem.parse_equation(self, "\\ln 5"))),math.log(5))
        self.assertEqual((float(MathProblem.parse_equation(self, "\\ln 5+10").subs("x",10))),math.log(5)+10)
        self.assertEqual((float(MathProblem.parse_equation(self, "\\ln5x").subs("x",10))),math.log(50))
        self.assertEqual((float(MathProblem.parse_equation(self, "\\log xy").subs([("x",10), ("y",100)]))),3)
        self.assertEqual((float(MathProblem.parse_equation(self, "\\left(\\log x\\right)y").subs([("x",100), ("y",10)]))),20)



    def test_single_char_subscripts(self):
        self.assertEqual((int(MathProblem.parse_equation(self, "x_1").subs("x_{1}",10))),10)
        self.assertEqual((int(MathProblem.parse_equation(self, "x_1+x_2").subs([("x_{1}",1), ("x_{2}", 4)]))),5)
        self.assertEqual((int(MathProblem.parse_equation(self, "x_1x_2").subs([("x_{1}",2), ("x_{2}", 5)]))),10)
        self.assertEqual((int(MathProblem.parse_equation(self, "x_1^{x_2}").subs([("x_{1}",2), ("x_{2}", 3)]))),8)
        self.assertEqual((int(MathProblem.parse_equation(self, "x_y").subs([("x_{y}",3)]))),3)
        self.assertEqual((int(MathProblem.parse_equation(self, "2x_1").subs([("x_{1}",3)]))),6)
        self.assertEqual((int(MathProblem.parse_equation(self, "x_12").subs([("x_{1}",3)]))),6)
        self.assertEqual((int(MathProblem.parse_equation(self, "x_1^3").subs([("x_{1}",3)]))),27)
        self.assertEqual((int(MathProblem.parse_equation(self, "x_1^{x_2}").subs([("x_{1}",3), ("x_{2}", 2)]))),9)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\frac{x_1}{x_2}").subs([("x_{1}",10), ("x_{2}", 2)]))),5)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\log x_1").subs([("x_{1}",100)]))),2)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\log2x_1").subs([("x_{1}",50)]))),2)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\log10^{x_1}").subs([("x_{1}",3)]))),3)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\sqrt{\\log2x_1}").subs([("x_{1}",5000)]))),2)
        self.assertEqual((float(MathProblem.parse_equation(self, "\\log\\left(x_1x_2\\right)").subs([("x_{1}",10), ("x_{2}", 2)]))),math.log10(20))


    def test_multi_char_subscripts(self):
        self.assertEqual((int(MathProblem.parse_equation(self, "x_{12}").subs("x_{12}",10))),10)
        self.assertEqual((int(MathProblem.parse_equation(self, "x_{12}x_{13}").subs([("x_{12}",3),("x_{13}", 4)]))),12)
        self.assertEqual((int(MathProblem.parse_equation(self, "x_{12}2").subs("x_{12}",10))),20)
        self.assertEqual((int(MathProblem.parse_equation(self, "2x_{12}").subs("x_{12}",10))),20)
        self.assertEqual((int(MathProblem.parse_equation(self, "2x_{12}2").subs("x_{12}",10))),40)
        self.assertEqual((int(MathProblem.parse_equation(self, "x_{12}+x_{13}").subs([("x_{12}",3),("x_{13}", 4)]))),7)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\log x_{12}").subs("x_{12}",100))),2)
        self.assertEqual((int(MathProblem.parse_equation(self, "2\\log x_{12}").subs("x_{12}",100))),4)
        self.assertEqual((float(MathProblem.parse_equation(self, "\\log2x_{12}").subs("x_{12}",100))),math.log10(200))
        self.assertEqual((int(MathProblem.parse_equation(self, "a_{xy}").subs("a_{x*y}",100))),100) # a multicharacter subscript containing letter(s) such as x_{ab} is translated into x_{a*b}
        self.assertEqual((int(MathProblem.parse_equation(self, "\\sqrt{x_{12}}").subs("x_{12}",100))),10)
        self.assertEqual((int(MathProblem.parse_equation(self, "5x_{11}\\sqrt{x_{12}}").subs([("x_{11}",3),("x_{12}", 4)]))),30)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\ln e+x").subs("x",5))),6)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\ln e^x").subs("x",5))),5)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\ln e^{xy}").subs([("x",2),("y", 3)]))),6)
        self.assertEqual((int(MathProblem.parse_equation(self, "\\ln e^{x_1x_2}").subs([("x_{1}",2),("x_{2}", 3)]))),6)


    def test_all_together(self):
        self.assertEqual((float(MathProblem.parse_equation(self, "\\frac{\\sqrt{x_{11}x_{12}+x_{13}x_{14}}}{\\sqrt[3]{x_{15}^{x_{12}}}x_{11}}").subs([("x_{11}",1),("x_{12}", 2),("x_{13}", 3),("x_{14}", 4),("x_{15}", 5)]))), math.sqrt(14)/(25**(1/3)))
        self.assertEqual((float(MathProblem.parse_equation(self, "\\frac{\\sqrt{x_{11}x_{12}+x_{13}x_{14}}}{\\log\\left(\\sqrt[3]{x_{15}^{x_{12}}}\\right)}").subs([("x_{11}",1),("x_{12}", 2),("x_{13}", 3),("x_{14}", 4),("x_{15}", 5)]))), math.sqrt(14)/math.log10(25**(1/3)))
        self.assertEqual((float(MathProblem.parse_equation(self, "\\left(\\frac{\\sqrt{x_{11}x_{12}+x_{13}x_{14}}}{\\log\\left(\\sqrt[3]{x_{15}^{x_{12}}}\\right)}\\right)^{\\log\\left(x_{12}x_{13}\\right)}").subs([("x_{11}",1),("x_{12}", 2),("x_{13}", 3),("x_{14}", 4),("x_{15}", 5)]))), (math.sqrt(14)/math.log10(25**(1/3)))**math.log10(6))
        self.assertEqual((float(MathProblem.parse_equation(self, "\\sqrt{\\left(\\frac{x_{12}^{x_{14}}}{x_{13}^{x_{12}}}\\right)}").subs([("x_{11}",1),("x_{12}", 2),("x_{13}", 3),("x_{14}", 4),("x_{15}", 5)]))), 4/3)
        self.assertEqual((float(MathProblem.parse_equation(self, "\\int_0^1\\sqrt{\\left(\\frac{x_{12}^{x_{14}}}{x_{13}^{x_{12}}}\\right)}").subs([("x_{11}",1),("x_{12}", 2),("x_{13}", 3),("x_{14}", 4),("x_{15}", 5)]))), 4/3)
        self.assertEqual(float(MathProblem.parse_equation(self, "2\\pi* r_1").subs("r_{1}",10)), 2*math.pi*10)





if __name__ == '__main__':
    unittest.main()


