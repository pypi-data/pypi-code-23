"""
QuantGo services definitions
"""

EQUITIES_TAQ = {
                "name": "EQUITIES_TAQ",
                "bucket": "us-equity-taq",
                "type": "equities",
                "file_structure": 0
               }

EQUITIES_1MIN = {
                 "name": "EQUITIES_1MIN",
                 "bucket": "us-equity-1min",
                 "type": "equities",
                 "file_structure": 0
               }

EQUITIES_TRADES = {
                   "name": "EQUITIES_TRADES",
                   "bucket": "us-equity-trades",
                   "type": "equities",
                   "file_structure": 0
                   }

EQUITIES_1MIN_TRADES = {
                        "name": "EQUITIES_1MIN_TRADES",
                        "bucket": "us-equity-1min-trades",
                        "type": "equities",
                        "file_structure": 0
                        }

FUTURES_OLD_TAQ = {
                   "name": "FUTURES_OLD_TAQ",
                   "bucket": "us-futures-taq",
                   "type": "futures",
                   "file_structure": 1
                   }

FUTURES_OLD_1MIN = {
                    "name": "FUTURES_OLD_1MIN",
                    "bucket": "us-futures-1min",
                    "type": "futures",
                    "file_structure": 1
                    }

FUTURES_OLD_1MIN_TRADES = {
                           "name": "FUTURES_OLD_1MIN_TRADES",
                           "bucket": "us-futures-1min-trades",
                           "type": "futures",
                           "file_structure": 1
                           }

FUTURES_TAQ = {
               "name": "FUTURES_TAQ",
               "bucket": "us-futures-taq-%d",
               "type": "futures",
               "start_year": 2009,
               "file_structure": 2
               }

FUTURES_TRADES = {
                  "name": "FUTURES_TRADES",
                  "bucket": "us-futures-trades-%d",
                  "type": "futures",
                  "start_year": 2009,
                  "file_structure": 2
                  }

FUTURES_1MIN = {
                "name": "FUTURES_1MIN",
                "bucket": "us-futures-1min-taq-%d",
                "type": "futures",
                "start_year": 2009,
                "file_structure": 2
                }

FUTURES_1MIN_TRADES = {
                       "name": "FUTURES_1MIN_TRADES",
                       "bucket": "us-futures-1min-trades-%d",
                       "type": "futures",
                       "start_year": 2009,
                       "file_structure": 2
                       }

FUTURES_OPTIONS_TAQ = {
                       "name": "FUTURES_OPTIONS_TAQ",
                       "bucket": "us-futures-options-taq-%d",
                       "type": "futures",
                       "start_year": 2009,
                       "file_structure": 2
                       }

FUTURES_OPTIONS_TRADES = {
                          "name": "FUTURES_OPTIONS_TRADES",
                          "bucket": "us-futures-options-trades-%d",
                          "type": "futures",
                          "start_year": 2009,
                          "file_structure": 2
                          }

FUTURES_OPTIONS_1MIN = {
                        "name": "FUTURES_OPTIONS_1MIN",
                        "bucket": "us-futures-options-1min-taq-%d",
                        "type": "futures",
                        "start_year": 2009,
                        "file_structure": 2
                        }

FUTURES_OPTIONS_1MIN_TRADES = {
                               "name": "FUTURES_OPTIONS_1MIN_TRADES",
                               "bucket": "us-futures-options-1min-trades-%d",
                               "type": "futures",
                               "start_year": 2009,
                               "file_structure": 2
                               }

OPTIONS_TAQ = {
               "name": "OPTIONS_TAQ",
               "bucket": "us-options-taq-%d",
               "type": "options",
               "start_year": 2016,
               "file_structure": 3
               }

OPTIONS_TRADES = {
                  "name": "OPTIONS_TRADES",
                  "bucket": "us-options-trades-%d",
                  "type": "options",
                  "start_year": 2016,
                  "file_structure": 3
                  }

OPTIONS_1MIN = {
                "name": "OPTIONS_1MIN",
                "bucket": "us-options-1min-taq-%d",
                "type": "options",
                "start_year": 2016,
                "file_structure": 3
                }

OPTIONS_1MIN_TRADES = {
                       "name": "OPTIONS_1MIN_TRADES",
                       "bucket": "us-options-1min-trades-%d",
                       "type": "options",
                       "start_year": 2016,
                       "file_structure": 3
                       }