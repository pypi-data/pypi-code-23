from dataclay.util.MgrObject import ManagementObject


class Contract(ManagementObject):
    _fields = ["dataClayID",
               "namespace",
               "providerAccountName",
               "applicantsNames",
               "beginDate",
               "endDate",
               "publicAvailable",
               "interfacesInContractSpecs",
               ]
    _internal_fields = ["providerAccountID",
                        "namespaceID",
                        "applicantsAccountsIDs",
                        "interfacesInContract",
                        ]
