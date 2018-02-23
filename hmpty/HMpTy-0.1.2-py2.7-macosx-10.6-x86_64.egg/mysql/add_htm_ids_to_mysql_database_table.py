#!/usr/local/bin/python
# encoding: utf-8
"""
*Given a database connection, a name of a table and the column names for RA and DEC, generates ID for one or more HTM level in the table*

:Author:
    David Young

:Date Created:
    June 21, 2016
"""
################# GLOBAL IMPORTS ####################
import sys
import os
os.environ['TERM'] = 'vt100'
from fundamentals import tools


# OR YOU CAN REMOVE THE CLASS BELOW AND ADD A WORKER FUNCTION ... SNIPPET TRIGGER BELOW
# xt-worker-def

class add_htm_ids_to_mysql_database_table():
    """
    *The worker class for the add_htm_ids_to_mysql_database_table module*

    **Key Arguments:**
        - ``log`` -- logger
        - ``settings`` -- the settings dictionary

    **Usage:**
        .. todo::

            - add usage info
            - create a sublime snippet for usage

        .. code-block:: python 

            usage code   

    .. todo::

        - @review: when complete, clean add_htm_ids_to_mysql_database_table class
        - @review: when complete add logging
        - @review: when complete, decide whether to abstract class to another module
    """
    # Initialisation
    # 1. @flagged: what are the unique attrributes for each object? Add them
    # to __init__

    def __init__(
            self,
            log,
            settings=False,

    ):
        self.log = log
        log.debug("instansiating a new 'add_htm_ids_to_mysql_database_table' object")
        self.settings = settings
        # xt-self-arg-tmpx

        # 2. @flagged: what are the default attrributes each object could have? Add them to variable attribute set here
        # Variable Data Atrributes

        # 3. @flagged: what variable attrributes need overriden in any baseclass(es) used
        # Override Variable Data Atrributes

        # Initial Actions

        return None

    # 4. @flagged: what actions does each object have to be able to perform? Add them here
    # Method Attributes
    def get(self):
        """
        *get the add_htm_ids_to_mysql_database_table object*

        **Return:**
            - ``add_htm_ids_to_mysql_database_table``

        .. todo::

            - @review: when complete, clean get method
            - @review: when complete add logging
        """
        self.log.info('starting the ``get`` method')

        add_htm_ids_to_mysql_database_table = None

        self.log.info('completed the ``get`` method')
        return add_htm_ids_to_mysql_database_table

    # xt-class-method

    # 5. @flagged: what actions of the base class(es) need ammending? ammend them here
    # Override Method Attributes
    # method-override-tmpx
