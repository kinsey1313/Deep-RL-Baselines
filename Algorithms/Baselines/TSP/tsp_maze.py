import gym
import gym_scalable
import random
import numpy as np
import time
import os
import mlrose
from itertools import permutations


print(os.getcwd())
from pympler.tracker import SummaryTracker

tracker = SummaryTracker()

config = {"mapfile": "/home/krer/Documents/Deep-RL-Baselines/gym-scalable/gym_scalable/envs/grid/mazes/map_3x3.txt",
          "normalize_state": True,"randomize_goals":True, "randomize_start": True, "num_goals": 3,
          "capture_reward": False}
env = gym.make('n-maze-v0', config=config)

state = env.reset()

goal = env.grid.goal


def get_dist(order, coords_list):
    dist = 0
    for i in range(0, len(order) - 1):
        pos = order[i]
        next_pos = order[i + 1]
        dist += env.grid.get_astar_distance(coords_list[pos], coords_list[next_pos])
    return dist



def best_dist(order, coords_list):
    """
    Gets the best possible path distance given the TSP order
    """

    dist_for = 0
    dist_back = 0
    order_for, order_back = None, None
    # print(order)
    for x, pos in enumerate(order):
        if pos == 0:

            order_for = np.concatenate((order[x:], order[:x]))
            order_back = np.concatenate(([order_for[0]], order_for[1:][::-1]))
            # print(order_for)
            # print(order_back)
            dist_for = get_dist(order_for, coords_list)
            dist_back = get_dist(order_back, coords_list)

    if dist_for < dist_back:
        return order_for, dist_for
    return order_back, dist_back

def get_tsp_optim_dist(coords_list, dist_list):
    #entity_pos = env.entity.get_pos()


    fitness_coords = mlrose.TravellingSales(coords=coords_list)
    fitness_dists = mlrose.TravellingSales(distances=dist_list)

    problem_fit = mlrose.TSPOpt(length=len(coords_list), fitness_fn=fitness_dists, maximize=False)

    best_state, best_fitness = mlrose.genetic_alg(problem_fit)

    best_states, dist = best_dist(best_state, coords_list)

    dist = 0
    for i in range(0, len(best_states) - 1):
        pos = best_states[i]
        next_pos = best_states[i + 1]
        #print((coords_list[pos],coords_list[next_pos]))

        d = env.grid.get_astar_distance(coords_list[pos], coords_list[next_pos])

        dist += d

    #print(f"distance: {dist}")

    return dist

def calc_dist(path):
    dist = 0

    for i in range(0,len(path)-1):
        pos = path[i]
        next_pos = path[i+1]
        dist+= env.grid.get_astar_distance(pos, next_pos)
        #print(f"{pos} {next_pos} with d : {env.grid.get_astar_distance(pos, next_pos)}")

    return dist


def get_tsp_greedy_dist(coords_list, dist_list):

    start = coords_list[0]
    rest = coords_list[1:]
    combos = permutations(rest,len(rest))
    best_dist = 100
    best_path = []

    for i in combos:
        path = [start] + list(i)
        #print(path)
        d = calc_dist(path)

        if d < best_dist:
            best_dist = d
            best_path = [start] + list(i)
    return best_dist


dists = []
i = 0
while i < 10000:

    i += 1
    #env.render()


    coords_list, dist_list = env.grid.get_dist_list(env.entity.get_pos())

    dists.append(get_tsp_greedy_dist(coords_list, dist_list))

    env.reset()

print(dists)
print(np.average(dists))

