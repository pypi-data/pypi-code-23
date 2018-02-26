def compound_interest(capital, iterations, interest_rate):
    """Computes compound interest
    >>> print(compound_interest(100, 3, 9.1))
    [109.1, 228.1281, 357.9877571]
    """
    results = []
    cummulative_total = 0

    for i in range(0, iterations):
        cummulative_total += capital
        cummulative_total *= (interest_rate / 100) + 1
        results.append(cummulative_total)

    return results

# implememt a main method so that this thing can be run as a script as well as imported i.e it needs to take in params
