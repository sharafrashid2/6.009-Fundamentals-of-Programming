#!/usr/bin/env python3

import pickle
# NO ADDITIONAL IMPORTS ALLOWED!

# Note that part of your checkoff grade for this lab will be based on the
# style/clarity of your code.  As you are working through the lab, be on the
# lookout for things that would be made clearer by comments/docstrings, and for
# opportunities to rearrange aspects of your code to avoid repetition (for
# example, by introducing helper functions).  See the following page for more
# information: https://py.mit.edu/fall21/notes/style


def transform_data(raw_data):
    """
    Given the raw data set, transforms it into a data structure that is a dictionary
    with keys containing each actor, and within each key, there is a dictionary with
    keys for actors the actor has acted with, and within the keys, a set ofthe movies,
    they have in common.
    """
    updated_ds = {}
    for item in raw_data:
        # Adds actor from the tuple's first index 
        if item[0] not in updated_ds:
            updated_ds[item[0]] = {}
        # Adds actors the actor in the first index has acted with
        if item[1] not in updated_ds[item[0]]:
            updated_ds[item[0]][item[1]] = set()
        # Adds movies that the two actors have acted in together
        updated_ds[item[0]][item[1]].add(item[2])
        # Does same as above code except now the tuple's second index is added
        if item[1] not in updated_ds:
            updated_ds[item[1]] = {}
        if item[0] not in updated_ds[item[1]]:
            updated_ds[item[1]][item[0]] = set()
        updated_ds[item[1]][item[0]].add(item[2])    
    return updated_ds


def acted_together(transformed_data, actor_id_1, actor_id_2):
    """
    Given the transformed data set and two actors' IDs, returns True if 
    the two actors have acted together and False otherwise.
    """
    if actor_id_1 == actor_id_2:
        return True
    elif actor_id_2 in transformed_data[actor_id_1]:
        return True
    else:
        return False
    

def actors_with_bacon_number(transformed_data, n):
    """
    Given the transformed data set and a Bacon number, n, returns a
    set of all actors in the data set with that specific Bacon number.
    """
    return actors_with_connections_number(transformed_data, 4724, n)

def bacon_path(transformed_data, actor_id):
    """
    Given the transformed data set and an actor's ID number, returns the shortest
    possible path, if one exists, connecting Kevin Bacon to that actor.
    """
    return actor_to_actor_path(transformed_data, 4724, actor_id)


def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    """
    Given the transformed data set and two actor's ID numbers, returns the shortest
    possible path, if one exists, connecting the first actor to the second actor.
    """
    # Gets number of connections away actor 2 is from actor 1)
    n = get_connections_number(transformed_data, actor_id_1, actor_id_2)
    if n == None:
        return None
    # If a number of connections exists, the function works its way backwards from the farthest possible connection to find the path to the first actor
    path = [actor_id_2]
    actor_to_check = actor_id_2
    while n > 0:
        for actor in actors_with_connections_number(transformed_data, actor_id_1, n-1):
            if actor_to_check in transformed_data[actor]:
                path.append(actor)
                actor_to_check = actor
                break
        n -= 1
    path = path[::-1]
    return path

def films_connecting_actors(transformed_data, movie_names, actor_id_1, actor_id_2):
    """
    Given the transformed data set, a dictionary containing names for each movie ID, and two
    actor's ID's, returns a list of movies connecting the first actor to the second actor.
    """
    # Retrieves the actors connecting one actor to another
    path = actor_to_actor_path(transformed_data, actor_id_1, actor_id_2)
    start_point = path[0]
    path = path[1:]
    movie_path = []

    for actor in path:
        # Finds each movie connecting two actors 
        connectingMovie = list(transformed_data[actor][start_point])[0]
        if connectingMovie not in movie_path:
            movie_path.append(connectingMovie)
        start_point = actor

    # Convert movie ID's to names
    movie_path_names = []

    for movie_id in movie_path:
        movie_path_names.append(get_key(movie_names, movie_id))

    return movie_path_names

def actor_path(transformed_data, actor_id, goal_test_function):
    """
    Given the transformed data set, an actor's id number, and a goal test function that returns either
    True or False, returns the shortest path from the first actor to any actor that passes the goal
    test function.
    """
    # Finds the actor out of the possible set that has the shortest path from the given actor
    end_goal = find_end_goal(transformed_data, actor_id, goal_test_function)
    if end_goal == None:
        return None
    return actor_to_actor_path(transformed_data, actor_id, end_goal)

def actors_connecting_films(transformed_data, film1, film2):
    """
    Given the transformed data set and the ID's of two films, returns the shortest possible
    path connecting those two films.
    """
    # Gets all the actors each film has 
    actors_film1 = list(find_actors_for_movie(transformed_data, film1))
    actors_film2 = find_actors_for_movie(transformed_data, film2)

    # Adds all possible paths of actors between the two films to a list
    possible_paths = []
    for actor in actors_film1:
        path = actor_path(transformed_data, actor, lambda p: p in actors_film2)
        if path != None:
            possible_paths.append(path)

    # Finds the shortest possible path and returns it
    if len(possible_paths) == 0:
        return None
    min_path = min(possible_paths, key = len)
    return min_path

# Helper Functions
def get_connections_number(transformed_data, actor_id_1, actor_id_2):
    """
    Given the transformed data set and two actor's ID numbers, returns how many
    connections (people in between) away the second actor is from the first actor.
    """
    n = 0
    row = actors_with_connections_number(transformed_data, actor_id_1, n)
    while len(row) != 0:
        if actor_id_2 in row:
            return n
        else:
            n += 1
            row = actors_with_connections_number(transformed_data, actor_id_1, n)
    return None

def get_key(dict, id):
    """
    Given a dictionary and a value in the dictionary, returns the key associated
    with that value.
    """
    keyValuePairs = dict.items()

    for item in keyValuePairs:
        if item[1] == id:
            return item[0]

def actors_with_connections_number(transformed_data, actor_id, n):
    """
    Given the transformed data set, a number, n, and a specified actor's id,
    returns a set of all actors in the data set that are all n connections 
    away from the specified actor.
    """
    if n == 0:
        return {actor_id}
    previous_set = {actor_id}
    already_seen = {actor_id}

    for i in range(0, n):
        new_set = set()
        # Loops through actors of the previous bacon number and finds the actors that they have acted with
        for actor in previous_set:
            common_actors = set(transformed_data[actor].keys())
            new_set.update(common_actors)
            already_seen.add(actor)
        # This line ensures actors with a lesser bacon number don't appear
        new_set.difference_update(already_seen)
        previous_set = new_set
        # Stops the loop from searching further if a set with zero values has already been produced
        if new_set == set():
            return new_set

    return new_set

def find_end_goal(transformed_data, actor_id, goal_test_function):
    """
    (Helper function for actor_paths function) Given the transformed data set, an actor's id number, 
    and a goal test function that returns either True or False, returns the actor that has the shortest
    path from the first actor.
    """
    n = 0
    actors_with_n_connections = actors_with_connections_number(transformed_data, actor_id, n)
    end_goal = None

    # Loop to look for actor       
    while len(actors_with_n_connections) != 0:
        for actor in actors_with_n_connections:
            if goal_test_function(actor) == True:
                return actor
        n += 1
        actors_with_n_connections = actors_with_connections_number(transformed_data, actor_id, n)

    if end_goal == None:
        return None
    
def find_actors_for_movie(transformed_data, film_id):
    """
    (Helper function for actors_connecting_films function) Given the transformed data set and a 
    film, returns all the actors in a film as a set.
    """
    actors_in_movie = set()

    for actor1 in transformed_data:
        for actor2 in transformed_data[actor1]:
            for movie in transformed_data[actor1][actor2]:
                if movie == film_id:
                    actors_in_movie.update([actor1, actor2])

    return actors_in_movie

                

if __name__ == '__main__':



    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    pass
