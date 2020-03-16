import random
import pygame
import numpy as np


from gym_scalable.envs.pathing.grid_entity import *

"""
Grid which serves as the lower level of all pathing environments
i.e. maze solver, chaser, evader etc

"""

class Node:
    """
    Node for A*
    """
    def __init__(self, parent = None, position = None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

class GridMap:
    map = []
    colours = {'O' : (255,255,255), 'G':(0,255,0), 'X':(0,0,255), 'S':(255,0,0), '-':(255,0,0), '+':(255,0,0)}

    walkable = set()
    a_searched = set()
    marked_blocks = set()

    entities = []

    def __init__(self, mapfile, screen_width):

        self.map = self.read_map(mapfile)
        self.screen_width = screen_width

        self.width = len(self.map[0]) // 2
        self.height = len(self.map) // 2
        self.block_size = screen_width / len(self.map[0])

        self.block_width = screen_width / self.width
        self.block_height = screen_width / self.height

        # print(f"start : {self.start}")
        # print(f"end : {self.goal}")

        # Action conversion:
        left = np.asarray([1, 0, 0, 0])
        right = np.asarray([0, 1, 0, 0])
        up = np.asarray([0, 0, 1, 0])
        down = np.asarray([0, 0, 0, 1])

        self.actions_table = {(-2, 0): left, (2, 0): right, (0, -2): up, (0, 2): down}

    def update(self):
        for entity in self.entities:
            entity.update()


    def render(self, screen):

        for y in range(0,len(self.map)):
            for x in range(0,len(self.map[0])):
                #We're at a wall row
                if y%2==0:
                    if(self.map[y][x] == '+'):
                        #pygame.draw.rect(screen, (0, 0, 255), r)
                        continue
                    if(self.map[y][x] == '-'):

                        r = (((x-1)/2) * self.block_width,(y/2) * self.block_height, self.block_width, 10)
                        pygame.draw.rect(screen, (255, 0, 0), r)

                #Either columns or walls
                elif x % 2 == 0:
                    if(self.map[y][x] == '|'):

                        r = ((x / 2) * self.block_width, ((y-1) / 2) * self.block_height, 10, self.block_height)
                        pygame.draw.rect(screen, (255, 0, 0), r)
                else:
                    pass
                    # print("rest: " + self.map[y][x])

                #Goal and start
                if(self.map[y][x] == 'G'):
                    r_start = ((round(((x - 1) / 2) * self.block_width + (self.block_width / 2))),round((((y - 1) / 2) * self.block_height + (self.block_height / 2))), 10, 10)
                    pygame.draw.rect(screen, (50, 255, 0), r_start)
                if(self.map[y][x] == 'S'):
                    r_start = ((round(((x - 1) / 2) * self.block_width + (self.block_width / 2))),
                               round((((y - 1) / 2) * self.block_height + (self.block_height / 2))), 10, 10)
                    pygame.draw.rect(screen, (255, 50, 0), r_start)

    def convert_action(self, dir):
        return self.actions_table[dir]

    def get_astar_action(self, pos, goal):
        path = self.astar_path(pos[0], pos[1], goal[0], goal[1])
        #print(path)
        path = path[1]
        #print(path)
        action = self.convert_action((pos[0] - path[0], pos[1] - path[1]))
        return action


    def add_entity(self, entity):
        self.entities.append(entity)

    def remove_entity(self):
        #TODO
        pass

    def manhatten_dist(self, x, y, gX, gY):
        return abs(x-gX) + abs(y-gY)

    def get_astar_move(self, startX, startY, endX, endY):
        """
        Gets the single move from A*
        :param startX:
        :param startY:
        :param endX:
        :param endY:
        :return:
        """
        return self.astar_path(startX, startY, endX, endY)[1]

    def astar_path(self, startX, startY, endX, endY):
        """
        A star path, returns the path as a list of block coordinates
        :param startX:
        :param startY:
        :param endX:
        :param endY:
        :return:
        """
        #TODO fix up innefficiencies in the
        start_node = Node(None, (startX, startY))
        end_node = Node(None, (endX, endY))
        start_node.g = start_node.h = start_node.f = 0
        end_node.g = end_node.h = end_node.f = 0

        open_list = []
        closed_list = []

        path = []

        open_list.append(start_node)

        while len(open_list) > 0:
            current_node = open_list[0]
            current_index = 0

            #print(current_node.position)

            #[TODO DO WITH HEAP]
            for index, item in enumerate(open_list):
                if(item.f < current_node.f):
                    current_node = item
                    current_index = index

            open_list.pop(current_index)
            closed_list.append(current_node)


            if current_node == end_node:
                #print("FOUND GOAL")

                current = current_node

                #track backwards through the path
                while current:
                    path.append(current.position)
                    current = current.parent
                break


            children = []
            for new_pos in self.get_neighbours(current_node.position[0], current_node.position[1]):
                new_node = Node(current_node, new_pos)
                children.append(new_node)
                #print("here")

            for child in children:
                if child in closed_list:
                    continue

                child.g = current_node.g+1
                child.h = self.manhatten_dist(child.position[0], child.position[1],
                                              end_node.position[0], end_node.position[1])
                child.f = child.g + child.h

                #[TODO] Do this with a heap
                for open_node in open_list:
                    if(child == open_node and child.g > open_node.g):
                        continue

                open_list.append(child)

        return path[::-1]



    def mark_block(self, x, y):
        """
        Marks a block for rendering purposes
        TODO NOT WORKING
        :param x:
        :param y:
        :return:
        """
        self.marked_blocks.add((x,y))

    def is_walkable(self, x, y):
        if(x >= len(self.map[0]) or y >= len(self.map)):
            return False
        if self.map[y][x] == ' ' or self.map[y][x] == 'G':
            return True
        return False

    def is_goal(self, x, y):
        if self.map[y][x] == 'G':
            return True
        return False

    def get_neighbours(self, x, y, check_searched = False):
        out = []
        if self.is_walkable(x+1, y) and (x+2, y) not in self.a_searched:
            out.append((x+2, y))
        if self.is_walkable(x-1, y) and (x-2, y) not in self.a_searched:
            out.append((x-2, y))
        if self.is_walkable(x, y+1) and (x, y+2) not in self.a_searched:
            out.append((x, y+2))
        if self.is_walkable(x, y-1) and (x, y-2) not in self.a_searched:
            out.append((x, y-2))
        return out


    def read_map(self, filename):
        out = []
        f = open(filename)
        for i in f.readlines():
            out.append(list(i.strip('\n')))
        print(out)

        for y in range(0,len(out)):
            for x in range(len(out[0])):
                if(out[y][x] == 'G'):
                    self.goal = (x,y)
                if(out[y][x] == 'S'):
                    self.start = (x,y)
        return out


