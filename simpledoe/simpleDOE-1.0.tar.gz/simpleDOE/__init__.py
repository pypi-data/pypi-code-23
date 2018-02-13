"""
SIMPLE DOE V1.0

@author: Flavio Bossolan
flavio.bossolan.github.io

This project is ment to be a python package with simple functions that compute the statistical significance of
tests of proportions. These types of tests are widely used in marketing and A/B testing.

These functionare ment to cover from the planning phase (DOE) to the measurement phase of the hypothesis.

For more help on the functions one can visit XXXXX or type the function name followed by a "?" as in standart
python programming.

For questions, support or to get involved please email flavio.bossolan@gmail.com

"""

import math
from scipy.stats import norm

# Point Statistic Functions

def prop_test_power(n1, n2, p1, p2, alpha=0.05):
    '''
    Returns the power of a test of two proportions. A power equal or
    higher to 0.8 is usually considered acceptable for a test.
    
    PARAMETERS:
    - n1 and n2: sizes of groups 1 and 2 used in the test.
    - p1 and p2: proportions being tested related to each group.
    - alpha: desired confidence level. 0.05 is the standard value widely used.
    
    RESULT:
    - The function returns only one value: the statistical power of the test.
    
    EXAMPLES:
    1. A marketing manager wants to execute an experiment testing two different 
    emails offering a product. He divides his population in two groups: test1 
    and test2 containing 20000 and 10000 email receivers respectively.
    He expects a response rate of 2% for his test1 and 1.4% for his test2. 
    Is this test significant and does it have significant statistical power?
    
    prop_test_power(20000, 10000, 0.02, 0.014)
    - The result is 0.95772126714949513 which is considered an acceptable level 
    of power in this case. The manager can proceed with the experiment.
    
    2. A marketing manager of an insurance company wants to determine the power
    of an experiment he proposes. He wants to send a letter inviting 50000 randomly
    selected people to buy insurance in his company offering a bonus of 30% discount.
    He keeps a control group of 10000 possible customers for a baseline comparison.
    Based on previous campaigns he expects that the test response rate will be
    3% and the control/baseline will be 1%. What is the power of the test?
    
    prop_test_power(50000, 10000, 0.03, 0.01)
    - The test has a very good statistical power of 1
    '''
    
    weighted_prop = (n1*p1+n2*p2)/(n1+n2)
    pooled_stderr = math.sqrt(weighted_prop*(1-weighted_prop)*(1/n1+1/n2))
    m0 = 0
    m1 = abs(p1-p2)
    z1 = norm.ppf(alpha/2)
    z2 = -z1
    x1 = m0+(z1*pooled_stderr)
    x2 = m0+(z2*pooled_stderr)
    b1 = norm.cdf(x2, loc=m1, scale=pooled_stderr)
    b2 = norm.cdf(x1, loc=m1, scale=pooled_stderr)
    return 1-(b1-b2) 
    

    
def prop_test_pvalue(n1, n2, p1, p2 ,alpha=0.05, tail=1):
    ''' 
    Returns the p-value of a Z test of 2 proportions.
    
    PARAMETERS:
    - n1 and n2: sizes of groups 1 and 2 used in the test.
    - p1 and p2: proportions being tested related to each group.
    - alpha: desired confidence level. 0.05 is the standard value widely used.
    - tail: 1 (default) of 2.
    
    RESULT:
    - The funtion returns the p-value of the 2 proportion z test.
    
    EXAMPLES:
    1. A marketing manager wants to execute an experiment testing two different 
    emails offering a product. He divides his population in two groups: test1 
    and test2 containing 20000 and 10000 email receivers respectively.
    He expects a response rate of 2% for his test1 and 1.4% for his test2. 
    Is this test significant?
    
    prop_test_pvalue(20000, 10000, 0.02, 0.014)
    - The result is 0.00011444227679380248 which is below the alpha level of the
    test. We consider the test results to be statistically significant.
    
    2. A marketing manager of an insurance company wants to determine the 
    significance of an experiment he proposes. He wants to send a letter 
    inviting 50000 randomly selected people to buy insurance in his company 
    offering a bonus of 30% discount. He keeps a control group of 10000 possible 
    customers for a baseline comparison. Based on previous campaigns he expects
    that the test response rate will be 3% and the control/baseline will be 1%.
    Are the results statistically significant?
    
    prop_test_pvalue(50000, 10000, 0.03, 0.01)
    - The p-value is really close to 0, so we reject the null hypothesis and 
    conclude that these results are statistically significant.
    '''
    
    weighted_prop = (n1*p1+n2*p2)/(n1+n2)
    pooled_stderr = math.sqrt(weighted_prop*(1-weighted_prop)*(1/n1+1/n2))
    z_score = abs(p1-p2)/pooled_stderr
    
    if tail == 2:
        return norm.cdf(-z_score)*2
    elif tail ==1:
        return 1-norm.cdf(z_score)
    else:
        return "Exception: Tail must be 1 or 2."


def prop_test_conf_interval(p, n, alpha=0.05):
    ''' 
    Returns the confidence interval for a test of proportions.
    
    PARAMETERS:
    - p: Proportion that is the result of the test.
    - n: Total population of the test.
    - alpha: Confidence level (0.05 standart).
    
    RESULT:
      - The function returns a list with 3 values, the parameter resulting from
      the confidence interval calculation, the lower bound and the upper bound.
    
    EXAMPLE:
    A marketing manager ran an experiment that resulted in significant lift
    mailing a population of 50000 customers with an offer. His response rate
    was 3%. What is the confidence interval he can expect if he executes the 
    same experiment?
    
    prop_test_conf_interval(0.03, 50000)
    - [0.0014952354442173917, 0.028504764555782606, 0.031495235444217388]
    He can expect his results to range from 2.8% and 3.1%
    '''
    
    beta = 1- (alpha/2)
    coef = norm.ppf(beta)
    int_coef= coef*math.sqrt(p*(1-p)/n)
    return [int_coef, p-int_coef, p+int_coef]
        
# Optimization Functions

def optimal_experiment_test_prop(n, p1, p2, alpha=0.05, power=0.8):
    '''
    Calculates the optimal sizes for a test given certain parameters.
    
    PARAMETERS:
    - n: Total available population for a test.
    - p1: Expected proportion of test population 1.
    - p2: Expected proportion of test population 2.
    - alpha: Confidence level of the test.
    - power: Desired power for the test.
    
    RESULT:
    - The function returns a list containing:
        - Total population;
        - Optimal population for test group 1;
        - Optimal population for test group 2;
        - P-value of the test;
        - Power of the test.
        
    EXAMPLE:
    A marketing manager has a population of 50000 people to mail a letter
    with a bonus offer for a marketing experiment. How should he split his 
    test/control groups knowing that he expects a response rate of 3% for his
    test group and 2% for his control based on his past learnings? He wants
    a power of 90% for this experiment.
    
    optimal_experiment_test_prop(50000, 0.03, 0.02, power=0.9)
    - [50000, 46800, 3200, 0.0011871645573293369, 0.9000756458257636]
    He can divide his experiment in 46800 for test and 3200 as control. This
    way he maximizes his targeting maintaining a considerable holdout for his
    test.
    '''
    
    n1 = n-1
    n2 = n-n1
    pwr = prop_test_power(n1, n2, p1, p2 ,alpha= alpha)    
    
    while pwr < power:
        n2 += 1
        n1 = n-n2
        pwr = prop_test_power(n1, n2, p1, p2 ,alpha= alpha)
        if n1 == 1:
            break   
    return [(n1+n2), n1, n2, prop_test_pvalue(n1, n2, p1, p2 ,alpha=alpha, tail=2), pwr]
    

def optimal_experiment_size(n1_ratio, p1, p2, alpha=0.05, power=0.8):
    '''
    calculates the optimal size for a 2 group test given a desired ratio.
    
    PARAMETERS:
    - n1_ratio: % ratio desired for test group 1. Must be between 0 and 1.
    - p1: Expected proportion of test population 1.
    - p2: Expected proportion of test population 2.
    - alpha: Confidence level of the test.
    - power: Desired power for the test.
    
    RESULT:
    - The function returns a list containing:
        - Total population;
        - Optimal population for test group 1;
        - Optimal population for test group 2;
        - P-value of the test;
        - Power of the test.
        
    EXAMPLE:
    A marketing manager wants to know whow many customers he needs to include
    in his next campaigns test/control groups giving the fact that he expects
    a 3% response rate for his test population and 2% for his control population.
    He wants to have a ratio of 70/30 in his test/control group size.
    
    optimal_experiment_size(0.7, 0.03, 0.02)
    - [9819, 6873, 2945, 0.0050851051615335924, 0.8000030155231419]
    The minimal quantity he needs to have a significant test with a power of 
    at least 0.8 is 6873 for his test group and 2945 for his control group.
    '''
    
    n= 1
    n1= n * n1_ratio
    n2= n - n1
    pwr = prop_test_power(n1, n2, p1, p2 ,alpha= alpha)
    
    while pwr < power:
        n+=1
        n1= n * n1_ratio
        n2= n - n1
        pwr = prop_test_power(n1, n2, p1, p2 ,alpha= alpha)
    
    return [n, int(n1), int(n2), prop_test_pvalue(n1, n2, p1, p2 ,alpha=alpha, tail=2), pwr]


def optimal_control_size(test_n, p1, p2, alpha=0.05, power=0.8):
    '''
    Calculates the minimal size expected for a control population given a test
    population and expected proportions.
    
    PARAMETERS:
    - test_n: Test group population.
    - p1: Expected proportion of test population 1.
    - p2: Expected proportion of test population 2.
    - alpha: Confidence level of the test.
    - power: Desired power for the test.
    
    RESULT:
    - The function returns a list containing:
        - Total population;
        - Population for test group 1;
        - Optimal population for control or test group 2;
        - P-value of the test;
        - Power of the test.
        
    EXAMPLE:
    A marketing manager will mail a promotion to 20000 customers. Based on his
    experience he expects a response rate of 3% for test and 2% for control. What
    is the minimum control population size he needs if he aims for a test with 90%
    statistical power?
    
    optimal_control_size(20000, 0.03, 0.02, power=0.9)
    - [23411, 20000, 3411, 0.0011878322023432199, 0.90004753759736567]
    His control size should have at least 3411 customers.
    '''
    
    n1 = test_n
    n2 = 1
    pwr = prop_test_power(n1, n2, p1, p2 ,alpha= alpha)
    
    while pwr < power:
        n2+=1
        pwr = prop_test_power(n1, n2, p1, p2 ,alpha= alpha)
        
    return [(n1+n2), n1, n2, prop_test_pvalue(n1, n2, p1, p2 ,alpha=alpha, tail=2), pwr]

# End of program
