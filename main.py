import numpy as np
import random
from deap import tools, base, creator, algorithms
import customfunctions
import itertools

def main():
    #multiobjective- maximize reward, minimize missed opportunities
    creator.create("FitnessMulti", base.Fitness, weights=(1.0,-1.0))
    creator.create("Individual", list, fitness=creator.FitnessMulti)


    IND_SIZE = 70    #length of genome
    POP_SIZE = 150   #number of members in the population


    toolbox = base.Toolbox()    #initialize toolbox
    toolbox.register("attr_int", random.randint, 0 , 0) #initialize to 0



    toolbox.register("bit", random.randint, 0, 1) #create a bit 0 or 1
    toolbox.register("genome", tools.initRepeat, list, toolbox.bit, IND_SIZE) #list of bits makes up genome
    toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.genome, toolbox.attr_int,toolbox.attr_int,toolbox.attr_int,toolbox.attr_int, toolbox.attr_int), n=1)    #creates an individual with genome and scores
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)  #list of individuals makes up population
    population = toolbox.population(n=POP_SIZE) #initialize population

    #initialize evolution methods
    toolbox.register("evaluate", deapplaygame.evaluate)
    toolbox.register("mate", tools.cxOnePoint)
    toolbox.register("mutate", )
    toolbox.register("select", tools.selNSGA2)

    NGEN = 5000 #number of generations of evolution


if __name__ == "__main__":
    main()
