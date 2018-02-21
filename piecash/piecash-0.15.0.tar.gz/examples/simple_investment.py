# coding=utf-8
from __future__ import unicode_literals

# from gnucash import Session, Account, Transaction, Split, GncNumeric
# import gnucash
from piecash import Account
from piecash import open_book


bookname = r"../gnucash_books/investment.gnucash"

with open_book(bookname,open_if_lock=True, echo=False) as b:
    veur = b.commodities(mnemonic="VEUR")
    eur = b.currencies(mnemonic="EUR")

    for acc in veur.accounts:
        print("{} account has a balance of {} and holds a quantity {} of {}".format(
            acc.name,
            # acc.currency,
            acc.get_balance(),
            acc.get_quantity(),
            acc.commodity))

    print("$"*100)
    for acc in eur.accounts:
        print("{} account has a balance of {} and holds a quantity {} of {}".format(
            acc.name,
            # acc.currency,
            acc.get_balance(),
            acc.get_quantity(),
            acc.commodity))
