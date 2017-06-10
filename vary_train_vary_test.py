#
# Iterated Passenger's Dilemma
#
# Train the population against the "real players" and test against the "real players"
# The real population changes for every flight during training
#

import numpy as np
import random
from datetime import datetime
import itertools
import math

from deap import tools, base, creator, algorithms
import customfunctions
import real_players
from globals import index as i, rewards, genome_len


def main():
    # get list of real players
    # player_list = real_players.getVariedPopList()

    # multiobjective:
    #                   maximize avg reward,
    #             XX      minimize offers accepted/flights,
    #             XX      minimize missed opportunities/flights,
    #                   maximize success rate (successes/attempts)
    creator.create("FitnessMulti", base.Fitness, weights=(1.0, 1.0))
    # creator.create("FitnessMax", base.Fitness, weights=(-1.0,))

    creator.create("Individual", list, fitness=creator.FitnessMulti)
    # creator.create("Member", list, fitness=creator.FitnessMulti)

    POP_SIZE = 100          # number of members in the population
    EVOLVE_POP_SIZE = 50    # number of members of evolving population
    FLIGHTS_PER_GEN = 100   # number of simulations in one generation

    # get list of player names (not uniform)
    # larger than needed to allow shuffling to get different mixes of members
    player_list = real_players.getRealMix(3 * POP_SIZE)

    toolbox = base.Toolbox()                                            # initialize toolbox
    toolbox.register("initZero", random.randint, 0, 0)                  # create a bit 0
    toolbox.register("bit", random.randint, 0, 1)                       # create a bit 0 or 1
    toolbox.register("decision", random.randint, 0, 3)                  # create an int 0 to 3
    toolbox.register("type", customfunctions.get_next, player_list)     # get type from player list

    toolbox.register("genome", tools.initRepeat, list, toolbox.bit, genome_len)   # list of bits makes up genome

    # number of flights
    # total of rewards
    # number of offers accepted
    # number of offers lost
    # number of attempts to accept an offer
    toolbox.register("scores", tools.initRepeat, list, toolbox.initZero, 5)     # list of bits makes up genome

    # member is used in the real population
    # name: member type
    # scores: as defined above
    # initZero: bit indicating if an offer accepted this flight
    # initZero: decision this round
    toolbox.register("member", tools.initCycle, creator.Individual,
                                    (toolbox.type, toolbox.scores, toolbox.initZero, toolbox.initZero), n=1)

    # individual is used in evolving population
    # genome: decision bits
    # scores: as defined above
    # initZero: bit indicating if an offer accepted this flight
    # initZero: decision this round
    toolbox.register("individual", tools.initCycle, creator.Individual,
                                    (toolbox.genome, toolbox.scores, toolbox.initZero, toolbox.initZero), n=1)

    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("real_pop", tools.initRepeat, list, toolbox.member)

    # initialize evolution methods
    toolbox.register("evaluate", customfunctions.evaluate)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", customfunctions.mutateFlipBit, indpb=0.015)
    toolbox.register("select", tools.selNSGA2)

    NGEN = 2000             # number of generations of evolution
    CXPB = 0.9              # crossover probability
    MUTPB = 0.05            # mutation probability

    round_reached = [0] * len(rewards)

    #
    # create the population of members to be trained
    evolving_pop = toolbox.population(n=EVOLVE_POP_SIZE)  # initialize population


    # some number of flights in each generation
    for flight in range(FLIGHTS_PER_GEN):

        # shuffle the player list to get a different mix
        random.shuffle(player_list)

        # now create the population of real members for this flight
        real_pop = toolbox.real_pop(n=POP_SIZE)

        # print the population mix
        if flight == 0:
            print real_players.count_types(real_pop)

        # get number of offers for this flight so that it can be reused
        # for each member of the evolving population
        offers_this_flight = random.randint(2, 7)

        # play each member of evolving_pop against real_pop
        for ind in evolving_pop:

            # initial number of "free tickets"
            # new flight
            offersLeft = offers_this_flight
            roundNumber = 0

            while offersLeft > 0 and roundNumber < len(rewards):
                # determine decision for evolving member
                customfunctions.getDecisionBinary(offersLeft, roundNumber, ind)
                # determine decisinos for real members
                for real_member in real_pop:
                    customfunctions.getRealPlayerDecision(real_member, roundNumber, offersLeft, flight)
                # so the first members aren't always the same
                random.shuffle(real_pop)
                # determine in what position the evolving member gets to go
                ind_turn = random.randint(0, POP_SIZE - 1)
                # goes through everyone in population to decide whether to accept or reject the reward
                j = 0
                for real_member in real_pop:
                    if j == ind_turn:
                        # this is the evolving member
                        if ind[i.already] == 0 and ind[i.decision] == 1:
                            offersLeft = customfunctions.applyDecisionBinary(offersLeft, roundNumber, ind)
                        # reset decision
                        ind[i.decision] = 0
                    # real_member for this iteration
                    if real_member[i.already] == 0 and real_member[i.decision] == 1:
                        offersLeft = customfunctions.applyDecisionBinary(offersLeft, roundNumber, real_member)
                    # reset decision
                    real_member[i.decision] = 0

                    j += 1

                # keep track of how many flights reach each round
                if offersLeft == 0 or roundNumber == len(rewards) - 1:
                    round_reached[roundNumber] += 1

                roundNumber += 1

                # # reset decisions
                # ind[i.decision] = 0
                # customfunctions.resetDecisions(real_pop)

            # reset the accepted offer flags for next flight
            customfunctions.resetAccepts(real_pop)
            customfunctions.resetAccepts(evolving_pop)

    # add flights to parents
    for ind in evolving_pop:
        ind[i.scores][i.flights] += FLIGHTS_PER_GEN

    # evaluate parents
    fits = toolbox.map(toolbox.evaluate, evolving_pop)
    for fit, ind in zip(fits, evolving_pop):
        ind.fitness.values = fit

    #
    # main loop -- for NGEN generations
    for gen in range(NGEN):

        if gen % 100 == 0:
            t = datetime.now()
            print("\nGeneration: {0:5d}    {1:02d}:{2:02d}:{3:02d}\n".format(gen, t.hour, t.minute, t.second))

        # create offspring
        offspring = toolbox.map(toolbox.clone, evolving_pop)

        # crossover and mutation
        # if members aren't crossed-over, mutate them
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1[i.genome], child2[i.genome])
                # del child1.fitness.values
                # customfunctions.memberReset(child1)
                # del child2.fitness.values
                # customfunctions.memberReset(child2)
            else:
                toolbox.mutate(child1)
                toolbox.mutate(child2)
            del child1.fitness.values
            del child2.fitness.values

        '''
        # mutation
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values
                # customfunctions.memberReset(mutant)
        '''

        # create combined population
        evolving_pop.extend(offspring)
        evolving_pop = toolbox.map(toolbox.clone, evolving_pop)

        # some number of flights in each generation
        for flight in range(FLIGHTS_PER_GEN):

            # shuffle the player list to get a different mix
            random.shuffle(player_list)

            # now create the population of real members for this flight
            real_pop = toolbox.real_pop(n=POP_SIZE)

            # print the population mix
            if flight == 0:
                print real_players.count_types(real_pop)

            # get number of offers for this flight so that it can be reused
            # for each member of the evolving population
            offers_this_flight = random.randint(2, 7)

            # play each member of evolving_pop against real_pop
            for ind in evolving_pop:

                # initial number of "free tickets"
                # new flight
                offersLeft = offers_this_flight
                roundNumber = 0

                while offersLeft > 0 and roundNumber < len(rewards):
                    # determine decision for evolving member
                    customfunctions.getDecisionBinary(offersLeft, roundNumber, ind)
                    # determine decisions for real members
                    for real_member in real_pop:
                        customfunctions.getRealPlayerDecision(real_member, roundNumber, offersLeft, flight)
                    # so the first members aren't always the same
                    random.shuffle(real_pop)
                    # determine in what position the evolving member gets to go
                    ind_turn = random.randint(0, POP_SIZE - 1)
                    # goes through everyone in population to decide whether to accept or reject the reward
                    j = 0
                    for real_member in real_pop:
                        # if it's the evolving member's turn and they haven't already accepted an offer this flight
                        if j == ind_turn:
                            if ind[i.already] == 0 and ind[i.decision] == 1:
                                offersLeft = customfunctions.applyDecisionBinary(offersLeft, roundNumber, ind)
                            # reset decision
                            ind[i.decision] = 0
                        # real_member for this iteration
                        if real_member[i.already] == 0 and real_member[i.decision] == 1:
                            offersLeft = customfunctions.applyDecisionBinary(offersLeft, roundNumber, real_member)
                        # reset decision
                        real_member[i.decision] = 0

                        j += 1

                    # keep track of how many flights reach each round
                    if offersLeft == 0 or roundNumber == len(rewards) - 1:
                        round_reached[roundNumber] += 1

                    roundNumber += 1

                    # # reset decisions
                    # ind[i.decision] = 0
                    # customfunctions.resetDecisions(real_pop)

                # reset the accepted offer flags for next flight
                customfunctions.resetAccepts(real_pop)
                customfunctions.resetAccepts(evolving_pop)

        # add flights to offspring
        for ind in evolving_pop:
            ind[i.scores][i.flights] += FLIGHTS_PER_GEN

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
        # o1, o2, o3, o4 = customfunctions.evaluate(ind)
        o1, o2 = customfunctions.evaluate(ind)
        # print "{0}  {1}  {2}  {3}\n".format(o1, o2, o3, o4)
        print "{0}  {1}\n".format(o1, o2)

    print round_reached

    customfunctions.graphObjectives(evolving_pop)

    #
    # now compete best member of evolved population against "real players"
    #
    print
    print "Best player vs population of real players: \n"

    NUM_FLIGHTS = 10000

    # reset round_reached for testing phase
    round_reached = [0] * len(rewards)

    # now create the pool of real players from which real_pop will be chosen for each flight
    pool = toolbox.real_pop(n=3*POP_SIZE)

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
    best_member = toolbox.member()
    best_member[i.type] = 'best_player'

    # count rounds in which best member accepts an offer
    best_accepts = [0] * len(rewards)

    # run a tournament for NUM_FLIGHTS flights
    for flight in range(NUM_FLIGHTS):
        # initial number of "free tickets"
        # new flight
        offersLeft = random.randint(2, 7)
        roundNumber = 0

        # shuffle the pool of real players and create the real population for this flight
        random.shuffle(pool)
        real_pop = pool[:POP_SIZE - 1]
        # delete these members from pool -- will add them back in after flight
        # this is so that pool will include the updated statistics for those
        pool = pool[POP_SIZE - 1:]

        while offersLeft > 0 and roundNumber < len(rewards):
            # determine decisions for real population
            for real_member in real_pop:
                customfunctions.getRealPlayerDecision(real_member, roundNumber, offersLeft, flight)
            # determine decision for best evolved member
            customfunctions.getDecisionBinary(offersLeft, roundNumber, best)

            # so the order of turns is different for each flight
            random.shuffle(real_pop)
            # determine where the best evolved member goes in the order
            best_turn = random.randint(0, POP_SIZE - 2)
            # goes through everyone in population to decide whether to accept or reject the reward
            count = 0
            for member in real_pop:
                if count == best_turn:
                    # if member hasn't already accepted an offer
                    if best[i.already] == 0 and best[i.decision] == 1:
                        # temporary to track rounds in which offers accepted by best member
                        if offersLeft > 0:
                            best_accepts[roundNumber] += 1
                        offersLeft = customfunctions.applyDecisionBinary(offersLeft, roundNumber, best)
                    # reset decision
                    best[i.decision] = 0

                # member gets a turn also
                if member[i.already] == 0 and member[i.decision] == 1:
                    offersLeft = customfunctions.applyDecisionBinary(offersLeft, roundNumber, member)
                # reset decision
                member[i.decision] = 0

                count += 1

            # keep track of how many flights reach each round
            if offersLeft == 0 or roundNumber == len(rewards) - 1:
                round_reached[roundNumber] += 1

            roundNumber += 1

            # # reset decisions
            # best[i.decision] = 0
            # customfunctions.resetDecisions(real_pop)

        # reset the accepted offer flags for next flight
        customfunctions.resetAccepts(real_pop)
        best[i.already] = 0

        # add the population from completed flight back into the pool
        pool.extend(real_pop)

    # add flights to members
    for member in real_pop:
        member[i.scores][i.flights] += NUM_FLIGHTS

    best[i.scores][i.flights] += NUM_FLIGHTS

    # calculate fitness of population
    fits = toolbox.map(toolbox.evaluate, real_pop)
    for fit, ind in zip(fits, real_pop):
        ind.fitness.values = fit

    # evaluate the evolved player and print
    print 'Best evolved member:'
    print "['best_player', {0}]".format(best[1])
    # o1, o2, o3, o4 = customfunctions.evaluate(ind)
    o1, o2 = customfunctions.evaluate(best)
    # print "{0}  {1}  {2}  {3}\n".format(o1, o2, o3, o4)
    print "{0}  {1}\n".format(o1, o2)
    print
    print("Best player accepts by round: {0}\n".format(best_accepts))

    # print output with top members
    print '\nEntire population, including best evolved member:'
    pool.append(best)
    all_ind = tools.selBest(pool, POP_SIZE)
    for ind in all_ind:
        print str(ind)
        o1, o2 = customfunctions.evaluate(ind)
        # print "{0}  {1}  {2}  {3}\n".format(o1, o2, o3, o4)
        print "{0}  {1}\n".format(o1, o2)

    print round_reached


if __name__ == "__main__":
    main()
