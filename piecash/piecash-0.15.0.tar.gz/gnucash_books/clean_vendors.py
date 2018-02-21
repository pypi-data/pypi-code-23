
import shutil

from piecash import Invoice

#shutil.copy("invoices.gnucash", "test_vendor_exp.gnucash")

import piecash


with piecash.open_book("test_vendor_exp.gnucash", readonly=False) as book:
    for i, v in enumerate(book.customers):
        v.name = f"customer-{i}"
    for i, v in enumerate(book.vendors):
        v.name = f"vendor-{i}"

    #book.invoices[0].owner=book.vendors[0]
    #book.save()

with piecash.open_book("test_vendor_exp.gnucash", readonly=True) as book:
    for i,v in enumerate(book.vendors):
        print(v.name)
    for v in book.invoices:
        print(v.owner_guid)
        print(v.owner)
