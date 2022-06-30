import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    var = False
    # Where all operation dunder methods are located
    def __add__(self, other):
        return Add(self, other)

    def __sub__(self, other):
        return Sub(self, other)

    def __truediv__(self, other):
        return Div(self, other)

    def __mul__(self, other):
        return Mul(self, other)
    
    def __pow__(self, other):
        return Pow(self, other)
    
    def __radd__(self, other):
        return Add(other, self)

    def __rsub__(self, other):
        return Sub(other, self)

    def __rtruediv__(self, other):
        return Div(other, self)

    def __rmul__(self, other):
        return Mul(other, self)
    
    def __rpow__(self, other):
        return Pow(other, self)
    

class Var(Symbol):
    var = True
    precedence = 3
    def __init__(self, n):
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Var(" + repr(self.name) + ")"
    
    def deriv(self, var):
        return Num(1) if self.name == var else Num(0)
    
    def simplify(self):
        return self

class Num(Symbol):
    precedence = 3
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return "Num(" + repr(self.n) + ")"
    
    def deriv(self, var):
        return Num(0)
    
    def simplify(self):
        return self

def make_compatible_type(value):
    """
    Helper function that ensures that the left and right values of
    a BinOp object are the correct type.
    """
    if isinstance(value, (int, float)):
        return Num(value)
    elif isinstance(value, str):
        return Var(value)
    elif isinstance(value, Symbol):
        return value
    raise TypeError

class BinOp(Symbol):
    def __init__(self, left, right):
        self.left = make_compatible_type(left)
        self.right = make_compatible_type(right)

    def __str__(self):
        """
        Sample string representation: 'x + y - 2'
        """
        left_str = str(self.left)
        right_str = str(self.right)
        if (self.left.precedence < self.precedence) or (self.precedence == 2 and self.left.precedence <= self.precedence):
            left_str = '(' + left_str + ')'
        if (self.right.precedence < self.precedence) or (self.special_case == True and self.right.precedence == self.precedence):
            right_str = '(' + right_str + ')'
        return left_str + self.operator + right_str
    
    def __repr__(self):
        """
        Sample representation: Add(Var('x'), Sub(Var('y'), Num(2)))
        """
        return self.name + "(" + repr(self.left) + ', ' + repr(self.right) + ")"

    def simplify(self):
        """
        Utilizes the base simplify of whichever BinOp it is to recursively simplify
        the expression.
        """
        left = self.left.simplify()
        right = self.right.simplify()
        return self.base_simplify(left, right)
    
    def base_eval(self, vars, left, right):
        """
        Helper function to eval that does evaluation at the base level of when
        the left and right are numbers or varaibles.
        """
        ops = {' + ': (lambda x,y: x+y), 
               ' - ': (lambda x,y: x-y), 
               ' * ': (lambda x,y: x*y), 
               ' / ': (lambda x,y: x/y),
               ' ** ': (lambda x,y: x**y)
                }
        if (left.var == True and left.name not in vars) or (right.var == True and right.name not in vars):
            raise LookupError('Variable does not have a mapping in the dictionary')
        if left.var == True and left.name in vars:
            left = Num(vars[left.name])
        if right.var == True and right.name in vars:
            right = Num(vars[right.name])        
        result = ops[self.operator](left, right)
        return result.simplify()

    def _eval(self, vars):
        """
        Helper function to eval that does the recursive evaluating.
        """
        # if left is not a variable or number, recursively calls eval function 
        left = self.left._eval(vars) if self.left.precedence != 3 else self.left
        right = self.right._eval(vars) if self.right.precedence != 3 else self.right
        return self.base_eval(vars, left, right)
    
    def eval(self, vars):
        """
        Returns the number value of the evaluated expression.
        """
        return self._eval(vars).n

        

class Add(BinOp):
    operator = ' + '
    precedence = 0
    special_case = False
    name = 'Add'

    def deriv(self, var):
        return self.left.deriv(var) + self.right.deriv(var)
    
    def base_simplify(self, left, right):
        # If right added by 0, return right
        if isinstance(left, Num) and left.n == 0:
            return right
        # If left added by 0, return left
        elif isinstance(right, Num) and right.n == 0:
            return left
        # If two numbers, compute the numbers
        elif isinstance(left, Num) and isinstance(right, Num):
            return Num(left.n+right.n)
        return Add(left, right)

class Sub(BinOp):
    operator = ' - '
    precedence = 0
    special_case = True
    name = 'Sub'

    def deriv(self, var):
        return self.left.deriv(var) - self.right.deriv(var)
    
    def base_simplify(self, left, right):
        # If left subtracted by 0, return left
        if isinstance(right, Num) and right.n == 0:
            return left
        # If two numbers, compute the subtraction
        elif isinstance(left, Num) and isinstance(right, Num):
            return Num(left.n-right.n)
        return Sub(left, right)
    

class Mul(BinOp):
    operator = ' * '
    precedence = 1
    special_case = False
    name = 'Mul'

    def deriv(self, var):
        return self.left*self.right.deriv(var) + self.right*self.left.deriv(var)
    
    def base_simplify(self, left, right):
        # If right multiplied by 1, return right
        if isinstance(left, Num) and left.n == 1:
            return right
        # If left multiplied by 1, return left
        elif isinstance(right, Num) and right.n == 1:
            return left
        # If multiplied by 0, return 0
        elif (isinstance(right, Num) and right.n == 0) or (isinstance(left, Num) and left.n == 0):
            return Num(0)
        # If two numbers, compute the multiplication
        elif isinstance(left, Num) and isinstance(right, Num):
            return Num(left.n*right.n)
        return Mul(left, right)
      
class Div(BinOp):
    operator = ' / '
    precedence = 1
    special_case = True
    name = 'Div'

    def deriv(self, var):
        return ((self.right*self.left.deriv(var) - self.left*self.right.deriv(var)) / (self.right * self.right))
    
    def base_simplify(self, left, right):
        # If 0 divided by something, return 0
        if isinstance(left, Num) and left.n == 0:
            return Num(0)
        # If number/var divided by 1, return self
        elif isinstance(right, Num) and right.n == 1:
            return left
        # If two numbers, compute the division
        elif isinstance(left, Num) and isinstance(right, Num):
            return Num(left.n/right.n)
        return Div(left, right)
    
class Pow(BinOp):
    operator = ' ** '
    name = 'Pow'
    precedence = 2
    special_case = False

    def deriv(self, var):
        return ((self.right * self.left ** (self.right - 1)) * self.left.deriv(var))
    
    def base_simplify(self, left, right):
        # If to power of 0, return 1
        if isinstance(right, Num) and right.n == 0:
            return Num(1)
        # If to power of self, return self
        elif isinstance(right, Num) and right.n == 1:
            return left
        # If 0 to positive int power or variable power, return 0
        elif isinstance(left, Num) and ((isinstance(right, Num) and right.n > 0) or (isinstance(right, Symbol) and not isinstance(right, Num))) and left.n == 0:
            return Num(0)
        # If two numbers, compute power
        elif isinstance(left, Num) and isinstance(right, Num):
            return Num(left.n ** right.n) 
        return Pow(left, right)

def tokenize(expression):
    tokens = expression.replace('(', ' ( ').replace(')', ' ) ').split()
    return tokens

def parse(tokens):
    """
    Given a list of tokens, parses through the list using the parse_expression helper function.
    """
    digits = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9'}
    operators = {'(', ')', '+', '-', '/', '*'}
    op_dict = { '+': Add,
                '-': Sub,
                '*': Mul,
                '/': Div,
                '**': Pow
    }
    def parse_expression(index):
        """
        Given the starting index, parses the list of tokens into the correct symbolic expression
        representation.
        """
        # Checks to see if character at index is a variable
        if len(tokens[index]) == 1 and tokens[index] not in operators and tokens[index] not in digits:
            return Var(tokens[index]), index+1
        # Checks to see if character at index is a number
        elif tokens[index] not in operators:
            return Num(float(tokens[index])), index+1
        # Otherwise, recursively finds operations in the form (e1 op e2)
        else:
            left, index = parse_expression(index+1)
            operator = op_dict[tokens[index]]
            right, index = parse_expression(index +1)
            return operator(left, right), index + 1
    parsed_expression = parse_expression(0)[0]
    return parsed_expression

def sym(expression):
    """

    Using both the tokenize and parse helper functions, takes in an expression, converts it 
    to a list of tokens and uses that list of tokens to create a matching symbolic expression
    representation.
    """
    return parse(tokenize(expression))

print(sym('(x * (2 + 3))'))

# print(tokenize('35 + -456'))
# print(tokenize("(x * (2 + 3))"))

if __name__ == "__main__":
    doctest.testmod()
    # z = Mul(Var('x'), Add(Var('y'), Var('z')))
    y = Mul(Var('x'), 2) + Mul(Add(Var('y'), 5), 2)
    # y = Var('x') + Var('y')
    vars = {'x': 3}
    z = Pow(Var('x'), 3)
    print(z.eval(vars))
    result = Add(Mul(Var('x'), Var('y')), Var('z'))
    print(result.deriv('x'))
    print(result)
    print((result.eval({'z': 758, 'y': 95, 'x': -530})))
    # z.base_eval(vars, z.left, z.right)
    # print(repr(y))
    # y.eval(vars)
   
