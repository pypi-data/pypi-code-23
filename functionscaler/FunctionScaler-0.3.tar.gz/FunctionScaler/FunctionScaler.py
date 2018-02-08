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

    def inv_cdf(self, n_points=100):
        inv_cdf_points = np.array(range(1,1+n_points))/(1.+n_points)
        return inv_cdf_points


class TransformedFunction_Gauss(TransformedFunction):

    def inv_cdf(self, n_points=100):
        # ppf is the inverse of cdf as shown by
        # norm.cdf(norm.ppf(0.95)) = 0.95
        # scipy.stats.norm.ppf = scipy.special.ndtri
        inv_cdf_points = norm.ppf( np.array(range(1,1+n_points))/(1.+n_points)  )
        return inv_cdf_points

def name_to_TransformedFunction(name):
    if name=="gauss" or name=="normal": return TransformedFunction_Gauss()
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

class FunctionScaler:
    def __init__(self, aTransformedFunction):
        if isinstance(aTransformedFunction, TransformedFunction):
            self.aTransformedFunction = aTransformedFunction
        elif isinstance(aTransformedFunction, str):
            self.aTransformedFunction = name_to_TransformedFunction(aTransformedFunction)
        else:
            self.aTransformedFunction = aTransformedFunction


    def fit(self, data):
        data = np.array(data)
        if data.ndim ==1 : data =data.reshape(-1,1)

        n_points = data.shape[0]
        self.n_feats   = data.shape[1]

        self.LearnedFunctions = []
        self.LearnedInvFunctions = []

        if isinstance(self.aTransformedFunction, TransformedFunction):
            y = self.aTransformedFunction.inv_cdf(n_points)
        else:
            y = np.array(self.aTransformedFunction)

        for i_feats in range(self.n_feats):

            data_1D = np.sort(data[:,i_feats])

            #data_1D_no_duplicates, y_no_duplicates = remove_duplicates(data_1D, y)
            #self.LearnedFunctions.append(interp1d( data_1D_no_duplicates , y_no_duplicates, kind='linear', fill_value="extrapolate"))
            #self.LearnedInvFunctions.append(interp1d( y_no_duplicates, data_1D_no_duplicates, kind='linear', fill_value="extrapolate"))
            self.makeLearnedFunctions(data_1D, y)

    def makeLearnedFunctions(self, data, y):
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


        for i_feats in range(self.n_feats):
            if i_feats == 0: data_trans = self.LearnedInvFunctions[i_feats](data[:, i_feats])
            else:
                data_trans_slice =self.LearnedInvFunctions[i_feats](data[:, i_feats])
                data_trans = np.c_[data_trans, data_trans_slice]


        return data_trans



