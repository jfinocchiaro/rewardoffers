# -*- coding: utf-8 -*-
import random
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from deap import tools, base, creator, algorithms
import real_players
from globals import index, rewards


# return element at front of list
# add back to end of list
def get_next(l):
    elt = l.pop(0)
    l.append(elt)
    return elt


# evaluate score maximizing financial gains and minimizing missed oppotunities
# def evaluate(member):
#     # reward = 0
#     reward = member[1][0]
#     missedOpps = member[1][1]
#     return reward, missedOpps

def evaluate(member):
    avg_reward = 0.0
    scaled_accept = scaled_lost = success_rate = 0.0
    if member[index.scores][index.offers_accept] > 0:
        # calculate average accepted offer
        avg_reward = float(member[index.scores][index.reward_total]) / member[index.scores][index.offers_accept]
    '''
    if member[1][2] > 0:
        scaled_accept = (float(member[1][2]) / member[1][0]) * 100  # calculate accepted scaled by flights
    if member[1][3] > 0:
        scaled_lost = (float(member[1][3]) / member[1][0]) * 100    # calculate lost scaled by flights
    '''
    if member[index.scores][index.attempts] > 0:
        success_rate = (float(member[index.scores][index.offers_accept]) / member[index.scores][index.attempts])
    # return avg_reward, scaled_accept, scaled_lost, success_rate
    return avg_reward, success_rate


def resetScores(population):
    for member in population:
        for i in range(len(member[index.scores])):
            member[index.scores][i] = 0


def memberReset(member):
    for i in range(len(member[index.scores])):
        member[index.scores][i] = 0


def resetAccepts(population):
    for member in population:
        member[index.already] = 0


def resetDecisions(population):
    for member in population:
        member[index.decision] = 0


# offersLeft number between 0 and 8 in decimal
# roundNumber is what index in the rewards list they're in (0, 1, 2, ... ,7 )
# member is the member of the population (list of lists)
def makeDecisionConditional(offersLeft, roundNumber, member):
    decision = 0

    # offer stored in rewards
    offer = rewards[roundNumber]
    # print "offer:\t" + str(offer)

    # roundBin = int(str(roundNumber), 2)
    roundBin = format(roundNumber, 'b').zfill(3)
    # offersLeftBin = int(str(offersLeft), 2)
    offersLeftBin = format(offersLeft, 'b').zfill(3)

    decision_spot = roundBin + offersLeftBin

    decision_spot = int(decision_spot, 2)

    decision_bit = member[0][decision_spot]
    # print "decision bit:\t" + str(decision_bit)

    if offersLeft > 0 and decision_bit == 0:
        decision = 0
    elif offersLeft > 0 and decision_bit == 1:
        if offersLeft < 3:
            decision = 1
            offersLeft -= 1
            member[1][0] += offer
    elif offersLeft > 0 and decision_bit == 2:
        if offersLeft < 2:
            decision = 1
            offersLeft -= 1
            member[1][0] += offer
    elif offersLeft > 0 and decision_bit == 3:
        decision = 1
        offersLeft -= 1
        member[1][0] += offer
    elif offersLeft == 0 and decision_bit != 0:
        member[1][1] += 1  # missed opportunity increment
        decision = 0

    # print "Offers left: \t" + str(offersLeft)
    return [decision, offersLeft]


def makeDecisionBinary(offersLeft, roundNumber, member):

    # offer stored in rewards
    offer = rewards[roundNumber]

    roundBin = format(roundNumber, 'b').zfill(3)
    offersLeftBin = format(offersLeft, 'b').zfill(3)

    decision_spot = roundBin + offersLeftBin

    decision_spot = int(decision_spot, 2)
    decision_bit = member[index.genome][decision_spot]

    if offersLeft > 0 and decision_bit == 1:
        member[index.scores][index.reward_total] += offer       # update total reward
        member[index.scores][index.offers_accept] += 1          # increment offers accepted
        member[index.already] = 1                               # set bit indicating offer accepted
        offersLeft -= 1                                         # decrement offers remaining
        member[index.scores][index.attempts] += 1               # increment attempts

    elif offersLeft == 0 and decision_bit == 1:
        member[index.scores][index.offers_lost] += 1            # increment offers lost
        member[index.scores][index.attempts] += 1               # increment attempts

    return offersLeft


# determine and set decision for an evolving member
def getDecisionBinary(offersLeft, roundNumber, member):

    roundBin = format(roundNumber, 'b').zfill(3)
    offersLeftBin = format(offersLeft, 'b').zfill(3)

    decision_spot = roundBin + offersLeftBin
    decision_spot = int(decision_spot, 2)

    member[index.decision] = member[index.genome][decision_spot]


# apply the decision of a member
# assumes that the decision bit is 1
def applyDecisionBinary(offersLeft, roundNumber, member):

    # offer stored in rewards
    offer = rewards[roundNumber]

    if offersLeft > 0:
        member[index.scores][index.reward_total] += offer       # update total reward
        member[index.scores][index.offers_accept] += 1          # increment offers accepted
        member[index.already] = 1                               # set bit indicating offer accepted
        offersLeft -= 1                                         # decrement offers remaining
        member[index.scores][index.attempts] += 1               # increment attempts

    elif offersLeft == 0:
        member[index.scores][index.offers_lost] += 1            # increment offers lost
        member[index.scores][index.attempts] += 1               # increment attempts

    return offersLeft


# # determine and process decision for a member of real_population
# # return the number of offers remaining after processing the decision
# def getRealPlayerDecision(real_member, round_num, offers_left, flt):
#     if real_member[0] == 'couple':
#         if real_member[index.already] == 0:
#             decision = real_players.playVariedPop('couple', round_num, offers_left, flt)
#             if decision == 1 and offers_left >= 2:
#                 offers_left -= 2
#                 real_member[index.scores][index.reward_total] += 2 * rewards[round_num]
#                 real_member[index.scores][index.offers_accept] += 2
#                 real_member[index.scores][index.attempts] += 2
#                 real_member[index.already] = 1
#             elif decision == 1 and offers_left < 2:
#                 real_member[index.scores][index.offers_lost] += 2
#                 real_member[index.scores][index.attempts] += 2
#     else:
#         if real_member[index.already] == 0:
#             decision = real_players.playVariedPop(real_member[0], round_num, offers_left, flt)
#             if decision == 1 and offers_left >= 1:
#                 offers_left -= 1
#                 real_member[index.scores][index.reward_total] += rewards[round_num]
#                 real_member[index.scores][index.offers_accept] += 1
#                 real_member[index.scores][index.attempts] += 1
#                 real_member[index.already] = 1
#             elif decision == 1 and offers_left == 0:
#                 real_member[index.scores][index.offers_lost] += 1
#                 real_member[index.scores][index.attempts] += 1
#     return offers_left


# determine and set decision for a member of real_population
def getRealPlayerDecision(real_member, round_num, offers_left, flt):
    # default value
    decision = 0

    if real_member[0] == 'couple':
        if real_member[index.already] == 0:
            real_member[index.decision] = real_players.playVariedPop('couple', round_num, offers_left, flt)
    else:
        if real_member[index.already] == 0:
            real_member[index.decision] = real_players.playVariedPop(real_member[0], round_num, offers_left, flt)


def mutateFlipBit(individual, indpb=0.015):
    genome = individual[index.genome]
    #print genome
    genome = tools.mutFlipBit(genome, indpb)[0]
    #print genome
    individual[0] = genome
    return individual,


def pareto_frontier(Xs, Ys, maxX = True, maxY = False):
    # Sort the list in either ascending or descending order of X
    myList = sorted([[Xs[i], Ys[i]] for i in range(len(Xs))], reverse=maxX)
    # Start the Pareto frontier with the first value in the sorted list
    p_front = [myList[0]]
    # Loop through the sorted list
    for pair in myList[1:]:
        if maxY:
            if pair[1] >= p_front[-1][1]:
                p_front.append(pair)
        else:
            if pair[1] <= p_front[-1][1]:  # Look for lower values of Y…
                p_front.append(pair)  # … and add them to the Pareto frontier
    # Turn resulting pairs back into a list of Xs and Ys
    p_frontX = [pair[0] for pair in p_front]
    p_frontY = [pair[1] for pair in p_front]
    return p_frontX, p_frontY


def graphObjectives(population):
    xs = []
    ys = []
    zs = []
    for member in population:
        x, y, z = evaluate(member)
        xs.append(x)     # average reward
        ys.append(y)     # scaled offers accepted
        zs.append(z)     # scaled offers lost

    p_front = pareto_frontier(xs, ys, maxX = True, maxY = False)

    # plt.scatter(xs, ys)
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(xs, ys, zs, c='b', marker='x')


    ax.set_xlabel('Avg Reward')
    ax.set_ylabel('Offers Accepted')
    ax.set_zlabel('Offers Lost')

    # Axes3D.scatter(xs, ys, zs)
    # plt.plot(p_front[0], p_front[1])
    plt.show()
