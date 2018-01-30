# -*- coding: utf-8 -*-

"""
Wrapper around the python requests module for ease of interaction with all
CloudCIX services

Basic usage: ``cloudcix.api.<application>.<service>.<method>``

More detailed usage information will be available under each of the above terms

To see even more details about the API you can visit our
`HTTP API Reference <https://docs.cloudcix.com/>`_

To see more information about the various methods (list, read, etc.), see the
:doc:`client_reference` page

For examples of a call for each of these methods, see the :doc:`examples` page

.. warning:: Some applications and/or services are private and can only be used
  by Users in the CloudCIX Member.

  These are still documented here but will be marked clearly
"""

from cloudcix.client import Client


class app_manager:
    """
    The App Manager Application is a software system that manages CloudCIX Apps

    It allows Users to select and use apps, and allows Administrators to select
    which apps to deploy and give permissions to other Users.

    Basic usage: ``cloudcix.api.app_manager.<service>.<method>``

    **Services**

    - **App**
        - An App is a web Application available through CloudCIX website
        - Basic usage: ``cloudcix.api.app_manager.app.<method>``
        - Available Methods
            - ``cloudcix.api.app_manager.app.list``
                - Return a list of all Apps available.
            - ``cloudcix.api.app_manager.app.create``
                - Create a new App
            - ``cloudcix.api.app_manager.app.read``
                - Returns an App and its details if the Member invoking this
                  method has the App associated
            - ``cloudcix.api.app_manager.app.update``
                - Update an App
            - ``cloudcix.api.app_manager.app.delete``
                - Delete an App

    - **App Member Link**
        - An App Member Link is an association between a Member and an App they
          are allowed to use
        - Basic usage: ``cloudcix.api.app_manager.app_member.<method>``
        - Available Methods
            - ``cloudcix.api.app_manager.app_member.create``
                - Create a link between the Member calling the method and the
                  selected App
            - ``cloudcix.api.app_manager.app_member.delete``
                - Delete a link between the Member calling the method and the
                  selected App

    - **Menu Item**
        - This service provides methods to interact with an App's Menu Items
        - Basic Usage: ``cloudcix.api.app_manager.app_menu.<method>``
        - Available Methods
            - ``cloudcix.api.app_manager.app_menu.list``
                - Returns a list of Menu Items that belong to a given App.
                - This list will be filtered based on the permissions of the
                  User making the request
            - ``cloudcix.api.app_manager.app_menu.create``
                - Alows the User to create a menu item within a given App
            - ``cloudcix.api.app_manager.app_menu.read``
                - Returns a Menu Item with all its details
            - ``cloudcix.api.app_manager.app_menu.update``
                - Allows the User to update the details of the Menu Item
            - ``cloudcix.api.app_manager.app_menu.delete``
                - Allows the User to Delete a Menu Item from a given App

    - **Menu Item User Link**
        - An App Menu Item User Link is an association between a User and a
          Menu Item they're allowed to use/see
        - Basic Usage: ``cloudcix.api.app_manager.menu_item_user.<method>``
        - Available Methods:
            - ``cloudcix.api.app_manager.menu_item_user.list``
                - Returns a list of Menu Item IDs that the given User has
                  associated.
                - These items define the front end permissions for the given
                  User
            - ``cloudcix.api.app_manager.menu_item_user.update``
                - Updates the front end permissions for a given User
                - Only Administrators from the same Member are able to run this
                  method
    """
    _application_name = 'AppManager'

    app = Client(
        application=_application_name,
        service_uri='App/'
    )
    app_member = Client(
        application=_application_name,
        service_uri='App/{idApp}/Member/'
    )
    app_menu = Client(
        application=_application_name,
        service_uri='App/{idApp}/MenuItem/'
    )
    menu_item_user = Client(
        application=_application_name,
        service_uri='MenuItem/User/{idUser}/'
    )


class asset:
    """
    The Asset Application enables the management of Assets owned by a Member.

    Examples of Assets are buildings, machinery, furniture, vehicles, etc.

    Basic Usage: ``cloudcix.api.asset.<service>.<method>``

    **Services**

    - **Asset**
        - This service handles the Assets of a Member
        - Basic Usage: ``cloudcix.api.asset.asset.<method>``
        - Available Methods
            - ``cloudcix.api.asset.asset.list``
                - Returns a list of Assets owned by the acting Address of
                  the User who makes the request
            - ``cloudcix.api.asset.asset.create``
                - Allows a User to create a new Asset for its acting Address
            - ``cloudcix.api.asset.asset.read``
                - Returns a given Asset with all its details
            - ``cloudcix.api.asset.asset.update``
                - Allows a User to update an Asset for its acting Address

    - **Asset Transaction**
        - This service allows the User to create relationships between Assets
          and Financial Transactions
        - An Asset Transaction describes an operation or transaction on an
          Asset, which can be a purchase, a sale, or a depreciation
        - For a list of supported transactions, please see the Asset
          Application section of the
          `HTTP API Reference <https://docs.cloudcix.com/>`_
        - Basic Usage: ``cloudcix.api.asset.asset_transaction.<method>``
        - Available Methods
            - ``cloudcix.api.asset.asset_transaction.list``
                - Returns a list of Asset Transactions and their details
            - ``cloudcix.api.asset.asset_transaction.create``
                - Allows a User to create an association between an Asset and a
                  Financial Transaction, or depreciate an Asset, in which case
                  no transaction will be specified
            - ``cloudcix.api.asset.asset_transaction.read``
                - Returns an Asset Transaction with all its details

    - **Depreciation Type**
        - This service allows the User to generate Depreciation Types for
          their Assets
        - A Depreciation Type is the percentage of value an Asset will lose for
          a period time expressed in years until a certain date
        - Basic Usage: ``cloudcix.api.asset.depreciation_type.<method>``
        - Available Methods
            - ``cloudcix.api.asset.depreciation_type.list``
                - Returns a list of all Depreciation Types associated with the
                  Member of the User making the request
            - ``cloudcix.api.asset.depreciation_type.create``
                - Allows the User to create a new Depreciation Type
            - ``cloudcix.api.asset.depreciation_type.read``
                - Returns a given Depreciation Type with all its details
            - ``cloudcix.api.asset.depreciation_type.update``
                - Allows a User to update a given Depreciation Type
            - ``cloudcix.api.asset.depreciation_type.delete``
                - Allows a User to delete a Depreciation Type
                - A Depcreciation Type can only be deleted if it is no longer
                  associated with any Asset

    - **Off Rent**
        - This service allows the User to manage rentable Assets and return
          them from customers
        - The Asset must be set up as rentable in order to use this method.
        - The Asset must also be available and already on rent.
        - Every returned Asset will enter into the "for test" status
        - Basic Usage: ``cloudcix.api.asset.off_rent.<method>``
        - Available Methods
            - ``cloudcix.api.asset.off_rent.list``
                - Returns a list of Off Rent transactions
            - ``cloudcix.api.asset.off_rent.create``
                - Allows the User to create a record of an Asset being
                  returned from a customer.
                - These assets will automatically be entered into the
                  "for test" state
            - ``cloudcix.api.asset.off_rent.read``
                - Allows the User to get details about an Off Rent transaction
            - ``cloudcix.api.asset.off_rent.update``
                - Allows the User to update some details about an Off Rent
                  transaction

    - **Off Test**
        - This service allows the Users to manage their returned rentable
          Assets and take them out of the "for test" status
        - Basic Usage: ``cloudcix.api.asset.off_test.<method>``
        - Available Methods
            - ``cloudcix.api.asset.off_test.list``
                - Returns a list of Off Test transactions
            - ``cloudcix.api.asset.off_test.create``
                - Allows the User to create a record of an Asset that have
                  finished testing and can be made rentable again
            - ``cloudcix.api.asset.off_test.read``
                - Allows the User to get details about an Off Test transaction

    - **Rent**
        - This service allows the Users to manage rentable Assets and assign
          them to customers
        - The Asset must be set up as rentable in order to use this method
        - The Asset must also be available for rent, and not being tested or
          rented to another customer
        - Basic Usage: ``cloudcix.api.asset.rent.<method>``
        - Available Methods
            - ``cloudcix.api.asset.rent.list``
                - Returns a list of Rent transactions
            - ``cloudcix.api.asset.rent.create``
                - Allows the User to create a record of an Asset being
                  rented to a customer
            - ``cloudcix.api.asset.rent.read``
                - Allows the User to get details about a Rent transaction
            - ``cloudcix.api.asset.rent.update``
                - Allows the User to update some details about a Rent
                  transaction
                - The details can only be changed if at least one of the
                  associated Assets is still on rent.
    """
    _application_name = 'Asset'

    asset = Client(
        application=_application_name,
        service_uri='Asset/'
    )
    asset_transaction = Client(
        application=_application_name,
        service_uri='Asset/{idAsset}/Transaction/'
    )
    depreciation_type = Client(
        application=_application_name,
        service_uri='DepreciationType/'
    )
    off_rent = Client(
        application=_application_name,
        service_uri='OffRent/'
    )
    off_test = Client(
        application=_application_name,
        service_uri='OffTest/'
    )
    rent = Client(
        application=_application_name,
        service_uri='Rent/'
    )


class circuit:
    """
    The Circuit Application allows for the management of circuits and devices.

    Basic Usage: ``cloudcix.api.circuit.<service>.<method>``

    **Services**

    - **Circuit**
        - This service allows Users to manage their Circuits
        - A Circuit is a device installed in your active Address
        - Basic Usage: ``cloudcix.api.circuit.circuit.<method>``
        - Available Methods
            - ``cloudcix.api.circuit.circuit.list``
                - Returns a list of Circuits by owner, customer and supplier
                  based on the User's Address
            - ``cloudcix.api.circuit.circuit.create``
                - This method allows the User to add a Circuit to a Circuit
                  Class
            - ``cloudcix.api.circuit.circuit.read``
                - This method allows the User to get the details of a given
                  Circuit
                - Only owners, customers and suppliers are allowed to read a
                  Circuit
            - ``cloudcix.api.circuit.circuit.update``
                - Allows the User to update a Circuit
            - ``cloudcix.api.circuit.circuit.delete``
                - Allows the User to delete a Circuit
                - Note that the Circuit will no longer be available to update.
                - If a Circuit has been removed but the User wants to maintain
                  it in the list, it should be updated with a decommission date

    - **Circuit Class**
        - This service allows for the management of Circuit Classes
        - A Circuit Class is a classification for the Circuits
        - Basic Usage: ``cloudcix.api.circuit.circuit_class.<method>``
        - Available Methods
            - ``cloudcix.api.circuit.circuit_class.list``
                - Returns a list of Circuit Classes and their supported
                  Properties
            - ``cloudcix.api.circuit.circuit_class.create``
                - Allows the User to create a new Circuit Class for its Member
            - ``cloudcix.api.circuit.circuit_class.read``
                - Allows the User to get the details of a given Circuit Class
            - ``cloudcix.api.circuit.circuit_class.update``
                - Allows the User to update a Circuit Class.
                - If there are Circuits under the Circuit Class, new properties
                  cannot be required and old properties cannot be removed or
                  renamed


    - **Property Type**
        - This service is in place to offer a list of the supported Property
          Types
        - A Property Type is an identification of the expected input value for
          a given property.
        - Basic Usage: ``cloudcix.api.circuit.property_type.<method>``
        - Available Methods
            - ``cloudcix.api.circuit.property_type.list``
                - Returns a list of Property Types
    """
    _application_name = 'Circuit'

    circuit = Client(
        application=_application_name,
        service_uri='Circuit/'
    )
    circuit_class = Client(
        application=_application_name,
        service_uri='CircuitClass/'
    )
    property_type = Client(
        application=_application_name,
        service_uri='PropertyType/'
    )


class contacts:
    """
    The Contacts Application is a CRM application that exposes a REST API to
    manage a shared address book between Users in the same Member

    Contacts can be used as a sales and marketing tool or just as a general
    purpose address book.

    Basic Usage: ``cloudcix.api.contacts.<service>.<method>``

    **Services**

    - **Activity**
        - This service allows the user to manage the various Activities
        - An Activity is a sub category of an Activity Type
        - Each Activity has only one ActivityType but an ActivityType may have
          many Activities
        - Basic Usage: ``cloudcix.api.contacts.activity.<method>``
        - Available Methods
            - ``cloudcix.api.contacts.activity.list``
                - Returns a list of all Activities in your Member
                - If no Activities exist, a default list will be created and
                  returned
            - ``cloudcix.api.contacts.activity.create``
                - Creates one new Activity record for the selected Activity
                  Type
            - ``cloudcix.api.contacts.activity.read``
                - Returns an Activity with all its details
            - ``cloudcix.api.contacts.activity.update``
                - Updates an Activity record for the selected Activity Type
                - The properties can only be updated if there are no Campaign
                  records associated with the Activity
            - ``cloudcix.api.contacts.activity.delete``
                - Deletes an Activity record for the selected Activity Type
                - An Activity can only be deleted if there are no Campaigns
                  associated with it

    - **Activity Type**
        - This service allows the User to manage Activity Types
        - Basic Usage: ``cloudcix.api.contacts.activity_type.<method>``
        - Available Methods
            - ``cloudcix.api.contacts.activity_type.list``
                - Returns a list of supported Activity Types
            - ``cloudcix.api.contacts.activity_type.create``
                - Allows the User to create a new Activity Type record
            - ``cloudcix.api.contacts.activity_type.read``
                - Returns the selected Activity Type with all its details
            - ``cloudcix.api.contacts.activity_type.update``
                - Allows the User to update the details of an Activity Type
                  record
            - ``cloudcix.api.contacts.activity_type.delete``
                - Allows the User to delete one Activity Type record.
                - An Activity Type can only be deleted if there are no
                  Activities linked to the Activity Type

    - **Campaign**
        - This service allows for management of Campaigns
        - Campaigns are a many to many classification of Contacts
        - Basic Usage: ``cloudcix.api.contacts.campaign.<method>``
        - Available Methods
            - ``cloudcix.api.contacts.campaign.list``
                - Returns a list of all Campaigns associated with the Member of
                  the User calling this method
            - ``cloudcix.api.contacts.campaign.create``
                - Allows the User to create a new Campaign record
            - ``cloudcix.api.contacts.campaign.read``
                - Returns the details of one Campaign, including a list of
                  Contacts belonging to that Campaign
            - ``cloudcix.api.contacts.campaign.update``
                - Allows the User to update a Campaign record
            - ``cloudcix.api.contacts.campaign.delete``
                - Allows the User to delete one Campaign record, which includes
                  the links between the Campaign and any Contacts.

    - **Campaign Activity**
        - This service manages Campaign Activities related to a Campaign and an
          Activity
        - The Campaign Activity allows Users to organize Activities into
          further subcategories
        - Basic Usage: ``cloudcix.api.contacts.campaign_activity.<method>``
        - Available Methods
            - ``cloudcix.api.contacts.campaign_activity.list``
                - Return a list of Activities associated with a Campaign
            - ``cloudcix.api.contacts.campaign_activity.create``
                - Allows the User to create an Activity related to a Campaign
                  and an Activity Type.
            - ``cloudcix.api.contacts.campaign_activity.read``
                - Returns the details of a relation between a Campaign and an
                  Activity
            - ``cloudcix.api.contacts.campaign_activity.update``
                - Allows the User to update the relation between one Campaign
                  and one Activity
            - ``cloudcix.api.contacts.campaign_activity.delete``
                - Allows the User to delete an Activity related to a Campaign

    - **Campaign Contact**
        - This service manages the many to many links between Campaigns and
          Contacts
        - Basic Usage: ``cloudcix.api.contacts.campaign_contact.<method>``
        - Available Methods
            - ``cloudcix.api.contacts.campaign_contact.create``
                - Allows the User to create a relation between a Campaign and
                  a Contact
            - ``cloudcix.api.contacts.campaign_contact.update``
                - Allows the User to update the details of a relation between
                  a Campaign and a Contact
            - ``cloudcix.api.contacts.campaign_contact.delete``
                - Allows the User to delete a relation between a Campaign and a
                  Contact

    - **Contact**
        - This service allows for management of Contacts
        - Contacts are people that are potential customers
        - Basic Usage: ``cloudcix.api.contacts.contact.<method>``
        - Available Methods
            - ``cloudcix.api.contacts.contact.list``
                - Returns a list of all Contacts associated with the Member of
                  the User calling the method
            - ``cloudcix.api.contacts.contact.create``
                - Allows the User to create a new Contact record
            - ``cloudcix.api.contacts.contact.read``
                - Returns the details of a given Contact record including a
                  list of Campaigns and Groups to which that Contact belongs
            - ``cloudcix.api.contacts.contact.update``
                - Allows the User to update a Contact record
            - ``cloudcix.api.contacts.contact.delete``
                - Allows the User to delete a Contact record, including any
                  links between that Contact and any Campaigns or Groups

    - **Group**
        - This service allows for management of Groups
        - Groups are many to many classifications of Contacts
        - Basic Usage: ``cloudcix.api.contacts.group.<method>``
        - Available Methods
            - ``cloudcix.api.contacts.group.list``
                - Returns a list of all Groups belonging to the Member of the
                  User calling the method
            - ``cloudcix.api.contacts.group.create``
                - Allows the User to create a new Group record
            - ``cloudcix.api.contacts.group.read``
                - Returns a Group record with all its details
            - ``cloudcix.api.contacts.group.update``
                - Allows the User to update the details of a Group record
            - ``cloudcix.api.contacts.group.delete``
                - Allows the User to delete a Group record, including any links
                  between that Group and any Contact

    - **Group Contact**
        - This service manages the many to many links between Groups and
          Contacts
        - Basic Usage: ``cloudcix.api.contacts.group_contact.<method>``
        - Available Methods
            - ``cloudcix.api.contacts.group_contact.create``
                - Allows the User to create a relation between a Group and a
                  Contact
            - ``cloudcix.api.contacts.group_contact.delete``
                - Allows the User to delete a relation between a Group and a
                  Contact

    - **Opportunity**
        - This service allows for the management of Opportunity records
        - Opportunities are the estimated chances of getting into business with
          one more Contacts with its possible marketing value
        - Basic Usage: ``cloudcix.api.contacts.opportunity.<method>``
        - Available Methods
            - ``cloudcix.api.contacts.opportunity.list``
                - Return a list of all Opportunity records associated with the
                  User calling the method
            - ``cloudcix.api.contacts.opportunity.create``
                - Allows the User to create a new Opportunity record
            - ``cloudcix.api.contacts.opportunity.read``
                - Returns an Opportunity record along with all its details
            - ``cloudcix.api.contacts.opportunity.update``
                - Allows the User to update the details of an Opportunity
                  record
            - ``cloudcix.api.contacts.opportunity.delete``
                - Allows the User to delete an Opportunity record

    - **Opportunity Contact**
        - This service manages the many to many links between Opportunities
          and Contacts
        - Basic Usage: ``cloudcix.api.contacts.opportunity_contact.<method>``
        - Available Methods
            - ``cloudcix.api.contacts.opportunity_contact.create``
                - Allows the User to create a relation between an Opportunity
                  and a Contact
            - ``cloudcix.api.contacts.opportunity_contact.delete``
                - Allows the User to delete a relation between an Opportunity
                  and a Contact

    - **Opportunity History**
        - This service allows Users to log updates on an Opportunity, as well
          as sending emails to the associated Contacts
        - Basic Usage: ``cloudcix.api.contacts.opportunity_history.<method>``
        - Available Methods
            - ``cloudcix.api.contacts.opportunity_history.list``
                - Returns a list of history log entries for an Opportunity
            - ``cloudcix.api.contacts.opportunity_history.create``
                - Allows the User to create a new history log for an
                  Opportunity
    """
    _application_name = 'Contacts'

    activity = Client(
        application=_application_name,
        service_uri='ActivityType/{idActivityType}/Activity/'
    )
    activity_type = Client(
        application=_application_name,
        service_uri='ActivityType/'
    )
    campaign = Client(
        application=_application_name,
        service_uri='Campaign/'
    )
    campaign_activity = Client(
        application=_application_name,
        service_uri='Campaign/{idCampaign}/Activity/'
    )
    campaign_contact = Client(
        application=_application_name,
        service_uri='Campaign/{idCampaign}/Contact/'
    )
    contact = Client(
        application=_application_name,
        service_uri='Contact/'
    )
    group = Client(
        application=_application_name,
        service_uri='Group/'
    )
    group_contact = Client(
        application=_application_name,
        service_uri='Group/{idGroup}/Contact/'
    )
    opportunity = Client(
        application=_application_name,
        service_uri='Opportunity/'
    )
    opportunity_contact = Client(
        application=_application_name,
        service_uri='Opportunity/{idOpportunity}/Contact/'
    )
    opportunity_history = Client(
        application=_application_name,
        service_uri='Opportunity/{idOpportunity}/History/'
    )


class documentation:
    """
    .. warning:: This application is private and can only be used by Users
      within the CloudCIX company

    The Documentation Application reads the Repository database and
    generates responses to generate documentation via Swagger

    Basic Usage: ``cloudcix.api.documentation.<service>.<method>``

    **Services**

    - **Application**
        - This service manages the list of Applications in CloudCIX
        - Basic Usage: ``cloudcix.api.documenation.application.<method>``
        - Available Methods
            - ``cloudcix.api.documentation.application.list``
                - Returns a list of Applications
            - ``cloudcix.api.documentation.application.read``
                - Retrieves the information of an Application and generates
                  a file in a JSON format compatible with Swagger 2.0
    """
    _application_name = 'Documentation'

    application = Client(
        application=_application_name,
        service_uri='Application/'
    )


class financial:
    """
    Description

    Basic Usage:

    **Services**

    - **Service**
        - Description
        - Basic Usage
        - Available Methods
            - ``method``
                - Description
    """
    _application_name = 'Financial'

    account_purchase_adjustment = Client(
        application=_application_name,
        service_uri='AccountPurchaseAdjustment/'
    )
    account_purchase_adjustment_contra = Client(
        application=_application_name,
        service_uri='AccountPurchaseAdjustment/{idAddress}/Contra/'
    )
    account_purchase_debit_note = Client(
        application=_application_name,
        service_uri='AccountPurchaseDebitNote/'
    )
    account_purchase_debit_note_contra = Client(
        application=_application_name,
        service_uri='AccountPurchaseDebitNote/{idAddress}/Contra/'
    )
    account_purchase_invoice = Client(
        application=_application_name,
        service_uri='AccountPurchaseInvoice/'
    )
    account_purchase_invoice_contra = Client(
        application=_application_name,
        service_uri='AccountPurchaseInvoice/{idAddress}/Contra/'
    )
    account_purchase_payment = Client(
        application=_application_name,
        service_uri='AccountPurchasePayment/'
    )
    account_purchase_payment_contra = Client(
        application=_application_name,
        service_uri='AccountPurchasePayment/{idAddress}/Contra/'
    )
    account_sale_adjustment = Client(
        application=_application_name,
        service_uri='AccountSaleAdjustment/'
    )
    account_sale_adjustment_contra = Client(
        application=_application_name,
        service_uri='AccountSaleAdjustment/{idAddress}/Contra/'
    )
    account_sale_credit_note = Client(
        application=_application_name,
        service_uri='AccountSaleCreditNote/'
    )
    account_sale_credit_note_contra = Client(
        application=_application_name,
        service_uri='AccountSaleCreditNote/{idAddress}/Contra/'
    )
    account_sale_invoice = Client(
        application=_application_name,
        service_uri='AccountSaleInvoice/'
    )
    account_sale_invoice_contra = Client(
        application=_application_name,
        service_uri='AccountSaleInvoice/{idAddress}/Contra/'
    )
    account_sale_payment = Client(
        application=_application_name,
        service_uri='AccountSalePayment/'
    )
    account_sale_payment_contra = Client(
        application=_application_name,
        service_uri='AccountSalePayment/{idAddress}/Contra/'
    )
    allocation = Client(
        application=_application_name,
        service_uri='Allocation/'
    )
    business_logic = Client(
        application=_application_name,
        service_uri='BusinessLogic/'
    )
    cash_purchase_debit_note = Client(
        application=_application_name,
        service_uri='CashPurchaseDebitNote/'
    )
    cash_purchase_debit_note_contra = Client(
        application=_application_name,
        service_uri='CashPurchaseDebitNote/{idAddress}/Contra/'
    )
    cash_purchase_invoice = Client(
        application=_application_name,
        service_uri='CashPurchaseInvoice/'
    )
    cash_purchase_invoice_contra = Client(
        application=_application_name,
        service_uri='CashPurchaseInvoice/{idAddress}/Contra/'
    )
    cash_sale_credit_note = Client(
        application=_application_name,
        service_uri='CashSaleCreditNote/'
    )
    cash_sale_credit_note_contra = Client(
        application=_application_name,
        service_uri='CashSaleCreditNote/{idAddress}/Contra/'
    )
    cash_sale_invoice = Client(
        application=_application_name,
        service_uri='CashSaleInvoice/'
    )
    cash_sale_invoice_contra = Client(
        application=_application_name,
        service_uri='CashSaleInvoice/{idAddress}/Contra/'
    )
    creditor_account_history = Client(
        application=_application_name,
        service_uri='CreditorAccount/{id}/History/'
    )
    creditor_account_statement = Client(
        application=_application_name,
        service_uri='CreditorAccount/{id}/Statement/'
    )
    creditor_ledger_transaction = Client(
        application=_application_name,
        service_uri='CreditorLedger/Transaction/'
    )
    creditor_ledger_aged = Client(
        application=_application_name,
        service_uri='CreditorLedger/Aged/'
    )
    creditor_ledger_transaction_contra = Client(
        application=_application_name,
        service_uri='CreditorLedger/ContraTransaction/'
    )
    creditor_ledger = Client(
        application=_application_name,
        service_uri='CreditorLedger/'
    )
    debtor_account_history = Client(
        application=_application_name,
        service_uri='DebtorAccount/{id}/History/'
    )
    debtor_account_statement = Client(
        application=_application_name,
        service_uri='DebtorAccount/{id}/Statement/'
    )
    debtor_account_statement_log = Client(
        application=_application_name,
        service_uri='DebtorAccount/StatementLog/'
    )
    debtor_ledger_transaction = Client(
        application=_application_name,
        service_uri='DebtorLedger/Transaction/'
    )
    debtor_ledger_aged = Client(
        application=_application_name,
        service_uri='DebtorLedger/Aged/'
    )
    debtor_ledger_transaction_contra = Client(
        application=_application_name,
        service_uri='DebtorLedger/ContraTransaction/'
    )
    debtor_ledger = Client(
        application=_application_name,
        service_uri='DebtorLedger/'
    )
    journal_entry = Client(
        application=_application_name,
        service_uri='JournalEntry/'
    )
    nominal_account = Client(
        application=_application_name,
        service_uri='NominalAccount/'
    )
    nominal_account_history = Client(
        application=_application_name,
        service_uri='NominalAccount/{id}/History/'
    )
    nominal_account_type = Client(
        application=_application_name,
        service_uri='NominalAccountType/'
    )
    nominal_contra = Client(
        application=_application_name,
        service_uri='NominalContra/'
    )
    nominal_ledger_VIES_purchases = Client(
        application=_application_name,
        service_uri='NominalLedger/VIESPurchases/'
    )
    nominal_ledger_trial_balance = Client(
        application=_application_name,
        service_uri='NominalLedger/TrialBalance/'
    )
    nominal_ledger_purchases_by_country = Client(
        application=_application_name,
        service_uri='NominalLedger/PurchasesByCountry/'
    )
    nominal_ledger_sales_by_country = Client(
        application=_application_name,
        service_uri='NominalLedger/SalesByCountry/'
    )
    nominal_ledger_balance_sheet = Client(
        application=_application_name,
        service_uri='NominalLedger/BalanceSheet/'
    )
    nominal_ledger_profit_loss = Client(
        application=_application_name,
        service_uri='NominalLedger/ProfitLoss/'
    )
    nominal_ledger_VIES_sales = Client(
        application=_application_name,
        service_uri='NominalLedger/VIESSales/'
    )
    payment_method = Client(
        application=_application_name,
        service_uri='PaymentMethod/'
    )
    period_end = Client(
        application=_application_name,
        service_uri='PeriodEnd/'
    )
    tax_rate = Client(
        application=_application_name,
        service_uri='TaxRate/'
    )
    year_end = Client(
        application=_application_name,
        service_uri='YearEnd/'
    )


class helpdesk:
    """
    Description

    Basic Usage:

    **Services**

    - **Service**
        - Description
        - Basic Usage
        - Available Methods
            - ``method``
                - Description
    """
    _application_name = 'HelpDesk'

    iris_condition = Client(
        application=_application_name,
        service_uri='IRISCondition/'
    )
    iris_defect = Client(
        application=_application_name,
        service_uri='IRISDefect/'
    )
    iris_extended_condition = Client(
        application=_application_name,
        service_uri='IRISExtendedCondition/'
    )
    iris_ntf = Client(
        application=_application_name,
        service_uri='IRISNTF/'
    )
    iris_repair = Client(
        application=_application_name,
        service_uri='IRISRepair/'
    )
    iris_section = Client(
        application=_application_name,
        service_uri='IRISSection/'
    )
    iris_symptom = Client(
        application=_application_name,
        service_uri='IRISSymptom/'
    )
    item = Client(
        application=_application_name,
        service_uri=('Ticket/{idTransactionType}/'
                     '{transactionSequenceNumber}/Item/')
    )
    item_status = Client(
        application=_application_name,
        service_uri='ItemStatus/'
    )
    item_history = Client(
        application=_application_name,
        service_uri=('Ticket/{idTransactionType}/{transactionSequenceNumber}/'
                     'Item/{idItem}/History/')
    )
    item_part_used = Client(
        application=_application_name,
        service_uri=('Ticket/{idTransactionType}/{transactionSequenceNumber}/'
                     'Item/{idItem}/PartUsed/')
    )
    ticket = Client(
        application=_application_name,
        service_uri='Ticket/{idTransactionType}/'
    )
    ticket_history = Client(
        application=_application_name,
        service_uri=('Ticket/{idTransactionType}/'
                     '{transactionSequenceNumber}/History/')
    )
    status = Client(
        application=_application_name,
        service_uri='Status/'
    )
    reason_for_return = Client(
        application=_application_name,
        service_uri='ReasonForReturn/'
    )
    reason_for_return_translation = Client(
        application=_application_name,
        service_uri='ReasonForReturn/{idReasonForReturn}/Translation/'
    )
    ticket_question = Client(
        application=_application_name,
        service_uri='TicketQuestion/'
    )
    ticket_type = Client(
        application=_application_name,
        service_uri='TicketType/'
    )
    ticket_type_question = Client(
        application=_application_name,
        service_uri='TicketType/{id}/TicketQuestion/'
    )
    service_centre_logic = Client(
        application=_application_name,
        service_uri='ServiceCentreLogic/'
    )
    service_centre_warrantor = Client(
        application=_application_name,
        service_uri='ServiceCentre/{idAddress}/Warrantor/'
    )
    warrantor_logic = Client(
        application=_application_name,
        service_uri='WarrantorLogic/'
    )
    warrantor_service_centre = Client(
        application=_application_name,
        service_uri='Warrantor/{idAddress}/ServiceCentre/'
    )


class iaas:
    """
    Description

    Basic Usage:

    **Services**

    - **Service**
        - Description
        - Basic Usage
        - Available Methods
            - ``method``
                - Description
    """
    _application_name = 'DNS'

    aggregated_blacklist = Client(
        application=_application_name,
        service_uri='AggregatedBlacklist/'
    )
    allocation = Client(
        application=_application_name,
        service_uri='Allocation/'
    )
    asn = Client(
        application=_application_name,
        service_uri='ASN/'
    )
    blacklist = Client(
        application=_application_name,
        service_uri='CIXBlacklist/'
    )
    blacklist_source = Client(
        application=_application_name,
        service_uri='BlacklistSource/'
    )
    domain = Client(
        application=_application_name,
        service_uri='Domain/'
    )
    hypervisor = Client(
        application=_application_name,
        service_uri='Hypervisor/'
    )
    image = Client(
        application=_application_name,
        service_uri='Image/'
    )
    ipmi = Client(
        application=_application_name,
        service_uri='IPMI/'
    )
    ipaddress = Client(
        application=_application_name,
        service_uri='IPAddress/'
    )
    ip_validator = Client(
        application=_application_name,
        service_uri='IPValidator/'
    )
    location_hasher = Client(
        application=_application_name,
        service_uri='LocationHasher/'
    )
    nat = Client(
        application=_application_name,
        service_uri="NAT/"
    )
    nmap = Client(
        application=_application_name,
        service_uri='nmap/'
    )
    pool_ip = Client(
        application=_application_name,
        service_uri='PoolIP/'
    )
    project = Client(
        application=_application_name,
        service_uri='Project/'
    )
    record = Client(
        application=_application_name,
        service_uri='Record/'
    )
    recordptr = Client(
        application=_application_name,
        service_uri='RecordPTR/'
    )
    router = Client(
        application=_application_name,
        service_uri='Router/'
    )
    subnet = Client(
        application=_application_name,
        service_uri='Subnet/'
    )
    subnet_space = Client(
        application=_application_name,
        service_uri='Allocation/{idAllocation}/Subnet_space/'
    )
    virtualrouter = Client(
        application=_application_name,
        service_uri='VirtualRouter/'
    )
    vm = Client(
        application=_application_name,
        service_uri='VM/'
    )
    vm_history = Client(
        application=_application_name,
        service_uri="VMHistory/"
    )
    vm_ipaddress = Client(
        application=_application_name,
        service_uri='VM/{idVM}/IPAddress/'
    )
    vpn_tunnel = Client(
        application=_application_name,
        service_uri="VPNTunnel/"
    )
    whitelist = Client(
        application=_application_name,
        service_uri='CIXWhitelist/'
    )


class membership:
    """
    Description

    Basic Usage:

    **Services**

    - **Service**
        - Description
        - Basic Usage
        - Available Methods
            - ``method``
                - Description
    """
    _application_name = 'Membership'
    address = Client(
        application=_application_name,
        service_uri='Address/'
    )
    address_link = Client(
        application=_application_name,
        service_uri='Address/{idAddress}/Link/'
    )
    country = Client(
        application=_application_name,
        service_uri='Country/'
    )
    currency = Client(
        application=_application_name,
        service_uri='Currency/'
    )
    department = Client(
        application=_application_name,
        service_uri='Member/{idMember}/Department/'
    )
    language = Client(
        application=_application_name,
        service_uri='Language/'
    )
    member = Client(
        application=_application_name,
        service_uri='Member/'
    )
    member_link = Client(
        application=_application_name,
        service_uri='Member/{idMember}/Link/'
    )
    notification = Client(
        application=_application_name,
        service_uri='Address/{idAddress}/Notification/'
    )
    profile = Client(
        application=_application_name,
        service_uri='Member/{idMember}/Profile/'
    )
    subdivision = Client(
        application=_application_name,
        service_uri='Country/{idCountry}/Subdivision/'
    )
    team = Client(
        application=_application_name,
        service_uri='Member/{idMember}/Team/'
    )
    territory = Client(
        application=_application_name,
        service_uri='Member/{idMember}/Territory/'
    )
    timezone = Client(
        application=_application_name,
        service_uri='Timezone/'
    )
    transaction_type = Client(
        application=_application_name,
        service_uri='TransactionType/'
    )
    user = Client(
        application=_application_name,
        service_uri='User/'
    )


class reporting:
    """
    Description

    Basic Usage:

    **Services**

    - **Service**
        - Description
        - Basic Usage
        - Available Methods
            - ``method``
                - Description
    """
    _application_name = 'Reporting'

    export = Client(
        application=_application_name,
        service_uri='Export/'
    )
    package = Client(
        application=_application_name,
        service_uri='Package/'
    )
    report = Client(
        application=_application_name,
        service_uri='Report/'
    )
    report_template = Client(
        application=_application_name,
        service_uri='ReportTemplate/'
    )


class repository:
    """
    Description

    Basic Usage:

    **Services**

    - **Service**
        - Description
        - Basic Usage
        - Available Methods
            - ``method``
                - Description
    """
    _application_name = 'SupportFramework'

    application = Client(
        application=_application_name,
        service_uri='Member/{idMember}/Application/'
    )
    dto = Client(
        application=_application_name,
        service_uri='DTO/'
    )
    dto_parameter = Client(
        application=_application_name,
        service_uri='DTO/{idDTO}/Parameter/'
    )
    exception_code = Client(
        application=_application_name,
        service_uri='ExceptionCode/'
    )
    language_exception_code = Client(
        application=_application_name,
        service_uri='ExceptionCode/{exception_code}/Language/'
    )
    member = Client(
        application=_application_name,
        service_uri='Member/'
    )
    method = Client(
        application=_application_name,
        service_uri=('Member/{idMember}/Application/{idApplication}/Service/'
                     '{idService}/Method/'))
    method_parameter = Client(
        application=_application_name,
        service_uri=('Member/{idMember}/Application/{idApplication}/Service/'
                     '{idService}/Method/{idMethod}/Parameter/'))
    service = Client(
        application=_application_name,
        service_uri='Member/{idMember}/Application/{idApplication}/Service/')


class scm:
    """
    Description

    Basic Usage:

    **Services**

    - **Service**
        - Description
        - Basic Usage
        - Available Methods
            - ``method``
                - Description
    """
    _application_name = 'SCM'

    brand = Client(
        application=_application_name,
        service_uri='Brand/'
    )
    bin = Client(
        application=_application_name,
        service_uri='Bin/'
    )
    bin_sku = Client(
        application=_application_name,
        service_uri='Bin/{id}/SKU/'
    )
    # idSKUComponent should be passed as pk to resource methods
    critical_bom = Client(
        application=_application_name,
        service_uri='SKU/{idSKU}/BOM/'
    )
    # CriticalBOM for member returns all BOM records for the idMember
    # doing the request
    critical_bom_for_member = Client(
        application=_application_name,
        service_uri='SKU/BOM/'
    )
    manufactured_item = Client(
        application=_application_name,
        service_uri='ManufacturedItem/'
    )
    return_question = Client(
        application=_application_name,
        service_uri='ReturnQuestion/'
    )
    return_question_field_type = Client(
        application=_application_name,
        service_uri='ReturnQuestionFieldType/'
    )
    service_group = Client(
        application=_application_name,
        service_uri='ServiceGroup/'
    )
    sku = Client(
        application=_application_name,
        service_uri='SKU/'
    )
    sku_stock = Client(
        application=_application_name,
        service_uri='SKU/{idSKU}/Stock/'
    )
    sku_value = Client(
        application=_application_name,
        service_uri='SKU/{idSKU}/Value/'
    )
    sku_category = Client(
        application=_application_name,
        service_uri='SKUCategory/'
    )
    sku_category_return_question = Client(
        application=_application_name,
        service_uri='SKUCategory/{idSKUCategory}/ReturnQuestion/'
    )
    sku_stock_adjustment = Client(
        application=_application_name,
        service_uri='SKUStockAdjustment/'
    )


class scheduler:
    """
    Description

    Basic Usage:

    **Services**

    - **Service**
        - Description
        - Basic Usage
        - Available Methods
            - ``method``
                - Description
    """
    _application_name = 'Scheduler'

    execute_task = Client(
        application=_application_name,
        service_uri='Task/{idTask}/execute/'
    )
    task = Client(
        application=_application_name,
        service_uri='Task/'
    )
    task_log = Client(
        application=_application_name,
        service_uri='TaskLog/'
    )


class security:
    """
    Description

    Basic Usage:

    **Services**

    - **Service**
        - Description
        - Basic Usage
        - Available Methods
            - ``method``
                - Description
    """
    _application_name = 'Security'

    security_event = Client(
        application=_application_name,
        service_uri='SecurityEvent/'
    )
    security_event_logout = Client(
        application=_application_name,
        service_uri='SecurityEvent/{idUser}/Logout/'
    )


class training:
    """
    The Training Application exposes a REST API capable of managing Training
    records

    Basic Usage: ``cloudcix.api.training.<service>.<method>``

    **Services**

    - **Class**
        - This services allows for the management of Class records.
        - A Class record represents a Class in a Syllabus, and each one has a
          trainer assigned, as well as both a start and end date
        - Basic Usage: ``cloudcix.api.training.cls.<method>``
        - Available Methods
            - ``cloudcix.api.training.cls.list``
                - Return a list of all classes in a selected Syllabus
            - ``cloudcix.api.training.cls.create``
                - Allows the Use to create a new Class record
            - ``cloudcix.api.training.cls.read``
                - Returns the selected Class, along with its details
            - ``cloudcix.api.training.cls.update``
                - Allows the User to update the details of a Class record
            - ``cloudcix.api.training.cls.delete``
                - Allows the User to delete a Class record

    - **Student**
        - This service allows for the management of Student records.
        - Students are Users that are enrolled for one or more Classes
        - Basic Usage: ``cloudcix.api.training.student.<method>``
        - Available Methods
            - ``cloudcix.api.training.student.list``
                - Returns a list of Students in a selected Class
            - ``cloudcix.api.training.student.create``
                - Allows a User to create a Student record by adding a User to
                  a Class
            - ``cloudcix.api.training.student.read``
                - Returns the selected Student record with all its details
            - ``cloudcix.api.training.student.update``
                - Allows a User to update a Student's records.
                - Students can become Self Managed which means they can manage
                  themselves
            - ``cloudcix.api.training.student.delete``
                - Allows a User to delete a Student record

    - **Syllabus**
        - This service
        - Basic Usage: ``cloudcix.api.training.syllabus.<method>``
        - Available Methods
            - ``cloudcix.api.training.syllabus.list``
                - Returns a list of all Syllabus records available for a
                  Student
            - ``cloudcix.api.training.syllabus.create``
                - Allows a User to create a new Syllabus
            - ``cloudcix.api.training.syllabus.read``
                - Returns the details of the selected Syllabus
            - ``cloudcix.api.training.syllabus.update``
                - Allows a User to update the details of a given Syllabus
            - ``cloudcix.api.training.syllabus.delete``
                - Allows a User to delete a given Syllabus
    """
    _application_name = 'Training'

    cls = Client(
        application=_application_name,
        service_uri='Class/'
    )
    student = Client(
        application=_application_name,
        service_uri='Student/'
    )
    syllabus = Client(
        application=_application_name,
        service_uri='Syllabus/'
    )
