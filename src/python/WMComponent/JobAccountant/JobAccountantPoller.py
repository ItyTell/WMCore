#!/usr/bin/env python
"""
_JobAccountant_

Poll WMBS for complete jobs and process their framework job reports.
"""

__revision__ = "$Id: JobAccountantPoller.py,v 1.4 2009/11/06 22:13:15 sfoulkes Exp $"
__version__ = "$Revision: 1.4 $"

import time
import threading
import logging

from logging.handlers import RotatingFileHandler

from WMCore.WorkerThreads.BaseWorkerThread import BaseWorkerThread

from WMCore.Agent.Harness import Harness
from WMCore.DAOFactory import DAOFactory
from WMCore.ProcessPool.ProcessPool import ProcessPool

class JobAccountantPoller(BaseWorkerThread):
    def __init__(self, config):
        BaseWorkerThread.__init__(self)
        self.config = config
        return
    
    def setup(self, parameters):
        """
        _preInitialization_

        Instantiate the requisite number of accountant workers and create a
        processpool with them.  Also instantiate all the DAOs that we will use.
        """
        slaveInit = {"couchURL": self.config.JobStateMachine.couchurl,
                     "couchDBName": self.config.JobStateMachine.couchDBName}
        self.processPool = ProcessPool("JobAccountant.AccountantWorker",
                                       totalSlaves = self.config.JobAccountant.workerThreads,
                                       componentDir = self.config.JobAccountant.componentDir,
                                       config = self.config,
                                       slaveInit = slaveInit)

        myThread = threading.currentThread()
        daoFactory = DAOFactory(package = "WMCore.WMBS", logger = myThread.logger,
                                dbinterface = myThread.dbi)
        self.getJobsAction = daoFactory(classname = "Jobs.GetFWJRByState")
        return
    
    def algorithm(self, parameters):
        """
        _pollForJobs_

        Poll WMBS for jobs in the "Complete" state and then pass them to the
        ThreadPool so that they can be processed.  This will block until all
        jobs have been processed.
        """
        completeJobs = self.getJobsAction.execute(state = "complete")
        logging.info("algorithm(): %s" % completeJobs)        
        self.processPool.enqueue(completeJobs)
        self.processPool.dequeue(len(completeJobs))
        return
