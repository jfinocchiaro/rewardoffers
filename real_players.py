import random

rewards = [500, 1000, 2000, 3000, 4000, 5000, 7500, 10000]

def getVariedPopList():
    #return ['coop']
    return ['business', 'last', 'ka-ching', 'ka-ching+', 'random', 'mod10', 'mod25']

def playVariedPop(oppName, round, offers, flight):

    # always decline
    if oppName == 'business':
        decision2 = 0

    # always accept
    elif oppName == 'dude':
        decision2 = 1

    # accept 2 offers if available
    elif oppName == 'couple':
        if offers >= 2:
            decision2 = 1
        else:
            decision2 = 0

    # accept if one left
    elif oppName == 'last':
        if offers == 1:
            decision2 = 1
        else:
            decision2 = 0

    # accept if two or fewer left
    elif oppName == 'last2':
        if 0 < offers <= 2:
            decision2 = 1
        else:
            decision2 = 0

    # accept if round at least 4
    elif oppName == 'ka-ching':
        if round >= 4:
            decision2 = 1
        else:
            decision2 = 0

    # accept if last round
    elif oppName == 'ka-ching+':
        if round == len(rewards)-1:
            decision2 = 1
        else:
            decision2 = 0

    # random
    elif oppName == 'random':
        decision2 = random.randint(0, 1)

    # accept every 10th flight
    elif oppName == 'mod10':
        if flight % 10 == 0:
            decision2 = 1
        else:
            decision2 = 0

    # accept every 25th flight
    elif oppName == 'mod25':
        if flight % 25 == 1:
            decision2 = 1
        else:
            decision2 = 0

    # else
    else:
        print "Error invalid Axelrod player"
        decision2 = -1

    return decision2

