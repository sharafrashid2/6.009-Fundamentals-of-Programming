#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

# NO IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION

def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, False, False, False]
        [False, False, False, False]
    state: ongoing
    """
    return new_game_nd((num_rows, num_cols), bombs)


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['mask'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['mask'][bomb_location] ==
    True), 'victory' when all safe squares (squares that do not contain a bomb)
    and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    mask:
        [False, True, True, True]
        [False, False, True, True]
    state: victory

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    mask:
        [True, True, False, False]
        [False, False, False, False]
    state: defeat

    >>> game = new_game_2d(6, 6, [(3, 0), (0, 5), (1, 3), (2, 3)])
    >>> dig_2d(game, 1, 0)
    9
    >>> dump(game)
    board:
    [0, 0, 1, 1, 2, '.']
    [0, 0, 2, '.', 3, 1]
    [1, 1, 2, '.', 2, 0]
    ['.', 1, 1, 1, 1, 0]
    [1, 1, 0, 0, 0, 0]
    [0, 0, 0, 0, 0, 0]
    dimensions: (6, 6)
    mask:
        [True, True, True, False, False, False]
        [True, True, True, False, False, False]
        [True, True, True, False, False, False]
        [False, False, False, False, False, False]
        [False, False, False, False, False, False]
        [False, False, False, False, False, False]
    state: ongoing

    >>> dig_2d(game, 5, 4)
    21
    >>> dump(game)
    board:
        [0, 0, 1, 1, 2, '.']
        [0, 0, 2, '.', 3, 1]
        [1, 1, 2, '.', 2, 0]
        ['.', 1, 1, 1, 1, 0]
        [1, 1, 0, 0, 0, 0]
        [0, 0, 0, 0, 0, 0]
    dimensions: (6, 6)
    mask:
        [True, True, True, False, False, False]
        [True, True, True, False, True, True]
        [True, True, True, False, True, True]
        [False, True, True, True, True, True]
        [True, True, True, True, True, True]
        [True, True, True, True, True, True]
    state: ongoing
    """
    return dig_nd(game, (row, col))
   

def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['mask'] indicates which squares should be visible.  If xray
    is True (the default is False), game['mask'] is ignored and all cells are
    shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'mask':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    return render_nd(game, xray)

def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['mask']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'mask':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'

    """
    twod_list = render_2d_locations(game, xray)
    n_rows = game['dimensions'][0]
    n_columns = game['dimensions'][1]
    str_rendition = ""

    for r in range(n_rows):
        for c in range(n_columns):
            if r > 0 and c == 0:
                str_rendition += '\n'
            str_rendition += twod_list[r][c]
    return str_rendition

# 2-D Helper Functions 

def vis_output(value, mask_bool, xray):
    """
    Returns the value that should be printed in the 2d locations
    rendition depending on the given value, value in the mask 2-d list,
    and x-ray condition.

    Parameters:
        value (str): the value at a given location
        mask_bool (bool): the mask boolean at a given location (whether you can see value or not)
        xray (bool): whether the xray is on or off

    Returns:
        the correct value that is printed out on the game board
    """
    if  mask_bool == True or xray == True:
        if value == 0:
            return ' '
        return value
    elif xray == False and mask_bool == False:
        return '_'


# N-D IMPLEMENTATION

def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'mask' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of lists, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: ongoing  
    """
    game = {}
    game['board'] = nd_list_creator(dimensions, 0)

    for bomb in bombs:
        val_at_coord_replace(game['board'], bomb, '.')

    all_coordinates = flat_board(dimensions)

    for coordinate in all_coordinates:
        bomb_neighbors = 0
        if coordinate_indexer(game['board'], coordinate) != '.':
            neighbors = neighbors_without_self(coordinate, dimensions)
            for neighbor in neighbors:
                if coordinate_indexer(game['board'], neighbor) == '.':
                    bomb_neighbors += 1
            val_at_coord_replace(game['board'], coordinate, bomb_neighbors)
    game['dimensions'] = dimensions
    game['mask'] = nd_list_creator(dimensions, False)
    game['state'] = 'ongoing'
    return game

# Helper Functions

def nd_list_creator(dimensions, value):
    """
    Creates a list of n-dimensional size according to the specified dimensions
    and fills each item in that list with the specified value.

    >>> nd_list_creator((3, 3, 3), 5)
    [[[5, 5, 5], [5, 5, 5], [5, 5, 5]], [[5, 5, 5], [5, 5, 5], [5, 5, 5]], [[5, 5, 5], [5, 5, 5], [5, 5, 5]]]
    """
    # works
    dimension_number = len(dimensions)
    if dimension_number == 1:
        return [value] * dimensions[0]
    else:
        return [nd_list_creator(dimensions[1:], value) for _ in range(dimensions[0])]
        

def coordinate_indexer(board, coordinates):
    """
    Given coordinates and the board associated with them, returns the 
    value at those coordinates.

    >>> board = [[[0, 0], [1, 1], [1, 1]], [[0, 0],
    ...          [1, 1], ['.', 1]], [[0, 0], [1, 1],
    ...          [1, 1]]]
    >>> coordinate_indexer(board, (0, 1, 1))
    1
    """
    # works
    if len(coordinates) == 1:
        return board[coordinates[0]]
    else:
        coordinate_reduced = list(coordinates)
        length = coordinate_reduced.pop()
        return coordinate_indexer(board, coordinate_reduced)[length]

def val_at_coord_replace(board, coordinates, value):
    """
    Given the coordinates and the board associated with it, replaces
    the value at the coordinate with the value inputted into the 
    function.

    >>> board = [[[0, 0], [1, 1], [1, 1]], [[0, 0],
    ...          [1, 1], ['.', 1]], [[0, 0], [1, 1],
    ...          [1, 1]]]
    >>> val_at_coord_replace(board, (0, 1, 1), 12)
    >>> print(board)
    [[[0, 0], [1, 12], [1, 1]], [[0, 0],
    [1, 1], ['.', 1]], [[0, 0], [1, 1],
    [1, 1]]]
    """
    #works
    coordinate_reduced = list(coordinates)
    current = board
    while len(coordinate_reduced) > 1:
        current = current[coordinate_reduced[0]]
        coordinate_reduced.pop(0)
    current[coordinate_reduced[0]] = value

def find_neighbors_nd(coordinates, dimensions):
    """
    Given the dimensions of the game board and a coordinate, returns the 
    coordinates of all the neighbors of the original coordinate.
    """
    neighbors = []
    if len(coordinates) == 1:
        for i in range(coordinates[0] - 1, coordinates[0] + 2):
            if 0 <= i < dimensions[0]:
                neighbors.append([i])
        return neighbors
    else:
        for sub_dim in find_neighbors_nd(coordinates[1:], dimensions[1:]):
            for i in range(coordinates[0] - 1, coordinates[0] + 2):
                if 0 <= i < dimensions[0]:
                    neighbors.append([i] + sub_dim)
        return neighbors

def neighbors_without_self(coordinates, dimensions):
    """
    Returns a list of the neighbors of a given coordinate that do not
    include that coordinate.

    >>> neighbors_without_self((5, 13, 0), (10, 20, 3))
    [[4, 12, 0], [5, 12, 0], [6, 12, 0], [4, 13, 0], [6, 13, 0], [4, 14, 0], [5, 14, 0],
     [6, 14, 0], [4, 12, 1], [5, 12, 1], [6, 12, 1], [4, 13, 1], [5, 13, 1], [6, 13, 1], 
     [4, 14, 1], [5, 14, 1], [6, 14, 1]]
    """
    neighbors = find_neighbors_nd(coordinates, dimensions)
    neighbors.remove(list(coordinates))
    return neighbors

def flat_board(dimensions):
    """
    Given the dimensions for a game board, returns all possible coordinates in
    that game board.

    >>> flat_board((4, 3, 2))
    [[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0], [0, 1, 0], [1, 1, 0], [2, 1, 0],
     [3, 1, 0], [0, 2, 0], [1, 2, 0], [2, 2, 0], [3, 2, 0], [0, 0, 1], [1, 0, 1], 
     [2, 0, 1], [3, 0, 1], [0, 1, 1], [1, 1, 1], [2, 1, 1], [3, 1, 1], [0, 2, 1], 
     [1, 2, 1], [2, 2, 1], [3, 2, 1]]
    """
    all_coordinates = []
    if len(dimensions) == 1:
        for i in range(dimensions[0]):
            all_coordinates.append([i])
        return all_coordinates
    else:
        for sub_dim in flat_board(dimensions[1:]):
            for i in range(dimensions[0]):
                all_coordinates.append([i] + sub_dim)
        return all_coordinates

def deep_copy(nd_list):
    """
    Given a list, returns a deep copy for that list.
    """
    if not isinstance(nd_list, list):
        return nd_list
    else:
        container = []
        for sub_layer in nd_list:
            container.append(deep_copy(sub_layer))
        return container

def check_game_state(game):
    """
    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[True, False], [True, True], [True, True],
    ...                [True, True]],
    ...               [[False, True], [True, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> check_game_state(g)
    'victory'

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[True, False], [True, True], [True, True],
    ...                [True, True]],
    ...               [[False, True], [True, True], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> check_game_state(g)
    'defeat'

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[True, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, True], [True, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> check_game_state(g)
    'ongoing'
    """
    vis_safe_squares = 0
    bombs = 0

    for coord in flat_board(game['dimensions']):
        coord_val = coordinate_indexer(game['board'], coord)
        mask_val = coordinate_indexer(game['mask'], coord)
        if coord_val == '.' and mask_val == True:
            return 'defeat'
        elif coord_val == '.' and mask_val == False:
            bombs += 1
        elif coord_val != '.' and mask_val == True:
            vis_safe_squares += 1 
    total_coords = 1 

    for dimension in game['dimensions']:
        total_coords *= dimension

    if vis_safe_squares == (total_coords - bombs):
        return 'victory'
    else:
        return 'ongoing'
            


def dig_nd(game, coordinates, first=True):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the mask to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    state: ongoing
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    mask:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    state: defeat
    """
    # Initial check to make sure a victory or defeat board isn't inputted
    if game['state'] == 'defeat' or game['state'] == 'victory':
        game['state'] = game['state']  # keep the state the same
        return 0

    # Base Case
    if coordinate_indexer(game['mask'], coordinates) != True:
        val_at_coord_replace(game['mask'], coordinates, True)
        revealed = 1
    else:
        return 0 
    
    # Recursive Case
    if coordinate_indexer(game['board'], coordinates) == 0:
        neighbors = neighbors_without_self(coordinates, game['dimensions'])
        for neighbor in neighbors:
            if coordinate_indexer(game['board'], neighbor) != '.' and coordinate_indexer(game['mask'], neighbor) == False:
                revealed += dig_nd(game, neighbor, False)
    if first == True:
        game['state'] = check_game_state(game)
    return revealed

def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares
    neighboring bombs).  The mask indicates which squares should be
    visible.  If xray is True (the default is False), the mask is ignored
    and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    the mask

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'mask': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
    all_coordinates = flat_board(game['dimensions'])
    rendition = deep_copy(game['board'])
    for coordinate in all_coordinates:
        coordinate_value = coordinate_indexer(game['board'], coordinate)
        if coordinate_value == 0:
                val_at_coord_replace(rendition, coordinate, ' ')
        else:
                val_at_coord_replace(rendition, coordinate, str(coordinate_value))
        if coordinate_indexer(game['mask'], coordinate) == False and xray == False:
            val_at_coord_replace(rendition, coordinate, '_')
    return rendition

if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    #doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #

    doctest.run_docstring_examples(
       nd_list_creator,
       globals(),
       optionflags=_doctest_flags,
       verbose=False)
