import numpy as np
import random
from deap import tools, base, creator, algorithms
import customfunctions
import itertools
import math

def main():
    #multiobjective- maximize reward, minimize missed opportunities
    creator.create("FitnessMulti", base.Fitness, weights=(1.0,-1.0))
    creator.create("Individual", list, fitness=creator.FitnessMulti)


    IND_SIZE = 8     #length of genome
    POP_SIZE = 120    #number of members in the population
    DECISION_SIZE = 3 #four decisions can be made

    toolbox = base.Toolbox()    #initialize toolbox
    toolbox.register("initZero", random.randint, 0 , 0) #initialize to 0
    toolbox.register("bit", random.randint, 0, 1) #create a bit 0 or 1
    toolbox.register("decision", random.randint, 0, 3) #create a bit 0 to 3

    toolbox.register("genome", tools.initRepeat, list, toolbox.decision, IND_SIZE) #list of bits makes up genome
    toolbox.register("offerAmts", tools.initRepeat, list, toolbox.bit, DECISION_SIZE) #list of bits makes up genome
    toolbox.register("scores", tools.initRepeat, list, toolbox.initZero, 2) #list of bits makes up genome

    toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.genome, toolbox.offerAmts, toolbox.scores), n=1)    #creates an individual with genome and scores
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)  #list of individuals makes up population
    population = toolbox.population(n=POP_SIZE) #initialize population

    #initialize evolution methods
    toolbox.register("evaluate", customfunctions.evaluate)
    toolbox.register("mate", tools.cxOnePoint)
    toolbox.register("mutate", tools.mutShuffleIndexes)
    toolbox.register("select", tools.selNSGA2)

    NGEN = 5000 #number of generations of evolution
    CXPB = (0.9)
    MUTPB = (0.1)


    #3 bits for offers remaining, 3 bits for offer amount (values in [500, 1000, 2000, 3000, 4000, 5000, 7500, 10000])
    for gen in range(NGEN):
        offersLeft = random.randint(2, 16)
        random.shuffle(population)
        while(offersLeft > 0):
            for member in population:
                toolbox.evaluate

        offspring = algorithms.varAnd(population, toolbox, cxpb=CXPB, mutpb=MUTPB)
        fits = toolbox.map(toolbox.evaluate, offspring)
        for fit, ind in zip(fits, offspring):
            ind.fitness.values = fit
        population = offspring


if __name__ == "__main__":
    main()
