"""6.009 Lab 9: Snek Interpreter Part 2"""

import sys
import doctest
sys.setrecursionlimit(10_000)

# KEEP THE ABOVE LINES INTACT, BUT REPLACE THIS COMENT WITH YOUR lab.py FROM
# THE PREVIOUS LAB, WHICH SHOULD BE THE STARTING POINT FOR THIS LAB.

class SnekError(Exception):
    """
    A type of exception to be raised if there is an error with a Snek
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """
    pass


class SnekSyntaxError(SnekError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """
    pass


class SnekNameError(SnekError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """
    pass


class SnekEvaluationError(SnekError):
    """
    Exception to be raised if there is an error during evaluation other than a
    SnekNameError.
    """
    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(x):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Snek
                      expression
    """
    tokenized = source.replace('(', ' ( ').replace(')', ' ) ').replace('\n', ' )n ').split()
    i = 0
    remove = False 

    while i < (len(tokenized)):
         # Removes new lines
        if tokenized[i] == ')n':
            remove = False
            tokenized.pop(i)
            i -= 1

        # Ignores comments
        if ';' in tokenized[i] or remove == True:
            remove = True
            tokenized.pop(i)
            i -= 1
        i += 1

    return tokenized


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens

    >>> print(parse(tokenize('(lambda () (+ 2 3 5))')))
    ['lambda', [], ['+', 2, 3, 5]]

    >>> print(parse(tokenize('(define square (lambda (2) ((* x x))))')))
    ['define', 'square', ['lambda', [2], [['*', 'x', 'x']]]]
    """

    # Raises error if there are an uneven number of parentheses
    open_parens = 0
    close_parens = 0
    for i in range(len(tokens)):
        if tokens[i] == '(':
            open_parens += 1
        elif tokens[i] == ')' and close_parens + 1 > open_parens:
            raise SnekSyntaxError
        elif tokens[i] == ')':
            close_parens += 1
    
    if (len(tokens) > 1 and tokens[0] != '(') or open_parens != close_parens or (open_parens == 0 and len(tokens) > 1):
        raise SnekSyntaxError
    
    # Helper function that does the actual parsing
    def parse_expression(tokens):
        # If number or symbol
        if len(tokens) == 1:
            return number_or_symbol(tokens[0]), 1
        # S-expression
        # Case for lambda with empty list of arguments
        exp = []
        index = 1
        while index < len(tokens):
            # When close paren is reached, returns the expression
            if tokens[index] == ')':
                return exp, index + 1
            # Parses all that is inside the parentheses
            elif tokens[index] == '(':
                val, updated_index = parse_expression(tokens[index:])
                exp.append(val)
                index += updated_index
            # Case if there is a number or variable
            else:
                exp.append(number_or_symbol(tokens[index]))
                index += 1
        return exp, index
        
    parsed_expression = parse_expression(tokens)
    if parsed_expression[0] == [] or not isinstance(parsed_expression[0], list):
        return parsed_expression[0]

    # Error cases with define
    if parsed_expression[0][0] == 'define' and (len(parsed_expression[0]) != 3 or isinstance(parsed_expression[0][1], (int, float))):
        raise SnekSyntaxError

    # Error cases with shorthand functions
    if parsed_expression[0][0] == 'define' and (isinstance(parsed_expression[0][1], list) and len(parsed_expression[0][1]) == 0):
        raise SnekSyntaxError

    # Error cases with lambda
    if parsed_expression[0][0] == 'lambda' and (len(parsed_expression[0]) != 3 or not isinstance(parsed_expression[0][1], list)):
        raise SnekSyntaxError

    # Error case where function parameters are a number and not a variable (both for lambda and shorthand form)
    elif ((parsed_expression[0][0] == 'define' and isinstance(parsed_expression[0][1], list) or parsed_expression[0][0] == 'lambda')):
        for elt in parsed_expression[0][1]:
            if isinstance(elt, (int, float)):
                raise SnekSyntaxError
    
    # Error case with if
    if parsed_expression[0][0] == 'if' and len(parsed_expression[0]) != 4:
        raise SnekSyntaxError

    return parsed_expression[0]

##############
# Pairs #
##############

class Pair():
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail

    def __eq__(self, other):
        if type(other) == Pair and self.head == other.head and self.tail == other.tail:
            return True
        return False

    def __repr__(self):
        return '(' + str(self.head) + ' ' + str(self.tail) + ')'




######################
# Built-in Functions #
######################

def product(iter):
    """
    Given an iterable, returns the product of all values in the iterable.
    """
    product = 1
    for val in iter:
        product *= val
    return product

# print('prod ', product([2, 3, 5, 10]))

def quotient(iter):
    """
    Given an iterable, returns the product of all values in the iterable.
    """
    for i in range(1, len(iter)):
        iter[i] = 1/iter[i]
    return product(iter)

def equals(iter):
    """
    Given an iterable, returns True if all arguments are equal to each other; otherwise, false.
    """

    for i in range(len(iter)-1):
        if iter[i] != iter[i+1]:
            return '#f'
    return '#t'

def greater(iter):
    """
    Given an iterable, returns True if arguments are in decreasing order; otherwise, false.
    """
    for i in range(len(iter) - 1):
        if iter[i] <= iter[i+1]:
            return '#f'
    return '#t'

def greater_equal(iter):
    """
    Given an iterable, returns True if arguments are in nonincreasing order; otherwise, false.
    """
    for i in range(len(iter) - 1):
        if iter[i] < iter[i+1]:
            return '#f'
    return '#t'

def less(iter):
    """
    Given an iterable, returns True if arguments are in increasing order; otherwise, false.
    """
    for i in range(len(iter) - 1):
        if iter[i] >= iter[i+1]:
            return '#f'
    return '#t'

def less_equal(iter):
    """
    Given an iterable, returns True if arguments are in increasing order; otherwise, false.
    """
    for i in range(len(iter) - 1):
        if iter[i] > iter[i+1]:
            return '#f'
    return '#t'

def _not(arg):
    """
    Given an argument, returns opposite of the argument.
    """
    if len(arg) == 0 or len(arg) > 1:
        raise SnekEvaluationError
    elif arg[0] == '#t':
        return '#f'
    return '#t'

def pair(arg):
    """
    Creates a pair object.
    """
    if len(arg) != 2:
        raise SnekEvaluationError
    return Pair(arg[0], arg[1])


def head(arg):
    """
    Given a pair, returns the head (first item) of the pair.
    """
    if arg == [] or not isinstance(arg[0], Pair) or len(arg) != 1:
        raise SnekEvaluationError
    return arg[0].head

def tail(arg):
    """
    Given a pair, returns the tail (second item) of the pair.
    """
    if arg == [] or not isinstance(arg[0], Pair) or len(arg) != 1:
        raise SnekEvaluationError
    return arg[0].tail

def list_eval(arg):
    """
    Evaluates a list so that it is in the form of a linked list made of Pairs.
    """
    # empty list case
    if len(arg) == 0:
        return 'nil'
    # helper function
    def _list_eval(index, arg):
        arg_len = len(arg) - 1
        # base case
        if index == 0:
            return Pair(arg[arg_len], 'nil')
        # recursive case
        return Pair(arg[arg_len - index], _list_eval(index-1, arg))
    return _list_eval(len(arg) - 1, arg)

def islist(l1):
    """
    Helper Function: Checks to see if a pair is a list.
    """
    # if 'nil' then it is an empty list
    if l1 == 'nil':
        return True
    # raises error if argument not a Pair
    elif type(l1) != Pair:
        raise SnekEvaluationError
    # if ends with a tail that is nil, then it is a list
    elif l1.tail == 'nil':
        return True
    elif type(l1.tail) == Pair:
        return islist(l1.tail)
    return False

def length(l1, index=1, start=True):
    """
    Finds the length of a list.
    """
    if start==True:
        if len(l1) != 1:
            raise SnekEvaluationError
        _list = l1[0]
    else:
        _list = l1
    
    # raises error if argument not a list
    if islist(_list) == False:
        raise SnekEvaluationError
    # base case empty list
    if _list == 'nil':
        return 0
    # base case list of length 1
    elif _list.tail == 'nil':
        return index
    # recursive case
    return length(_list.tail, index+1, False)


def nth(iter, l1 = None, i = None, start=True):
    """
    Finds the nth value of a list.
    """
    _list = iter[0] if start == True else l1
    index = iter[1] if start == True else i

    # Raises error if item not a pair
    if not isinstance(_list, Pair) or islist(_list) == False and index != 0:
        raise SnekEvaluationError
    elif index == 0:
        return _list.head
    return nth(iter, _list.tail, index-1, False)


def append_list(l1, val):
    """
    Helper function to the concat function that adds a Pair to the end of the list.
    """
    if l1 == 'nil':
        return val
    if l1.tail == 'nil':
        new = Pair(l1.head, val)
        return new
    return Pair(l1.head, append_list(l1.tail, val))

# print(append_list('nil', Pair(2, 'nil')))

def concat(iter):
    """
    Concatenates multiple lists together.
    """
    
    if len(iter) == 0:
        return 'nil'

    concatenated = 'nil'
    # if inital item in argument not a list, raise rror

    # loops through every list
    for i in range(len(iter)):
        current = iter[i]
        # raises error if item in argument is not a list
        if concatenated != 'nil' and islist(concatenated) == False:
            raise SnekEvaluationError
        # case if list is empty
        elif concatenated == 'nil':
            concatenated = current
            continue
        elif current != 'nil':
            concatenated = append_list(concatenated, current)
    return concatenated

def _map(iter, f1 = None, l1 = None, start=True):
    """
    Applies a function to every item in the list
    """
    _func = iter[0] if start == True else f1
    _list = iter[1] if start == True else l1

    # empty list case
    if _list == 'nil':
        return 'nil'

    #if argument not a list
    elif islist(_list) == False:
        raise SnekEvaluationError
    # base case
    elif _list.tail == 'nil':
        return Pair(_func([_list.head]), 'nil')
    # recursive case
    return Pair(_func([_list.head]), _map(iter, _func, _list.tail, False))

def _filter(iter):
    """
    Returns a new list with only values that return true when inputted into the given function.
    """
    bool_list = _map(iter)
    _list = iter[1]
    new_list = 'nil'

    #loops through every value
    for i in range(length(bool_list, start=False)):
        #only gets added to new list if value in list after function applied is true
        if nth(None, bool_list, i, False) == '#t':
            val = nth(None, _list, i, False)
            new_list = append_list(new_list, Pair(val, 'nil'))
    return new_list

def reduce(iter, f1 = None, l1 = None, initval = None, start = True):
    """
    First applies function on initial value and first value of given list
    and stores the result as an intermediate value. Then continues to do the same
    with the current intermediate value and next value in the list until all values
    have been interated through. Once done, returns the result.
    """
    _func = iter[0] if start == True else f1
    _list = iter[1] if start == True else l1
    _initval = iter[2] if start == True else initval
    
    if _list == 'nil':
        return _initval
    current = _func([_initval, nth(None, _list, 0, False)])
    # loops through remaining 
    for i in range(1, length(_list, start=False)):
        current = _func([current, nth(None, _list, i, False)])
    return current

def begin(iter):
    """
    Runs commands successively but only returns the last value
    """
    # Just this is needed because due to how evaluate is structured, the previous lines have already been evaluated
    return iter[-1]


snek_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*":  product,
    "/": quotient,
    "=?": equals,
    ">": greater,
    ">=": greater_equal,
    "<": less,
    "<=": less_equal,
    "not": _not,
    "define": None,
    "lambda": None,
    "and": None,
    "or": None,
    "if": None,
    "#t": "#t",
    "#f": "#f",
    "pair": pair,
    "head": head,
    "tail": tail,
    "nil": "nil",
    "list": list_eval,
    "length": length,
    "nth": nth,
    "concat": concat,
    "map": _map,
    "filter": _filter,
    "reduce": reduce,
    "begin": begin, 
    "del": None,
    "let": None,
    "set!": None,
}

##############
# Environments #
##############

class Environment():
    """

    Class to represent environments that are created to determine scope
    when evaluating code in an interpreter.
    """
    def __init__(self, variables = {}, parent=None):
        """
        Initializes an environment object with existing variable assignments if 
        there are any, and a parent environment if there is any.
        """
        self.parent = parent
        self.variables = variables

    def __setitem__(self, var, val):
        """
        Adds a variable binding to the environment.
        """
        self.variables[var] = val
    
    def __getitem__(self, var):
        """
        Retrieves a variable's value.
        """
        if var in self.variables:
            return self.variables[var]
        elif self.parent != None:
            return self.parent[var]
        else:
            raise SnekNameError
    
    def __str__(self):
        """
        String representation of an environnment that 
        lists all existing variable bindings.
        """
        return str(self.variables)
    
    def __contains__(self, item):
        """
        Checks if a variable is in the environment, and if not,
        if it is in the parent environment.
        """
        if item in self.variables:
            return True
        elif self.parent != None:
            return item in self.parent
        else:
            return False
    
    def in_local(self, var):
        """
        Check if a variable is in just the local environment.
        """
        if var in self.variables:
            return True
        return False
    
    def update_var(self, var, val):
        """
        Changes a variable's binding in the closest environment from the current one.
        """
        if self.in_local(var):
            self.variables[var] = val
        elif self.parent != None:
            return self.parent.update_var(var, val)
        return None
    
    def remove_var(self, var):
        """
        Removes a variable's binding from the environment.
        """
        self.variables.pop(var)

##########################
# User-defined Functions #
##########################       
class Function():
    """
    Class to represent the function object in our LISP interpreter.
    """
    def __init__(self, parameters, expression, pointer_envir):
        """
        Initializes the function object with parameters, an expression, and
        a pointer environment.
        """
        self.parameters = parameters
        self.expression = expression
        self.pointer_envir = pointer_envir

    def __call__(self, args):
        """
        Method for calling a function, returning the result of the call.
        """
        # Makes sure argument and parameter lists have same length
        if len(args) != len(self.parameters):
            raise SnekEvaluationError

        variables = {}
        # Sets each variable in the argument to the parameter
        for i in range(len(args)):
            variables[self.parameters[i]] = args[i] 

        # Creates a new environment where the result is evaluated
        new_envir = Environment(variables, self.pointer_envir)
        result = evaluate(self.expression, new_envir)
        return result


##############
# Evaluation #
##############

def evaluate(tree, envir=Environment({}, Environment(snek_builtins)), test=False):
    """
    Evaluate the given syntax tree according to the rules of the Snek
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    
    >>> print(evaluate(['+', 3, ['-', 7, 5]]))
    5
    >>> print(evaluate(['define', 'x', 4]))
    4
    >>> print(evaluate([['lambda', [], ['+', 2, 3, 5]]]))
    10

    """
    l1 = []

    if tree == []:
        raise SnekEvaluationError
    # Case for when there is a variable in the expression that has been defined
    elif not isinstance(tree, list) and isinstance(tree, str):
        return envir[tree] if test == False else (envir[tree], envir)
    
    # Case for when there is a number
    if not isinstance(tree, list):
        return tree if test == False else(tree, envir)

    # Case for when lambda is in the expression
    elif tree[0] == 'lambda':
        func = Function(tree[1], tree[2], envir)
        return func if test == False else (func, envir)
    
    # Case for when define is in the expression
    elif tree[0] == 'define':
        # Special case for when the short hand notation for defining a function is used
        if isinstance(tree[1], list) and (len(tree[1]) > 0):
            params = [elt for elt in tree[1][1:]]
            body = tree[2]
            func = Function(params, body, envir)
            envir[tree[1][0]] = func
            return func if test == False else (func, envir)
        # Standard procedure for define
        val = evaluate(tree[2], envir)
        envir[tree[1]] = val
        return val if test == False else (val, envir)
    
    # Error case where multiple numbers are inputted between parentheses
    elif all([isinstance(val, (int, float)) for val in tree]):
        raise SnekEvaluationError

    # Case for when there is a variable in a function body that has not been defined
    elif not isinstance(tree[0], list) and tree[0] not in envir:
        raise SnekNameError
    
    # Case of in line lambda evaluation
    elif isinstance(tree[0], list):
        temp_func = evaluate(tree[0], envir)
        arguments = [evaluate(elt, envir) for elt in tree[1:]]
        return temp_func(arguments) if test == False else (temp_func(arguments), envir)
    
    # Case for when 'and' is in the expression
    elif tree[0] == 'and':
        for val in tree[1:]:
            result = evaluate(val, envir)
            if result == '#f':
                return '#f' if test == False else ('#f', envir)
        return '#t' if test == False else ('#t', envir)
    
    # Case for when 'or' is in the expression
    elif tree[0] == 'or':
        for val in tree[1:]:
            result = evaluate(val, envir)
            if result == '#t':
                return '#t' if test == False else ('#t', envir)
        return '#f' if test == False else ('#f', envir)
    
    # Case for when 'if' is in the expression
    elif tree[0] == 'if':
        result = evaluate(tree[1], envir)
        if result == "#t":
            path1 = evaluate(tree[2], envir)
            return path1 if test == False else (path1, envir)
        path2 = evaluate(tree[3], envir)
        return path2 if test == False else (path2, envir)
    
    # Case for when 'del' is in the expression
    elif tree[0] == 'del':
        var = tree[1]
        if envir.in_local(var) == False:
            raise SnekNameError
        val = evaluate(var, envir)
        envir.remove_var(var)
        return val if test == False else (val, envir)
    
    # Case for when 'let' is in the expression
    elif tree[0] == 'let':
        v_list = tree[1]
        body = tree[2]
        variables = {var[0]:evaluate(var[1], envir) for var in v_list}
        new_envir = Environment(variables, envir)
        return evaluate(body, new_envir) if test == False else (evaluate(body, new_envir), envir)
    
    # Case for when 'set!' is in the expression
    elif tree[0] == 'set!':
        var = tree[1]
        val = evaluate(tree[2], envir)
        if var not in envir:
            raise SnekNameError
        envir.update_var(var, val)
        return val if test == False else(val, envir)
        
    
    # Simplifies an expression until all that is left is an s expression that can be evaluated
    for i in range(1, len(tree)):
        val = evaluate(tree[i], envir)
        l1.append(val)

    return envir[tree[0]](l1) if test == False else (envir[tree[0]](l1), envir)


def evaluate_file(file_n, envir = None):
    """
    Given a file name, and if desired, an environment, evaluates
    all the code in the file.
    """
    file = open(file_n)
    file_str = file.read()
    tokens = tokenize(file_str)
    parsed = parse(tokens)
    if envir == None:
        return evaluate(parsed)
    return evaluate(parsed, envir)

    

def result_and_env(tree, envir = None):
    """
    Evaluates a given tree and returns the result as well as the environment in which the tree
    was evaluated.
    """
    if envir == None:
        envir = Environment({}, Environment(snek_builtins))
    return evaluate(tree, envir, True)


##############
# REPL #
##############

if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()

    envir = Environment({}, Environment(snek_builtins))
    for i in range(1, len(sys.argv)):
        evaluate_file(sys.argv[i], envir)
    # print(envir)
    while True:
        inp = input('in> ')
        if inp == 'QUIT':
            break
        tokens = tokenize(inp)
        parsed = parse(tokens)
        result, envir = result_and_env(parsed, envir)
        print('out> ', result)