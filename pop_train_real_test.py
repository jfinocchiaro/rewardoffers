import numpy as np
import random
from deap import tools, base, creator, algorithms
import customfunctions
import real_players
import itertools
import math

def main():
    # get list of real players
    player_list = real_players.getVariedPopList()

    # multiobjective- maximize reward, minimize missed opportunities
    creator.create("FitnessMulti", base.Fitness, weights=(1.0, -1.0, -1.0))
    # creator.create("FitnessMax", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMulti)
    # creator.create("Member", list, fitness=creator.FitnessMulti)

    IND_SIZE = 64           # length of genome
    POP_SIZE = 100          # number of members in the population
    FLIGHTS_PER_GEN = 100   # number of simulations in one generation

    toolbox = base.Toolbox()                                # initialize toolbox
    toolbox.register("initZero", random.randint, 0, 0)      # create a bit 0
    # toolbox.register("bit", random.choice, init_bits)     # create a bit 0 or 1
    toolbox.register("bit", random.randint, 0, 1)           # create a bit 0 or 1
    toolbox.register("decision", random.randint, 0, 3)      # create an int 0 to 3
    toolbox.register("name", random.choice, player_list)    # create a name from list of possible players

    toolbox.register("genome", tools.initRepeat, list, toolbox.bit, IND_SIZE)          # list of bits makes up genome
    # flights, total reward, offers accepted, offers lost
    toolbox.register("scores", tools.initRepeat, list, toolbox.initZero, 4)  # list of bits makes up genome

    toolbox.register("member", tools.initCycle, creator.Individual, (toolbox.name, toolbox.scores), 1)
    toolbox.register("individual", tools.initCycle, creator.Individual,
                     (toolbox.genome, toolbox.scores), n=1)       # creates an individual with genome and scores
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)  # list of individuals makes up population
    toolbox.register("real_pop", tools.initRepeat, list, toolbox.member)

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

    # print round_reached

    # customfunctions.graphObjectives(population)


    # now compete best member of evolved population against "real players"
    print
    print "Best player vs population of real players: \n"
    NUM_FLIGHTS = 5000
    round_reached = [0, 0, 0, 0, 0, 0, 0, 0]

    # get best player -- all_ind is the sorted population
    best = all_ind[0]
    customfunctions.memberReset(best)       # reset scores of best member
    del best.fitness.values                 # delete fitness values of best member

    # create population of real players
    real_pop = toolbox.real_pop(n=POP_SIZE)
    real_pop[0][0] = 'best_player'          # replace a member of real_pop with best

    # run a tournament for NUM_FLIGHTS flights
    for flight in range(NUM_FLIGHTS):
        # initial number of "free tickets"
        # new flight
        offersLeft = random.randint(6, 7)
        roundNumber = 0

        while offersLeft > 0 and roundNumber < len(rewards):
            # so the first members aren't always the same
            random.shuffle(real_pop)
            # goes through everyone in population to decide whether to accept or reject the reward
            for member in real_pop:
                if member[0] == 'best_player':
                    offersLeft = customfunctions.makeDecisionBinary(offersLeft, roundNumber, best)
                elif member[0] == 'couple':
                    decision = real_players.playVariedPop('couple', roundNumber, offersLeft, flight)
                    if decision == 1 and offersLeft >= 2:
                        offersLeft -= 2
                        member[1][1] += 2*rewards[roundNumber]
                        member[1][2] += 2
                    elif decision == 1 and offersLeft < 2:
                        member[1][3] += 2
                else:
                    decision = real_players.playVariedPop(member[0], roundNumber, offersLeft, flight)
                    if decision == 1 and offersLeft >= 1:
                        offersLeft -= 1
                        member[1][1] += rewards[roundNumber]
                        member[1][2] += 1
                    elif decision == 1 and offersLeft == 0:
                        member[1][3] += 1

            # keep track of how many flights reach each round
            if offersLeft == 0 or roundNumber == len(rewards) - 1:
                round_reached[roundNumber] += 1

            roundNumber += 1

    # add flights to members
    for member in real_pop:
        member[1][0] += NUM_FLIGHTS

    # calculate fitness of population
    fits = toolbox.map(toolbox.evaluate, real_pop)
    for fit, ind in zip(fits, real_pop):
        ind.fitness.values = fit

    # print output with top members
    all_ind = tools.selBest(real_pop, len(real_pop))
    for ind in all_ind:
        print str(ind)
        o1, o2, o3 = customfunctions.evaluate(ind)
        print "{0}  {1}  {2}\n".format(o1, o2, o3)

    print round_reached


if __name__ == "__main__":
    main()
