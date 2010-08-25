#!/usr/bin/env python
"""
_AcquireFiles_

Oracle implementation of Subscription.GetAvailableFiles

Return a list of files that are available for processing.
Available means not acquired, complete or failed.
"""
__all__ = []
__revision__ = "$Id: GetAvailableFiles.py,v 1.9 2009/05/01 14:53:18 sryu Exp $"
__version__ = "$Revision: 1.9 $"

from WMCore.WMBS.MySQL.Subscriptions.GetAvailableFiles import \
     GetAvailableFiles as GetAvailableFilesMySQL

class GetAvailableFiles(GetAvailableFilesMySQL):
    
    def getSQLAndBinds(self, subscription, conn = None, transaction = None):
        sql = ""
        binds = {'subscription': subscription}
        
        sql = '''select count(valid), valid from wmbs_subscription_location
        where subscription = :subscription group by valid'''
        result = self.dbi.processData(sql, binds, 
                                      conn = conn, transaction = transaction)
        result = self.format(result)
        
        whitelist = False
        blacklist = False
        
        for i in result:
            # i is a tuple with count and valid, 0 = False
            if i[0] > 0 and i[1] == '0':
                blacklist = True
            elif i[0] > 0 and i[1] == '1':
                whitelist = True

        sql = """SELECT wff.fileid FROM wmbs_fileset_files wff 
                  INNER JOIN wmbs_subscription ws ON ws.fileset = wff.fileset 
                  INNER JOIN wmbs_file_location wfl ON wfl.fileid = wff.fileid
                  LEFT OUTER JOIN  wmbs_sub_files_acquired wa ON wa.fileid = wff.fileid
                  LEFT OUTER JOIN  wmbs_sub_files_failed wf ON wf.fileid = wff.fileid
                  LEFT OUTER JOIN  wmbs_sub_files_complete wc ON wc.fileid = wff.fileid
                  WHERE ws.id=:subscription AND wa.fileid is NULL 
                        AND wf.fileid is NULL AND wc.fileid is NULL    
              """
        
        if whitelist:
            sql += """ AND wfl.location IN (select location from wmbs_subscription_location wsl where
                        wsl.subscription=:subscription AND valid = 1)"""
        elif blacklist:
            sql += """ AND wfl.location NOT IN (select location from wmbs_subscription_location wsl where
                        wsl.subscription=:subscription AND valid = 0)"""
                
        return sql, binds
