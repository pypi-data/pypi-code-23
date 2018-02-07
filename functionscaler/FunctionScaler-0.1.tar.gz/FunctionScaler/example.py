from FunctionScaler import *
import numpy as np
import matplotlib.pyplot as plt

n_points = 100



### Testing different ways of initialising FunctionScaler

#fs = FunctionScaler("unif")  # calling the uniform function by name
#fs = FunctionScaler("gauss") # calling the normal function by name 
#fs = FunctionScaler(TransformedFunction_Gauss()) # calling the normal function by class
fs = FunctionScaler(np.array(range(1,1+n_points))/(1.+n_points) ) # calling the uniform function directly by inv_cdf value


if False:
    # Testing 1 D operation
    mu, sigma  = 2., 0.5
    data = np.random.normal(mu, sigma, n_points)

    fs.fit(data)
    data_transf = fs.transform(data)
    data_invtransf = fs.invtransform(data_transf)

    if True:
        # Testing standard 1 D operation
        count, bins, ignored = plt.hist(data, 30, normed=True, alpha= 0.5, color="blue")
        #plt.hist(data_transf, 30, normed=True)
        plt.hist(data_invtransf, bins, normed=True, alpha = 0.5, color = "red")
        #plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (bins - mu)**2 / (2 * sigma**2) ), linewidth=2, color='r')



    if False:
        # Testing if data outside the trained range is handled correctly
        extrapolated_data = [2, -4, 6]
        data_p_exp = np.append(extrapolated_data,data)
        data_p_exp_transf = fs.transform(data_p_exp)
        data_p_exp_invtransf = fs.invtransform(data_p_exp_transf)

        #count, bins, ignored = plt.hist(data_p_exp, 30, normed=True)
        #plt.hist(data_p_exp_transf, 30, normed=True)
        count, bins, ignored = plt.hist(data_p_exp_invtransf, 30, normed=True)
        #plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (bins - mu)**2 / (2 * sigma**2) ), linewidth=2, color='r')

if True:
    # Testing 1 D operation with 0 variance
    mu, sigma  = 2., 0.
    data = np.random.normal(mu, sigma, n_points-1)
    data = np.append(data, 5)

    fs.fit(data)
    data_transf = fs.transform(data)
    data_invtransf = fs.invtransform(data_transf)

    if False:
        # Testing standard 1 D operation
        count, bins, ignored = plt.hist(data, 30, normed=True, alpha= 0.5, color="blue")
        #plt.hist(data_transf, 30, normed=True)
        plt.hist(data_invtransf, bins, normed=True, alpha = 0.5, color = "red")
        #plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (bins - mu)**2 / (2 * sigma**2) ), linewidth=2, color='r')



    if True:
        # Testing if data outside the trained range is handled correctly
        extrapolated_data = [20]
        print fs.transform(extrapolated_data)
        data_p_exp = np.append(extrapolated_data,data)
        data_p_exp_transf = fs.transform(data_p_exp)
        data_p_exp_invtransf = fs.invtransform(data_p_exp_transf)

        #count, bins, ignored = plt.hist(data_p_exp, 30, normed=True, alpha= 0.5, color="blue")
        plt.hist(data_p_exp_transf, 30, normed=True)
        #plt.hist(data_p_exp_invtransf, bins, normed=True, alpha = 0.5, color = "red")
        #plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (bins - mu)**2 / (2 * sigma**2) ), linewidth=2, color='r')


if False:
    # Testing 2 D operation
    mu = [ 0, -5, 20]
    sigma = [1, 2, 2]
    data = np.random.normal(mu[0], sigma[0], n_points)
    for i_feat in range(1,len(mu)): data = np.c_[data, np.random.normal(mu[i_feat], sigma[i_feat], n_points)]

    fs.fit(data)
    data_transf = fs.transform(data)
    data_invtransf = fs.invtransform(data_transf)

    i_plot = 2

    #count, bins, ignored = plt.hist(data, 30, normed=True)
    #plt.hist(data_transf, 30, normed=True)
    plt.hist(data_invtransf, 30, normed=True)
    #plt.plot(bins, 1/(sigma * np.sqrt(2 * np.pi)) * np.exp( - (bins - mu)**2 / (2 * sigma**2) ), linewidth=2, color='r')


plt.show()

