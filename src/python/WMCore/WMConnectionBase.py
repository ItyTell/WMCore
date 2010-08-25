#!/usr/bin/env python
"""
_WMBSBase_

Generic methods used by all of the WMBS classes.
"""

__revision__ = "$Id: WMConnectionBase.py,v 1.6 2010/01/27 17:12:18 sfoulkes Exp $"
__version__ = "$Revision: 1.6 $"

import threading

from WMCore.Database.Transaction import Transaction
from WMCore.DAOFactory import DAOFactory

class WMConnectionBase:
    """
    Generic db connection and transaction methods used by all of the WMCore classes.
    """
    def __init__(self, daoPackage, logger=None, dbi=None):
        """
        ___init___

        Initialize all the database connection attributes and the logging
        attritbutes.  Create a DAO factory for given daoPackage as well. Finally,
        check to see if a transaction object has been created.  If none exists,
        create one but leave the transaction closed.
        """
        myThread = threading.currentThread()
        if not logger:
            logger = myThread.logger

        if not dbi:
            dbi = myThread.dbi

        myThread.daoFactory = DAOFactory(package = daoPackage,
                                         logger = logger,
                                         dbinterface = dbi)

        if "transaction" not in dir(myThread):
            myThread.transaction = Transaction(dbi)
            myThread.transaction.commit()
            
        return

    def getDBConn(self):
        """
        _getDBConn_

        Retrieve the database connection that is associated with the current
        dataabase transaction.
        It transaction exists, it will return connection 
        which that transaction belong to.
        This won't create the transaction if it doesn't exist, it will just return 
        None. 
        """
        myThread = threading.currentThread()

        if "transaction" not in dir(myThread):
            return None

        return myThread.transaction.conn
            
    def beginTransaction(self):
        """
        _beginTransaction_

        Begin a database transaction if one does not already exist.
        """
        myThread = threading.currentThread()

        if "transaction" not in dir(myThread):
            myThread.transaction = Transaction(myThread.dbi)
            return False
        
        if myThread.transaction.transaction == None:
            myThread.transaction.begin()
            return False

        return True

    def existingTransaction(self):
        """
        _existingTransaction_

        Return True if there is an open transaction, False otherwise.
        """
        myThread = threading.currentThread()

        if "transaction" not in dir(myThread):
            return False
        elif myThread.transaction.transaction != None:
            return True

        return False

    def commitTransaction(self, existingTransaction):
        """
        _commitTransaction_

        Commit a database transaction that was begun by self.beginTransaction().
        """
        if not existingTransaction:
            myThread = threading.currentThread()
            myThread.transaction.commit()
            
        return

    def daofactory(self, classname):
        """
        _daofactory_

        The DAOFactory object moved into the thread storage so that we can
        actually pickle objects that inherit from this (we don't want to
        pickle any database code). 
        """
        myThread = threading.currentThread()
        return myThread.daoFactory(classname = classname)
