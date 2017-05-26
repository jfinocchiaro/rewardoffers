import random

rewards = [500, 1000, 2000, 3000, 4000, 5000, 7500, 10000]

# real member types:
#
# business:   never accept
# dude:       always accept
# last:       accept last available offer
# ka-ching:   accept if 5th round or higher
# ka-ching+:  accept if last round
# mod25:      accept if flight count % 25 == 0
# rand-ching-low: accept at random -- prob increases with amount - max prob = 0.5
# rand-ching-high: accept at random - prob increases with amount - max prob = 1


# not currently being used
def getVariedPopList():
    return ['business', 'last', 'ka-ching', 'ka-ching+', 'random', 'mod10', 'mod25']


def getRealMix(length):
    l = []
    # about 12% of passengers, on average, are business travelers
    business_num = int(random.gauss(0.15, 0.06) * length)
    for i in range(business_num):
        l.append('business')
    l.append('dude')
    l.append('dude')
    num_left = length - len(l)
    for i in range(int(random.gauss(0.25, 0.08) * num_left)):
        l.append('last')
    for i in range(int(random.gauss(0.45, 0.08) * num_left)):
        l.append('rand-ching-low')
    for i in range(length - len(l)):
        l.append('rand-ching-high')
    return l


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

    elif oppName == 'rand-ching-low':
        # if random.randint(0, 15) < round + 1:
        if random.randint(0, 20000) < rewards[round]:
            decision2 = 1
        else:
            decision2 = 0

    elif oppName == 'rand-ching-high':
        # if random.randint(0, 7) < round + 1:
        if random.randint(0, 10000) < rewards[round]:
            decision2 = 1
        else:
            decision2 = 0

    # else
    else:
        print "Error invalid varied player"
        decision2 = -1

    return decision2
