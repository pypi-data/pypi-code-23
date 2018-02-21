from scipy.interpolate import interp1d
from scipy.stats import norm
import numpy as np

class TransformedFunction:
    def __init__(self):
        pass
    def inv_cdf(self,n_points=100):
        print "This should be implemented in the daughter class"
        return None


class TransformedFunction_Uniform(TransformedFunction):

    def __init__(self, outofbounds_frac=0.5):
        self.outofbounds_frac = outofbounds_frac

    def inv_cdf(self, n_points=100):
        cdf_fractions =  np.array(range(1,1+n_points))/(1.+n_points)
        inv_cdf_points = cdf_fractions
        
        cdf_fractions_outofbounds  = np.array([ cdf_fractions[0]*(1. - self.outofbounds_frac)   ,  cdf_fractions[-1]+ cdf_fractions[0]*self.outofbounds_frac])
        inv_cdf_points_outofbounds = cdf_fractions_outofbounds
        return [inv_cdf_points, inv_cdf_points_outofbounds]


class TransformedFunction_Gauss(TransformedFunction):

    def __init__(self, mean=0, std_dev=1, outofbounds_frac=0.5):
        self.mean    = mean
        self.std_dev = std_dev
        self.outofbounds_frac = outofbounds_frac # The lower this is the more you flatten out the cdf equivalent curve and the more outofbounds points get downplayed as the most extreem SEEN example 

    def inv_cdf(self, n_points=100):
        # ppf is the inverse of cdf as shown by
        # norm.cdf(norm.ppf(0.95)) = 0.95
        # scipy.stats.norm.ppf = scipy.special.ndtri
        cdf_fractions =  np.array(range(1,1+n_points))/(1.+n_points)
        inv_cdf_points = norm.ppf(cdf_fractions, self.mean, self.std_dev)

        cdf_fractions_outofbounds  = np.array([ cdf_fractions[0]*(1. - self.outofbounds_frac)   ,  cdf_fractions[-1]+ cdf_fractions[0]*self.outofbounds_frac])        
        inv_cdf_points_outofbounds = norm.ppf(cdf_fractions_outofbounds, self.mean, self.std_dev)
        return [inv_cdf_points, inv_cdf_points_outofbounds]


def name_to_TransformedFunction(name):
    if name=="gauss" or name=="normal": return TransformedFunction_Gauss()
    elif name=="gauss01" or name=="normal01": return TransformedFunction_Gauss(0.5,1./12.) #Gaussian between 0 and 1
    elif name=="gauss-11" or name=="normal-11": return TransformedFunction_Gauss(0.,1./6.) #Gaussian between -1 and 1
    elif name=="unif" or name=="uniform": return TransformedFunction_Uniform()


def unique_mask(data):
    # data has to be sorted
    # when we get duplicates, use the "middle one"
    mask = np.zeros_like(data)
    last = np.inf
    n_same = 0 #start counting from 0
    duplicates_found = False
    for i, d in enumerate(data):
        if d == last:
            n_same += 1
            duplicates_found = True
        else:
            if duplicates_found:
                if n_same %2==0: i_dupl_used =     n_same/2
                else:            i_dupl_used = int(n_same/2) + np.random.choice(2)
                #print "i_dupl_used : ", i_dupl_used
                for n in range(n_same+1):
                    mask[i-n-1] =1
                mask[i-i_dupl_used-1] = 0
                n_same = 0
                duplicates_found = False
        last = d

    return mask


def aTransformedFunction_to_y(aTransformedFunction, n_points):
    if isinstance(aTransformedFunction, str):
        aTransformedFunction = name_to_TransformedFunction(aTransformedFunction)

    if isinstance(aTransformedFunction, TransformedFunction):
        y, y_outofbounds = aTransformedFunction.inv_cdf(n_points)
    else:
        y, y_outofbounds = np.array(aTransformedFunction[0]), np.array(aTransformedFunction[1])

    return y, y_outofbounds


class FunctionScaler:
    def __init__(self, aTransformedFunction, downplay_outofbounds_lower_n_range = None, downplay_outofbounds_upper_n_range = None, downplay_outofbounds_lower_set_point = None, downplay_outofbounds_upper_set_point = None):

        # downplay_outofbounds_lower_set_point overwrites downplay_outofbounds_lower_n_range

        self.aTransformedFunction = aTransformedFunction
        #assert downplay_outofbounds in ["not", "both", "lower", "upper"] #if off outliers matter a lot, if on they are just treated as the most extreme example seen. it can be true for lower and/or upper tails
        self.downplay_outofbounds_lower_n_range   = downplay_outofbounds_lower_n_range
        self.downplay_outofbounds_upper_n_range   = downplay_outofbounds_upper_n_range
        self.downplay_outofbounds_lower_set_point = downplay_outofbounds_lower_set_point
        self.downplay_outofbounds_upper_set_point = downplay_outofbounds_upper_set_point

    def fit(self, data):
        data = np.array(data)
        if data.ndim ==1 : data =data.reshape(-1,1)

        self.n_points = data.shape[0]
        self.n_feats   = data.shape[1]

        y_allD, y_outofbounds_allD = None, None

        if not isinstance(self.aTransformedFunction, list):
            y_allD, y_outofbounds_allD = aTransformedFunction_to_y(self.aTransformedFunction, self.n_points)


        if not isinstance(self.downplay_outofbounds_lower_n_range, list):
            self.downplay_outofbounds_lower_n_range = [self.downplay_outofbounds_lower_n_range]*self.n_feats

        if not isinstance(self.downplay_outofbounds_upper_n_range, list):
            self.downplay_outofbounds_upper_n_range = [self.downplay_outofbounds_upper_n_range]*self.n_feats


        if not isinstance(self.downplay_outofbounds_lower_set_point, list):
            self.downplay_outofbounds_lower_set_point = [self.downplay_outofbounds_lower_set_point]*self.n_feats

        if not isinstance(self.downplay_outofbounds_upper_set_point, list):
            self.downplay_outofbounds_upper_set_point = [self.downplay_outofbounds_upper_set_point]*self.n_feats


        self.LearnedFunctions = []
        self.LearnedInvFunctions = []


        for i_feats in range(self.n_feats):

            if y_allD is not None:
                y, y_outofbounds = y_allD, y_outofbounds_allD
            else:
                y, y_outofbounds = aTransformedFunction_to_y(self.aTransformedFunction[i_feats], self.n_points)


            data_1D = np.sort(data[:,i_feats])

            #data_1D_no_duplicates, y_no_duplicates = remove_duplicates(data_1D, y)
            #self.LearnedFunctions.append(interp1d( data_1D_no_duplicates , y_no_duplicates, kind='linear', fill_value="extrapolate"))
            #self.LearnedInvFunctions.append(interp1d( y_no_duplicates, data_1D_no_duplicates, kind='linear', fill_value="extrapolate"))
            self.makeLearnedFunctions(data_1D, y, y_outofbounds, i_feats)

    def makeLearnedFunctions(self, data, y, y_outofbounds, i_feats):
        #self.makeLearnedFunctions_mask(data_1D, y)        
        # data has to be sorted
        # when we get duplicates, use the "middle one"
        data_no_duplicates, y_no_duplicates = [], []


        if data[0] == data[-1]:
            self.LearnedFunctions.append(    lambda arg: arg)
            self.LearnedInvFunctions.append( lambda arg: arg)

        else:

            mask = np.zeros_like(data)
            last = np.inf
            n_same = 0 #start counting from 0
            duplicates_found = False
            for i, d in enumerate(data):
                if d == last:
                    test = np.inf
                    try: test = data[i-2]
                    except: pass
                    if test != np.inf:
                        data_no_duplicates = data_no_duplicates[:-1]
                        data_no_duplicates.append( 0.999*data[i] + 0.001*data[i-1])

                    n_same += 1
                    duplicates_found = True
                else:
                    if duplicates_found:
                        d_next = np.inf
                        try: d_next = data[i+1]
                        except: pass
                        #print "test"
                        if last != np.inf:
                            data_no_duplicates.append(0.999*data[i] + 0.001*data[i-1] )
                            y_no_duplicates.append(y[i])
                        else:
                            data_no_duplicates.append(data[i])
                            y_no_duplicates.append(y[i])
                        n_same = 0
                        duplicates_found = False
                    else:
                        data_no_duplicates.append(data[i])
                        y_no_duplicates.append(y[i])
                last = d


            if self.downplay_outofbounds_lower_set_point[i_feats] is not None:
                y_no_duplicates = np.r_[y_outofbounds[0], y_no_duplicates]
                data_no_duplicates  = np.r_[ self.downplay_outofbounds_lower_set_point[i_feats] , data_no_duplicates]  

            elif self.downplay_outofbounds_lower_n_range[i_feats] is not None: 
                y_no_duplicates = np.r_[y_outofbounds[0], y_no_duplicates]
                #data_no_duplicates  = np.r_[ data_no_duplicates[0] + (data_no_duplicates[0]- data_no_duplicates[1])/(y_no_duplicates[1]-y_no_duplicates[0])/self.n_points , data_no_duplicates]  # Extrapolate from last point
                data_no_duplicates  = np.r_[ data_no_duplicates[0] - (data_no_duplicates[-1]- data_no_duplicates[0])*self.downplay_outofbounds_lower_n_range[i_feats] , data_no_duplicates]  # Extrapolate from last point


            if self.downplay_outofbounds_upper_set_point[i_feats] is not None:
                y_no_duplicates = np.r_[y_no_duplicates, y_outofbounds[1]]
                data_no_duplicates  = np.r_[data_no_duplicates,  self.downplay_outofbounds_upper_set_point[i_feats] ]

            elif self.downplay_outofbounds_upper_n_range[i_feats] is not None: 
                y_no_duplicates = np.r_[y_no_duplicates, y_outofbounds[1]]
                #data_no_duplicates  = np.r_[data_no_duplicates, data_no_duplicates[-1] + ( data_no_duplicates[-1]- data_no_duplicates[-2])/(y_no_duplicates[-1]-y_no_duplicates[-2])/self.n_points  ]  # Extrapolate from last point
                data_no_duplicates  = np.r_[data_no_duplicates, data_no_duplicates[-1] + ( data_no_duplicates[-1]- data_no_duplicates[0])*self.downplay_outofbounds_upper_n_range[i_feats]  ]  # Extrapolate from last point


            #print "y_no_duplicates : ",  y_no_duplicates
            #print "data_no_duplicates : ", data_no_duplicates 
            self.LearnedFunctions.append(interp1d( data_no_duplicates , y_no_duplicates, kind='linear', fill_value="extrapolate"))
            self.LearnedInvFunctions.append(interp1d( y_no_duplicates, data_no_duplicates, kind='linear', fill_value="extrapolate"))




    def makeLearnedFunctions_mask(self, data_1D, y):
        data_1D_mask = unique_mask(data_1D)
        data_1D_no_duplicates, y_no_duplicates = (  np.ma.compressed(np.ma.array(data_1D, mask=data_1D_mask))   ,  np.ma.compressed(np.ma.array(y, mask=data_1D_mask)) )
        self.LearnedFunctions.append(interp1d( data_1D_no_duplicates , y_no_duplicates, kind='linear', fill_value="extrapolate"))
        self.LearnedInvFunctions.append(interp1d( y_no_duplicates, data_1D_no_duplicates, kind='linear', fill_value="extrapolate"))

    def transform(self, data):
        data = np.array(data)
        if data.ndim ==1 : data = data.reshape(-1,1)
        assert data.shape[1] == self.n_feats, "Need to have the same number of features as in training. data.shape[1] {}\t self.n_feats  {}".format(data.shape[1], self.n_feats) 

        for i_feats in range(self.n_feats):
            if i_feats == 0: data_trans = self.LearnedFunctions[i_feats](data[:, i_feats])
            else:
                data_trans_slice =self.LearnedFunctions[i_feats](data[:, i_feats])
                data_trans = np.c_[data_trans, data_trans_slice]


        return data_trans

    def fit_transform(self, data):
        self.fit(data)
        return self.transform(data)

    def invtransform(self, data):
        data = np.array(data)
        if data.ndim ==1 : data = data.reshape(-1,1)
        assert data.shape[1] == self.n_feats, "Need to have the same number of features as in training. data.shape[1] {}\t self.n_feats  {}".format(data.shape[1], self.n_feats)

        for i_feats in range(self.n_feats):
            if i_feats == 0: data_trans = self.LearnedInvFunctions[i_feats](data[:, i_feats])
            else:
                data_trans_slice =self.LearnedInvFunctions[i_feats](data[:, i_feats])
                data_trans = np.c_[data_trans, data_trans_slice]


        return data_trans



