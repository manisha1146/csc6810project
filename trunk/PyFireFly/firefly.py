""" This module contains the Population class and Firefly class for
    continuous optimization problems"""
from random import *
from math import *
from functions import *

def writeCoords(filename, pop):
    with open(filename, 'w') as f:
        for fly in pop.pop:
            for coord in fly.coords:
                f.write(str(coord) + " ")
            f.write("\n")

class Population:
    """ The Population class is responsible for maintaining the fireflies and
        running the rounds of optimization"""

    NORMAL = 1
    HYBRID = 2

    __funcs = {"dejung" : DeJung }

    def __init__(self, gen, size, dim, alpha, beta, gamma, funcName, style=NORMAL):

        """ Setup sets the initialization parameters 
            for the population"""

        self.gen = gen
        self.alpha = self.alpha0 = alpha
        self.beta0 = beta
        self.gamma = gamma
        self.func = self.__funcs[funcName](dim)
        self.style = style
        self.rand = Random()
        self.rand.seed()
        self.pop = self.__generate_pop(size, dim)
        self.oldpop = self.__generate_pop(size, dim)

    def run(self):
        """ Run begins the optimization based 
            on the initialization parameters given """
        
        if self.style == Population.NORMAL:
            self.__npop()
        else:
            self.__hpop()

        self.pop.sort()
        return self.pop[0]

    def __generate_pop(self, size, dim):
        """ initializes our population """
        return [FireFly(self.func, self, dim)  for i in xrange(size)]

    def __npop(self):
        """ __npop runs the normal firefly algorithm """

        for i in xrange(self.gen):
            self.__copy_pop(self.pop, self.oldpop)
            self.pop = [self.__nmappop(fly) for fly in self.pop]

    def __hpop(self):
        """ __hpop runs the hybrid firefly algorithm """

        #start at 2 for the log function. do same amount of steps
        for i in xrange(2, self.gen + 2):
            self.alpha = self.alpha0 / log(i)
            self.__copy_pop(self.pop, self.oldpop)
            self.pop = [self.__hmappop(fly) for fly in self.pop]

    def __nmappop(self, fly):
        """ ___nmappop maps a firefly to its new position """
        fly.moved = False
        fly = reduce(flyfold, self.oldpop, fly)
        fly.eval()
        return fly

    def __hmappop(self, fly):
        """ __hmappop maps a firefly to its new 
            position using the hybrid technique """

        fly.moved = False
        fly = reduce(flyfold, self.oldpop, fly)
        if not fly.moved:
            fly.move_random()
        fly.eval()
        return fly
    
    def __copy_pop(self, population, oldpopulation):
        """ copies the population coords to oldpopulation coords """
        #there must be a better way to copy these without having to make a new list
        for f in xrange(len(population)):
            oldpopulation[f].copy(population[f])


class FireFly:
    """ A FireFly is a point in hyperdimensional space """

    def __init__(self, objfunc, population, dim):
        self.func = objfunc
        self.pop = population
        self.coords = [(self.pop.rand.random()*(self.func.maxs[x] - self.func.mins[x]) + self.func.mins[x]) for x in xrange(dim)]
        self.val = self.func.eval(self.coords)
        self.moved = False

    def __cmp__(self, fly):
        if isinstance(fly, FireFly):
            return cmp(self.val, fly.val)
        else:
            return cmp(self.val, fly)

    def __str__(self):
        return str(self.val)

    def __repr__(self):
        return str(self.val)

    def eval(self):
        """ eval evaluates the firefly given its current coordinates """

        self.val = self.func.eval(self.coords)

    def copy(self, fly):
        """ copy the coordinates and val from fly to this """

        self.val = fly.val
        for i in xrange(len(fly.coords)):
            self.coords[i] = fly.coords[i]

    def nfoldf(self, fly):
        """ our fold function to use over a list of flies """

        if self.val > fly.val:
            #calculate the distance
            dist = self.__calculate_dist(fly)
            #calculate the attractiveness beta
            beta = self.__calculate_beta(dist, self.pop.beta0, self.pop.gamma)
            #move towards fly
            self.move(self.pop.alpha, beta, self.pop.rand, fly)
            #we moved
            self.moved = True

        return self

    def move(self, alpha, beta, rand, fly):
        """ moves towards another fly based on the 
            values of alpha and beta """

        for i in xrange(len(self.coords)):
            # calc the temp value to set as coord
            tval = ((1 - beta) * fly.coords[i]) + \
                    (beta * self.coords[i]) + (alpha * (rand.random() - 0.5))
            # set as coord if within bounds
            self.coords[i] = self.func.mins[i] if tval < self.func.mins[i] \
                    else self.func.maxs[i] if tval > self.func.maxs[i] else tval

    def move_random(self):
        """ moves a little random bit"""
        alpha = self.pop.alpha
        rand = self.pop.rand

        for i in xrange(len(self.coords)):
            # calc the temp value to set as coord
            tval = self.coords[i] + (alpha * (rand.random() - 0.5))
            # set as coord if within bounds
            self.coords[i] = self.func.mins[i] if tval < self.func.mins[i] \
                    else self.func.maxs[i] if tval > self.func.maxs[i] else tval

    def __calculate_dist(self, fly):
        """ calculates the euclidean distance between flies """
        sum = 0.0
        for i in xrange(len(self.coords)):
            sum += (self.coords[i] - fly.coords[i])**2

        return sqrt(sum)

    def __calculate_beta(self, dist, beta0, gamma):
        return beta0 * exp((-gamma) * (dist**2))


def flyfold(fly, otherfly):
    return fly.nfoldf(otherfly)

