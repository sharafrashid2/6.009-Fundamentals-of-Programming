#!/usr/bin/env python3
"""6.009 Lab 6 -- Boolean satisfiability solving"""

from doctest import UnexpectedException
import sys
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS

def deep_copy(l1):
    """
    Returns a deep copy of a nested list.
    """
    new = []
    for i in range(len(l1)):
        if not isinstance(l1[i], list):
            new.append(l1[i])
        else:
            new.append(deep_copy(l1[i]))
    return new


def update_formula(formula, assignment):
    """
    >>> formula = [[('a', True), ('b', True), ('c', True)],
    ...              [('a', False), ('f', True)],
    ...              [('d', False), ('e', True), ('a', True), ('g', True)],
    ...              [('h', False), ('c', True), ('a', False), ('f', True)],
    ...           ]
    >>> update_formula(formula, ('a', True))
    [[('f', True)], [('h', False), ('c', True), ('f', True)]]

    >>> formula = [[('a', True), ('b', True), ('c', True)],
    ...              [('a', False), ('f', True)],
    ...              [('d', False), ('e', True), ('a', True), ('g', True)],
    ...              [('h', False), ('c', True), ('a', False), ('f', True)],
    ...           ]
    >>> update_formula(formula, ('a', False))
    [[('b', True), ('c', True)], [('d', False), ('e', True), ('g', True)]]
    """
    remove_clause = False
    clause_to_remove = ()
    new = deep_copy(formula)
    n_clauses_removed = 0
    # Loops through every literal in the formula
    for i in range(len(formula)):
        n_literals_removed = 0
        for j in range(len(formula[i])):
            # If the literal is same variable as assignment and the booleans match, makes note of the entire clause that the literal is in
            if formula[i][j][0] == assignment[0] and formula[i][j][1] == assignment[1]:
                remove_clause = True
                clause_to_remove = i
            # If the literal is same variable as assignment and booleans don't match, removes the literal from the clause it is in
            elif formula[i][j][0] == assignment[0]:
                new[i-n_clauses_removed].pop(j-n_literals_removed)
                n_literals_removed += 1

        # Removes the clause from earlier that was saved to a variable
        if remove_clause == True:
            new.pop(clause_to_remove-n_clauses_removed)
            n_clauses_removed += 1
            remove_clause = False
    return new

def satisfying_assignment(formula, assignments = {}):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    #Check if formula contains any unit clauses
    refined_formula = formula
    added_assignments = {}
    while True:
        unit_assignments = {}
        # Loops through each clause, finding unit clauses, and adding their assignments to a dictionary
        for clause in refined_formula:
            if len(clause) == 1:
                unit_assignments[clause[0][0]] = clause[0][1]
        # If no unit assignments remaining, exit loop
        if unit_assignments == {}:
            break
        # Applies the found assignments to the original formula
        for assignment in unit_assignments.items():
                refined_formula = update_formula(refined_formula, assignment)
        added_assignments = {**unit_assignments, **added_assignments}
    # If problem has no solutions after unit clause assignment, return None
    for clause in refined_formula:
            if clause == []:
                added_assignments = {}
                return None
    # Recursive Case
    if refined_formula == []:
        return {**added_assignments, **assignments}
    
    # Base Case
    else:
        # Loop through both True or False cases for assignment
        for bool in [True, False]:
            guess = refined_formula[0][0][0]
            # Apply all assignments to the formula and updates formula
            f_1 = update_formula(refined_formula, (guess, bool))
            # Skips to next possible assignment if current assignment results in a contradiction
            if [] in f_1:
                continue
            else:
                new_assignments = {guess:bool, **added_assignments, **assignments}
                output = satisfying_assignment(f_1, new_assignments)
                if isinstance(output, dict):
                    return output
    return None

        
def desired_sections(student_preferences):
    """
    (Helper function)
    Returns a CNF formula for the condition:
    For each student, they must have a room that they selected as one of their preferences.

    >>> stud_prefs = {'Alice': {'basement', 'penthouse'},
    ...               'Bob': {'kitchen'},
    ...               'Charles': {'basement', 'kitchen'},
    ...               'Dana': {'kitchen', 'penthouse', 'basement'}}
    >>> desired_sections(stud_prefs)
    [[('Alice_penthouse', True), ('Alice_basement', True)], [('Bob_kitchen', True)], [('Charles_kitchen', True), ('Charles_basement', True)], [('Dana_penthouse', True), ('Dana_kitchen', True), ('Dana_basement', True)]]
    """
    formula = []
    # Loops through each student and adds only the desired rooms to the formula
    for name in student_preferences:
        clause = []
        for room in student_preferences[name]:
            clause.append((name+'_'+room, True))
        formula.append(clause)
    return formula

def combination(students, n):
    """
    (Helper function)
    Given a list of student's names and a number n, returns all possible combinations for
    n groups of the students.

    >>> combination(['Bob', 'Smith', 'John', 'Harry'], 2)
    [['Bob', 'Smith'], ['Bob', 'John'], ['Bob', 'Harry'], ['Smith', 'John'], ['Smith', 'Harry'], ['John', 'Harry']]
    """
    # Base case
    if n == 0:
        return [[]]
    # Recursive case
    combinations = []
    # Loops through every student
    for i in range(0, len(students)):
        m = students[i]
        other_students = students[i + 1:]
        # Recursively adds all the combinations together, by decrementing n by 1 and using the other students remaining
        for p in combination(other_students, n-1):
            combinations.append([m]+p)
    return combinations

def one_session(student_preferences, room_capacities):
    """
    (Helper Function)
    Returns a CNF formula for the condition:
    Each student is assigned to at most one room, In other words, for any pair of rooms, any given student can be in only one of them.

    >>> stud_prefs = {'Alice': {'basement', 'penthouse'},
    ...               'Bob': {'kitchen'},
    ...               'Charles': {'basement', 'kitchen'},
    ...               'Dana': {'kitchen', 'penthouse', 'basement'}}
    >>> room_cap = {'basement': 1,
    ...             'kitchen': 2,
    ...             'penthouse': 4}
    >>> one_session(stud_prefs, room_cap)
    [[('Alice_basement', False), ('Alice_kitchen', False)], [('Alice_basement', False), ('Alice_penthouse', False)], [('Alice_kitchen', False), ('Alice_penthouse', False)], [('Bob_basement', False), ('Bob_kitchen', False)], [('Bob_basement', False), ('Bob_penthouse', False)], [('Bob_kitchen', False), ('Bob_penthouse', False)], [('Charles_basement', False), ('Charles_kitchen', False)], [('Charles_basement', False), ('Charles_penthouse', False)], [('Charles_kitchen', False), ('Charles_penthouse', False)], [('Dana_basement', False), ('Dana_kitchen', False)], [('Dana_basement', False), ('Dana_penthouse', False)], [('Dana_kitchen', False), ('Dana_penthouse', False)]]
    """
    rooms = [room for room in room_capacities]
    formula = []
    # Loops through every student and adds all possible combinations of pairs for rooms
    for student in student_preferences:
        stud_room = [(student + '_' + room, False) for room in rooms]
        formula += combination(stud_room, 2)
    return formula


def no_oversubscribed(student_preferences, room_capacities):
    """
    (Helper Function)
    Returns a CNF formula for the condition:
    if a given room can contain N students, then in every possible group of N+1 students,
    there must be at least one student who is not in the given room.

    >>> stud_prefs = {'Alice': {'basement', 'penthouse'},
    ...               'Bob': {'kitchen'},
    ...               'Charles': {'basement', 'kitchen'},
    ...               'Dana': {'kitchen', 'penthouse', 'basement'}}
    >>> room_cap = {'basement': 1,
    ...             'kitchen': 2,
    ...             'penthouse': 4}
    >>> one_session(stud_prefs, room_cap)
    [[('Alice_basement', False), ('Bob_basement', False)], [('Alice_basement', False), ('Charles_basement', False)], [('Alice_basement', False), ('Dana_basement', False)], [('Bob_basement', False), ('Charles_basement', False)], [('Bob_basement', False), ('Dana_basement', False)], [('Charles_basement', False), ('Dana_basement', False)], [('Alice_kitchen', False), ('Bob_kitchen', False), ('Charles_kitchen', False)], [('Alice_kitchen', False), ('Bob_kitchen', False), ('Dana_kitchen', False)], [('Alice_kitchen', False), ('Charles_kitchen', False), ('Dana_kitchen', False)], [('Bob_kitchen', False), ('Charles_kitchen', False), ('Dana_kitchen', False)]]
    """
    students = [student for student in student_preferences]
    rooms = [room for room in room_capacities.items() if room[1] < len(student_preferences)]
    formula = []
    # Loops through the rooms and adds all possible combinations of students in groups of each room's capacity number plus 1
    for room in rooms:
        stud_room = [(student + '_' + room[0], False) for student in students]
        formula += combination(stud_room, room[1]+1)
    return formula
            
def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz-room-scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a set
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    combined = desired_sections(student_preferences) + one_session(student_preferences, room_capacities) + no_oversubscribed(student_preferences, room_capacities)
    return combined

if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    # doctest.testmod(optionflags=_doctest_flags)
    doctest.run_docstring_examples(
       one_session,
       globals(),
       optionflags=_doctest_flags,
       verbose=False)
