Subproblems types
=================

The plugin provides four more types of subproblems:

*math* type
-----------

This type is used for basic math question where the answer is a simple expression. This expression can contain fractions, logarithms, exponentials, trigonometry and even complexes.
Depending of the expected answer, it is necessary to look into the *other options* tab and check all the options matching the expected solution.

These options are :
    - *Symbolic comparison* or *perfect match* : the first one allows the student to answer with an expression equivalent to the solution when the second one force the student to answer with the exact same expression as the expected solution.
    - *Contains logarithms* : check this box if the solution contains any logarithms.
    - *Contains trigonometry* : check this box if the solution contains any trigonometry.
    - *Contains complexes* : check this box if the domain of at least one variable contains complexes.

All the options checked influence the way the student's answer will be compare to the expected solution and determined as correct or not.
By default the first option is *symbolic comparison* and the other checkboxes are unchecked.

Another option is available and is about the visibility of the error messages :
    - *Always visible* : every time the student makes a mistake, the error message will be displayed.
    - *Visible after X attemps* : The error message will be displayed after the student have made at least X mistakes.
    - *Hidden until X date* : The error message will remain hidden until a certain date is passed.

This option only concerns the visibility of the *error message* box.

*math-matrix* type
------------------

The *math-matrix* type has to be used if you need a solution that is a matrix, a vector, or cartesian/spatial point.
Matrix are encoded such as [a,b:c,d] and vectors such as [a,b,c]. Elements must be mathematical expressions or numerical values.
[] symbols can be added or removed around the entire matrix or vector, such as [a,b:c,d] or a,b:c,d without impact.
Vectors of size 2 such as [a,b] are perfect for cartesian points and size 3 such as [a,b,c] for spatial points.


*math-interval* type
--------------------

This subproblem type is designed for intervals such as [0,2]∪[5,∞). The [] symbols represent inclusion and () symbols represent exclusion.
The union symbol is available in the visual editor.
As a convention, we advise to always exclude infinity.
It is advised to only ask for a single answer for this problem type. If you want, for example, 2 domains for 2 different functions, please create two subproblems.


*math-set* type
---------------

The last type is designed for sets. Sets can be defined as implicit sets, {x|x²<25 |N} or as explicit sets, such as {1,2,3,4}.
Please select a format with the checkbox and don't mix them both. This will also tell the student which format to use in his answer.

Explicit sets:
For these sets, the union ∪ and intersection ∩ symbols are available.
Please note the union is computed first then the intersection is computed at the end.
In other words, A∪B∩C means (A∪B)∩C and A∩B∪C means A∩(B∪C).

Implicit sets:
These allow to represent a high number of elements in a set without explicitly writing them one by one.
With the format {v|c|d}:
    - v is the variable such as x
    - c is the condition such as x²<25
    - d is the domain such as N

Condition can be:
    - A single condition such as x²>25
    - Multiple conditions such as (x²>25)&(x³<1000)

Domain can be:
    - N for positive integers excluding 0
    - Z+ for positive integers including 0
    - Z- for negative integers including 0
    - Z for all the integers
    - R for reals
    - Q for rationals
    - {1,2,3} for a specific set as domain

It is advised to specify to the students which domain to use since different domains with different conditions leading to the same mathematical result may not be considered equals.
It is also advised to only ask for a single answer for this problem type. Adding multiple answers with the button add answer may lead to errors.