import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
#    source = person_id_for_name("Tom Holland")
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
#    target = person_id_for_name("Daniel Radcliffe")
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)
#    print("path = ",path)
    
    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        print(path)
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.
    """
      
    neighbors = list(neighbors_for_person(source))
#    print(neighbors)
    
    # first step : check if the other actor is in neighbors (1 deg of sep)
    for n in neighbors:
#        print(n[1])
        if n[1] == target:
            result_list = [n]
            return result_list
    
    # Keep track of number of states explored
    num_explored = 0

    # Initialize frontier to the starting position
    start = Node(state= source, 
                 parent=None, 
                 action= None)
    # path is used to show us what the algorithm do
    # it is not the solution
    path = []
    # tuplet_start = (start.action, start.state)
    # path.append(tuplet_start)
#   print("start state =", start.state)
#   print("start action =", start.action)
    
    frontier = QueueFrontier()
    frontier.add(start)

    # Initialize an empty explored set
    explored = set()
    # we add the start state to avoid going back at it
    explored.add(start.state)


    # Keep looping until solution found
    while True:
        # If nothing left in frontier, then no path
        if frontier.empty():
            raise Exception("no solution")
            return None

        # Choose a node from the frontier
        node = frontier.remove()
        
        # if node.parent != None:
        #     print("after node, node.parent.state =", node.parent.state)
        # else:
        #     print("after node, none.parent is None")
        
        num_explored += 1

        tuplet = (node.action, node.state)
        # update of the path
        if tuplet[0] != None:
            path.append(tuplet)
            print(movies[tuplet[0]]["title"], " avec :",
              people[tuplet[1]]["name"])            

        if node.state == target:
            actions = []
            cells = []
            while node.parent is not None:
                actions.append(node.action)
                cells.append(node.state)
                node = node.parent
                # if node.parent != None:
                #     print("node.parent.state =", node.parent.state)
                # else:
                #     print("none.parent is None")
            actions.reverse()
            cells.reverse()
            # print("actions = ", actions)
            # print("cells = ", cells)
            # solution is a list of 2 lists : the actions and the states
            solution = list((actions, cells))
#            print(solution)
            # convert list of list into list of tuple (newsolution)
            newsolution = []
            for i in range(len(solution[0])):
                newsolution.append(tuple([solution[0][i], 
                                          solution[1][i]]))
#            print("newsolution = ", newsolution)
            return newsolution

        # Mark node as explored
        explored.add(node.state)
        # print("node.state = ", node.state)
        
        # if node.parent != None:
        #     print("node.parent.state =", node.parent.state)
        # else:
        #     print("none.parent is None")

        # Add neighbors to frontier
#        print("node state = ", node.state)
        
#        print(len(neighbors_for_person(node.state)))

        for action, state in neighbors_for_person(node.state):
            # # when we enter into node.state, we add it to solutions if
            # # we are not the source
            # if node.state != source:
            #     tupp = (node.action, node.state)
            #     solutions.append(tupp)
            if not frontier.contains_state(state) and state not in explored:
    #           print("state", state)
                child = Node(state=state, parent=node, action=action)
#                print("child added !")
                frontier.add(child)
                # if state == target:
                #     tuplet = (action, state)
                #     path.append(tuplet)
                #     return path
                # if node is node goal, we return the solution immediately
                if state == target:
                    node = child
#                    print("node.state = ", node.state)
                    node.action = action
                    node.state = state
#                    print("target =", target)
#                    print("state =", state)
                    actions = []
                    cells = []
                    while node.parent is not None:
                        actions.append(node.action)
                        cells.append(node.state)
                        node = node.parent
                        # if node.parent != None:
                        #     print("node.parent.state =", node.parent.state)
                        # else:
                        #     print("none.parent is None")
                    actions.reverse()
                    cells.reverse()
#                    print("actions = ", actions)
#                    print("cells = ", cells)
                    # solution is a list of 2 lists : the actions and the states
                    solution = list((actions, cells))
#                    print(solution)
                    # convert list of list into list of tuple (newsolution)
                    newsolution = []
                    for i in range(len(solution[0])):
                        newsolution.append(tuple([solution[0][i], 
                                                  solution[1][i]]))
#                    print("newsolution = ", newsolution)
                    return newsolution


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
