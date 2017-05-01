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


    IND_SIZE = 64       s#length of genome
    POP_SIZE = 100      #number of members in the population
    DECISION_SIZE = 3   #four decisions can be made
    FLIGHTS_PER_GEN = 1 #number of simulations in one generation

    toolbox = base.Toolbox()    #initialize toolbox
    toolbox.register("initZero", random.randint, 0 , 0) #initialize to 0
    toolbox.register("bit", random.randint, 0, 1) #create a bit 0 or 1
    toolbox.register("decision", random.randint, 0, 3) #create a bit 0 to 3

    toolbox.register("genome", tools.initRepeat, list, toolbox.decision, IND_SIZE) #list of bits makes up genome
    toolbox.register("offerAmts", tools.initRepeat, list, toolbox.bit, DECISION_SIZE) #list of bits makes up genome
    toolbox.register("scores", tools.initRepeat, list, toolbox.initZero, 2) #list of bits makes up genome

    toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.genome, toolbox.scores), n=1)    #creates an individual with genome and scores
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)  #list of individuals makes up population
    population = toolbox.population(n=POP_SIZE) #initialize population

    #initialize evolution methods
    toolbox.register("evaluate", customfunctions.evaluate)
    toolbox.register("mate", tools.cxOnePoint)
    toolbox.register("mutate", customfunctions.mutateFlipBit)
    toolbox.register("select", tools.selNSGA2)

    NGEN = 5000 #number of generations of evolution
    CXPB = (0.9)
    MUTPB = (0.1)

    rewards = [500, 1000, 2000, 3000, 4000, 5000, 7500, 10000]

    #3 bits for offers remaining, 3 bits for offer amount (values in [500, 1000, 2000, 3000, 4000, 5000, 7500, 10000])
    for gen in range(1):

        if gen % 50 == 0:
            print "Generation " + str(gen)

        for x in range(FLIGHTS_PER_GEN):
            #initial number of "free tickets"
            #new flight
            offersLeft = random.randint(1, 7)
            roundNumber = 0

            while(offersLeft > 0 and roundNumber < len(rewards)):
                #so the first members aren't always the same
                random.shuffle(population)


                #goes through everyone in population to decide whether to accept or reject the reward
                for member in population:
                    [decision, offersLeft] = customfunctions.makeDecisionConditional(offersLeft, roundNumber, member)
                roundNumber += 1

        offspring = algorithms.varAnd(population, toolbox, cxpb=CXPB, mutpb=MUTPB)
        fits = toolbox.map(toolbox.evaluate, offspring)
        for fit, ind in zip(fits, offspring):
            ind.fitness.values = fit
        population = offspring


    #print output with top members
    all_ind = tools.selBest(population, len(population))
    for ind in all_ind:
        print ind[1]


if __name__ == "__main__":
    main()
