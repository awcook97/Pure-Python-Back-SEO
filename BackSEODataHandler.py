import os
import multiprocessing
from multiprocessing import Queue, Process, Lock
from multiprocessing.pool import Pool
from queue import Empty
import dearpygui.dearpygui as dpg
import json
from BackSEOSettings import BackSEOSettings
from SEO.Resources.ReportCreator import (
    createLocalReport,
    createSearchReport,
    createSitemapAuditReport,
    SEOAgency,
    SEOClient,
)
from typing import Dict, List


class BackSEODataHandler:
    pass
    """
     This handles all of the data in the Back SEO Application.
    """

    def __init__(self, job_queue: Queue, results_queue: Queue):
        self.job_queue = job_queue
        self.results_queue = results_queue
        self.savejQueue = Queue()
        self.saverQueue = Queue()
        self.updateall = False
        self.updateMessage = ("", "")
        self.vprestasks = dict()
        self.localReports: Dict[str, List[str]] = dict()
        self.searchReports: Dict[str, List[str]] = dict()
        self.siteAuditReports: Dict[str, List[str]] = dict()
        self.bseoObjects: Dict[str, object] = dict()
        self.bseoSaveObjects: Dict[str, object] = dict()
        # self.registry()

    def add_object(self, objectToAdd: object, name: str, saveState: bool = False):
        if saveState:
            self.bseoSaveObjects[name] = objectToAdd
        else:
            self.bseoObjects[name] = objectToAdd

    def saveData(self, dataCat, dataName, dataValue):
        if dataCat not in self.dataHolders:
            self.dataHolders[dataCat] = dict()
        self.dataHolders[dataCat][dataName] = dataValue
        with open("bseodata", "w") as f:
            json.dump(self.dataHolders, f, indent=4)
        self.updateall = True
        self.updateMessage = ("fileupdate", dataValue)

    def savenoupdate(self, dataCat, dataName, dataValue):
        if dataCat not in self.dataHolders:
            self.dataHolders[dataCat] = dict()
        self.dataHolders[dataCat][dataName] = dataValue
        with open("bseodata", "w") as f:
            json.dump(self.dataHolders, f, indent=4)

    def finishedUpdates(self):
        self.updateall = False

    def load(self):
        if os.path.exists("bseodata"):
            with open("bseodata", "r") as f:
                k = json.load(f)
            return k
        return dict()

    def loaddata(self, dataCat, dataName):
        if dataCat in self.dataHolders:
            if dataName in self.dataHolders[dataCat]:
                return self.dataHolders[dataCat][dataName]
            else:
                self.dataHolders[dataCat][dataName] = None
                return None
        else:
            self.dataHolders[dataCat] = dict()
            self.dataHolders[dataCat][dataName] = None
            return None

    def registry(self):
        self.dataHolders = self.load()
        self.register = dpg.add_value_registry()
        self.loader1 = dpg.add_float_value(
            parent=self.register, default_value=0.0, tag="SomeLameTag1"
        )
        self.loader2 = dpg.add_float_value(
            parent=self.register, default_value=0.0, tag="SomeLameTag2"
        )
        self.loader3 = dpg.add_float_value(
            parent=self.register, default_value=0.0, tag="SomeLameTag3"
        )
        self.strLoader1 = dpg.add_string_value(
            parent=self.register, default_value="FPS"
        )
        self.strLoader2 = dpg.add_string_value(
            parent=self.register, default_value="Current Inspect File"
        )
        dpg.set_viewport_resize_callback(getBackSEODataHandler().vpresize)

    def add_loader(self, loader: int, value: int):
        if loader == 1:
            loaded = "SomeLameTag1"
        elif loader == 2:
            loaded = "SomeLameTag2"
        elif loader == 3:
            loaded = "SomeLameTag3"
        else:
            return
        firstval = dpg.get_value(loaded)
        newVal = firstval + float(value / 100)
        if newVal > 1.0:
            newVal = 1.0
        dpg.set_value(loaded, newVal)

    def backEndSave(self, objectToSave):
        self.savejQueue.put(objectToSave)
        result = self.saverQueue.get()
        return result

    def vpresize(self):
        for cb, args in self.vprestasks.items():
            if args:
                cb(*args)
            else:
                cb()

    def addtovpresize(self, cb: callable, args=None):
        self.vprestasks[cb] = args

    def putIntoJobQueue(self, item):
        self.job_queue.put(item)

    def getFromResultsQueue(self, item):
        self.results_queue.get()

    def requestData(self, requestor, useQ: Queue):
        self.dataHolders[requestor] = useQ

    def sendData(self, result):
        requestor = result[0]
        if requestor in self.dataHolders:
            self.dataHolders[requestor].put(result)

    def getJobQ(self):
        return self.job_queue

    def getRQ(self):
        return self.results_queue

    def setPool(self, pool: Pool):
        self.pool = pool

    def getPool(self):
        return self.pool

    def setLock(self, lock):
        self.lock = lock

    def getLock(self):
        return self.lock

    def setSettings(self, backSEOSettings: BackSEOSettings):
        self.backSEOSettings: BackSEOSettings = backSEOSettings

    def getSettings(self) -> BackSEOSettings:
        return self.backSEOSettings

    def setAgency(self, agency: SEOAgency):
        self.agency: SEOAgency = agency

    def getAgency(self) -> SEOAgency:
        return self.agency

    def localReportAdd(self, report, client="General"):
        if client not in self.localReports:
            self.localReports[client] = list()
        self.localReports[client].append(createLocalReport(report))

    def searchReportAdd(self, report, client="General"):
        if not client:
            client = "General"
        if not report["client"]:
            report["client"] = "General"
        if client not in self.searchReports:
            self.searchReports[client] = list()
        self.searchReports[client].append(createSearchReport(report))

    def siteAuditReportAdd(self, report, client="General"):
        if not client:
            client = "General"
        if not report["clientName"]:
            report["clientName"] = "General"
        if client not in self.siteAuditReports:
            self.siteAuditReports[client] = list()
        self.siteAuditReports[client].append(createSitemapAuditReport(report))


jq = Queue()
rq = Queue()
theHandler = BackSEODataHandler(jq, rq)


def getBackSEODataHandler() -> BackSEODataHandler:
    return theHandler


# BackSEODataHandler.register('core', get_module('core'))
# BackSEODataHandler.register('core', get_module('core'))
# BackSEODataHandler.register('core', get_module('core'))
# BackSEODataHandler.register('core', get_module('core'))
