from scipy import stats
import pandas as pd
import numpy as np
import datetime
from datetime import timedelta
from . import settings
import logging
import logging.config
from .cbci_wrapper import Connect

logging.config.dictConfig(settings.LOGGING)

DISTRIBUTION_Q = settings.DATA_FILES_DICT['DISTRIBUTION_Q']
DISTRIBUTION_M = settings.DATA_FILES_DICT['DISTRIBUTION_M']


class Bills_Scorer(object):
    ''' Bills Scorer

        A class to calculate a profile score from R, F, C features
        derived from bills payment transactions.

        R : recency feature
        F : frequency feature
        C : consistency feature
    '''

    def __init__(self, w, rec):
        '''
        Initialize the historical feature scorer.

        Args:
            w (list of floats) : weight vector for (R, F, C)
            rec : Q if quarterly bill, M if monthly bill
        '''
        if rec == 'Q':
            self.dist = pd.read_csv(DISTRIBUTION_Q)
        elif rec == 'M':
            self.dist = pd.read_csv(DISTRIBUTION_M)
        self.w = w

    def score(self, trans):
        '''
        Transform R, F, C features into R, F, C scores

        Args:
            trans (list of floats) : list in the form of (R, F, C)

        Returns:
            profile score out of 100
        '''

        r = trans[0]
        f = trans[1]
        c = trans[2]

        fx = lambda x, d: stats.percentileofscore(d, x, kind='weak')

        rs, fs, cs = (fx(r, self.dist['R']),
                      fx(-f, -self.dist['F']),
                      fx(-c, -self.dist['C']))

        hs = self.w[0] * rs + self.w[1] * fs + self.w[2] * cs

        return np.round(hs, 2)


def biller_to_model(biller_code):
    '''
    Return M (Q) if biller is a monthly (quarterly) bill.
    Arg:
        billercode
    '''
    monthly = ['PWCOR', 'MWSIN', 'GLOBE']
    quarterly = ['PHLTH']
    if biller_code in monthly:
        return 'M'
    elif biller_code in quarterly:
        return 'Q'


def extract_R_raw(df, reference, rec):
    '''
    Extract the Recency feature from transactions df at the date reference.

    Args:
        df : dataframe with column 'TRANSACTION_DATE'
             containing the bill payment dates
        reference : datetime object
        rec : Q if quarterly bill, M if monthly bill

    Returns:
        R_raw : weighted sum of the number of transactions in the last
                6 mos, last year, last two years in the case of monthly
                payments. For quarterly payments,
                only consider the last year and last two years.
    '''

    numtranslast6mos = (df['TRANSACTION_DATE']>=pd.to_datetime(reference-datetime.timedelta(days=180))).sum()
    numtranslastyr = (df['TRANSACTION_DATE']>=pd.to_datetime(reference-datetime.timedelta(days=360))).sum()
    numtranslast2yrs = (df['TRANSACTION_DATE']>=pd.to_datetime(reference-datetime.timedelta(days=720))).sum()
    if rec == 'M':
        R_raw = (1/6)*(1/24)*numtranslast2yrs + (2/6)*(1/12)*numtranslastyr + (3/6)*(1/6)*numtranslast6mos
    elif rec == 'Q':
        R_raw = (2/3)*(1/4)*numtranslastyr+ (1/3)*(1/8)*numtranslast2yrs
    return R_raw

def extract_FC_raw(df, rec):
    '''
    Extract the Frequency and Consistency features from transactions df.

    Args:
        df : dataframe with column 'TRANSACTION_DATE' containing the bill payment dates
        rec : Q if quarterly bill, M if monthly bill

    Returns:
        F_raw : average days bet payments minus the expected pattern
        C_raw : standard deviation of the distribution of days bet payments
    '''

    df = df.sort_values('TRANSACTION_DATE')
    diff = (df['TRANSACTION_DATE'] - df['TRANSACTION_DATE'].shift(1)).iloc[1:]
    if rec == 'M':
        pattern = 30
    elif rec == 'Q':
        pattern = 90
    F_raw = diff.mean().days - pattern
    C_raw = diff.std().days
    return F_raw, C_raw

def extract_RFC_raw(df, reference, rec):
    '''
    Extract the Recency, Frequency and Consistency features from transactions df at the date reference.

    Args:
        df : dataframe with column 'TRANSACTION_DATE' containing the bill payment dates
        reference : datetime object
        rec : Q if quarterly bill, M if monthly bill

    Returns:
        R_raw : raw recency
        F_raw : raw frequency
        C_raw : raw consistency
    '''

    df['TRANSACTION_DATE'] = pd.to_datetime(df['TRANSACTION_DATE'])
    R_raw = extract_R_raw(df, reference, rec)
    F_raw, C_raw = extract_FC_raw(df, rec)
    return R_raw, F_raw, C_raw

def transaction_to_score(trans, rec):
    '''
        Transform a dataframe of top-up transactions to the forecast score.

        Args:
            trans : dataframe with columns facevalue and date_created
            rec : Q if quarterly bill, M if monthly bill
        Returns:
            float : forecast score of trans
    '''

    logging.info("Grabbing Bills Score")
    bills_scorer = Bills_Scorer([1/3]*3, rec)
    rfc = extract_RFC_raw(trans, datetime.datetime(2016,1,1), rec)
    logging.info("Done calculating metrics")
    logging.info("Return Score")
    return bills_scorer.score(rfc)

def load_json(json_file):
    '''
        Load the JSON file and rename columns.

        Args:
            json_file : JSON file of an account's transactions
                        Four fields: acct #, amount, biller code, txn date
        Returns:
            jf : DataFrame with renamed columns
    '''

    jf = pd.DataFrame(json_file)
    jf.columns = ['BILLER_CODE', 'ACCOUNT_NUMBER', 'AMOUNT', 'TRANSACTION_DATE']
    jf['TRANSACTION_DATE'] = pd.to_datetime(jf['TRANSACTION_DATE']).dt.date
    jf.groupby('TRANSACTION_DATE')['AMOUNT'].sum().reset_index()
    return jf


def main(biller_code, account_no):
    logging.info("Loading JSON data")
    cbci_connect = Connect()
    jf = cbci_connect.get_transactions(biller_code=biller_code, account_no=account_no)
    trans = load_json(jf)
    logging.info("Transaction To Score")
    logging.info("{}: {}".format(biller_code, account_no))
    hs = transaction_to_score(trans, biller_to_model(biller_code))
    print("Your score is " + str(hs) + ".")
    return str(hs)


if __name__ == '__main__':
    main(biller_code="MWSIN", account_no="57699266")
