#
# Train the population against the "real players" and test against the "real players"
#

import numpy as np
import random
from deap import tools, base, creator, algorithms
import customfunctions
import real_players
import itertools
import math

def main():
    # get list of real players
    # player_list = real_players.getVariedPopList()

    # multiobjective- maximize reward, minimize missed opportunities
    creator.create("FitnessMulti", base.Fitness, weights=(1.0, -1.0, -1.0))
    # creator.create("FitnessMax", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMulti)
    # creator.create("Member", list, fitness=creator.FitnessMulti)

    IND_SIZE = 64           # length of genome
    POP_SIZE = 100          # number of members in the population
    EVOLVE_POP_SIZE = 50    # number of members of evolving population
    FLIGHTS_PER_GEN = 100   # number of simulations in one generation

    # get list of player names (not uniform)
    player_list = real_players.getRealMix(POP_SIZE)

    toolbox = base.Toolbox()                                # initialize toolbox
    toolbox.register("initZero", random.randint, 0, 0)      # create a bit 0
    # toolbox.register("bit", random.choice, init_bits)     # create a bit 0 or 1
    toolbox.register("bit", random.randint, 0, 1)           # create a bit 0 or 1
    toolbox.register("decision", random.randint, 0, 3)      # create an int 0 to 3
    toolbox.register("name", customfunctions.get_next, player_list)    # create a name from list of possible players

    toolbox.register("genome", tools.initRepeat, list, toolbox.bit, IND_SIZE)          # list of bits makes up genome
    # flights, total reward, offers accepted, offers lost
    toolbox.register("scores", tools.initRepeat, list, toolbox.initZero, 4)  # list of bits makes up genome

    # member is used in the real population
    # name: member type, scores: as defined above, initZero: bit indicating if an offer accepted this flight
    toolbox.register("member", tools.initCycle, creator.Individual, (toolbox.name, toolbox.scores, toolbox.initZero), 1)
    # individual is used in evolving population
    # genome: decision bits, scores: as defined above, initZero: biti indicating if an offer accepted this flight
    toolbox.register("individual", tools.initCycle, creator.Individual,
                     (toolbox.genome, toolbox.scores, toolbox.initZero), n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
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
    # create the population of members to be trained
    evolving_pop = toolbox.population(n=EVOLVE_POP_SIZE)  # initialize population

    # create the population of real members to train against
    real_pop = toolbox.real_pop(n=POP_SIZE)

    # play each member of evolving_pop against real_pop
    for member in evolving_pop:

        # get data for parents
        for flight in range(FLIGHTS_PER_GEN):
            # initial number of "free tickets"
            # new flight
            offersLeft = random.randint(2, 7)
            roundNumber = 0

            while offersLeft > 0 and roundNumber < len(rewards):
                # so the first members aren't always the same
                random.shuffle(real_pop)
                # determine in what position the evolving member gets to go
                member_turn = random.randint(0, 100)
                # goes through everyone in population to decide whether to accept or reject the reward
                i = 0
                for real_member in real_pop:
                    if member_turn == i and member[2] == 0:
                        offersLeft = customfunctions.makeDecisionBinary(offersLeft, roundNumber, member)
                    if real_member[0] == 'couple':
                        if real_member[2] == 0:
                            decision = real_players.playVariedPop('couple', roundNumber, offersLeft, flight)
                            if decision == 1 and offersLeft >= 2 and real_member[2] == 0:
                                offersLeft -= 2
                                real_member[1][1] += 2 * rewards[roundNumber]
                                real_member[1][2] += 2
                                real_member[2] = 1
                            elif decision == 1 and offersLeft < 2:
                                real_member[1][3] += 2
                    else:
                        if real_member[2] == 0:
                            decision = real_players.playVariedPop(real_member[0], roundNumber, offersLeft, flight)
                            if decision == 1 and offersLeft >= 1 and real_member[2] == 0:
                                offersLeft -= 1
                                real_member[1][1] += rewards[roundNumber]
                                real_member[1][2] += 1
                                real_member[2] = 1
                            elif decision == 1 and offersLeft == 0:
                                real_member[1][3] += 1

                    i += 1

                # keep track of how many flights reach each round
                if offersLeft == 0 or roundNumber == len(rewards) - 1:
                    round_reached[roundNumber] += 1

                roundNumber += 1

            # reset the accepted offer flags for next flight
            customfunctions.resetAccepts(real_pop)
            customfunctions.resetAccepts(evolving_pop)

    # add flights to parents
    for member in evolving_pop:
        member[1][0] += FLIGHTS_PER_GEN

    # evaluate parents
    fits = toolbox.map(toolbox.evaluate, evolving_pop)
    for fit, ind in zip(fits, evolving_pop):
        ind.fitness.values = fit

    #
    # main loop -- for NGEN generations
    for gen in range(NGEN):

        if gen % 100 == 0:
            print "Generation " + str(gen)

        # create offspring
        offspring = toolbox.map(toolbox.clone, evolving_pop)

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
        evolving_pop.extend(offspring)
        evolving_pop = toolbox.map(toolbox.clone, evolving_pop)

        for member in evolving_pop:

            # flights for combined population
            for flight in range(FLIGHTS_PER_GEN):
                # initial number of "free tickets"
                # new flight
                offersLeft = random.randint(2, 7)
                roundNumber = 0

                while offersLeft > 0 and roundNumber < len(rewards):
                    # so the first members aren't always the same
                    random.shuffle(real_pop)
                    # determine in what position the evolving member gets to go
                    member_turn = random.randint(0, 100)
                    # goes through everyone in population to decide whether to accept or reject the reward
                    i = 0
                    for real_member in real_pop:
                        # if it's the evolving member's turn and they haven't already accepted an offer this flight
                        if member_turn == i and member[2] == 0:
                            offersLeft = customfunctions.makeDecisionBinary(offersLeft, roundNumber, member)
                        if real_member[0] == 'couple':
                            # if this member hasn't already accepted an offer for this flight
                            if real_member[2] == 0:
                                decision = real_players.playVariedPop('couple', roundNumber, offersLeft, flight)
                                if decision == 1 and offersLeft >= 2:
                                    offersLeft -= 2
                                    real_member[1][1] += 2 * rewards[roundNumber]
                                    real_member[1][2] += 2
                                    real_member[2] = 1
                                elif decision == 1 and offersLeft < 2:
                                    real_member[1][3] += 2
                        else:
                            if real_member[2] == 0:
                                decision = real_players.playVariedPop(real_member[0], roundNumber, offersLeft, flight)
                                if decision == 1 and offersLeft >= 1 and real_member[2] == 0:
                                    offersLeft -= 1
                                    real_member[1][1] += rewards[roundNumber]
                                    real_member[1][2] += 1
                                    real_member[2] = 1
                                elif decision == 1 and offersLeft == 0:
                                    real_member[1][3] += 1

                        i += 1

                    # keep track of how many flights reach each round
                    if offersLeft == 0 or roundNumber == len(rewards) - 1:
                        round_reached[roundNumber] += 1

                    roundNumber += 1

                # reset the accepted offer flags for next flight
                customfunctions.resetAccepts(real_pop)
                customfunctions.resetAccepts(evolving_pop)

        # add flights to offspring
        for member in evolving_pop:
            member[1][0] += FLIGHTS_PER_GEN

        # calculate fitness of population
        fits = toolbox.map(toolbox.evaluate, evolving_pop)
        for fit, ind in zip(fits, evolving_pop):
            ind.fitness.values = fit

        # survival of the fittest
        evolving_pop = toolbox.select(evolving_pop, EVOLVE_POP_SIZE)
        evolving_pop = toolbox.map(toolbox.clone, evolving_pop)


    # print output with top members
    all_ind = tools.selBest(evolving_pop, len(evolving_pop))
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
    # reset round_reached for testing phase
    round_reached = [0, 0, 0, 0, 0, 0, 0, 0]

    # get best player -- all_ind is the sorted population
    best = toolbox.clone(all_ind[0])
    customfunctions.memberReset(best)       # reset scores of best member
    del best.fitness.values                 # delete fitness values of best member

    # create population of real players
    # real_pop = toolbox.real_pop(n=POP_SIZE)
    customfunctions.resetScores(real_pop)

    # put this in real_pop so that the best player will
    # get a turn in the rotation -- but real_pop does
    # not contain the player.  best is the player since
    # we need to keep the genome bits for that player
    real_pop[0][0] = 'best_player'

    # run a tournament for NUM_FLIGHTS flights
    for flight in range(NUM_FLIGHTS):
        # initial number of "free tickets"
        # new flight
        offersLeft = random.randint(2, 7)
        roundNumber = 0

        while offersLeft > 0 and roundNumber < len(rewards):
            # so the first members aren't always the same
            random.shuffle(real_pop)
            # goes through everyone in population to decide whether to accept or reject the reward
            for member in real_pop:
                if member[0] == 'best_player':
                    if best[2] == 0:
                        offersLeft = customfunctions.makeDecisionBinary(offersLeft, roundNumber, best)
                        for i in range(len(member[1])):
                            member[1][i] = best[1][i]
                elif member[0] == 'couple':
                    if member[2] == 0:
                        decision = real_players.playVariedPop('couple', roundNumber, offersLeft, flight)
                        if decision == 1 and offersLeft >= 2:
                            offersLeft -= 2
                            member[1][1] += 2*rewards[roundNumber]
                            member[1][2] += 2
                            member[2] = 1
                        elif decision == 1 and offersLeft < 2:
                            member[1][3] += 2
                else:
                    if member[2] == 0:
                        decision = real_players.playVariedPop(member[0], roundNumber, offersLeft, flight)
                        if decision == 1 and offersLeft >= 1 and member[2] == 0:
                            offersLeft -= 1
                            member[1][1] += rewards[roundNumber]
                            member[1][2] += 1
                            member[2] = 1
                        elif decision == 1 and offersLeft == 0:
                            member[1][3] += 1

            # keep track of how many flights reach each round
            if offersLeft == 0 or roundNumber == len(rewards) - 1:
                round_reached[roundNumber] += 1

            roundNumber += 1

        # reset the accepted offer flags for next flight
        customfunctions.resetAccepts(real_pop)
        best[2] = 0

    # add flights to members
    for member in real_pop:
        member[1][0] += NUM_FLIGHTS

    best[1][0] += NUM_FLIGHTS

    # calculate fitness of population
    fits = toolbox.map(toolbox.evaluate, real_pop)
    for fit, ind in zip(fits, real_pop):
        ind.fitness.values = fit

    # evaluate the evolved player and print
    print "['best_player', {0}]".format(best[1])
    o1, o2, o3 = customfunctions.evaluate(best)
    print "{0}  {1}  {2}\n".format(o1, o2, o3)
    print

    # print output with top members
    all_ind = tools.selBest(real_pop, len(real_pop))
    for ind in all_ind:
        print str(ind)
        o1, o2, o3 = customfunctions.evaluate(ind)
        print "{0}  {1}  {2}\n".format(o1, o2, o3)

    print round_reached


if __name__ == "__main__":
    main()
