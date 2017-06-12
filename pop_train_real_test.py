import numpy as np
import random
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

    # IND_SIZE = 64           # length of genome
    POP_SIZE = 100          # number of members in the population
    EVOLVE_POP_SIZE = 100    # number of members of evolving population
    FLIGHTS_PER_GEN = 100   # number of simulations in one generation

    # get list of player names (not uniform)
    player_list = real_players.getRealMix(POP_SIZE)

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
    toolbox.register("mate", tools.cxUniform, indpb=0.5)
    toolbox.register("mutate", customfunctions.mutateFlipBit, indpb=0.015)
    toolbox.register("select", tools.selNSGA2)

    NGEN = 3000             # number of generations of evolution
    CXPB = 0.9              # crossover probability
    MUTPB = 0.1             # mutation probability

    round_reached = [0] * len(rewards)

    #
    # create the population of members to be trained
    evolving_pop = toolbox.population(n=EVOLVE_POP_SIZE)  # initialize population

    # create the population of real members to train against
    real_pop = toolbox.real_pop(n=POP_SIZE)

    total_offers_made = 0
    total_offers_accepted = 0

    # get data for parents
    for flight in range(FLIGHTS_PER_GEN):
        # initial number of "free tickets"
        # new flight
        offersLeft = random.randint(2, 7)
        roundNumber = 0

        while offersLeft > 0 and roundNumber < len(rewards):
            # determine decisions
            for ind in evolving_pop:
                customfunctions.getDecisionBinary(offersLeft, roundNumber, ind)
            # so the first members aren't always the same
            random.shuffle(evolving_pop)

            # goes through everyone in population to decide whether to accept or reject the reward
            for ind in evolving_pop:
                if ind[i.already] == 0 and ind[i.decision] == 1:
                    offersLeft = customfunctions.applyDecisionBinary(offersLeft, roundNumber, ind)
                # reset decision
                ind[i.decision] = 0

            # keep track of how many flights reach each round
            if offersLeft == 0 or roundNumber == len(rewards) - 1:
                round_reached[roundNumber] += 1

            roundNumber += 1

        # reset the accepted offer flags for next flight
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

        # flights for combined population
        for flight in range(FLIGHTS_PER_GEN):
            # initial number of "free tickets"
            # new flight
            offersLeft = random.randint(2, 7)
            roundNumber = 0

            while offersLeft > 0 and roundNumber < len(rewards):
                # determine decisions
                for ind in evolving_pop:
                    customfunctions.getDecisionBinary(offersLeft, roundNumber, ind)
                # so the first members aren't always the same
                random.shuffle(evolving_pop)

                # goes through everyone in population to decide whether to accept or reject the reward
                for ind in evolving_pop:
                    if ind[i.already] == 0 and ind[i.decision] == 1:
                        offersLeft = customfunctions.applyDecisionBinary(offersLeft, roundNumber, ind)
                    # reset decision
                    ind[i.decision] = 0

                # keep track of how many flights reach each round
                if offersLeft == 0 or roundNumber == len(rewards) - 1:
                    round_reached[roundNumber] += 1

                roundNumber += 1

            # reset the accepted offer flags for next flight
            customfunctions.resetAccepts(evolving_pop)

        # add flights to parents
        for ind in evolving_pop:
            ind[i.scores][i.flights] += FLIGHTS_PER_GEN

        # evaluate parents
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

    print '\nCount of rounds reached for training phase:'
    print round_reached

    # customfunctions.graphObjectives(population)

    #
    # now compete best member of evolved population against "real players"
    print
    print "Best player vs population of real players: \n"

    NUM_FLIGHTS = 10000

    # reset round_reached for testing phase
    round_reached = [0] * len(rewards)

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
    real_pop.append(best_member)

    # count rounds in which best member accepts an offer
    best_accepts = [0] * len(rewards)

    # run a tournament for NUM_FLIGHTS flights
    for flight in range(NUM_FLIGHTS):
        # initial number of "free tickets"
        # new flight
        offersLeft = random.randint(2, 7)
        total_offers_made += offersLeft

        roundNumber = 0

        while offersLeft > 0 and roundNumber < len(rewards):
            # determine decisions
            for real_member in real_pop:
                if real_member[i.type] == 'best_player':
                    customfunctions.getDecisionBinary(offersLeft, roundNumber, best)
                else:
                    customfunctions.getRealPlayerDecision(real_member, roundNumber, offersLeft, flight)

            # so the first members aren't always the same
            random.shuffle(real_pop)
            # goes through everyone in population to decide whether to accept or reject the reward
            for member in real_pop:
                if member[i.type] == 'best_player':
                    # if member hasn't already accepted an offer
                    if best[i.already] == 0 and best[i.decision] == 1:
                        # temporary to track rounds in which offers accepted by best member
                        if offersLeft > 0:
                            best_accepts[roundNumber] += 1
                        offersLeft = customfunctions.applyDecisionBinary(offersLeft, roundNumber, best)
                        # copy scores from best player to best player's placeholder in real_pop
                        for s in range(len(member[i.scores])):
                            member[i.scores][s] = best[i.scores][s]
                    # reset decision
                    best[i.decision] = 0
                else:
                    if member[i.already] == 0 and member[i.decision] == 1:
                        offersLeft = customfunctions.applyDecisionBinary(offersLeft, roundNumber, member)
                    # reset decision
                    member[i.decision] = 0

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

    # add flights to members
    for member in real_pop:
        member[i.scores][i.flights] += NUM_FLIGHTS

    best[i.scores][i.flights] += NUM_FLIGHTS

    # calculate fitness of population
    fits = toolbox.map(toolbox.evaluate, real_pop)
    for fit, ind in zip(fits, real_pop):
        ind.fitness.values = fit

    # evaluate the evolved player and print
    print "['best_player', {0}]".format(best[1])
    # o1, o2, o3, o4 = customfunctions.evaluate(ind)
    o1, o2 = customfunctions.evaluate(best)
    # print "{0}  {1}  {2}  {3}\n".format(o1, o2, o3, o4)
    print "{0}  {1}\n".format(o1, o2)
    print("Best player accepts by round: {0}\n".format(best_accepts))

    # print output with top members
    all_ind = tools.selBest(real_pop, len(real_pop))
    for ind in all_ind:
        print str(ind)
        # o1, o2, o3, o4 = customfunctions.evaluate(ind)
        o1, o2 = customfunctions.evaluate(ind)
        # print "{0}  {1}  {2}  {3}\n".format(o1, o2, o3, o4)
        print "{0}  {1}\n".format(o1, o2)

    print 'Count of rounds reached for testing phase:'
    print round_reached
    print


if __name__ == "__main__":
    main()
