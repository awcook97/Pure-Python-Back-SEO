# Editor.py
"""
TODO:	Relevance Score

"""
import os
from core_ui import Core_UI
import dearpygui.dearpygui as dpg
import certifi
import Utils
from Utils import search
import Utils._Scraperz
from Utils._Scraperz import CompareAudit
from core_ui.Widgets.ContentScore import CoreContentScore
from core_ui.Widgets.CheckBrowser import CheckBrowser
import pickle
import multiprocessing.pool


class CoreEditor(Core_UI):
    def __init__(self):
        self.bname = __name__
        self.valueKeywords = dict()
        self.editorRegistry = dpg.add_value_registry()
        self.usertext = dpg.add_string_value(parent=self.editorRegistry)
        self.contentScore = CoreContentScore(
            [
                ("Example", 2),
            ],
            10,
            10,
            12,
            self.usertext,
        )
        self.btnColors()

    def save_data(self, df):
        self.bseoData.saveData("Editor", "Searches", df)

    def load_data(self):
        pass

    def _create_menu(self, parent, before):
        return 0

    def _create_tab(self, parent, plug):
        with dpg.tab(
            label="Scraper and Editor", parent=parent, before=plug
        ) as self.theTab:
            self._makeTopScraperSection()
            self._makeArticleTextAndSHeaders()
            self._makeCommonKeywords()
            self._makeCEWin()
            self._makeEditWin()
        return self.theTab

    def update(self, piece, data):
        if piece == "search":
            self.myData, filename = data
            self.save_data(filename)
            self.addHeaders()
            self.addKWs()

    def updateUData(self):
        self.actualKeyword, self.actualProxy, self.actualNumResult = dpg.get_values(
            (self.searchkeyword, self.searchProxy, self.numResult)
        )
        ud = (self.actualKeyword, self.actualProxy, self.actualNumResult, "Editor")
        dpg.set_item_user_data(self.searchkeyword, ud)
        dpg.set_item_user_data(self.searchProxy, ud)
        dpg.set_item_user_data(self.searchButton, ud)

    def _makeTopScraperSection(self):
        with dpg.child_window(autosize_x=True, height=120) as self.topScraperSection:
            with dpg.group(horizontal=True):
                dpg.add_text("Keyword: ")
                self.searchkeyword = dpg.add_input_text(
                    label="",
                    hint="Enter a Keyword",
                    width=200,
                    callback=search,
                    on_enter=True,
                )
                dpg.add_text("Proxy: ")
                self.searchProxy = dpg.add_input_text(
                    label="",
                    hint="http://your_user:your_password@your_proxy_url:your_proxy_port",
                    callback=search,
                    on_enter=True,
                )
            with dpg.group(horizontal=True, tag="SearchEditGroup"):
                self.searchButton = dpg.add_button(
                    label="Search", callback=search, enabled=True
                )
                dpg.add_button(
                    label="Edit Search",
                    tag="editButton",
                    user_data=self.bname,
                    callback=self.editSearch,
                )
                with dpg.tooltip("editButton"):
                    dpg.add_text("Edit the keywords displayed in the current search.")
                self.numResult = dpg.add_input_int(
                    label="Number of Results",
                    width=125,
                    min_value=1,
                    max_value=100,
                    default_value=10,
                    min_clamped=True,
                    max_clamped=True,
                )
            with dpg.group(horizontal=True, tag="rcmdLengthAndOutline"):
                dpg.add_text("Recommended Length: ", tag="rcmdLengthText")
                self.adjRcmdText = dpg.add_text("0")
                dpg.add_text("Recommended # of Headers: ", tag="rcmdNumHeaders")
                self.adjRcmdHeaders = dpg.add_text("0")
                dpg.add_text("Best Readability: ")
                self.adjRcmdRead = dpg.add_text("12")

    def _makeArticleTextAndSHeaders(self):
        with dpg.child_window(
            autosize_x=True, height=425
        ) as self.articleTextAndSHeaders:
            with dpg.group(horizontal=True):
                self.articleText = dpg.add_input_text(
                    source=self.usertext,
                    height=400,
                    multiline=True,
                    user_data=self.bname,
                    callback=self.compare,
                    hint="Content Editor. Put your article here to compare it with the common keywords from the search below.",
                )
                with dpg.child_window(
                    label="Suggested Headers", tag="suggested_headers", height=400
                ) as self.suggested_headers:
                    dpg.add_text("Suggested Headers")

    def _makeCommonKeywords(self):
        with dpg.group(horizontal=True) as self.commonKeywords:
            with dpg.child_window(
                label="common keywords", autosize_y=True, width=-300
            ) as self.common_keyword_box:
                dpg.add_text("Common Keywords")
                with dpg.group() as self.common_keyword_group:
                    self.kwButtons = dict()
                    self.kwButtons["Example"] = dict()
                    self.kwButtons["Example"]["Button"] = dpg.add_button(
                        label=f"Example: 0/2"
                    )
                    self.kwButtons["Example"]["Num"] = 2
            with dpg.child_window(
                label="Content Score",
                tag="cwScrapContentScore",
                autosize_x=True,
                autosize_y=True,
            ) as self.cscorecwin:
                dpg.add_text("Content Score")
                self.contentScore.draw(self.cscorecwin)
                dpg.add_button(
                    label="Check Detected Keywords",
                    user_data=self.bname,
                    callback=self.cbScraperContentKeywords,
                    tag="btnScraperContentKeywords",
                )
                myBrowser = CheckBrowser(source=self.usertext, parent=self.cscorecwin)

    def _makeCEWin(self):
        with dpg.window(
            label="Content Editor Keywords",
            width=300,
            height=200,
            show=False,
            tag="cewinKeywords",
            pos=(
                dpg.get_viewport_width() / 2 - 300,
                dpg.get_viewport_height() / 2 - 200,
            ),
        ) as self.cewinKeywords:
            with dpg.group(horizontal=True):
                with dpg.child_window(width=275, autosize_y=True):
                    self.txtScraperContentKeywords = dpg.add_text("", wrap=0)
                # with dpg.child_window(autosize_x=True):
                # 	with dpg.group(horizontal=True):
                # 		dpg.add_text("Readability: ")
                # 		dpg.add_text("", tag="txtBSEOUIScraperReadability")
                # 	with dpg.group(horizontal=True):
                # 		dpg.add_text("Grade: ")
                # 		dpg.add_text("", tag="txtBSEOUIScraperGrade")
                # 	with dpg.group(horizontal=True):
                # 		dpg.add_text("Relevance Score: ")
                # 		dpg.add_text("", tag="txtBSEOUIScraperRelevancyScore")
                # 	with dpg.child_window(tag="cwCEOverUsed", width=-1, height=75):
                # 		dpg.add_text("All Good :)", tag="txtCEOverUsed")

    def _makeEditWin(self):
        with dpg.window(
            label="Edit Keywords",
            width=300,
            height=200,
            show=False,
            pos=(
                dpg.get_viewport_width() / 2 - 300,
                dpg.get_viewport_height() / 2 - 200,
            ),
        ) as self.editWindow:
            self.mainKeyword = dpg.add_input_text(
                label="Main Keyword", callback=self.loadEditKWs, on_enter=True
            )
            with dpg.group(horizontal=True):
                self.loadKWsButton = dpg.add_button(
                    label="Load Keywords",
                    user_data=self.bname,
                    callback=self.loadEditKWs,
                )
                self.saveKWsButton = dpg.add_button(
                    label="Save Keywords",
                    user_data=self.bname,
                    callback=self.saveEditKWs,
                )
                self.addKWButton = dpg.add_button(
                    label="Add Keyword", user_data=self.bname, callback=self.addKW
                )
            self.editTable = dpg.add_table(
                header_row=True,
                sortable=True,
                row_background=True,
                callback=Utils.sort_callback,
                delay_search=True,
                clipper=True,
                sort_multi=True,
            )
            dpg.add_table_column(label="Keyword", parent=self.editTable)
            dpg.add_table_column(label="Count", parent=self.editTable)
            dpg.add_table_column(label="Remove", parent=self.editTable)

    def addKW(self, *args, **kwargs):
        rand = dpg.generate_uuid()
        # print(rand)
        with dpg.table_row(parent=self.editTable) as self.editKWDict[f"{rand}"]:
            dpg.add_input_text(label="")
            dpg.add_input_int(label="")
            dpg.add_button(label="Remove", user_data=f"{rand}", callback=self.removeKW)
        # print(self.editKWDict)

    def saveEditKWs(self, *args, **kwargs):
        mykw = dpg.get_value(self.mainKeyword)
        self.fname = (
            Utils.cleanFilename(mykw).strip().replace("\t", "").replace("\n", "")
        )
        fname = self.fname
        nfname = f"output/custom/{fname}.ckw"
        kws = list()
        for i in dpg.get_item_children(self.editTable, 1):
            kw = dpg.get_item_children(i, 1)[0]
            num = dpg.get_item_children(i, 1)[1]
            kws.append((dpg.get_value(kw), dpg.get_value(num)))
        self.kwData["avgCommonKWs"] = kws
        kwsd = dict()
        kwsd["avgCommonKWs"] = kws
        open(nfname, "wb").write(pickle.dumps(kwsd, indent=4))

    def loadEditKWs(self, *args, **kwargs):
        mykw = dpg.get_value(self.mainKeyword)
        self.fname = (
            Utils.cleanFilename(mykw).strip().replace("\t", "").replace("\n", "")
        )
        fname = self.fname
        nfname = f"output/custom/{fname}.ckw"
        if not os.path.exists(nfname):
            nfname = f"output/search_results_audit/{fname}.caudit"
        dpg.delete_item(self.editTable, children_only=True)
        dpg.add_table_column(label="Keyword", parent=self.editTable)
        dpg.add_table_column(label="Count", parent=self.editTable)
        dpg.add_table_column(label="Remove", parent=self.editTable, no_sort=True)
        self.editKWDict = dict()
        if os.path.exists(nfname):
            try:
                with open(nfname, "rb") as f:
                    self.kwData = pickle.load(f)
                if "avgCommonKWs" in self.kwData:
                    kws = self.kwData["avgCommonKWs"]
                else:
                    kws = list()
                    self.kwData["avgCommonKWs"] = kws
            except:
                self.kwData = dict()
                return
        else:
            self.kwData = dict()
            return
        count = 0
        for kw, num in kws:
            with dpg.table_row(parent=self.editTable) as self.editKWDict[f"{count}"]:
                dpg.add_input_text(default_value=kw)
                dpg.add_input_int(default_value=num)
                dpg.add_button(
                    label="Remove", user_data=f"{count}", callback=self.removeKW
                )
            count += 1

    def removeKW(self, a, user_data, *args, **kwargs):
        try:
            # print(a, user_data)
            # print(self.editKWDict)
            # if len(args):
            # print(args)
            dpg.delete_item(self.editKWDict[user_data])
        except:
            pass

    def addHeaders(self):
        myC = self.myData
        if not myC.audits:
            return
        dpg.delete_item(self.suggested_headers, children_only=True)
        # print("hea")
        mainkw = myC.main_kw
        headers = list(set(myC.all_headings))
        superHeaders = list()
        parth = list()
        for h in headers:
            if mainkw in h:
                superHeaders.append(h)
            else:
                for word in mainkw.split(" "):
                    if word in h:
                        parth.append(h)
        superHeaders.extend(myC.common_headings)
        while len(list(set(superHeaders))) < myC.average_header:
            if len(parth):
                superHeaders.append(parth.pop())
            else:
                break
        for h in list(set(superHeaders)):
            dpg.add_button(
                label=h,
                tag=h,
                parent=self.suggested_headers,
                user_data=self.articleText,
                callback=popheader,
            )
        return

    def addKWs(self):
        myC = self.myData
        if not myC.audits:
            return
        # print("kws")
        myKWs = myC.avgCommonKWs
        numKWs = len(myC.avgCommonKWs)
        dpg.delete_item(self.common_keyword_group, children_only=True)
        if numKWs < 5:
            count = 0
            for kw, num in myC.all_keywords.items():
                myKWs.append(num)
                count += 1
                if count == 5:
                    break
        self.kwButtons = dict()
        theG = dpg.add_group(horizontal=True, parent=self.common_keyword_group)
        i = 0
        self.myKWs = myKWs
        self.contentScore.updateSources(0, self.myKWs)
        for kw, num in myKWs:
            self.kwButtons[kw] = dict()
            self.kwButtons[kw]["Button"] = dpg.add_button(
                label=f"{kw}: 0/{num}", parent=theG
            )
            self.kwButtons[kw]["Num"] = num
            i += 1
            if i == 5:
                i = 0
                theG = dpg.add_group(horizontal=True, parent=self.common_keyword_group)
        self.contentScore.updateSources(1, myC.average_header)
        self.contentScore.updateSources(2, myC.average_length)
        self.contentScore.updateSources(3, myC.bestReadability)
        dpg.configure_item(self.adjRcmdText, default_value=str(int(myC.average_length)))
        dpg.configure_item(
            self.adjRcmdHeaders, default_value=str(int(myC.average_header))
        )
        dpg.configure_item(
            self.adjRcmdRead, default_value=str(int(myC.bestReadability))
        )

    def _create_window(self):
        return 0

    def editSearch(self, *args, **kwargs):
        mykw = self.actualKeyword
        mynr = self.actualNumResult
        self.fname = (
            Utils.cleanFilename(mykw).strip().replace("\t", "").replace("\n", "")
        )
        fname = self.fname
        nfname = f"output/search_results_audit/{fname}{Utils.cleanFilename(str(mynr))}.caudit"
        if os.path.exists(nfname):
            self.myData = pickle.load(open(nfname, "rb"))
            # self.myData = CompareAudit.fromJson(nfname)
            self.addHeaders()
            self.addKWs()
        else:
            self.recKWs = list()
        dpg.set_value(self.mainKeyword, f"{mykw}{mynr}")
        dpg.configure_item(self.editWindow, show=True)
        self.loadEditKWs()

    def compare(self, *args, **kwargs):
        kwCounts = self.contentScore.updateSources(4, self.usertext)
        for kw, count in kwCounts.items():
            btn = self.kwButtons[kw]["Button"]
            num = self.kwButtons[kw]["Num"]
            n = int(num)
            c = int(count)
            dpg.configure_item(
                btn, label=f"{kw}: {str(int((count)))}/{str(int((num)))}"
            )
            if c >= n and c <= n + 2:
                dpg.bind_item_theme(btn, self.green_theme)
            elif c >= n + 2:
                dpg.bind_item_theme(btn, self.yellow_theme)
            elif c < n and c > 0:
                dpg.bind_item_theme(btn, self.blue_theme)
            else:
                dpg.bind_item_theme(btn, self.red_theme)

    def cbScraperContentKeywords(self, *args, **kwargs):
        myKws = Utils.get_keyword_count(dpg.get_value(self.usertext))
        myRstr = ""
        if not len(myKws):
            myRstr = "No keywords detected"
        else:
            for kw, count in myKws:
                myRstr += f"{kw}: {count}\n"
        dpg.configure_item(self.txtScraperContentKeywords, default_value=myRstr)
        dpg.configure_item(self.cewinKeywords, show=True)

    def btnColors(self):
        with dpg.theme() as self.yellow_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(
                    dpg.mvThemeCol_Button, (248, 255, 0), category=dpg.mvThemeCat_Core
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_Text, (0, 0, 0, 255), category=dpg.mvThemeCat_Core
                )
        with dpg.theme() as self.pb_yellow_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(
                    dpg.mvThemeCol_PlotHistogram,
                    (248, 255, 0, 255),
                    category=dpg.mvThemeCat_Core,
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_Text, (0, 0, 0, 255), category=dpg.mvThemeCat_Core
                )
        with dpg.theme() as self.green_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(
                    dpg.mvThemeCol_Button, (0, 255, 0), category=dpg.mvThemeCat_Core
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_Text, (0, 0, 0, 255), category=dpg.mvThemeCat_Core
                )
        with dpg.theme() as self.pb_green_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(
                    dpg.mvThemeCol_PlotHistogram,
                    (0, 255, 0, 255),
                    category=dpg.mvThemeCat_Core,
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_Text, (0, 0, 0, 255), category=dpg.mvThemeCat_Core
                )
        with dpg.theme() as self.blue_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(
                    dpg.mvThemeCol_Button, (0, 0, 255), category=dpg.mvThemeCat_Core
                )
        with dpg.theme() as self.pb_blue_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(
                    dpg.mvThemeCol_PlotHistogram,
                    (0, 0, 255, 255),
                    category=dpg.mvThemeCat_Core,
                )
        with dpg.theme() as self.red_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(
                    dpg.mvThemeCol_Button, (255, 0, 0), category=dpg.mvThemeCat_Core
                )
        with dpg.theme() as self.pb_red_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(
                    dpg.mvThemeCol_PlotHistogram,
                    (255, 0, 0, 255),
                    category=dpg.mvThemeCat_Core,
                )


def popheader(h, b, c):
    article = dpg.get_value(c)
    dpg.set_value(c, f"{article}{h}\n")
    dpg.delete_item(h)
