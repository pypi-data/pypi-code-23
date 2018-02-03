from test_helper import midtrans, unittest

class TestTransaction(unittest.TestCase):

    # def test_create(self):
    #     transaction = midtrans.BankTransferTransaction({
    #         "payment_type": "bank_transfer",
    #         "bank_transfer": {
    #             "bank": "permata"
    #         },
    #         "transaction_details": {
    #             "order_id": "C17550",
    #             "gross_amount": 145000
    #         },
    #         "custom_field1": "custom field 1 content",
    #         "custom_field2": "custom field 2 content",
    #         "custom_field3": "custom field 3 content"
    #     })
    #     # self.assertEqual(transaction.charge(), False)
    #     responseTransaction = midtrans.Transaction({
    #         "status_code": "200",
    #         "status_message": "Success, Credit Card transaction is successful",
    #         "transaction_id": "1eae238a-cb9e-4f92-b284-aac8b39e4eab",
    #         "order_id": "C17550",
    #         "gross_amount": "145000.00",
    #         "payment_type": "bank_transfer",
    #         "transaction_time": "2018-01-28 20:06:27",
    #         "transaction_status": "pending",
    #         "fraud_status": "accept",
    #         'permata_va_number': '8778005797429288'
    #     })
    #     self.assertEqual(responseTransaction.get_status(), False)

    def test_charge_permata_va(self):
        transaction_data = {
            "payment_type": "bank_transfer",
            "bank_transfer": {
                # "bank": "permata!!"
                "va_number": "123132131321"
            },
            "transaction_details": {
                "order_id": "C17550",
                "gross_amount": 145000
            },
            # "custom_field1": "custom field 1 content",
            # "custom_field2": "custom field 2 content",
            # "custom_field3": "custom field 3 content"
        }
        transaction = midtrans.PermataVATransaction(transaction_data)
