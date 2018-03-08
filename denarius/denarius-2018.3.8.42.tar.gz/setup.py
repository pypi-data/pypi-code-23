#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

import setuptools

def main():

    setuptools.setup(
        name             = "denarius",
        version          = "2018.03.08.0042",
        description      = "currency and other utilities",
        long_description = long_description(),
        url              = "https://github.com/wdbm/denarius",
        author           = "Will Breaden Madden",
        author_email     = "wbm@protonmail.ch",
        license          = "GPLv3",
        packages         = [
                           "denarius"
                           ],
        install_requires = [
                           "beautifulsoup4",
                           "che_guevara_otp",
                           "currencyconverter",
                           "dataset",
                           "datavision",
                           "graphviz",
                           "krakenex",
                           "pandas",
                           "pymonzo",
                           "pypng",
                           "pyprel",
                           "pyqrcode",
                           "pytrends",
                           "propyte",
                           "selenium",
                           "sklearn"
                           ],
        scripts          = [
                           "buy_BTC_for_EUR_last_price_on_Kraken.py",
                           "create_paper_wallet.py",
                           "create_QR_codes_of_public_and_private_keys.py",
                           "denarius_graph_Bitcoin.py",
                           "denarius_loop_save_KanoPool.py",
                           "denarius_loop_save_Nanopool.py",
                           "denarius_loop_save_SlushPool.py",
                           "denarius_save_stock_prices.py",
                           "detect_transaction_RBS.py",
                           "get_account_balance_RBS.py",
                           "login_web_Kraken.py",
                           "login_web_LocalBitcoins.py",
                           "loop_display_arbitrage_data.py",
                           "loop_save_arbitrage_data_Kraken_LocalBitcoins_UK.py",
                           "loop_save_LocalBitcoins_values_to_database.py",
                           "loop_save_RBS_to_CSV.py",
                           "loop_save_Santander_to_CSV.py",
                           "print_Kraken_balances.py",
                           "print_Kraken_last_price_BTC_EUR.py",
                           "print_table_bank_account.py",
                           "web_display_arbitrage_data.py"
                           ]
    )

def long_description(
    filename = "README.md"
    ):

    if os.path.isfile(os.path.expandvars(filename)):
        try:
            import pypandoc
            long_description = pypandoc.convert_file(filename, "rst")
        except ImportError:
            long_description = open(filename).read()
    else:
        long_description = ""
    return long_description

if __name__ == "__main__":
    main()
