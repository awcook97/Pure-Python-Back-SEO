# widget for displaying audit results
from typing import List
from Utils import sort_callback
from core_ui.Widgets.ContentScore import CoreContentScore
from core_ui.Widgets.Add_Info import Add_InfoWidget
import dearpygui.dearpygui as dpg
from Utils._Scraperz import PageAudit, CompareAudit
from multiprocessing.pool import ThreadPool
from BackSEODataHandler import getBackSEODataHandler
import webbrowser
import requests


class AuditView:
    def __init__(self, parent, doPAA=True):
        self.parent = parent
        self.doPAA = doPAA
        with dpg.group(horizontal=True, parent=self.parent) as self.auditViewGroup:
            self.rightSection()
            self.leftSection()
        self.dh = getBackSEODataHandler()
        self.currentPageAudit = PageAudit(("", ""))
        self.saveSeries = dict()
        self.seriesValue = dpg.add_series_value(parent=self.dh.register)
        self.dh.addtovpresize(self._repoRightSection)
        self.load_data()

    def load_data(self):
        # self.saveSeries = self.dh.loaddata("AuditView", "saveSeries")
        self.saveSeries = None
        if self.saveSeries is None:
            self.saveSeries = dict()

    def save_data(self):
        pass
        # self.dh.saveData("AuditView", "AuditView", self.saveSeries)

    def _repoRightSection(self):
        dpg.set_item_width(self.rightSectioncw, dpg.get_viewport_width() / 4)
        # dpg.set_item_height(self.rightTop,dpg.get_viewport_height()/4)
        dpg.set_item_width(self.leftSectioncw, dpg.get_viewport_width() * (46 / 64))

    def build(self, audit: CompareAudit):
        self.compareAudit = audit
        self.workingFile = dpg.get_value(self.dh.strLoader2)

        self.saveSeries[self.workingFile] = dict()
        # General
        avgLength = self.compareAudit.average_length
        bestReadability = self.compareAudit.bestTitle
        bestReadabilityURL = self.compareAudit.bestURL
        longestArticle = self.compareAudit.longestArt
        longestArticleURL = self.compareAudit.longestURL
        numAudits = self.compareAudit.numAudits
        dpg.configure_item(
            self.avgLength, default_value=f"Average Length: {avgLength} words"
        )
        dpg.configure_item(
            self.bestReadability, default_value=f"Best Readability: {bestReadability}"
        )
        dpg.configure_item(
            self.bestReadabilityURL, default_value=f"---> {bestReadabilityURL}"
        )
        dpg.configure_item(
            self.longestArticle, default_value=f"Longest Article: {longestArticle}"
        )
        dpg.configure_item(
            self.longestArticleURL, default_value=f"--->{longestArticleURL}"
        )
        dpg.configure_item(self.numAudits, default_value=f"Pages Audited: {numAudits}")
        # Page Audits
        self.urlList = self.compareAudit.urls
        dpg.configure_item(
            self.urlListBox, items=self.urlList, default_value=self.urlList[0]
        )
        if self.doPAA and self.compareAudit.hasPAA():
            dpg.configure_item(self.paaInfo, items=self.compareAudit.people_also_ask)
        elif self.doPAA:
            dpg.configure_item(self.paaInfo, items=["No PAA"], default_value="No PAA")
        self.currentPageAudit = self.compareAudit.cluster[self.compareAudit.urls[0]]
        self.updatePageAudit()
        # Common Keywords
        self.avgcommonKeywords = self.compareAudit.avgCommonKWs
        self.buildKWTable()
        self.getContentScores()

    def getContentScores(self):
        """We spin up a threadpool and run a second function using the threadpool
        to calculate the content scores for each page audit. Then we use the results
        to build the graph on the general page. The variables that stay the same in
        every content score function call are:
                - recKWs			:self.compareAudit.avgCommonKWs
                - recHead			:self.compareAudit.average_header
                - recLength			:self.compareAudit.average_length
                - recReadability	:self.compareAudit.bestReadability
        We go through the items in the self.compareAudit.cluster and pass the following in the init:
                - target			:pageAudit.article
        Then do ContentScore.updateSources() with:
                - (tarHead, tarLength, tarReadability, target) len(PageAudit.headers), PageAudit.length, PageAudit.readability_score, PageAudit.article
        updateSources will return (kwC, hrC, lnC, dnC, score) keywordCount, headerCount, lengthCount, readabilityCount, score
        """

        dpg.delete_item(self.barchartTable, children_only=True)
        if self.compareAudit.average_length == 0.0:
            return
        self.createTheTable(self.barchartTable)

    def createTheTable(
        self,
        parent=None,
        client="THISISTHECLIENTSTRING",
        clientSite: str = "THISISTHECLIENTSITESTRING",
    ):
        if parent is None:
            parent = self.barchartTable
        if self.currentPageAudit.rank > 0:
            dpg.add_table_column(
                label="Rank",
                parent=parent,
                width=45,
                default_sort=True,
                width_fixed=True,
            )
        dpg.add_table_column(label="Title", parent=parent, width_stretch=True)
        dpg.add_table_column(label="URL", parent=parent, no_sort=True, width_fixed=True)
        dpg.add_table_column(label="Num. Headers", parent=parent)
        dpg.add_table_column(label="Length", parent=parent, width_fixed=True)
        dpg.add_table_column(label="Readability", parent=parent)
        dpg.add_table_column(
            label="Content Score",
            parent=parent,
            no_sort=True,
            init_width_or_weight=175,
            width=175,
        )
        dpg.add_table_column(
            label="Score", parent=parent, init_width_or_weight=50, width=50
        )
        recKWs = self.compareAudit.avgCommonKWs
        recHead = self.compareAudit.average_header
        recLength = self.compareAudit.average_length
        recReadability = self.compareAudit.bestReadability
        del self.contenscore
        self.contenscore = CoreContentScore([], 0, 0, 0)
        self.contenscore.updateSources(0, recKWs)
        self.contenscore.updateSources(1, recHead)
        self.contenscore.updateSources(2, recLength)
        self.contenscore.updateSources(3, recReadability)
        for pageAudit in self.compareAudit.cluster.values():
            self.createScores(pageAudit, parent, client=client, clientSite=clientSite)

    def createScores(
        self,
        pageAudit: PageAudit,
        parent=None,
        client="THISISTHECLIENTSTRING",
        clientSite="THISISTHECLIENTSITESTRING",
    ):
        """This function will be called by the threadpool to create the scores for each page audit.
        We will need to create a ContentScore object, then call updateSources() with the following:
                - (tarHead, tarLength, tarReadability, target) len(PageAudit.headers), PageAudit.length, PageAudit.readability_score, PageAudit.article
        Then we return the score
        """
        if parent is None:
            parent = self.barchartTable
        if client is None or clientSite is None:
            client = "THISISTHECLIENTSTRING"
            clientSite = "THISISTHECLIENTSITESTRING"
        if pageAudit.length < 50 and client not in pageAudit.url:
            return
        if clientSite in pageAudit.url:
            myColor = (0, 255, 0, 255)
        else:
            myColor = (255, 0, 0, 255)
        tarHead = len(pageAudit.headers)
        tarLength = pageAudit.length
        tarReadability = pageAudit.readability_score
        target = pageAudit.article
        theRow = dpg.add_table_row(parent=parent, height=25)
        if pageAudit.rank > 0:
            dpg.add_input_int(
                default_value=pageAudit.rank,
                readonly=True,
                step=0,
                parent=theRow,
                use_internal_label=False,
                width=-1,
            )
        fee = dpg.add_text(
            default_value=str(pageAudit.title).strip(), parent=theRow, color=myColor
        )
        with dpg.group(parent=theRow):
            myB = dpg.add_button(
                label="Visit",
                callback=lambda: webbrowser.open(pageAudit.url),
                small=True,
            )
        dpg.add_input_int(
            default_value=tarHead, readonly=True, step=0, parent=theRow, width=-1
        )
        dpg.add_input_int(
            default_value=pageAudit.length,
            readonly=True,
            step=0,
            parent=theRow,
            width=-1,
        )
        dpg.add_input_float(
            default_value=pageAudit.readability_score,
            readonly=True,
            step=0,
            parent=theRow,
            width=-1,
        )
        score = self.contenscore.addSource(
            tarHead, tarLength, tarReadability, target, theRow
        )
        dpg.add_input_float(
            default_value=score, readonly=True, step=0, parent=theRow, width=-1
        )

        # ftt = dpg.add_tooltip(fee)
        # dpg.add_text(pageAudit.url, parent=ftt)
        btt = dpg.add_tooltip(myB)
        dpg.add_text(pageAudit.url, parent=btt)

    def buildKWTable(self, parent=None) -> list[dict]:
        if parent == None:
            parent = self.commonKeywords
        dpg.delete_item(parent, children_only=True)
        dpg.add_table_column(label="Keyword", parent=parent, width=100)
        dpg.add_table_column(
            label="Average Occurences", parent=parent, width=100, width_fixed=True
        )
        dpg.add_table_column(label="Volume", parent=parent, width=100, width_fixed=True)
        sendkws = list(self.compareAudit.common_keywords.keys())
        myreq = requests.post(
            "https://app.seo.ai/api/searchvolume/get",
            allow_redirects=True,
            json={"country": "usa", "keywords": sendkws[:799]},
        )
        if myreq.status_code == 200:
            kwsv = myreq.json()
        else:
            kwsv = list()
        kwd = dict()
        for keywor in kwsv:
            kwd[keywor["keyword"]] = keywor["search_volume"]
        rl: List[dict] = list()
        for kw, count in self.avgcommonKeywords:
            if kw in kwd:
                cou = kwd[kw]
            else:
                cou = -1
            with dpg.table_row(parent=parent):
                dpg.add_text(kw)
                dpg.add_input_int(label="", default_value=count, readonly=True, step=0)
                dpg.add_input_int(label="", default_value=cou, readonly=True, step=0)
            if cou < 0:
                cow = "No Data"
            else:
                cow = str(cou)
            rl.append({"kw": kw, "count": str(count), "volume": str(cow)})
        return rl

    def updatePageAudit(self):
        cpa = self.currentPageAudit
        pageAuditTitle = cpa.title
        pageAuditArticle = cpa.article
        pageAuditImages = cpa.images
        pageAuditMeta_tags = cpa.meta_tags
        pageAuditArticle_outline = cpa.article_outline
        pageAuditHeaders = cpa.headers
        pageAuditLength = cpa.length
        pageAuditArticle_keywords = cpa.article_keywords
        pageAuditKeyword_count = cpa.keyword_count
        pageAuditReadability_score = cpa.readability_score
        pageAuditGrade_level = cpa.grade_level
        pageAuditStats = cpa.stats
        pageAuditRelevance_score = cpa.relevance_score
        pageAuditInbound_links = cpa.inbound_links
        pageAuditOutbound_links = cpa.outbound_links
        pageAuditSchema = cpa.schema
        dpg.configure_item(self.pageAuditTitle, default_value=pageAuditTitle, wrap=-1)
        # dpg.configure_item(self.pageAuditArticle, default_value=pageAuditArticle, wrap=-1)
        self.pageAuditArticle.update(
            str(pageAuditArticle)
            .replace("\n\n", "")
            .replace("\t\t", "\t")
            .replace("\r\r", "\r")
        )
        # dpg.configure_item(self.pageAuditImages, default_value=pageAuditImages, wrap=-1)
        # dpg.configure_item(self.pageAuditMeta_tags, default_value=pageAuditMeta_tags, wrap=-1)
        # dpg.configure_item(self.pageAuditArticle_outline, default_value=pageAuditArticle_outline, wrap=-1)
        # dpg.configure_item(self.pageAuditHeaders, default_value=pageAuditHeaders, wrap=-1)
        dpg.configure_item(self.pageAuditLength, default_value=pageAuditLength, wrap=-1)
        # dpg.configure_item(self.pageAuditArticle_keywords, default_value=pageAuditArticle_keywords, wrap=-1)
        # dpg.configure_item(self.pageAuditKeyword_count, default_value=pageAuditKeyword_count, wrap=-1)
        dpg.configure_item(
            self.pageAuditReadability_score,
            default_value=pageAuditReadability_score,
            wrap=-1,
        )
        dpg.configure_item(
            self.pageAuditGrade_level, default_value=pageAuditGrade_level, wrap=-1
        )
        # dpg.configure_item(self.pageAuditStats, default_value=pageAuditStats, wrap=-1)
        dpg.configure_item(
            self.pageAuditRelevance_score,
            default_value=pageAuditRelevance_score,
            wrap=-1,
        )
        # dpg.configure_item(self.pageAuditInbound_links, default_value=pageAuditInbound_links, wrap=-1)
        # dpg.configure_item(self.pageAuditOutbound_links, default_value=pageAuditOutbound_links, wrap=-1)
        # dpg.configure_item(self.pageAuditSchema, default_value=pageAuditSchema, wrap=-1)
        self.pageAuditImages.update(pageAuditImages)
        self.pageAuditMeta_tags.update(pageAuditMeta_tags)
        self.pageAuditArticle_outline.update(pageAuditArticle_outline)
        self.pageAuditHeaders.update(pageAuditHeaders)
        self.pageAuditArticle_keywords.update(pageAuditArticle_keywords)
        self.pageAuditKeyword_count.update(pageAuditKeyword_count)
        self.pageAuditStats.update(pageAuditStats)
        self.pageAuditInbound_links.update(pageAuditInbound_links)
        self.pageAuditOutbound_links.update(pageAuditOutbound_links)
        self.pageAuditSchema.update(pageAuditSchema)
        self.updateSchema(page=cpa)
        # self.showContentScore()

    def updateSchema(self, page: PageAudit):
        dpg.delete_item(self.schemaNodeEditor, children_only=True)
        if "schema" in page.errors:
            return
        if page.schema is None:
            return
        self.taken = set()
        self.schemaItems = dict()
        self.recursSchema(page.schema, self.schemaNodeEditor)

    def recursSchema(
        self, schema, parent, layer: tuple[int, int] = (3, -1)
    ) -> int | str:
        x, y = layer
        posit: tuple[int, int] = (x * 110, y * 200)
        num = 1
        swapper: int = x
        while posit in self.taken:
            x: int = swapper
            num: int = num * -1
            if num > 0:
                if x < 0:
                    x *= -1
                x += num
            else:
                x += num
            posit = (x * 110, y * 200)
            if num > 0:
                num += 1
        self.taken.add(posit)
        label: str = f"{x}, {y}"
        if type(schema) == dict:
            if "@type" in schema:
                label = schema.pop("@type")
                if type(label) == list:
                    label = label[0]
                if not label in self.schemaItems:
                    self.schemaItems[label] = dict()
                if "@id" in schema:
                    theid = schema.pop("@id")
                    if theid in self.schemaItems:
                        theNode = self.schemaItems[theid]
                    else:
                        self.schemaItems[label][theid] = dpg.add_node(
                            parent=parent, pos=posit, label=label
                        )
                        theNode = self.schemaItems[label][theid]
                else:
                    theNode = dpg.add_node(parent=parent, pos=posit, label=label)
                    self.schemaItems[label][label] = theNode
            elif "@id" in schema:
                theid = schema.pop("@id")
                if theid in self.schemaItems:
                    theNode = self.schemaItems[theid]
                else:
                    theNode = dpg.add_node(parent=parent, pos=posit, label=label)
                    self.schemaItems[theid] = theNode
            else:
                theNode = dpg.add_node(parent=parent, pos=posit, label=label)
        else:
            theNode = dpg.add_node(parent=parent, pos=posit, label=label)

        theatt = dpg.add_node_attribute(
            label=f"List", parent=theNode, attribute_type=dpg.mvNode_Attr_Input
        )
        y += 1
        if x < 0:
            swapper *= -1
        elif swapper < 0:
            swapper *= -1
        x = swapper
        if type(schema) == list:
            count = 0
            for item in schema:
                count += 1
                thenatt = dpg.add_node_attribute(
                    label=f"List", parent=theNode, attribute_type=dpg.mvNode_Attr_Output
                )
                if type(item) is dict:
                    if "@type" in item:
                        label = item["@type"]
                        dpg.add_text(label, parent=thenatt, wrap=100)
                    else:
                        dpg.add_text(str(count), parent=thenatt, wrap=100)
                else:
                    dpg.add_text(str(count), parent=thenatt)
                theNextNode = self.recursSchema(item, parent, (x, y))

                dpg.add_node_link(thenatt, theNextNode, parent=parent)
                y += 1
        elif type(schema) == dict:
            count = 0
            for key, value in schema.items():
                if type(value) is dict:
                    kk = dpg.add_node_attribute(
                        label=f"{key}",
                        parent=theNode,
                        attribute_type=dpg.mvNode_Attr_Output,
                    )
                    dpg.add_text(f"{key}", parent=kk, wrap=100)
                    theNextNode = self.recursSchema(
                        value, parent, (layer[0] + 1, layer[1] + 1)
                    )
                    dpg.add_node_link(kk, theNextNode, parent=parent)
                elif type(value) is list:
                    thenatt = dpg.add_node_attribute(
                        label=f"List",
                        parent=theNode,
                        attribute_type=dpg.mvNode_Attr_Output,
                    )
                    for item in value:
                        count += 1
                        thenatt = dpg.add_node_attribute(
                            label=f"List",
                            parent=theNode,
                            attribute_type=dpg.mvNode_Attr_Output,
                        )
                        if type(item) is dict:
                            if "@type" in item:
                                label = item["@type"]
                                # label = item.pop("@type")
                                dpg.add_text(label, parent=thenatt, wrap=100)
                            else:
                                dpg.add_text(str(count), parent=thenatt, wrap=100)
                        else:
                            dpg.add_text(str(count), parent=thenatt)
                        theNextNode = self.recursSchema(item, parent, (x, y))
                        # myo = dpg.add_node_attribute(label="item", parent=theNode, attribute_type=dpg.mvNode_Attr_Output)
                        dpg.add_node_link(thenatt, theNextNode, parent=parent)
                else:
                    theatt = dpg.add_node_attribute(
                        label=f"{key}: {value}",
                        parent=theNode,
                        attribute_type=dpg.mvNode_Attr_Input,
                    )
                    if str(key).startswith("@"):
                        dpg.add_text(f"{key}: {value}", wrap=100, parent=theatt)
                    else:
                        dpg.add_text(f"{key}", wrap=175, parent=theatt)
        else:
            theatt = dpg.add_node_attribute(
                label=f"{schema}", parent=theNode, attribute_type=dpg.mvNode_Attr_Input
            )
            dpg.add_text(f"{schema}", wrap=175, parent=theatt)
        return theatt

    def rightSection(self):
        """The right section will have 2 subsections, a top and
        a bottom. The top contains a list box that has
        a list of the urls that are found in compare audit
        When a url is selected, the left section will display
        the audit results for that url.

        The bottom section will have an input box that will
        allow the user to search the results of the ComparedAudit.
        """
        with dpg.child_window(
            label="Right Section",
            parent=self.auditViewGroup,
            width=dpg.get_viewport_width() / 4,
            autosize_y=True,
            delay_search=True,
        ) as self.rightSectioncw:
            self.buildRightTop()
            # self.buildRightBottom()

    def buildRightTop(self):
        with dpg.group(parent=self.rightSectioncw) as self.rightTop:
            dpg.add_text("SERP Results")
            self.urlListBox = dpg.add_listbox(
                [], width=-1, num_items=10, callback=self.updateAudit
            )
            if self.doPAA:
                with dpg.group():
                    self.paaInfo = dpg.add_listbox(
                        [], num_items=5, label="People Also Ask"
                    )

    def buildRightBottom(self):
        with dpg.child_window(parent=self.rightSectioncw) as self.rightBottom:
            self.searchListBox = dpg.add_listbox(
                [], num_items=10, label="Search Results", callback=self.updateAudit
            )
            self.auditSearch = dpg.add_input_text(
                label="Search", hint="Search", callback=self.searchAudit, on_enter=True
            )
            with dpg.group(horizontal=True):
                self.auditSearchButton = dpg.add_button(
                    label="Search", callback=self.searchAudit
                )
                self.auditSearchClearButton = dpg.add_button(
                    label="Clear", callback=self.clearSearch
                )

    def leftSection(self):
        """
                It initially starts on the General page, which contains
                the information that is found in the CompareAudit object
                except for the page audits and URLs, as those can be found
                in the right section.

        CompareAudit has the following attributes:
                total_length		InitialValue: 0
                total_headings		InitialValue: 0
                average_length		InitialValue: 0
                average_header		InitialValue: 0
                bestReadability		InitialValue: 999999.9
                bestTitle			InitialValue: ""
                bestURL				InitialValue: ""
                longestNum			InitialValue: 0
                longestArt			InitialValue: ""
                longestURL			InitialValue: ""
                common_keywords		InitialValue: dict()
                common_headings		InitialValue: dict()
                common_oblinks		InitialValue: list()
                all_headings		InitialValue: list()
                all_keywords		InitialValue: dict()
                all_oblinks			InitialValue: list()
                avgCommonKWs		InitialValue: list()
                numAudits			InitialValue: len(self.audits)
                common_main_kws		InitialValue: dict()
                cluster				InitialValue: dict[str,PageAudit]
                urls				InitialValue: list(self.cluster.keys())
                audits				InitialValue: list(self.cluster.values())
        The way we're gonna set this up is that we're gonna have a tab bar
        that has the following tabs:
                General
                Common Keywords
                Common Schema Attributes
                Common Meta Data

        """
        with dpg.child_window(
            label="Left Section",
            parent=self.auditViewGroup,
            width=dpg.get_viewport_width() * (11 / 16),
            autosize_y=True,
            delay_search=True,
            before=self.rightSectioncw,
        ) as self.leftSectioncw:
            with dpg.tab_bar() as self.leftSectionTabBar:
                with dpg.tab(label="General") as self.generalTab:
                    self.buildGeneral()
                with dpg.tab(label="Common Keywords") as self.commonKeywordsTab:
                    self.buildCommonKeywords()
                with dpg.tab(label="Page Audits") as self.pageAuditsTab:
                    self.buildPageAudits()
                with dpg.tab(label="Schema Results") as self.schemaResults:
                    self.buildCommonSchemaAttributes()
                # with dpg.tab(label="Common Meta Data") as self.commonMetaDataTab:
                # 	self.buildCommonMetaData()

    def buildGeneral(self):
        """The General tab will have the following:
        Average Length
        Best Readability (and the URL it's found on)
        Longest Article (and the URL it's found on)
        Number of Audits
        Bar Chart displaying the Content Score of each audit
        """
        with dpg.group(parent=self.generalTab) as self.generalTabGroup:
            with dpg.group(horizontal=True) as self.avgLengthGroup:
                dpg.add_text(label="Average Length: ")
                self.avgLength = dpg.add_text("")
            with dpg.group(horizontal=True) as self.bestReadabilityGroup:
                dpg.add_text(label="Best Readability: ")
                self.bestReadability = dpg.add_text("")
            with dpg.group(horizontal=True) as self.bestReadabilityURLGroup:
                dpg.add_text(label="URL: ")
                self.bestReadabilityURL = dpg.add_text("")
            with dpg.group(horizontal=True):
                dpg.add_text(label="Longest Article: ")
                self.longestArticle = dpg.add_text("")
            with dpg.group(horizontal=True) as self.longestArticleURLGroup:
                dpg.add_text(label="URL: ")
                self.longestArticleURL = dpg.add_text("")
            with dpg.group(horizontal=True) as self.numAuditsGroup:
                dpg.add_text(label="Number of Audits: ")
                self.numAudits = dpg.add_text("")
            with dpg.group(horizontal=True) as self.barChartGroup:
                self.barchartTable = dpg.add_table(
                    header_row=True,
                    sortable=True,
                    row_background=True,
                    callback=sort_callback,
                    delay_search=True,
                    clipper=False,
                    sort_multi=True,
                    resizable=True,
                    inner_width=0,
                    no_pad_innerX=True,
                    no_pad_outerX=True,
                    policy=dpg.mvTable_SizingFixedFit,
                )
                # self.barChart = dpg.add_bar_series([0, 0, 0, 0, 0], label="Content Score", parent=self.generalTabGroup)

    def buildPageAudits(self):
        """This is the page that will be updated whenever the user clicks on a
        url in the right section. PageAudit is a class and holds the following:
                PageAudit.title
                PageAudit.article
                PageAudit.images
                PageAudit.meta_tags
                PageAudit.article_outline
                PageAudit.headers
                PageAudit.length
                PageAudit.article_keywords
                PageAudit.keyword_count
                PageAudit.readability_score
                PageAudit.grade_level
                PageAudit.stats
                PageAudit.relevance_score
                PageAudit.inbound_links
                PageAudit.outbound_links
                PageAudit.schema
        We will need to generate:
                Content Score
                Content Score Breakdown Tooltip
        """
        with dpg.group(parent=self.pageAuditsTab) as self.pageAuditsTabGroup:
            with dpg.group(horizontal=True) as self.pageAuditTitleGroup:
                dpg.add_text("Title: ")
                self.pageAuditTitle = dpg.add_text("")
                with dpg.group(horizontal=True) as self.pageAuditsContentScoreGroup:
                    dpg.add_text(label="Content Score: ")
                    self.contenscore = CoreContentScore([], 0, 0, 0)
            with dpg.group(horizontal=True) as self.pageAuditLengthGroup:
                dpg.add_text("Length: ")
                self.pageAuditLength = dpg.add_text("")
                dpg.add_text("Readability Score: ")
                self.pageAuditReadability_score = dpg.add_text("")

            with dpg.group(horizontal=True) as self.pageAuditRelevance_scoreGroup:
                dpg.add_text("Relevance Score: ")
                self.pageAuditRelevance_score = dpg.add_text("")
                dpg.add_text("Grade Level: ")
                self.pageAuditGrade_level = dpg.add_text("")

            with dpg.group(horizontal=True) as self.pageAuditArticleGroup:
                self.pageAuditArticle = Add_InfoWidget(
                    self.pageAuditArticleGroup, "Article"
                )
            with dpg.group(horizontal=True) as self.pageAuditImagesGroup:
                self.pageAuditImages = Add_InfoWidget(
                    self.pageAuditImagesGroup, "Images"
                )
            with dpg.group(horizontal=True) as self.pageAuditMeta_tagsGroup:
                self.pageAuditMeta_tags = Add_InfoWidget(
                    self.pageAuditMeta_tagsGroup, "Meta Tags"
                )
            with dpg.group(horizontal=True) as self.pageAuditArticle_outlineGroup:
                self.pageAuditArticle_outline = Add_InfoWidget(
                    self.pageAuditArticle_outlineGroup, "Article Outline"
                )
            with dpg.group(horizontal=True) as self.pageAuditHeadersGroup:
                self.pageAuditHeaders = Add_InfoWidget(
                    self.pageAuditHeadersGroup, "Headers"
                )

            with dpg.group(horizontal=True) as self.pageAuditArticle_keywordsGroup:
                self.pageAuditArticle_keywords = Add_InfoWidget(
                    self.pageAuditArticle_keywordsGroup, "Article Keywords"
                )

            with dpg.group(horizontal=True) as self.pageAuditKeyword_countGroup:
                self.pageAuditKeyword_count = Add_InfoWidget(
                    self.pageAuditKeyword_countGroup, "Keyword Count"
                )

            with dpg.group(horizontal=True) as self.pageAuditStatsGroup:
                self.pageAuditStats = Add_InfoWidget(self.pageAuditStatsGroup, "Stats")

            with dpg.group(horizontal=True) as self.pageAuditInbound_linksGroup:
                self.pageAuditInbound_links = Add_InfoWidget(
                    self.pageAuditInbound_linksGroup, "Inbound Links"
                )
            with dpg.group(horizontal=True) as self.pageAuditOutbound_linksGroup:
                self.pageAuditOutbound_links = Add_InfoWidget(
                    self.pageAuditOutbound_linksGroup, "Outbound Links"
                )
            with dpg.group(horizontal=True) as self.pageAuditSchemaGroup:
                self.pageAuditSchema = Add_InfoWidget(
                    self.pageAuditSchemaGroup, "Schema"
                )

    def buildCommonKeywords(self):
        """The Common Keywords tab will have the following:
        A list of the common keywords (and count)
        A Word Cloud of the 30 most common keywords and NGrams (Premium Feature)
        """
        with dpg.group(parent=self.commonKeywordsTab) as self.commonKeywordsTabGroup:
            with dpg.group(horizontal=True) as self.commonKeywordsGroup:
                dpg.add_text(label="Common Keywords: ")
                self.commonKeywords = dpg.add_table(
                    header_row=True,
                    sortable=True,
                    row_background=True,
                    callback=sort_callback,
                    delay_search=True,
                    clipper=True,
                    sort_multi=True,
                )
            with dpg.group(horizontal=True) as self.commonNGramsGroup:
                dpg.add_text(label="Common NGrams: ")
                self.commonNGrams = dpg.add_text("")
            # with dpg.group(horizontal=True) as self.wordCloudGroup:
            # 	dpg.add_text(label="Word Cloud: ")
            # 	self.wordCloud = dpg.add_text("wordCloud")

    def buildCommonSchemaAttributes(self):
        """The Common Schema Attributes tab will have the following:
                A list of the common schema attributes
                A list of pages that don't have a schema
                A list of the different types of schema found
        This is a premium feature, so it won't be implemented yet
        """
        self.schemaNodeEditor = dpg.add_node_editor(
            parent=self.schemaResults,
            callback=lambda sender, app_data: dpg.add_node_link(
                app_data[0], app_data[1], parent=sender
            ),
            delink_callback=lambda sender, app_data: dpg.delete_item(app_data),
            minimap=True,
            minimap_location=dpg.mvNodeMiniMap_Location_BottomLeft,
            menubar=True,
        )

    def buildCommonMetaData(self):
        """The Common Meta Data tab will have the following:
                A list of the common meta data
        This is a premium feature, so it won't be implemented yet
        """
        pass

    def showContentScore(self, *args, **kwargs):
        # self.contenscore = CoreContentScore(self.compareAudit.avgCommonKWs, self.compareAudit.average_header,
        # 				self.compareAudit.average_length, self.compareAudit.bestReadability,self.currentPageAudit.article)
        self.contenscore.updateSources(0, self.compareAudit.avgCommonKWs)
        self.contenscore.updateSources(1, self.compareAudit.average_header)
        self.contenscore.updateSources(2, self.compareAudit.average_length)
        self.contenscore.updateSources(3, self.compareAudit.bestReadability)
        self.contenscore.updateSources(
            5,
            (
                len(self.currentPageAudit.headers),
                self.currentPageAudit.length,
                self.currentPageAudit.readability_score,
                self.currentPageAudit.article,
            ),
        )

    def updateAudit(self, *args, **kwargs):
        if len(args):
            sender = args[0]
        self.currentPageAudit = self.compareAudit.cluster[dpg.get_value(sender)]
        self.updatePageAudit()

    def searchAudit(self, *args, **kwargs):
        pass

    def clearSearch(self, *args, **kwargs):
        dpg.set_value(self.auditSearch, "")
        self.searchAudit()
