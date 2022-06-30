"""6.009 Lab 10: Snek Is You Video Game"""

import doctest

# NO ADDITIONAL IMPORTS!

# All words mentioned in lab. You can add words to these sets,
# but only these are guaranteed to have graphics.
NOUNS = {"SNEK", "FLAG", "ROCK", "WALL", "COMPUTER", "BUG"}
PROPERTIES = {"YOU", "WIN", "STOP", "PUSH", "DEFEAT", "PULL"}
WORDS = NOUNS | PROPERTIES | {"AND", "IS"}

# Maps a keyboard direction to a (delta_row, delta_column) vector.
direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

def opp_direc(direc):
    if direc == 'up':
        return 'down'
    elif direc == 'down':
        return 'up'
    elif direc == 'left':
        return 'right'
    elif direc == 'right':
        return 'left'

class GameObject():
    def __init__(self, name, row_pos, col_pos):
        self.name = name
        self.row_pos = row_pos
        self.col_pos = col_pos

    def __repr__(self):
        return self.name + "_(" + str(self.row_pos) + ", " + str(self.col_pos) + ")"

    def move(self, direc, game, stops, pushes, pulls, alr_moved = []):
        """
        Moves the game object and if other objects move as a result, moves them
        accordingly.
        """
        # New positions after potential move is completed
        move_r = self.row_pos + direction_vector[direc][0]
        move_c = self.col_pos + direction_vector[direc][1]

        # Objects adjacent to self in specified direction
        adj = self.get_adjacent_val(game, direc)

        # Objects adjacenet to self in opposite specified direction
        opp_adj = self.get_adjacent_val(game, opp_direc(direc))
        
        push_obj = set()
        pull_obj = set()
        pushed = False
        moved = False

        # Checks to see if the move is within the bounds of the game board
        if (move_r >= 0 and move_r < game['dimensions'][0]) and (move_c >= 0 and move_c < game['dimensions'][1]):
            stop_cond = False

            #Finds adjacent objects and adds them to a list of things that will push when the object moves
            for obj in adj:
                if obj in stops and obj not in pushes:
                    stop_cond = True
                if obj in pushes and obj not in alr_moved:
                    push_obj.add(obj)
            
            # Finds adjacent objects and adds them to a list of things that will pull when the object moves
            for obj in opp_adj:
                if obj in pulls and obj not in alr_moved:
                    pull_obj.add(obj)
            
            # If nothing needs to be pushed or pulled, object just moves in specified direction
            if stop_cond == False and len(push_obj) == 0 and len(pull_obj) == 0:
                alr_moved.append(self)
                self.row_pos = move_r
                self.col_pos = move_c
            
            # Moves every object that needs to be pushed
            for obj in push_obj:
                if obj not in alr_moved and stop_cond == False:
                    old_r, old_c = obj.row_pos, obj.col_pos
                    obj.move(direc, game, stops, pushes, pulls, alr_moved)
                    if obj.row_pos != old_r or obj.col_pos != old_c:
                        alr_moved.append(obj)
                        pushed = True
            
            # If the push object moves, then the original object should move
            if (len(push_obj) == 0 and pushed == False and stop_cond == False) or (len(push_obj) != 0) and pushed == True:
                alr_moved.append(self)
                self.row_pos = move_r
                self.col_pos = move_c
                moved = True
            
            # If the original object moves, then moves every object that needs to be pulled
            if moved == True:
                for obj in pull_obj:
                    if obj not in alr_moved:
                        old_r, old_c = obj.row_pos, obj.col_pos
                        obj.move(direc, game, stops, pushes, pulls, alr_moved)
                        if obj.row_pos != old_r or obj.col_pos != old_c:
                            alr_moved.append(obj)

    def get_adjacent_val(self, game, direc):
        """
        Helper function that gets the value of the objects adjacent in a specified direction
        to the specified object.
        """
        adj_r = self.row_pos + direction_vector[direc][0]
        adj_c = self.col_pos + direction_vector[direc][1]
        adj = []

        for word in game['positions']:
            for obj in game['positions'][word]:
                if obj.row_pos == adj_r and obj.col_pos == adj_c:
                    adj.append(obj)
        return adj
    
    def is_collide(self, other):
        """
        Checks to see if two objects are occupying the same space on the board
        """
        if (self.row_pos, self.col_pos) == (other.row_pos, other.col_pos):
            return True
        return False

x = GameObject('YOU', 3, 2)
y = GameObject('IS', 4, 2)
game = {'state': 'ongoing', 'positions': {'WIN': [], 'PUSH': [], 'YOU': [GameObject('YOU', 3, 2)], 'DEFEAT': [], 'STOP': [], 'AND': [], 'PULL': [], 'Noun': [GameObject('SNEK', 3, 0)], 'IS': [GameObject('IS', 3, 1)], 'snek': [GameObject('snek', 1, 2)]}, 'board': [[[], [], [], []], [[], [], ['snek'], []], [[], [], [], []], [['SNEK'], ['IS'], ['YOU'], []]], 'dimensions': (4, 4)}


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, where UPPERCASE
    strings represent word objects and lowercase strings represent regular
    objects (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['snek'], []],
        [['SNEK'], ['IS'], ['YOU']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    graph_pos = {word.lower(): [] for word in NOUNS}
    positions = {word: [] for word in (PROPERTIES | {"AND", "IS", 'Noun'})}
    positions = {**positions, **graph_pos}

    # Loops through every word in the level description and creates and adds an object to the positions dictionary
    for r in range(len(level_description)):
        for c in range(len(level_description[0])):
            for object in level_description[r][c]:
                if object in NOUNS:
                    positions['Noun'].append(GameObject(object, r, c))
                else:
                    positions[object].append(GameObject(object, r, c))

    game_state = {'state': 'ongoing', 'positions': positions, 'board': level_description, 'dimensions': (len(level_description), len(level_description[0]))}
    return game_state



def parse_board(board):
    """
    Parses every row and every column on the board, and retrieves the text objects.
    """
    rules_horiz = []

    # Loops through every row in the board and adds to the rules, every text object
    for r in range(len(board)):
        rules_horiz.append([])
        for c in range(len(board[0])):
            if  len(board[r][c]) == 1 and board[r][c][0].isupper():
                rules_horiz[r].append(board[r][c][0])
            elif board[r][c] == []:
                rules_horiz[r].append('')
    
    # Loops through every colmumn in the board and adds to the rules, every text object
    rules_vert = []
    for c in range(len(board[0])):
        rules_vert.append([])
        for r in range(len(board)):
            if  len(board[r][c]) == 1 and board[r][c][0].isupper():
                rules_vert[c].append(board[r][c][0])
            elif board[r][c] == []:
                rules_vert[c].append('')

    rules = rules_vert + rules_horiz
    return rules

def refine_rules(rules):
    """
    Retrieves valid rules from the parsed board and adds them to a list of
    every rule on the board.
    """
    refined = [[]]
    j = 0

    for row in rules:
        sent_count = 0
        j += 1
        refined.append([])

        for i, word in enumerate(row):
            # A rule starts with a noun
            if sent_count == 0 and word in NOUNS:
                refined[j].append(word)
                sent_count += 1

            # Case when the word after the noun is an AND
            elif sent_count == 1 and word == 'AND':
                refined[j].append(word)
                sent_count = 0 

            # Case when the word after the noun is an IS
            elif sent_count == 1 and word == 'IS' and i + 1 < len(row):
                refined[j].append(word)
                sent_count += 1

            # Case when there are two words in the sentence and the next word is a property
            elif sent_count == 2 and word in PROPERTIES:
                refined[j].append(word)
                sent_count += 1

            # Case when there are two words in the sentence and the next word is a noun
            elif sent_count == 2 and word in NOUNS:
                refined[j].append(word)
                if i != len(row) - 1 and row[i+1] == 'AND':
                    sent_count = 3
                else:
                    sent_count = 1

            # Case when there are three words in a sentence and the next word is an AND
            elif sent_count == 3 and word == 'AND':
                refined[j].append(word)
                sent_count = 2

            # If another noun comes up, restarts the sentence
            elif word in NOUNS:
                refined.append([])
                j += 1
                refined[j].append(word)
                sent_count = 1

            # Restarts the sentences
            else:
                refined.append([])
                j += 1
                sent_count = 0

    refined = [item for item in refined if len(item) > 1 and len(item) % 2 == 1 and 'IS' in item]
    return refined

def extract_rules(refined, game):
    """
    From the refined rules, creates a dictionary storing all the objects associated with a rule to
    each corresponding rule.
    """

    rules_dict = {property:[] for property in PROPERTIES}
    noun_dict = {noun:[] for noun in NOUNS}
    rules_dict = {**rules_dict, **noun_dict}

    for rule in refined:
        is_count = 0

        # Gets the number of is' in the rule
        for word in rule:
            if word == 'IS':
                is_count += 1

        # Case for when it is a standard three word rule
        if len(rule) == 3 and rule[2] in PROPERTIES:
            rules_dict[rule[2]].extend(game['positions'][rule[0].lower()])

        # Case for when it is a chained noun is noun rule
        elif len(rule) > 3 and is_count > 1:
            for i in range(0, len(rule), 2):
                if i + 2 < len(rule):
                    rules_dict[rule[i+2]].extend(game['positions'][rule[i].lower()])           

        # Case for when there are AND's in the rule
        else:
            i = 0
            while rule[i] != 'IS':
                is_occurs = False

                if rule[i] != "AND":
                    for j in range(i, len(rule)):
                        if rule[j] == 'IS':
                            is_occurs = True

                        if rule[j] in PROPERTIES or (is_occurs == True and rule[j] in NOUNS):
                            rules_dict[rule[j]].extend(game['positions'][rule[i].lower()])
                i += 1

    return rules_dict

def create_rules(game, board):
    """
    Combines the helper functions parse_board, refine_rules, and extract_rules into one single function.
    """
    rules = extract_rules(refine_rules(parse_board(board)), game)
    return rules
    
def step_game(game, direction):
    """
    Given a game representation (as returned from new_game), modify that game
    representation in-place according to one step of the game.  The user's
    input is given by direction, which is one of the following:
    {'up', 'down', 'left', 'right'}.

    step_game should return a Boolean: True if the game has been won after
    updating the state, and False otherwise.
    """

    rules = create_rules(game, game['board'])
    defeat_enter = False
    win_condition = False

    # IS STOP Functionality
    stop_objects = rules['STOP']

    # IS PUSH Functionality
    push_objects = [word for word in game['positions']['Noun']] + rules['PUSH']

    # Case where object is STOP and PUSH
    new_stop_objects = []
    for obj in stop_objects:
        if obj not in push_objects:
            new_stop_objects.append(obj)

    for word in game['positions']:
        if word in {'AND', 'IS'} | PROPERTIES:
            push_objects.extend(game['positions'][word])
    
    # IS PULL Functionality
    pull_objects = rules['PULL']

    # INITIAL IS YOU Functionality
    you_objects = set(rules['YOU'])


    # Moves every object that is under the YOU rule
    alr_moved = []
    for you_object in you_objects:
        you_object.move(direction, game, new_stop_objects, push_objects, pull_objects, alr_moved)
    
    # Updates board and rule after moving all the you objects
    game['board'] = update_board(game)
    updated_rules = create_rules(game, game['board'])

    # Gets noun objects 
    noun_objects = []
    for rule in updated_rules:
        if rule in NOUNS:
            noun_objects.append((rule, updated_rules[rule]))

    # Maps in a dictionary a noun, to the noun it needs to be changed to
    nouns = {}
    for word in noun_objects:
        to_change_objs = []
        to_change_objs.extend(word[1])
        nouns[word[0].lower()] = to_change_objs

    # Changes a noun to the noun it needs to be according to whatever the rules are
    for word in nouns:
        if len(nouns[word]) != 0:
            for obj in nouns[word]:
                game['positions'][obj.name].remove(obj)
                obj.name = word
                game['positions'][word].append(obj)

    # Updates board and rules again
    game['board'] = update_board(game)
    updated_rules = create_rules(game, game['board'])

    defeat_objects = updated_rules['DEFEAT']
    you_objects = set(updated_rules['YOU'])

    # If collision with a defeat object, removes the you object from the board that collides
    for defeat_obj in defeat_objects:
        for you_object in you_objects:
            if you_object.is_collide(defeat_obj):
                game['positions'][you_object.name].remove(you_object)
                defeat_enter = True

    # POST IS YOU and WIN check
    post_you = set(updated_rules['YOU'])
    for you_object in post_you:
        if defeat_enter == False:
                win_objects = updated_rules['WIN']
                for win_obj in win_objects:
                    if you_object.is_collide(win_obj):
                        win_condition = True
    
    game['board'] = update_board(game)
    if win_condition == True:
        return True
    return False

def update_board(game):
    """
    Returns a board with new object positions according to each object's position coordinates.
    """
    board = []
    positions = game['positions']

    # Creates an empty board
    for r in range(game['dimensions'][0]):
        board.append([])
        for c in range(game['dimensions'][1]):
            board[r].append([])

    # Adds all objects to their appropriate position in the empty board
    for object in game['positions']:
        if not isinstance(positions[object], list):
            board[positions[object].row_pos][positions[object].col_pos].append(positions[object].name)
        else:
            for item in game['positions'][object]:
                board[item.row_pos][item.col_pos].append(item.name)

    return board

def dump_game(game):
    """
    Given a game representation (as returned from new_game), convert it back
    into a level description that would be a suitable input to new_game.

    This function is used by the GUI and tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    return game['board']
