#!/usr/bin/env python
from ants import *
import random

class MyBot:
    def __init__(self):
        pass
    
    # do_setup is run once at the start of the game
    # after the bot has received the game settings
    # the ants class is created and setup by the Ants.run method
    def do_setup(self, ants):
        # initialize data structures after learning the game settings
        self.dirs = ['s', 'e', 'w', 'n']
        self.hills = []
        self.razed_hills = []
        self.unseen = [(x, y) for x in xrange(ants.rows) for y in xrange(ants.cols)]

    # do_turn is run once per turn
    # the ants class has the game state and is updated by the Ants.run method
    # it also has several helper methods to use
    def do_turn(self, ants):
        # track all moves, prevent collisions
        orders = {}
        def do_move_direction(loc, direction):
            new_loc = ants.destination(loc, direction)
            if (ants.passable(new_loc) and ants.unoccupied(new_loc) and new_loc not in orders):
                ants.issue_order((loc, direction))
                orders[new_loc] = loc
                return True
            else:
                return False
        
        targets = {}
        def do_move_location(loc, dest):
            directions = ants.direction(loc, dest)
            random.shuffle(directions)
            for direction in directions:
                if do_move_direction(loc, direction):
                    targets[dest] = loc
                    return True
            return False
        
        def gather_food():
                ant_dist = []
                for food_loc in ants.food():
                    for ant_loc in ants.my_ants():
                        dist = ants.distance(ant_loc, food_loc)
                        ant_dist.append((dist, ant_loc, food_loc))
                ant_dist.sort()
                for dist, ant_loc, food_loc in ant_dist:
                    if food_loc not in targets:
                        do_move_location(ant_loc, food_loc)
                return True


        def attack_hills():
            for hill_loc, hill_owner in ants.enemy_hills():
                if hill_loc not in self.hills and hill_loc not in self.razed_hills:
                    self.hills.append(hill_loc)
            for hill_loc in self.hills:
                if hill_loc in ants.my_ants():
                    self.hills.remove(hill_loc)
                    self.razed_hills.append(hill_loc)
            ant_dist = []
            for hill_loc in self.hills:
                for ant_loc in ants.my_ants():
                    if ant_loc not in orders.values():
                        dist = ants.distance(ant_loc, hill_loc)
                        ant_dist.append((dist, ant_loc, hill_loc))
            ant_dist.sort()
            for dist, ant_loc, hill_loc in ant_dist:
                do_move_location(ant_loc, hill_loc)


        def explore_random(explorers):
            for ant_loc in explorers:
                if ant_loc not in orders.values():
                    random.shuffle(self.dirs)
                    for direction in self.dirs:
                        if do_move_direction(ant_loc, direction):
                            break
        
        
        def explore_fast(explorers):
            for loc in self.unseen[:]:
                if ants.visible(loc):
                    self.unseen.remove(loc)
            for ant_loc in explorers:
                if ant_loc not in orders.values():
                    unseen_dist = []
                    for unseen_loc in self.unseen:
                        dist = ants.distance(ant_loc, unseen_loc)
                        unseen_dist.append((dist, unseen_loc))
                    unseen_dist.sort()
                    for dist, unseen_loc in unseen_dist:
                        if do_move_location(ant_loc, unseen_loc):
                            break

        
        def unblock_hill():
            for hill_loc in ants.my_hills():
                if hill_loc in ants.my_ants() and hill_loc not in orders.values():
                    random.shuffle(self.dirs)
                    for direction in self.dirs:
                        if do_move_direction(hill_loc, direction):
                            break


        # prevent stepping on own hill
        for hill_loc in ants.my_hills():
            orders[hill_loc] = None

        # gather food
        if len(ants.my_hills()) > 0:
            gather_food()
        
        # attack hills
        attack_hills()
        
        # explore unseen areas
        if len(ants.my_ants()) < 40:
            explore_fast(ants.my_ants())
        else:
            explore_fast(ants.my_ants()[:40])
            explore_random(ants.my_ants()[40:])
        
        # unblock own hill
        unblock_hill()
        
        # have ants re-explore whole map when 90% has been seen
        if len(self.unseen) < (ants.rows * ants.cols / 10 ):
            self.unseen = [(x, y) for x in xrange(ants.rows) for y in xrange(ants.cols)]

            
if __name__ == '__main__':
    try:
        import psyco
        psyco.full()
    except ImportError:
        pass
    
    try:
        # if run is passed a class with a do_turn method, it will do the work
        # this is not needed, in which case you will need to write your own
        # parsing function and your own game state class
        Ants.run(MyBot())
    except KeyboardInterrupt:
        print('ctrl-c, leaving ...')
