from core_ui import Core_UI
import dearpygui.dearpygui as dpg
from core_ui.Widgets.AuditView import AuditView
from BackSEODataHandler import getBackSEODataHandler
import os
import json
from Utils._Scraperz import CompareAudit, CustomThread
from Utils._GoogleResults import GoogleResults
from Utils import cleanFilename, sort_callback
import pickle
import random
import time


class CoreInspectResults(Core_UI):
    def __init__(self):
        self.bname = __name__
        self.inspectorList = list()
        self.oldList = list()
        self.inspectorRegistry = dpg.add_value_registry()
        self.searchAuditList = dpg.add_series_value(
            parent=self.inspectorRegistry, default_value="Pick a previous search"
        )
        self.myData = None
        self.searching = False
        # dpg.set_value(self.searchAuditList, self.inspectorList)
        self.bseoData = getBackSEODataHandler()
        self.load_data()

    def save_data(self, df):
        self.bseoData.saveData("Inspect", "SearchAudits", df)

    def load_data(self):
        self.inspectorList = list()
        for audit in os.listdir("output/search_results_audit"):
            if audit.endswith(".caudit"):
                self.inspectorList.append(audit.split(".caudit")[0])

    def update(self, piece, data):
        if piece == "fileupdate":
            self.load_data()
            dpg.configure_item(self.inspectPicker, items=self.inspectorList)

    def updateUData(self):
        self.actualKeyword, self.actualProxy, self.actualNumResult = dpg.get_values(
            (self.searchkeyword, self.searchProxy, self.numResult)
        )
        ud = (self.actualKeyword, self.actualProxy, self.actualNumResult, "Editor")
        dpg.set_item_user_data(self.searchkeyword, ud)
        dpg.set_item_user_data(self.searchProxy, ud)
        dpg.set_item_user_data(self.numResult, ud)
        dpg.set_item_user_data(self.searchButton, ud)

        if self.oldList == self.inspectorList:
            return
        else:
            self.oldList = self.inspectorList.copy()
            dpg.configure_item(self.inspectPicker, items=self.inspectorList)

    def _create_menu(self, parent, before):
        return 0

    def __binit__(self):
        pass

    def _create_tab(self, parent, plug):
        with dpg.tab(
            label="Inspect Results", parent=parent, before=plug
        ) as self.theTab:
            with dpg.group() as self.inspectResultscw:
                with dpg.group(horizontal=True):
                    dpg.add_text("Keyword: ")
                    self.searchkeyword = dpg.add_input_text(
                        label="",
                        hint="Enter a Keyword",
                        width=dpg.get_viewport_width() / 6,
                        callback=self.startSearch,
                        on_enter=True,
                    )
                    dpg.add_spacer(width=dpg.get_viewport_width() / 4)
                    dpg.add_text("Proxy: ")
                    self.searchProxy = dpg.add_input_text(
                        label="",
                        hint="http://your_user:your_password@your_proxy_url:your_proxy_port",
                        callback=self.startSearch,
                        width=200,
                        on_enter=True,
                    )
                    self.doSCreenButton = dpg.add_button(
                        label="Create Report",
                        callback=self.createSearchReport,
                        enabled=True,
                    )
                with dpg.group(
                    horizontal=True, label="Search URL Group"
                ) as self.searchurlgroup:
                    dpg.add_text(
                        "# Results:",
                    )
                    self.numResult = dpg.add_input_int(
                        width=dpg.get_viewport_width() / 6,
                        min_value=1,
                        max_value=100,
                        default_value=10,
                        min_clamped=True,
                        max_clamped=True,
                        step=0,
                        step_fast=0,
                    )
                    # with dpg.child_window(autosize_x=True) as self.inspectSearchcw:
                    dpg.add_spacer(width=dpg.get_viewport_width() / 6)
                    dpg.add_text("Previous Searches:")
                    self.inspectPicker = dpg.add_combo(
                        self.inspectorList, callback=self.inspectAudit, width=300
                    )
                self.searchButton = dpg.add_button(
                    label="Search", callback=self.startSearch, enabled=True
                )
            self.auditView = AuditView(self.theTab)
        return self.theTab

    def loadingIndicator(self):
        # loader 1
        while self.searching:
            incmt = random.random()
            start = dpg.get_value(self.bseoData.loader2)
            curup = incmt

            settz = start + curup
            if settz > 1.0:
                settz = 1.0
            dpg.set_value(self.bseoData.loader1, settz)
            if settz == 1.0:
                dpg.set_value(self.bseoData.loader1, 0.0)
            time.sleep(random.Random().randint(1, 10) / 50)
        while settz < 1.0:
            settz += 0.05
            dpg.set_value(self.bseoData.loader1, settz)
            time.sleep(0.08)

    def startSearch(self, *args, **kwargs):
        if self.searching:
            return
        if dpg.get_value(self.searchkeyword) == "":
            return
        self.searching = True
        myT = CustomThread(target=self.loadingIndicator)
        myT.start()
        self.searchThread = CustomThread(target=self.doSearch)
        self.searchThread.start()

    def doSearch(self):
        self.updateUData()
        executor = self.bseoData.getPool()
        self.myData = GoogleResults(
            executor=executor,
            query=self.actualKeyword,
            proxy=self.actualProxy,
            numResults=self.actualNumResult,
        )
        self.audit = self.myData.search()
        self.saveSearch = CompareAudit(self.myData.audDict)
        fname = (
            cleanFilename(self.actualKeyword)
            .strip()
            .replace("\t", "")
            .replace("\n", "")
        )
        nfname = f"output/search_results_audit/{fname}{cleanFilename(str(self.actualNumResult))}.caudit"
        with open(nfname, "wb") as f:
            pickle.dump(self.audit, f, -1)
        self.update("fileupdate", self.saveSearch)
        self.auditView.build(self.audit)
        self.searching = False

    def inspectAudit(self, *args, **kwargs):
        with open(
            f"output/search_results_audit/{dpg.get_value(self.inspectPicker)}.caudit",
            "rb",
        ) as f:
            myj = pickle.load(f)
        self.audit = myj
        dpg.set_value(self.bseoData.strLoader2, dpg.get_value(self.inspectPicker))
        # print(f"building {self.audit}")
        self.auditView.build(self.audit)

    def _create_window(self):
        return 0

    def createSearchReport(self, keyword, client: str = "", clientSite: str = ""):
        width = dpg.get_viewport_width()
        height = dpg.get_viewport_height()
        w, h = (425, 425)
        tableWin = dpg.add_window(show=False, width=10000, height=10000)
        tblGrp = dpg.add_group(parent=tableWin)
        kwWin = dpg.add_window(show=False, width=10000, height=10000)
        kwGrp = dpg.add_group(parent=kwWin)
        barchartTable = dpg.add_table(
            header_row=True,
            sortable=True,
            row_background=True,
            callback=sort_callback,
            delay_search=False,
            clipper=False,
            sort_multi=True,
            resizable=False,
            inner_width=0,
            no_pad_innerX=True,
            no_pad_outerX=True,
            policy=dpg.mvTable_SizingFixedFit,
            parent=tblGrp,
            scrollY=False,
            scrollX=False,
        )
        kwTable = dpg.add_table(
            header_row=True,
            sortable=True,
            row_background=True,
            callback=sort_callback,
            delay_search=True,
            clipper=True,
            sort_multi=True,
            parent=kwGrp,
            resizable=False,
            inner_width=0,
            no_pad_innerX=True,
            no_pad_outerX=True,
            policy=dpg.mvTable_SizingFixedFit,
            scrollY=False,
            scrollX=False,
        )
        self.auditView.createTheTable(barchartTable, client, clientSite)
        kwstats = self.auditView.buildKWTable(kwTable)
        dpg.set_primary_window(self.real_primary_window, False)
        dpg.configure_item(self.real_primary_window, show=False)
        dpg.render_dearpygui_frame()
        tableImg = self.doScreenCap(tableWin, tblGrp, keyword, client, "scores")
        kwImg = self.doScreenCap(kwWin, kwGrp, keyword, client, "keywords")
        dpg.configure_item(self.real_primary_window, show=True)
        dpg.set_viewport_width(width)
        dpg.set_viewport_height(height)
        dpg.set_primary_window(self.real_primary_window, True)
        self.bseoData.searchReportAdd(
            {
                "keyword": keyword,
                "client": client,
                "tblimg": tableImg,
                "kwstats": kwstats,
            },
            client,
        )

    def doScreenCap(self, tableWin, tblGrp, keyword, client, titlez):
        dpg.configure_item(tableWin, show=True)
        dpg.set_primary_window(tableWin, True)
        dpg.set_viewport_width(10000)
        dpg.set_viewport_height(10000)
        # dpg.configure_item(tableWin, no_scrollbar=True)
        dpg.render_dearpygui_frame()
        wi, he = dpg.get_item_rect_size(tblGrp)
        # print(f"{wi} {he} -- {dpg.get_item_rect_max(tblGrp)} -- {dpg.get_item_rect_min(tblGrp)} -- {dpg.get_item_rect_size(tblGrp)}")
        dpg.set_viewport_width(wi + 25)
        dpg.set_viewport_height(he + 100)
        dpg.render_dearpygui_frame()
        outpath = f"output/reports/searches/{cleanFilename(str(keyword))}/{cleanFilename(client)}"
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        imgName = f"{outpath}/{titlez}{time.strftime('%b_%d_%y', time.gmtime())}.png"
        dpg.render_dearpygui_frame()
        dpg.output_frame_buffer(imgName)
        dpg.render_dearpygui_frame()
        dpg.configure_item(tableWin, show=False)
        dpg.set_primary_window(tableWin, False)
        return imgName
