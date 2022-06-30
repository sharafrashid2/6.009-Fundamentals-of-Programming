#!/usr/bin/env python3
"""6.009 Lab 8: Snek Interpreter"""

import doctest

# NO ADDITIONAL IMPORTS!


###########################
# Snek-related Exceptions #
###########################


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
    for item in tokens:
        if item == '(':
            open_parens += 1
        elif item == ')' and close_parens + 1 > open_parens:
            raise SnekSyntaxError
        elif item == ')':
            close_parens += 1
    
    if open_parens != close_parens or (open_parens == 0 and len(tokens) > 1):
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

    # Error cases with define
    if isinstance(parsed_expression[0], list) and parsed_expression[0][0] == 'define' and (
        (len(parsed_expression[0]) != 3 or isinstance(parsed_expression[0][1], (int, float)))):
        raise SnekSyntaxError
    # Error cases with shorthand functions
    if isinstance(parsed_expression[0], list) and parsed_expression[0][0] == 'define' and (
        isinstance(parsed_expression[0][1], list) and len(parsed_expression[0][1]) == 0):
        raise SnekSyntaxError
    # Error cases with lambda
    if isinstance(parsed_expression[0], list) and parsed_expression[0][0] == 'lambda' and (
        (len(parsed_expression[0]) != 3 or not isinstance(parsed_expression[0][1], list))):
        raise SnekSyntaxError
    # Error case where function parameters are a number and not a variable (both for lambda and shorthand form)
    elif isinstance(parsed_expression[0], list) and ((parsed_expression[0][0] == 'define' and (
        isinstance(parsed_expression[0][1], list)) or parsed_expression[0][0] == 'lambda')):
        for elt in parsed_expression[0][1]:
            if isinstance(elt, (int, float)):
                raise SnekSyntaxError

    return parsed_expression[0]



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

snek_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*":  product,
    "/": quotient
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
    # Case for when lambda is in the expression
    if isinstance(tree, list) and 'lambda' in tree:
        func = Function(tree[1], tree[2], envir)
        return func if test == False else (func, envir)
    
    # Case for when define is in the expression
    elif isinstance(tree, list) and 'define' in tree:
        # Special case for when the short hand notation for defining a function is used
        if isinstance(tree[1], list) and (len(tree[1]) > 0):
            print(tree[1])
            params = [elt for elt in tree[1][1:]]
            body = tree[2]
            func = Function(params, body, envir)
            envir[tree[1][0]] = func
            return func if test == False else (func, envir)
        # Standard procedure for define
        val = evaluate(tree[2], envir)
        envir[tree[1]] = val
        return val if test == False else (val, envir)
    
    # Case for when there is a variable in the expression that has been defined
    elif not isinstance(tree, list) and isinstance(tree, str):
        return envir[tree] if test == False else (envir[tree], envir)
    
    # Case for when there is a number
    elif not isinstance(tree, list):
        return tree if test == False else(tree, envir)
    
    # Case for when there is a variable that has not been defined
    elif not isinstance(tree[0], list) and tree[0] not in envir:
        raise SnekEvaluationError
    
    # Simplifies an expression until all that is left is an s expression that can be evaluated
    for i in range(1, len(tree)):
        val = evaluate(tree[i], envir)
        l1.append(val)
    
    # Case of in line lambda evaluation
    if isinstance(tree[0], list):
        temp_func = evaluate(tree[0], envir)
        arguments = [evaluate(elt, envir) for elt in tree[1:]]
        return temp_func(arguments) if test == False else (temp_func(arguments), envir)
        
    return envir[tree[0]](l1) if test == False else (envir[tree[0]](l1), envir)




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
    doctest.testmod()

    envir = Environment({}, Environment(snek_builtins))
    while True:
        inp = input('in> ')
        if inp == 'QUIT':
            break
        tokens = tokenize(inp)
        parsed = parse(tokens)
        result, envir = result_and_env(parsed, envir)
        print('out> ', result)
