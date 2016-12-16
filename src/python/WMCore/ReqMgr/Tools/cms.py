#!/usr/bin/env python
#-*- coding: utf-8 -*-
#pylint: disable=
"""
File       : cms.py
Author     : Valentin Kuznetsov <vkuznet AT gmail dot com>
Description: CMS modules
"""
from __future__ import (division, print_function)

# system modules
import os
import time
from collections import defaultdict

from WMCore.Cache.GenericDataCache import MemoryCacheStruct
# CMS modules
from WMCore.ReqMgr.DataStructs.RequestStatus import REQUEST_STATE_LIST, REQUEST_STATE_TRANSITION
from WMCore.Services.SiteDB.SiteDB import SiteDBJSON
from WMCore.ReqMgr.Utils.url_utils import getdata
from WMCore.ReqMgr.Utils.utils import xml_parser

def next_status(status=None):
    "Return next ReqMgr status for given status"
    if status:
        if status in REQUEST_STATE_TRANSITION:
            return REQUEST_STATE_TRANSITION[status]
        else:
            return 'N/A'
    return REQUEST_STATE_LIST

class TagCollector(object):
    """
    Class which provides interface to CMS TagCollector web-service.
    Provides both Production and Development releases (anytype=1)
    """
    def __init__(self, url="https://cmssdt.cern.ch/SDT/cgi-bin/ReleasesXML?anytype=1"):
        self.url = url
        self.cache = os.path.join(os.getcwd(), '.tagcollector')

    def data(self):
        "Fetch data from tag collector or local cache"
        tstamp = time.time()
        if  os.path.isfile(self.cache) and (tstamp - os.path.getmtime(self.cache)) < 3600:
            data = open(self.cache, 'r').read()
        else:
            params = {}
            data = getdata(self.url, params, verbose=1, jsondecoder=False)
            with open(self.cache, 'w') as ostream:
                ostream.write(data)
        pkey = 'architecture'
        for row in xml_parser(data, pkey):
            yield row[pkey]

    def releases(self, arch=None):
        "Yield CMS releases known in tag collector"
        arr = []
        for row in self.data():
            if  arch:
                if  arch == row['name']:
                    for item in row['project']:
                        arr.append(item['label'])
            else:
                for item in row['project']:
                    arr.append(item['label'])
        return list(set(arr))

    def architectures(self):
        "Yield CMS architectures known in tag collector"
        arr = []
        for row in self.data():
            arr.append(row['name'])
        return list(set(arr))
    
    def releases_by_architecture(self):
        "returns CMS architectures and realease in dictionary format"
        arch_dict = defaultdict(list)
        for row in self.data():
            for item in row['project']:
                arch_dict[row['name']].append(item['label'])
        return arch_dict
        

# initialize TagCollector instance to be used in this module
TC = TagCollector()

def sites():
    "Return known CMS site list from SiteDB"
    try:
        # Download a list of all the sites from SiteDB, uses v2 API.
        sitedb = SiteDBJSON()
        sites = sorted(sitedb.getAllCMSNames())
    except Exception as exc:
        msg = "ERROR: Could not retrieve sites from SiteDB, reason: %s" % str(exc)
        raise Exception(msg)
    return sites

# create a site cache and pnn cache 2 hour duration
SITE_CACHE = MemoryCacheStruct(5200, sites)

def pnns():
    """
    Returns all PhEDEx node names, excluding Buffer endpoints
    """
    try:
        sitedb = SiteDBJSON()
        pnns = sorted(sitedb.getAllPhEDExNodeNames(excludeBuffer=True))
    except Exception as exc:
        msg = "ERROR: Could not retrieve PNNs from SiteDB, reason: %s" % str(exc)
        raise Exception(msg)
    return pnns

# create a site cache and pnn cache 2 hour duration
PNN_CACHE= MemoryCacheStruct(5200, pnns)

def site_white_list():
    "site white list, default all T1"
    t1_sites = [s for s in SITE_CACHE.getData() if s.startswith('T1_')]
    return t1_sites

def site_black_list():
    "site black list, default all T3"
    t3_sites = [s for s in SITE_CACHE.getData() if s.startswith('T3_')]
    return t3_sites

def lfn_bases():
    "Return LFN Base list"
    storeResultLFNBase = [
        "/store/backfill/1",
        "/store/backfill/2",
        "/store/data",
        "/store/mc",
        "/store/generator",
        "/store/relval",
        "/store/hidata",
        "/store/himc",
        "/store/results/analysisops",
        "/store/results/b_physics",
        "/store/results/b_tagging",
        "/store/results/b2g",
        "/store/results/e_gamma_ecal",
        "/store/results/ewk",
        "/store/results/exotica",
        "/store/results/forward",
        "/store/results/heavy_ions",
        "/store/results/higgs",
        "/store/results/jets_met_hcal",
        "/store/results/muon",
        "/store/results/qcd",
        "/store/results/susy",
        "/store/results/tau_pflow",
        "/store/results/top",
        "/store/results/tracker_dpg",
        "/store/results/tracker_pog",
        "/store/results/trigger"]
    return storeResultLFNBase

def lfn_unmerged_bases():
    "Return list of LFN unmerged bases"
    out = ["/store/unmerged", "/store/data", "/store/temp"]
    return out

def web_ui_names():
    "Return dict of web UI JSON naming conventions"
    maps = {
            "TimePerEvent": "TimePerEvent (seconds)",
            "OpenRunningTimeout": "OpenRunningTimeout (deprecated)",
            "SizePerEvent": "SizePerEvent (KBytes)",
            "Memory": "Memory (MBytes)",
            "BlockCloseMaxSize": "BlockCloseMaxSize (Bytes)",
            "SoftTimeout": "SoftTimeout (seconds)",
            }
#     maps = {"InputDataset": "Input dataset",
#             "IncludeParents": "Include parents",
#             "PrepID": "Optional Prep ID String",
#             "BlockBlacklist": "Block black list",
#             "RequestPriority": "Request priority",
#             "TimePerEvent": "Time per event (seconds)",
#             "RunWhitelist": "Run white list",
#             "BlockWhitelist": "Block white list",
#             "OpenRunningTimeout": "Open Running Timeout",
#             "DQLUploadURL": "DQM URL",
#             "DqmSequences": "DQM Sequences",
#             "SizePerEvent": "Size per event (KBytes)",
#             "ScramArch": "Architecture",
#             "EnableHarvesting": "Enable DQM Harvesting",
#             "DQMConfigCacheID": "DQM Config CacheID",
#             "Memory": "Memory (MBytes)",
#             "RunBlacklist": "Run black list",
#             "RequestString": "Optional request ID string",
#             "CMSSWVersion": "Software releases",
#             "DQMUploadURL":"DQM URL",
#             "DQMSequences": "DQM sequences",
#             "DataPileup": "Data pileup",
#             "FilterEfficiency": "Filter efficiency",
#             "GlobalTag": "Global tag",
#             "MCPileup": "MonteCarlo pileup",
#             "PrimaryDataset": "Parimary dataset",
#             "Acquisitionera": "Acquisition era",
#             "CmsPath": "CMS path",
#             "DBS": "DBS urls",
#             "ProcessingVersion": "Processing version",
#             "ProcessingString": "Processing string",
#             "RequestType": "Request type",
#             "ACDCDatabase": "ACDC database",
#             "ACDCServer": "ACDC server",
#             "CollectionName": "Collection name",
#             "IgnoredOutputModules": "Ignored output modules",
#             "InitialTaskPath": "Initial task path",
#             "KeepStepOneOutput": "Keep step one output",
#             "KeepStepTwoOutput": "Keep step two output",
#             "StepOneConfigCacheID": "Step one config cache id",
#             "StepOneOutputModuleName": "Step one output module name",
#             "StepThreeConfigCacheID": "Step three config cache id",
#             "StepTwoConfigCacheID": "Step two config cache id",
#             "StepTwoOutputModuleName": "Step two output module name",
#             "Sitewhitelist": "Site white list",
#             "Siteblacklist": "Site black list",
#             "Mergedlfnbase": "Merged LFN base",
#             "Maxrss": "Max RSS",
#             "Trustsitelists": "Trust site lists",
#             "Unmergedlfnbase": "Unmerged LFN base",
#             "Minmergesize": "Min merge size",
#             "Maxmergesize": "Max merge size",
#             "Maxmergeevents": "Max merge events",
#             "Maxvsize": "Maximum VSize",
#             "Blockclosemaxwaittime": "Block close max wait time",
#             "Blockclosemaxfiles": "Block close max files",
#             "Blockclosemaxevents": "Block close max events",
#             "Blockclosemaxsize": "Block close max size",
#             "Softtimeout": "Soft time out",
#             "Graceperiod": "Grace period"
#             }
    return maps

def dqm_urls():
    "Return list of DQM urls"
    urls = [
            "https://cmsweb.cern.ch/dqm/dev",
            "https://cmsweb.cern.ch/dqm/offline",
            "https://cmsweb.cern.ch/dqm/relval",
            "https://cmsweb-testbed.cern.ch/dqm/dev",
            "https://cmsweb-testbed.cern.ch/dqm/offline",
            "https://cmsweb-testbed.cern.ch/dqm/relval",
            ]
    return urls

def dbs_urls():
    "Return list of DBS urls"
    urls = []
    base = "https://cmsweb.cern.ch/dbs/prod/global/DBSReader/"
    for inst in ["prod", "phys01", "phys02", "phys03"]:
        urls.append(base.replace("prod", inst))
    return urls

def couch_url():
    "Return central couch url"
    url = "https://cmsweb.cern.ch/couchdb"
    return url

def releases(arch=None):
    "Return list of CMSSW releases"
    return TC.releases(arch)

def architectures():
    "Return list of CMSSW architectures"
    return TC.architectures()

def scenarios():
    "Return list of scenarios"
    slist = ["pp", "cosmics", "hcalnzs", "preprodmc", "prodmc"]
    return slist

def cms_groups():
    "Return list of CMS data-ops groups"
    groups = ["DATAOPS"]
    return groups

def dashboardActivities():
    "Return list of dashboard activities"
    activity = ['reprocessing', 'production', 'relval', 'harvesting',
                'storeresults', 'integration', 'test']
    return activity
