import numpy as np
import random
from deap import tools, base, creator, algorithms
import customfunctions
import itertools
import math

def main():
    # sequence from which genome bits are chosen, uniformly
    init_bits = [1, 0, 0, 0, 0, 0, 0, 0, 0, 0]

    # multiobjective- maximize reward, minimize missed opportunities
    creator.create("FitnessMulti", base.Fitness, weights=(1.0, -1.0, -1.0))
    # creator.create("FitnessMax", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMulti)
    # creator.create("Individual", list, fitness=creator.FitnessMax)

    IND_SIZE = 64           # length of genome
    POP_SIZE = 100          # number of members in the population
    DECISION_SIZE = 3       # four decisions can be made
    FLIGHTS_PER_GEN = 100   # number of simulations in one generation

    toolbox = base.Toolbox()                                # initialize toolbox
    toolbox.register("initZero", random.randint, 0, 0)      # create a bit 0
    # toolbox.register("bit", random.choice, init_bits)     # create a bit 0 or 1
    toolbox.register("bit", random.randint, 0, 1)           # create a bit 0 or 1
    toolbox.register("decision", random.randint, 0, 3)      # create an int 0 to 3

    toolbox.register("genome", tools.initRepeat, list, toolbox.bit, IND_SIZE)          # list of bits makes up genome
    # flights, total reward, offers accepted, offers lost
    toolbox.register("scores", tools.initRepeat, list, toolbox.initZero, 4)  # list of bits makes up genome

    toolbox.register("individual", tools.initCycle, creator.Individual, (toolbox.genome, toolbox.scores), n=1)    # creates an individual with genome and scores
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)  # list of individuals makes up population

    # initialize evolution methods
    toolbox.register("evaluate", customfunctions.evaluate)
    toolbox.register("mate", tools.cxUniform, indpb=0.5)
    toolbox.register("mutate", customfunctions.mutateFlipBit, indpb=0.015)
    toolbox.register("select", tools.selNSGA2)

    NGEN = 2000             # number of generations of evolution
    CXPB = 0.9              # crossover probability
    MUTPB = 0.1             # mutation probability

    rewards = [500, 1000, 2000, 3000, 4000, 5000, 7500, 10000]
    round_reached = [0, 0, 0, 0, 0, 0, 0, 0]

    #
    # create first population and run through flights to create scores
    population = toolbox.population(n=POP_SIZE)  # initialize population

    # get data for parents
    for x in range(FLIGHTS_PER_GEN):
        # initial number of "free tickets"
        # new flight
        offersLeft = random.randint(2, 7)
        roundNumber = 0

        while offersLeft > 0 and roundNumber < len(rewards):
            # so the first members aren't always the same
            random.shuffle(population)
            # goes through everyone in population to decide whether to accept or reject the reward
            for member in population:
                offersLeft = customfunctions.makeDecisionBinary(offersLeft, roundNumber, member)

            # keep track of how many flights reach each round
            if offersLeft == 0 or roundNumber == len(rewards) - 1:
                round_reached[roundNumber] += 1

            roundNumber += 1

    # add flights to parents
    for member in population:
        member[1][0] += FLIGHTS_PER_GEN

    # evaluate parents
    fits = toolbox.map(toolbox.evaluate, population)
    for fit, ind in zip(fits, population):
        ind.fitness.values = fit

    #
    # main loop -- for NGEN generations
    for gen in range(NGEN):

        if gen % 100 == 0:
            print "Generation " + str(gen)

        # create offspring
        offspring = toolbox.map(toolbox.clone, population)

        # crossover
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1[0], child2[0])
                del child1.fitness.values
                # customfunctions.memberReset(child1)
                del child2.fitness.values
                # customfunctions.memberReset(child2)

        # mutation
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values
                # customfunctions.memberReset(mutant)

        # create combined population
        population.extend(offspring)
        population = toolbox.map(toolbox.clone, population)

        # flights for combined population
        for x in range(FLIGHTS_PER_GEN):
            # initial number of "free tickets"
            # new flight
            offersLeft = random.randint(2, 7)
            roundNumber = 0

            while offersLeft > 0 and roundNumber < len(rewards):
                # so the first members aren't always the same
                random.shuffle(population)
                # goes through everyone in population to decide whether to accept or reject the reward
                for member in population:
                    offersLeft = customfunctions.makeDecisionBinary(offersLeft, roundNumber, member)

                # keep track of how many flights reach each round
                if offersLeft == 0 or roundNumber == len(rewards) - 1:
                    round_reached[roundNumber] += 1

                roundNumber += 1

        # add flights to offspring
        for member in population:
            member[1][0] += FLIGHTS_PER_GEN

        # calculate fitness of population
        fits = toolbox.map(toolbox.evaluate, population)
        for fit, ind in zip(fits, population):
            ind.fitness.values = fit

        # survival of the fittest
        population = toolbox.select(population, POP_SIZE)
        population = toolbox.map(toolbox.clone, population)


    # print output with top members
    all_ind = tools.selBest(population, len(population))
    for ind in all_ind:
        print str(ind)
        o1, o2, o3 = customfunctions.evaluate(ind)
        print "{0}  {1}  {2}\n".format(o1, o2, o3)

    print round_reached

    customfunctions.graphObjectives(population)


if __name__ == "__main__":
    main()
