#
# values needed in multiple files in the project
#

# indicices into members and individuals
class index:
    def __init__(self):
        pass

    genome = 0          # for individual (evolving population)
    type = 0            # member type for member of real population
    scores = 1          # metrics tracked for individual and member
    already = 2         # bit indicating if offer accepted this flight for individual and member
    decision = 3        # whether to accept offer this round for individual and member

    # indices into scores - for both individuals and members
    flights = 0         # number of flights
    reward_total = 1    # total of accepted rewards
    offers_accept = 2   # number of offers accepted
    offers_lost = 3     # number of offers lost
    attempts = 4        # number of accept decisions


# sequence of rewards offered
rewards = [500, 750, 1000, 1500, 2500, 5000, 7500, 10000]

