# Audit
from core_ui import Core_UI
from core_ui.Widgets.BasicVroom import BasicVroom, PlotVroom
import dearpygui.dearpygui as dpg
from core_ui.Widgets.AuditView import AuditView
from Utils import cleanFilename, sort_callback
from Utils._Scraperz import CompareAudit, SiteMap, CustomThread
from typing import List, Dict, Literal
import json
import os
import pickle
import time
from multiprocessing.pool import Pool
import random
from multiprocessing import cpu_count
import math


class SiteTest:
    def __init__(
        self,
        name: str = "",
        url: str = "",
        sendingInternal: List[str] = [],
        sendingExternal: List[str] = [],
    ):
        self.name = name
        self.url = url
        self.drawLayer = None
        self.alturl = url.split("://")[1].replace("www.", "")
        if "/" in self.alturl: 
            self.alturl2 = self.alturl.split("/", 1)[1]
        else:
            self.alturl2 = self.alturl
        self.sendingInternal = sendingInternal
        self.sendingExternal = sendingExternal
        self.senderPos = list()
        self.senderAnno = list()
        self.receiving = list()

    def addReceiving(
        self,
        sitePos: tuple,
        siteCol: tuple = (125, 125, 125, 125),
        siteAnno: int | str = 0,
    ):
        recCol = (siteCol[0], siteCol[1], siteCol[2], 100)
        self.receiving.append((sitePos, recCol))
        self.senderAnno.append(siteAnno)

    def addSender(self, sitePos: tuple, siteAnno: int | str):
        self.senderPos.append(sitePos)
        self.senderAnno.append(siteAnno)

    def drawSendReceive(self, parent):
        dpg.configure_item(self.myAnno, show=True)
        if self.drawLayer is None:
            self.drawLayer = dpg.add_draw_layer(parent=parent)
            self.sendCol = (self.color[0], self.color[1], self.color[2], 255)
            for site in self.senderPos:
                dpg.draw_line(
                    self.cirPos, site, parent=self.drawLayer, color=self.sendCol
                )
            for site in self.receiving:
                dpg.draw_line(
                    site[0], self.cirPos, parent=self.drawLayer, color=site[1]
                )
        for site in self.senderAnno:
            dpg.configure_item(site, show=True)
        return self.drawLayer

    def drawNode(
        self,
        parent,
        pos: list = [0, 0],
        parent2=None,
        color: tuple = (125, 125, 125, 125),
    ):
        with dpg.node(
            label=self.name, parent=parent, pos=pos, draggable=False
        ) as self.node:
            with dpg.node_attribute(
                attribute_type=dpg.mvNode_Attr_Input
            ) as self.ninput:
                dpg.add_text("Inbound:")
            with dpg.node_attribute(
                attribute_type=dpg.mvNode_Attr_Output
            ) as self.noutput:
                dpg.add_text("Outbound:")
        if parent2 is not None:
            self.color = color
            self.bcolor = (255 - color[0], 255 - color[1], 255 - color[2], 255)
            self.cirPos = (pos[0] / 10, pos[1] / 10)
            self.myCircle = dpg.draw_circle(
                self.cirPos, radius=5, parent=parent2, color=self.color, fill=self.color
            )
            # self.myAnno = dpg.draw_text(self.cirPos, self.name, parent=parent2, color=self.bcolor, size=10)
            if self.cirPos[0] > 0:
                offx = -10
            elif self.cirPos[0] < 0:
                offx = 10
            else:
                offx = 0
            if self.cirPos[1] > 0:
                offy = -10
            elif self.cirPos[1] < 0:
                offy = 10
            else:
                offy = 0

            self.myAnno = dpg.add_plot_annotation(
                label=self.name,
                default_value=self.cirPos,
                parent=parent2,
                color=self.color,
                clamped=False,
            )


def createCircleFromPositions(
    numberOfPoints: int, radius: float, center: list = [0, 0]
) -> List[List[float]]:
    positions = []
    angle = 0
    if numberOfPoints == 0:
        numberOfPoints = 1
    angle_increment = 2 * math.pi / numberOfPoints
    for i in range(numberOfPoints):
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        positions.append([x, y])
        angle += angle_increment
    return positions


def drawLinks(parent, siteList: List[SiteTest], parent2=None) -> Dict[str, SiteTest]:
    tempDict: Dict[str, SiteTest] = dict()
    rDict: Dict[str, SiteTest] = dict()
    count: int = 0
    for site in siteList:
        tempDict[site.url] = site
        tempDict[site.alturl] = site
        tempDict[site.alturl2] = site
        rDict[site.name] = site
    for site in siteList:
        for internal in site.sendingInternal:
            count += 1
            if internal in tempDict:
                if count < 1000:
                    dpg.add_node_link(
                        site.noutput, tempDict[internal].ninput, parent=parent
                    )
                if parent2 is not None:
                    dpg.draw_line(
                        site.cirPos,
                        tempDict[internal].cirPos,
                        parent=parent2,
                        color=site.color,
                    )
                    tempDict[internal].addReceiving(
                        site.cirPos, site.color, site.myAnno
                    )
                    site.addSender(tempDict[internal].cirPos, tempDict[internal].myAnno)
        # if count > 1000: break
    return rDict


class ColorChanger:
    def __init__(self) -> None:
        self.alp = 200
        self.color = (0, 0, 0, self.alp)
        self.previousColors = list()
        self.colorIncrement = 10
        self.lastColor = (0, 0, 0, self.alp)
        self.lastChanged = "b"

    def changeColor(self):
        # Generate a new color that is not too similar to the previous colors
        r, g, b, a = self.color
        if self.lastChanged == "b":
            r = random.randint(0, 255)
        if self.lastChanged == "r":
            g = random.randint(0, 255)
        if self.lastChanged == "g":
            b = random.randint(0, 255)
        newColor = (r, g, b, self.alp)
        while self.colorSimilarity(newColor, self.color) > 0.5 or any(
            self.colorSimilarity(newColor, prevColor) > 0.5
            for prevColor in self.previousColors
        ):
            newColor = (
                random.randint(0, 255),
                random.randint(0, 255),
                random.randint(0, 255),
                self.alp,
            )

        # Update the color and previous colors list
        self.previousColors.append(self.color)
        self.lastColor = self.color
        self.color = newColor

    def colorSimilarity(self, color1, color2):
        # Calculate the similarity between two colors based on their RGB values
        r1, g1, b1, a1 = color1
        r2, g2, b2, a2 = color2
        return (abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)) / (255)


class CoreAudit(Core_UI):
    def __init__(self) -> None:
        self.auditing = False
        self.oldList = list()
        self.auditedList = list()
        self.auditScore = dict()
        self.auditRegistry: int | str = dpg.add_value_registry()
        self.textureRegistry: int | str = dpg.add_texture_registry(show=False)
        with dpg.value_registry() as self.auditValueRegistry:
            self.donthurtlineseriesregval: int | str = dpg.add_series_value()
            self.donthurtshadeseriesregval: int | str = dpg.add_series_value()
            self.minorlineseriesregval: int | str = dpg.add_series_value()
            self.minorshadeseriesregval: int | str = dpg.add_series_value()
            self.moderatelineseriesregval: int | str = dpg.add_series_value()
            self.moderateshadeseriesregval: int | str = dpg.add_series_value()
            self.criticallineseriesregval: int | str = dpg.add_series_value()
            self.criticalshadeseriesregval: int | str = dpg.add_series_value()
        self.url2title = dict()
        self.load_data()

    def __binit__(self) -> None:
        pass

    def save_data(self) -> None:
        pass

    def load_data(self) -> None:
        self.auditedList = list()
        for audit in os.listdir("output/sitemap_audits"):
            if audit.endswith(".caudit"):
                self.auditedList.append(audit.split(".caudit")[0])

    def _create_menu(self, parent, before) -> Literal[0]:
        # with dpg.menu(label="Inspect Results", parent=parent, before=before) as self.theMenu:
        return 0

    def _create_window(self) -> Literal[0]:
        # with dpg.window(label="General Audit Report") as self.theWindow:
        # 	self.auditView = AuditView(self.theWindow)
        # return self.theWindow
        return 0

    def _create_tab(self, parent, plug) -> int | str:
        with dpg.tab(label="Website Audit", parent=parent, before=plug) as self.theTab:
            with dpg.child_window(height=75) as self.auditsearchercw:
                with dpg.group(
                    horizontal=True, label="Search URL Group"
                ) as self.searchurlgroup:
                    dpg.add_text("Sitemap: ")
                    self.auditinput: int | str = dpg.add_input_text(
                        default_value="https://axel.llc/sitemap.xml",
                        hint="https://yoursite.com/sitemap.xml",
                        width=300,
                        callback=self.startAudit,
                        on_enter=True,
                    )
                    dpg.add_text("Proxy: ")
                    self.searchProxy: int | str = dpg.add_input_text(
                        label="",
                        hint="http://your_user:your_password@your_proxy_url:your_proxy_port",
                        callback=self.startAudit,
                        width=200,
                        on_enter=True,
                    )
                    self.searchButton: int | str = dpg.add_button(
                        label="Search", callback=self.startAudit, enabled=True
                    )
                self.auditPicker: int | str = dpg.add_combo(
                    label="Previous Audits", items=[], callback=self.loadAudit
                )
            with dpg.group(horizontal=True):
                self.iljcsvbutton: int | str = dpg.add_button(
                    label="Create ILJ CSV", callback=self.createILJCSV, enabled=False
                )
                self.createAuditButton: int | str = dpg.add_button(
                    label="Create Audit Report",
                    callback=self.createAuditReport,
                    enabled=True,
                )
                self.createFullAuditButton: int | str = dpg.add_button(
                    label="Create Full Audit Report",
                    callback=self._createAllAuditReport,
                    enabled=True,
                )
            self.auditView = AuditView(self.theTab, doPAA=False)
            self.siteAuditResults: int | str = dpg.add_tab(
                label="Sitemap Audit Results",
                parent=self.auditView.leftSectionTabBar,
                before=self.auditView.generalTab,
            )
            self.internalLinkVisuals: int | str = dpg.add_tab(
                label="Internal Link Visuals",
                parent=self.auditView.leftSectionTabBar,
                before=self.auditView.generalTab,
            )
            self.testNodes()
            self.sitemapAuditResultsInit()
        return self.theTab

    def bindColor(
        self,
        item: int | str,
        itemtype: int = dpg.mvPlotCol_Fill,
        category: int = -1,
        color: tuple = (125, 125, 125, 125),
    ):
        """
        bindColor Binds the color to the item given the itemtype and category

        Basic way to bind colors to things

        :param item: dpg item to bind to
        :type item: int | str
        :param itemtype: dpg item type, defaults to dpg.mvPlotCol_Fill
        :type itemtype: int, optional
        :param category: -1 = PLOTS, 0=CORE, 1=NODES, defaults to -1
        :type category: int, optional
        :param color: rgba, defaults to (125,125,125,125)
        :type color: tuple, optional
        """
        if category < 0:
            category = dpg.mvThemeCat_Plots
        elif category == 0:
            category = dpg.mvThemeCat_Core
        else:
            category = dpg.mvThemeCat_Nodes
        with dpg.theme() as colortheme:
            with dpg.theme_component(0):
                dpg.add_theme_color(itemtype, color, category=category)
        dpg.bind_item_theme(item, colortheme)

    #########################################
    # 	GET
    # 		CHARTS
    # 				HERE
    #
    ##########################################
    def sitemapAuditResultsInit(self) -> None:
        with dpg.template_registry() as self.whatevertemplate:
            self.tempVroom = BasicVroom(
                150,
                150,
                parent=self.whatevertemplate,
                start=0,
                pos=(200, 200),
                hasDrawList=True,
            )
        # self.myVroom = BasicVroom(600, 600, parent=self.siteAuditResults,start=0, pos=(100,0), hasDrawList=False, isPlot=False)
        with dpg.group(
            horizontal=True, parent=self.siteAuditResults
        ) as self.auditResultsGroup:
            # with dpg.group():
            # 	self.myVroom = BasicVroom(150, 150, parent=dpg.last_container(),start=0, pos=(200,200), hasDrawList=False)
            with dpg.subplots(
                rows=1,
                columns=2,
                width=-1,
                height=400,
                label="Site Audit Scores",
                pos=(0, 0),
            ) as self.auditSubPlot:
                with dpg.plot(
                    label="Page Score",
                    height=400,
                    width=400,
                    anti_aliased=True,
                    equal_aspects=True,
                ) as self.auditPie:
                    # with dpg.draw_layer():
                    # 	self.missingPieDraw = dpg.draw_circle([0.5, 0.5], 0.5, fill=[255,0,0,255], color=[255,0,0,255], thickness=0.0, segments=100, tag="Missing")
                    self.newVroom = PlotVroom(
                        (300, 270),
                        parent=self.auditPie,
                        radius1=35,
                        radius2=55,
                        text="Score",
                    )
                    # with dpg.draw_layer() as d:
                    # 	self.myVroom2 = BasicVroom(150, 150, parent=d, start=0, pos=(0,0), hasDrawList=True, isPlot = True)
                    leg: int | str = dpg.add_plot_legend()

                    xax: int | str = dpg.add_plot_axis(
                        dpg.mvXAxis,
                        no_gridlines=True,
                        no_tick_marks=True,
                        no_tick_labels=True,
                    )
                    dpg.set_axis_limits(xax, -75, 425)
                    with dpg.plot_axis(
                        dpg.mvYAxis,
                        no_gridlines=True,
                        no_tick_labels=True,
                        no_tick_marks=True,
                    ) as yax:
                        self.sitemapPie: int | str = dpg.add_pie_series(
                            200.5,
                            400.5,
                            200.5,
                            [0.45, 0.45],
                            ["Run an audit", "For results"],
                            format="",
                            angle=0,
                        )
                        # self.myVroom = BasicVroom(150, 150, parent=dpg.last_item(),start=0, pos=(200,200), hasDrawList=False)
                    dpg.set_axis_limits(yax, 200, 650)
                    dpg.set_axis_limits_auto(xax)
                    dpg.set_axis_limits_auto(yax)

                with dpg.plot(
                    label="Areas of Improvement",
                    height=400,
                    width=400,
                    anti_aliased=True,
                    equal_aspects=True,
                ) as self.auditPie:
                    self.pxax: int | str = dpg.add_plot_axis(dpg.mvXAxis)
                    with dpg.plot_axis(dpg.mvYAxis) as self.yxax:
                        theList: list[int] = [5, 4, 3, 4, 5]
                        self.donthurtlineseries: int | str = dpg.add_line_series(
                            [1, 2, 3, 4, 5], theList, label="donthurtlineseries"
                        )
                        self.bindColor(
                            self.donthurtlineseries,
                            itemtype=dpg.mvPlotCol_Line,
                            color=(125, 125, 125, 255),
                            category=-1,
                        )
                        self.donthurtshadeseries: int | str = dpg.add_shade_series(
                            [1, 2, 3, 4, 5],
                            theList,
                            y2=[0, 0, 0, 0, 0],
                            label="donthurtshadeseries",
                        )
                        self.bindColor(
                            self.donthurtshadeseries,
                            itemtype=dpg.mvPlotCol_Fill,
                            color=(125, 125, 125, 64),
                            category=-1,
                        )
                        self.minorlineseries: int | str = dpg.add_line_series(
                            [1, 2, 3, 4, 5], theList, label="minorlineseries"
                        )
                        self.bindColor(
                            self.minorlineseries,
                            itemtype=dpg.mvPlotCol_Line,
                            color=(32, 50, 165, 255),
                            category=-1,
                        )
                        self.minorshadeseries: int | str = dpg.add_shade_series(
                            [1, 2, 3, 4, 5],
                            [a * 2 for a in theList],
                            y2=theList,
                            label="minorshadeseries",
                        )
                        self.bindColor(
                            self.minorshadeseries,
                            itemtype=dpg.mvPlotCol_Fill,
                            color=(32, 50, 165, 64),
                            category=-1,
                        )
                        self.moderatelineseries: int | str = dpg.add_line_series(
                            [1, 2, 3, 4, 5], theList, label="moderatelineseries"
                        )
                        self.bindColor(
                            self.moderatelineseries,
                            itemtype=dpg.mvPlotCol_Line,
                            color=(150, 250, 20, 255),
                            category=-1,
                        )
                        self.moderateshadeseries: int | str = dpg.add_shade_series(
                            [1, 2, 3, 4, 5],
                            [a * 3 for a in theList],
                            y2=[a * 2 for a in theList],
                            label="moderateshadeseries",
                        )
                        self.bindColor(
                            self.moderateshadeseries,
                            itemtype=dpg.mvPlotCol_Fill,
                            color=(150, 250, 20, 64),
                            category=-1,
                        )
                        self.criticallineseries: int | str = dpg.add_line_series(
                            [1, 2, 3, 4, 5], theList, label="criticallineseries"
                        )
                        self.bindColor(
                            self.criticallineseries,
                            itemtype=dpg.mvPlotCol_Line,
                            color=(255, 0, 0, 255),
                            category=-1,
                        )
                        self.criticalshadeseries: int | str = dpg.add_shade_series(
                            [1, 2, 3, 4, 5],
                            [a * 4 for a in theList],
                            y2=[a * 3 for a in theList],
                            label="criticalshadeseries",
                        )
                        self.bindColor(
                            self.criticalshadeseries,
                            itemtype=dpg.mvPlotCol_Fill,
                            color=(255, 0, 0, 64),
                            category=-1,
                        )

                dpg.set_axis_limits_auto(self.yxax)
                dpg.set_axis_limits_auto(self.pxax)

        self.auditselectorCombo: int | str = dpg.add_combo(
            [],
            label="Select a page",
            callback=self.changeCharts,
            parent=self.siteAuditResults,
        )
        self.errorTextcritical: int | str = dpg.add_text(
            "critical errors", color=[255, 0, 0, 255], parent=self.siteAuditResults
        )
        self.errorTextmoderate: int | str = dpg.add_text(
            "moderate errors", color=[255, 255, 0, 255], parent=self.siteAuditResults
        )
        self.errorTextminor: int | str = dpg.add_text(
            "minor errors", color=[255, 255, 255, 255], parent=self.siteAuditResults
        )
        self.errorTextdonthurt: int | str = dpg.add_text(
            "donthurt errors", color=[125, 125, 125, 255], parent=self.siteAuditResults
        )

    def testNodes(self) -> None:
        self.intLinkTabBar: int | str = dpg.add_tab_bar(parent=self.internalLinkVisuals)
        self.intLinkTab0: int | str = dpg.add_tab(
            label="Internal Link Plot", parent=self.intLinkTabBar
        )
        self.intLinkTab1: int | str = dpg.add_tab(
            label="Internal Link Node", parent=self.intLinkTabBar
        )
        self.intLinkPlot: int | str = dpg.add_plot(
            label="Internal Links",
            width=-1,
            parent=self.intLinkTab0,
            anti_aliased=True,
            equal_aspects=True,
        )
        self.intLinkPlotx: int | str = dpg.add_plot_axis(
            dpg.mvXAxis,
            no_gridlines=True,
            no_tick_marks=True,
            no_tick_labels=True,
            parent=self.intLinkPlot,
        )
        self.intLinkPloty: int | str = dpg.add_plot_axis(
            dpg.mvYAxis,
            no_gridlines=True,
            no_tick_marks=True,
            no_tick_labels=True,
            parent=self.intLinkPlot,
        )
        self.generalDrawLayer: int | str = dpg.add_draw_layer(parent=self.intLinkPlot)
        self.intLinkCombo: int | str = dpg.add_combo(
            [],
            label="Select a page",
            callback=self.changeInternalLinkPlot,
            parent=self.intLinkTab0,
        )
        self.nodeEditor: int | str = dpg.add_node_editor(
            parent=self.intLinkTab1,
            callback=lambda sender, app_data: dpg.add_node_link(
                app_data[0], app_data[1], parent=sender
            ),
            delink_callback=lambda sender, app_data: dpg.delete_item(app_data),
            minimap=True,
            minimap_location=dpg.mvNodeMiniMap_Location_BottomLeft,
            menubar=True,
        )

    def changeInternalLinkPlot(self, *args, **kwargs):
        mySelection = dpg.get_value(self.intLinkCombo)
        dpg.configure_item(self.prevDrawLayer, show=False)
        if mySelection == "General":
            self.prevDrawLayer: int | str = self.generalDrawLayer
            for site in self.mySiteLinkDict.values():
                dpg.configure_item(site.myAnno, show=True)
                lastPos: tuple = site.cirPos
            dpg.set_axis_limits(self.intLinkPlotx, -1 * lastPos[0], lastPos[0])
            dpg.set_axis_limits(self.intLinkPloty, -1 * lastPos[1], lastPos[1])
            dpg.set_axis_limits_auto(self.intLinkPlotx)
            dpg.set_axis_limits_auto(self.intLinkPloty)
        else:
            for site in self.mySiteLinkDict.values():
                dpg.configure_item(site.myAnno, show=False)
            self.prevDrawLayer = self.mySiteLinkDict[mySelection].drawSendReceive(
                self.intLinkPlot
            )
            dpg.set_axis_limits(
                self.intLinkPlotx,
                self.mySiteLinkDict[mySelection].cirPos[0] - 100,
                self.mySiteLinkDict[mySelection].cirPos[0] + 100,
            )
            dpg.set_axis_limits(
                self.intLinkPloty,
                self.mySiteLinkDict[mySelection].cirPos[1] - 100,
                self.mySiteLinkDict[mySelection].cirPos[1] + 100,
            )
            # dpg.set_axis_limits_auto(self.intLinkPlotx)
            # dpg.set_axis_limits_auto(self.intLinkPloty)
        dpg.configure_item(self.prevDrawLayer, show=True)

    def startAudit(self, *args, **kwargs):
        if self.auditing:
            return
        self.auditing = True
        website, proxy = dpg.get_values((self.auditinput, self.searchProxy))
        self.auditThread = CustomThread(target=self.auditSiteMap, args=(website, proxy))
        self.auditThread.start()

    def loadingIndicator(self):
        # loader 1
        self.newVroom.doloading()
        while self.auditing:
            incmt: float = random.random()
            start = dpg.get_value(self.bseoData.loader2)
            curup: float = incmt
            settz = start + curup
            if settz > 1.0:
                settz = 1.0
            dpg.set_value(self.bseoData.loader2, settz)
            if settz == 1.0:
                dpg.set_value(self.bseoData.loader2, 0.0)
            time.sleep(random.Random().randint(1, 10) / 50)
        self.newVroom.loadzing = False
        while settz < 1.0:
            settz += 0.05
            dpg.set_value(self.bseoData.loader2, settz)
            time.sleep(0.03)

    def auditSiteMap(self, website: str, proxy: str):
        if not website.startswith("http") or not website.endswith("xml"):
            return
        webz: str = website.split("://")[1].replace("www.", "").replace("/", "_")
        fname: str = cleanFilename(webz).strip().replace("\t", "").replace("\n", "")
        self.title: str = fname
        nfname: str = f"output/sitemap_audits/{fname}.caudit"
        pool: Pool = self.bseoData.getPool()
        myT = CustomThread(target=self.loadingIndicator)
        myT.start()
        self.theMap = SiteMap(url=website, executor=pool, proxy=proxy)
        self.theMap.go()
        self.auditCompared = self.theMap.audits  # type: CompareAudit
        with open(nfname, "wb") as f:
            pickle.dump(self.auditCompared, f, pickle.HIGHEST_PROTOCOL)
        self.bseoData.saveData("siteAuditPickers", fname, self.theMap.netloc)

        self.update("WebsiteAudit", self.auditCompared)
        # self.auditing = False
        # myT.join()
        self.buildStuff()
        dpg.set_value(self.auditPicker, fname)

    def buildStuff(self) -> None:
        self.auditing = True
        myT = CustomThread(target=self.doBuild)
        myT.start()

    def doBuild(self) -> None:
        dpg.enable_item(self.iljcsvbutton)
        self.auditView.build(self.auditCompared)
        self.myComlis = self.auditCompared.toCSV()
        myT = CustomThread(target=self.siteAuditScore, args=(self.myComlis,))
        myT.start()
        dpg.delete_item(self.intLinkPlot, children_only=True)
        self.intLinkPlotx = dpg.add_plot_axis(
            dpg.mvXAxis,
            no_gridlines=True,
            no_tick_marks=True,
            no_tick_labels=True,
            parent=self.intLinkPlot,
        )
        self.intLinkPloty = dpg.add_plot_axis(
            dpg.mvYAxis,
            no_gridlines=True,
            no_tick_marks=True,
            no_tick_labels=True,
            parent=self.intLinkPlot,
        )
        mySiteTests: List[SiteTest] = list()
        for site in self.auditCompared.audits:  
            mySiteTests.append(
                SiteTest(
                    name=site.title,
                    url=site.url,
                    sendingInternal=list(site.inbound_links.keys()),
                    sendingExternal=list(site.outbound_links.keys()),
                )
            )
        posits: List[List[float]] = createCircleFromPositions(
            len(mySiteTests), len(mySiteTests) * 25
        )
        dpg.delete_item(self.nodeEditor, children_only=True)
        curColor = ColorChanger()
        for site in mySiteTests:
            curColor.changeColor()
            site.drawNode(
                parent=self.nodeEditor,
                pos=posits.pop(),
                parent2=self.intLinkPlot,
                color=curColor.color,
            )
        self.generalDrawLayer = dpg.add_draw_layer(parent=self.intLinkPlot)
        self.prevDrawLayer = self.generalDrawLayer
        self.mySiteLinkDict: Dict[str, SiteTest] = drawLinks(
            parent=self.nodeEditor, siteList=mySiteTests, parent2=self.generalDrawLayer
        )
        theList = list(self.mySiteLinkDict.keys())
        theList.insert(0, "General")
        dpg.configure_item(self.intLinkCombo, items=theList, default_value="General")
        self.auditing = False

    def siteAuditScore(self, comlist: List[dict]) -> None:
        """This is the score for the site audit. The calculation takes these things into account:
                Title, Number of H1, Article Length, Number of Headers, Number of Images,
                Number of Images with Alt Tag, Number of Images without Alt Tag, Number of Inbound Links,
                Number of Outbound Links, Meta Description Length, Meta: Twitter (True/False), Schema (True/False), URL
        Calculations will be calculated like this:
                Each piece will be given a score between 0.00 and 2.00
                Each piece will be multiplied by a weight based on importance (Ex: Multiple H1s isn't as important as missing meta description)
        """
        self.auditScore: dict[str, dict] = dict()
        self.auditScore["general"]= dict()
        self.auditScore["general"]["title"]= 0.0
        self.auditScore["general"]["h1"]= 0.0
        self.auditScore["general"]["article_length"]= 0.0
        self.auditScore["general"]["headers"]= 0.0
        self.auditScore["general"]["images"]= 0.0
        self.auditScore["general"]["images_alt"]= 0.0
        self.auditScore["general"]["images_noalt"]= 0.0
        self.auditScore["general"]["inbound_links"]= 0.0
        self.auditScore["general"]["outbound_links"]= 0.0
        self.auditScore["general"]["meta_description"]= 0.0
        self.auditScore["general"]["meta_twitter"]= 0.0
        self.auditScore["general"]["schema"]= 0.0
        self.auditScore["general"]["readability"]= 0.0
        self.auditScore["general"]["url"]= 0.0
        self.auditScore["general"]["missingz"]= 0.0
        self.auditScore["Errors"]= dict()
        self.auditScore["ErrorsTotal"]= dict()
        self.auditScore["Errors"]["critical"]= list()
        self.auditScore["Errors"]["moderate"]= list()
        self.auditScore["Errors"]["minor"]= list()
        self.auditScore["Errors"]["donthurt"]= list()
        self.auditScore["ErrorsTotal"]["critical"]= 0
        self.auditScore["ErrorsTotal"]["moderate"]= 0
        self.auditScore["ErrorsTotal"]["minor"]= 0
        self.auditScore["ErrorsTotal"]["donthurt"]= 0
        for site in comlist:
            title: str = site["Title"]
            self.url2title[site["URL"]] = title

            self.calculate_audit_score(
                site,
                title,
            )
        self.update_audit_score(comlist)

    def calculate_audit_score(
        self,
        site,
        title,
    ):
        numh1: int = site["Num H1"]
        numberhead: int = site["Number of Headers"]
        length: int = site["Length"]
        numberimg: int = site["Number of Images"]
        numberimgalt: int = site["Number of Images with Alt Text"]
        numberimgnoalt: int = site["Number of Images without Alt Text"]
        numberinbound: int = site["Number of Inbound Links"]
        numberoutbound: int = site["Number of Outbound Links"]
        metalen: int = site["Meta Description Length"]
        metatwit: bool = site["Meta:Twitter"]
        readability: float = site["Readability"]
        hasschema: bool = site["Schema"]
        theurl: str = site["URL"]
        critical: list = list()
        moderate: list = list()
        minor: list = list()
        donthurt: list = list()
        self.auditScore[theurl] = {
            "title": 0.0,
            "h1": 0.0,
            "article_length": 0.0,
            "headers": 0.0,
            "images": 0.0,
            "images_alt": 0.0,
            "images_noalt": 0.0,
            "inbound_links": 0.0,
            "outbound_links": 0.0,
            "meta_description": 0.0,
            "meta_twitter": 0.0,
            "schema": 0.0,
            "readability": 0.0,
            "url": 0.0,
            "missingz": 0.0,
            "series": [],
            "labels": [],
            "critical": critical,
            "moderate": moderate,
            "minor": minor,
            "donthurt": donthurt,
        }
        titleLen: int = len(title)
        if 30 < titleLen < 120:
            self.auditScore[theurl]["title"] += 2.0
        elif titleLen >= 120:
            moderate.append(f"Title is too long at {titleLen} characters.")
        elif titleLen <= 30:
            moderate.append(f"Title is too short at {titleLen} characters.")

        if numh1 == 1:
            self.auditScore[theurl]["h1"] += 2.0
        elif numh1 > 1:
            self.auditScore[theurl]["h1"] += 1.0
        else:
            critical.append(f"No H1.")

        maxHead = length / 50
        minHead = length / 400
        if minHead <= numberhead <= maxHead:
            self.auditScore[theurl]["headers"] += 1.0
        else:
            minor.append(
                f"Too many or too few headers. Recommended is {minHead}-{maxHead} headers."
            )

        if 300 <= length <= 5000:
            self.auditScore[theurl]["article_length"] += 2.0
        else:
            minor.append(
                f"The article is too short or too long at {length} words. Recommended is 300-5000 words."
            )

        # if 1000 <= length <= 3000:
        #     self.auditScore[theurl]["article_length"] += 1.0
        # else:
        #     donthurt.append(
        #         f"The article is too short or too long at {length} words. Recommended is 1000-3000 words."
        #     )

        if numberimg > 0:
            self.auditScore[theurl]["images"] += 2.0
            # if numberimg > 2:
            #     self.auditScore[theurl]["images"] += 1.0
            # else:
            #     moderate.append(f"Needs more images.")

        if numberimg > 0:
            self.auditScore[theurl]["images_alt"] = float(
                (numberimgalt / numberimg) * 2.0
            )
        if numberimg > 0 and numberimgnoalt == 0:
            self.auditScore[theurl]["images_noalt"] += 2.0
        if numberimgnoalt > 0 and numberimg > 0:
            self.auditScore[theurl]["images_noalt"] = 2.0 - float(
                (numberimgnoalt / numberimg) * 2.0
            )
        if numberimg == 0:
            critical.append(f"No images. Humans like media, add an image.")

        if numberimgalt < numberimg:
            critical.append(f"{numberimg - numberimgalt} images without alt text.")

        if numberinbound > 3:
            self.auditScore[theurl]["inbound_links"] += 1.0
        if numberinbound > 5:
            self.auditScore[theurl]["inbound_links"] += 1.0
        # if numberinbound < 10:
        #     critical.append(f"{numberinbound} inbound links. (Rec: 10-15+)")

        if numberoutbound > 5:
            self.auditScore[theurl]["outbound_links"] += 0.5
        if numberoutbound > 7:
            self.auditScore[theurl]["outbound_links"] += 0.5
        if numberoutbound == 0:
            critical.append(f"Needs external links")

        if metalen < 40 or metalen > 200:
            critical.append(
                f"Meta description is too short or too long at {metalen} characters. (Rec: 130-160)"
            )
        elif 40 < metalen < 200:
            self.auditScore[theurl]["meta_description"] += 1.0
        elif 60 < metalen < 195:
            self.auditScore[theurl]["meta_description"] += 1.1
        elif 70 < metalen < 190:
            self.auditScore[theurl]["meta_description"] += 1.2
        elif 80 < metalen < 185:
            self.auditScore[theurl]["meta_description"] += 1.3
        elif 90 < metalen < 180:
            self.auditScore[theurl]["meta_description"] += 1.4
        elif 100 < metalen < 175:
            self.auditScore[theurl]["meta_description"] += 1.5
        elif 110 < metalen < 170:
            self.auditScore[theurl]["meta_description"] += 1.6
        elif 120 < metalen < 165:
            self.auditScore[theurl]["meta_description"] += 1.7
        elif 130 < metalen < 160:
            self.auditScore[theurl]["meta_description"] += 2.0
        else:
            if 40 > metalen > 200:
                minor.append(
                    f"Meta description that is too short or too long at {metalen} characters. (Rec: 130-160)"
                )

        if metatwit:
            self.auditScore[theurl]["meta_twitter"] += 1.0
        else:
            donthurt.append(f"Needs a Twitter meta description")

        if readability < 18:
            self.auditScore[theurl]["readability"] += 1.0
        elif readability < 12:
            self.auditScore[theurl]["readability"] += 1.0

        if hasschema:
            self.auditScore[theurl]["schema"] += 1.0
        
        checkURL: str = str(theurl).split("://")[1]
        if "/" in checkURL: checkURL = checkURL.split("/", 1)[1]
        urlScore: float = (2.0 - float(len(checkURL) / 70)) + 1.0
        if urlScore > 2.0:
            urlScore = 2.0
        if urlScore < 0.0:
            urlScore = 0.0
            minor.append(f"URL is too long. Consider shortening for UX.")
        self.auditScore[theurl]["url"] = urlScore

        scoreList = []
        scoreLabels = []
        tot = 0.0
        for key, value in self.auditScore[theurl].items():
            if type(value) is list:
                continue
            thisScore = float(value * (1 / 22))
            tot += thisScore
            scoreList.append(thisScore)
            scoreLabels.append(f"{key} Score")
            self.auditScore["general"][key] += thisScore
        if tot > 1.0:
            tot = 1.0
        self.auditScore[theurl]["missingz"] = 1.0 - tot
        self.auditScore[theurl]["series"] = scoreList
        self.auditScore[theurl]["labels"] = scoreLabels
        self.auditScore[theurl]["critical"] = critical
        self.auditScore[theurl]["moderate"] = moderate
        self.auditScore[theurl]["minor"] = minor
        self.auditScore[theurl]["donthurt"] = donthurt

        self.auditScore["Errors"]["critical"].append(len(critical))
        self.auditScore["ErrorsTotal"]["critical"] += len(critical)
        self.auditScore["Errors"]["moderate"].append(len(moderate))
        self.auditScore["ErrorsTotal"]["moderate"] += len(moderate)
        self.auditScore["Errors"]["minor"].append(len(minor))
        self.auditScore["ErrorsTotal"]["minor"] += len(minor)
        self.auditScore["Errors"]["donthurt"].append(len(donthurt))
        self.auditScore["ErrorsTotal"]["donthurt"] += len(donthurt)

    def calculate_general_audit_score(self, comlist: List[dict]) -> None:
        numItems: int = len(comlist) or 1
        self.auditScore["general"] = {
            "title": float(self.auditScore["general"]["title"] / numItems),
            "h1": float(self.auditScore["general"]["h1"] / numItems),
            "article_length": float(
                self.auditScore["general"]["article_length"] / numItems
            ),
            "headers": float(self.auditScore["general"]["headers"] / numItems),
            "images": float(self.auditScore["general"]["images"] / numItems),
            "images_alt": float(self.auditScore["general"]["images_alt"] / numItems),
            "images_noalt": float(
                self.auditScore["general"]["images_noalt"] / numItems
            ),
            "inbound_links": float(
                self.auditScore["general"]["inbound_links"] / numItems
            ),
            "outbound_links": float(
                self.auditScore["general"]["outbound_links"] / numItems
            ),
            "meta_description": float(
                self.auditScore["general"]["meta_description"] / numItems
            ),
            "meta_twitter": float(
                self.auditScore["general"]["meta_twitter"] / numItems
            ),
            "schema": float(self.auditScore["general"]["schema"] / numItems),
            "readability": float(self.auditScore["general"]["readability"] / numItems),
            "url": float(self.auditScore["general"]["url"] / numItems),
        }
        self.auditScore["general"]["series"]= list()
        self.auditScore["general"]["labels"]= list()
        self.auditScore["general"].pop("series")
        self.auditScore["general"].pop("labels")
        miss: float = 1.0 - sum(self.auditScore["general"].values())
        labels: list[str]
        series: list[float]
        labels, series = [
            list(x)
            for x in zip(
                *[
                    (f"{key} Score", value)
                    for key, value in self.auditScore["general"].items()
                ]
            )
        ]
        self.auditScore["general"]["series"]= series
        self.auditScore["general"]["labels"]= labels
        self.auditScore["general"]["missingz"]= miss

    def update_audit_score(self, comlist: List[dict]) -> None:
        self.calculate_general_audit_score(comlist)
        scoreList = self.auditScore["general"]["series"]
        scoreLabels = self.auditScore["general"]["labels"]
        dpg.configure_item(self.sitemapPie, values=scoreList, labels=scoreLabels)

        xlist: list[int] = [
            i for i in range(0, len(self.auditScore["Errors"]["critical"]))
        ]
        donthurtGraph = [i * 5 for i in self.auditScore["Errors"].pop("donthurt")]
        minorGraph = [
            i[0] * 5 + i[1]
            for i in zip(self.auditScore["Errors"].pop("minor"), donthurtGraph)
        ]
        moderateGraph = [
            i[0] * 5 + i[1]
            for i in zip(self.auditScore["Errors"].pop("moderate"), minorGraph)
        ]
        criticalGraph = [
            i[0] * 5 + i[1]
            for i in zip(self.auditScore["Errors"].pop("critical"), moderateGraph)
        ]
        self.auditScore.pop("Errors")

        dpg.configure_item(self.donthurtlineseries, x=xlist, y=donthurtGraph)
        dpg.configure_item(self.donthurtshadeseries, x=xlist, y1=donthurtGraph)
        dpg.configure_item(self.minorlineseries, x=xlist, y=minorGraph)
        dpg.configure_item(
            self.minorshadeseries, x=xlist, y1=minorGraph, y2=donthurtGraph
        )
        dpg.configure_item(self.moderatelineseries, x=xlist, y=moderateGraph)
        dpg.configure_item(
            self.moderateshadeseries, x=xlist, y1=moderateGraph, y2=minorGraph
        )
        dpg.configure_item(self.criticallineseries, x=xlist, y=criticalGraph)
        dpg.configure_item(
            self.criticalshadeseries, x=xlist, y1=criticalGraph, y2=moderateGraph
        )

        comboList = list(self.auditScore.keys())
        comboList.remove("ErrorsTotal")
        dpg.configure_item(
            self.auditselectorCombo, items=comboList, default_value="general"
        )

        dpg.set_value(
            self.errorTextcritical,
            f"{self.auditScore['ErrorsTotal']['critical']} errors, select a page to view",
        )
        dpg.set_value(
            self.errorTextmoderate,
            f"{self.auditScore['ErrorsTotal']['moderate']} errors, select a page to view",
        )
        dpg.set_value(
            self.errorTextminor,
            f"{self.auditScore['ErrorsTotal']['minor']} errors, select a page to view",
        )
        dpg.set_value(
            self.errorTextdonthurt,
            f"{self.auditScore['ErrorsTotal']['donthurt']} errors, select a page to view",
        )
        self.newVroom.update(int(100 * (1.0 - self.auditScore["general"]["missingz"])))
        dpg.set_axis_limits(self.yxax, 0, 40)
        dpg.set_axis_limits(self.pxax, 0, len(xlist))

    def changeCharts(self, *args, **kwargs):
        theMap = dpg.get_value(self.auditselectorCombo)
        dpg.configure_item(
            self.sitemapPie,
            values=self.auditScore[theMap]["series"],
            labels=self.auditScore[theMap]["labels"],
        )

        self.newVroom.update((1.0 - self.auditScore[theMap]["missingz"]) * 100)
        if theMap == "general":
            return
        dpg.set_value(
            self.errorTextcritical, "\n".join(self.auditScore[theMap]["critical"])
        )
        dpg.set_value(
            self.errorTextmoderate, "\n".join(self.auditScore[theMap]["moderate"])
        )
        dpg.set_value(self.errorTextminor, "\n".join(self.auditScore[theMap]["minor"]))
        dpg.set_value(
            self.errorTextdonthurt, "\n".join(self.auditScore[theMap]["donthurt"])
        )

    def createILJCSV(self):
        dpg.disable_item(self.iljcsvbutton)
        myNetLoc = self.bseoData.loaddata(
            "siteAuditPickers", dpg.get_value(self.auditPicker)
        )
        if not myNetLoc:
            return
        else:
            _ = CustomThread(target=self._createILJCSV, args=(myNetLoc,))
            _.start()

    def _createILJCSV(self, myNetLoc: str) -> None:
        self.posts, self.pages = SiteMap.get_WP_ids(myNetLoc)
        postswithID = dict()
        pageswithID = dict()
        allIDs = dict()
        for post in self.posts:
            allIDs[post["id"]] = post["link"]
            postswithID[post["id"]] = post["title"]["rendered"]
        for page in self.pages:
            allIDs[page["id"]] = page["link"]
            pageswithID[page["id"]] = page["title"]["rendered"]
        tempclus = self.auditCompared.cluster
        commonkw = list(self.auditCompared.common_keywords.keys())
        tempNewb = dict()
        # ID ; Type ; Keywords (ILJ) ; Title ; URL
        for postid, linkz in allIDs.items():
            if linkz in tempclus:
                tempNewb[postid] = dict()
                tempNewb[postid]["id"] = postid
                if postid in postswithID:
                    tempNewb[postid]["type"] = "Post"
                    tempNewb[postid]["title"] = postswithID[postid]
                else:
                    tempNewb[postid]["type"] = "Page"
                    tempNewb[postid]["title"] = pageswithID[postid]
                tempNewb[postid]["keywords"] = set()
                tempNewb[postid]["url"] = linkz
                tempNewb[postid]["tempKWs"] = tempclus[linkz].article_keywords
                tempNewb[postid]["keywords"].add(tempclus[linkz].main_keyword)
        gotkw = set()
        loops = 0
        seenbefore = list()
        while len(commonkw):
            kw = commonkw.pop(0)
            seenbefore.append(kw)
            gonext = False
            for postid in allIDs.keys():
                if postid not in tempNewb:
                    continue
                if kw in tempNewb[postid]["tempKWs"] and postid not in gotkw:
                    if len(tempNewb[postid]["keywords"]) > 4:
                        continue
                    tempNewb[postid]["keywords"].add(kw)
                    gotkw.add(postid)
                    if len(gotkw) > 5:
                        gonext = True
                        #break
            if gonext:
                continue
            commonkw.append(kw)
            if kw in seenbefore:
                loops += 1
                gotkw = set()
                if loops > 10:
                    break
            continue
        # for page in tempNewb:
        #     if len(page["keywords"]) < 1 and len(page["tempKWs"]) > 0:
        
        self.tempNewb = tempNewb
        outputPath: str = self.bseoData.backSEOSettings.agencyOutput
        with open(f"{outputPath}/{myNetLoc}ILJ.csv", "w") as f:
            f.write('"ID";"Type";"Keywords (ILJ)";"Title";"Url"\n')
            for postid, data in tempNewb.items():
                f.write(
                    f'"{postid}";"{data["type"]}";"{",".join(data["keywords"])}";"{data["title"]}";"{data["url"]}"\n'
                )
        dpg.enable_item(self.iljcsvbutton)


    def updateUData(self):
        if self.oldList == self.auditedList:
            return
        else:
            self.oldList = self.auditedList.copy()
            dpg.configure_item(self.auditPicker, items=self.auditedList)

    def update(self, piece, data):
        if piece == "WebsiteAudit":
            self.load_data()
            dpg.configure_item(self.auditPicker, items=self.auditedList)

    def loadAudit(self, *args, **kwargs):
        self.title = dpg.get_value(self.auditPicker)
        with open(
            f"output/sitemap_audits/{dpg.get_value(self.auditPicker)}.caudit", "rb"
        ) as f:
            myj = pickle.load(f)
        self.audit = myj
        self.auditCompared = myj
        dpg.set_value(self.bseoData.strLoader2, dpg.get_value(self.auditPicker))
        # print(f"building {self.audit}")
        self.buildStuff()
        # self.auditView.build(self.audit)

    def _createAllAuditReport(self, *args, **kwargs):
        self.createAllAuditReport()

    def createAllAuditReport(
        self, sitemap: str = "", client: str = "", *args, **kwargs
    ):
        theMap = dpg.get_value(self.auditselectorCombo)
        if not theMap or theMap not in self.auditScore:
            return
        width = dpg.get_viewport_width()
        height = dpg.get_viewport_height()
        w, h = (425, 425)
        tableWin = dpg.add_window(show=False, width=10000, height=10000)
        # tblcw = dpg.add_child_window(parent=tableWin, autosize_x=True, autosize_y=True)
        tblGrp = dpg.add_group(parent=tableWin)
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
        myT = CustomThread(target=self.auditView.createTheTable, args=(barchartTable,))
        myT.start()
        with dpg.window(width=w, height=h, autosize=True, no_scrollbar=True) as tempwin:
            sitemapPie, auditPie = self.createGenericPie(
                [0, 1], ["", ""], parent=tempwin
            )
        w = dpg.get_item_width(auditPie)
        h = dpg.get_item_height(auditPie) + 25
        # print(w, h)
        with dpg.theme() as tempTheme:
            with dpg.theme_component():
                dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_CellPadding, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0)
                dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 0)
        with dpg.theme() as tempPlotTheme:
            with dpg.theme_component():
                dpg.add_theme_style(
                    dpg.mvPlotStyleVar_PlotBorderSize, 0, category=dpg.mvThemeCat_Plots
                )
                dpg.add_theme_style(
                    dpg.mvPlotStyleVar_PlotPadding, 0, 0, category=dpg.mvThemeCat_Plots
                )
                dpg.add_theme_style(
                    dpg.mvPlotStyleVar_LabelPadding, 0, 0, category=dpg.mvThemeCat_Plots
                )
                dpg.add_theme_style(
                    dpg.mvPlotStyleVar_LegendInnerPadding,
                    0,
                    0,
                    category=dpg.mvThemeCat_Plots,
                )
                dpg.add_theme_style(
                    dpg.mvPlotStyleVar_LegendPadding,
                    0,
                    0,
                    category=dpg.mvThemeCat_Plots,
                )
                dpg.add_theme_style(
                    dpg.mvPlotStyleVar_LegendSpacing,
                    0,
                    0,
                    category=dpg.mvThemeCat_Plots,
                )
                # dpg.add_theme_style(dpg.mvPlotStyleVar_, 0, 0, category=dpg.mvThemeCat_Plots)
        dpg.bind_item_theme(tempwin, tempTheme)
        dpg.bind_item_theme(sitemapPie, tempPlotTheme)
        dpg.bind_item_theme(auditPie, tempPlotTheme)
        w = dpg.get_item_width(auditPie)
        h = dpg.get_item_height(auditPie)
        # print(f"{w} {h}")
        dpg.set_viewport_width(w)
        dpg.set_viewport_height(h)
        siteAuditReport = dict()
        title = self.title
        if self.title.startswith("http"):
            title = title.split("://")[1]
        if "sitemap" in title:
            title = title.split("sitemap")[0]
        if title.endswith("/") or title.endswith("_"):
            title = title[:-1]
        siteAuditReport["baseURL"] = title
        siteAuditReport[
            "directory"
        ] = f"{self.bseoData.getSettings().agencyOutput}/reports/sitemaps/{self.title}"
        auditReports = list()
        siteAuditReport["criticalerrors"] = 0
        siteAuditReport["moderateerrors"] = 0
        siteAuditReport["minorerrors"] = 0
        siteAuditReport["suggestions"] = 0
        doGeneral = False
        for i in list(self.auditScore.keys()):
            if i == "ErrorsTotal":
                if "critical" in self.auditScore["ErrorsTotal"]:
                    siteAuditReport["criticalerrors"] = self.auditScore["ErrorsTotal"][
                        "critical"
                    ]
                if "moderate" in self.auditScore["ErrorsTotal"]:
                    siteAuditReport["moderateerrors"] = self.auditScore["ErrorsTotal"][
                        "moderate"
                    ]
                if "minor" in self.auditScore["ErrorsTotal"]:
                    siteAuditReport["minorerrors"] = self.auditScore["ErrorsTotal"][
                        "minor"
                    ]
                if "donthurt" in self.auditScore["ErrorsTotal"]:
                    siteAuditReport["suggestions"] = self.auditScore["ErrorsTotal"][
                        "donthurt"
                    ]
                continue
            if i == "general":
                doGeneral = True
            labels = self.auditScore[i]["labels"]
            values = self.auditScore[i]["series"]
            auditReport = dict()
            auditReport["url"] = i
            if i in self.url2title:
                auditReport["title"] = self.url2title[i]
            else:
                auditReport["title"] = i
            if "critical" in self.auditScore[i]:
                auditReport["errorTextcritical"] = "\n".join(
                    self.auditScore[i]["critical"]
                )
            if "moderate" in self.auditScore[i]:
                auditReport["errorTextmoderate"] = "\n".join(
                    self.auditScore[i]["moderate"]
                )
            if "minor" in self.auditScore[i]:
                auditReport["errorTextminor"] = "\n".join(self.auditScore[i]["minor"])
            if "donthurt" in self.auditScore[i]:
                auditReport["errorTextdonthurt"] = "\n".join(
                    self.auditScore[i]["donthurt"]
                )
            dpg.configure_item(sitemapPie, values=values, labels=labels)
            dpg.configure_item(auditPie, label=auditReport["title"])
            self.tempVroom.updateinstant((1.0 - self.auditScore[i]["missingz"]) * 100)
            # dpg.split_frame()
            dpg.render_dearpygui_frame()
            dpg.configure_item(self.real_primary_window, show=False)
            dpg.set_primary_window(self.real_primary_window, False)
            dpg.configure_item(tempwin, show=True)
            dpg.set_primary_window(tempwin, True)
            dpg.configure_item(tempwin, no_scrollbar=True)
            # dpg.set_item_pos(self.auditView.leftSectioncw, (-10,-10))
            dpg.render_dearpygui_frame()
            # time.sleep(0.001)
            dpg.render_dearpygui_frame()
            outpath = f"output/reports/sitemaps/{self.title}/{cleanFilename(i)}.png"
            if i == "general":
                siteAuditReport["generalImage"] = outpath
            else:
                auditReport["image"] = outpath
            if not os.path.exists(os.path.dirname(outpath)):
                os.makedirs(os.path.dirname(outpath))
            dpg.output_frame_buffer(outpath)
            # dpg.reset_pos(self.auditView.leftSectioncw)
            dpg.render_dearpygui_frame()
            # dpg.configure_item(tempwin, show=False)
            # dpg.set_primary_window(tempwin, False)
            # dpg.configure_item(self.real_primary_window, show=True)
            # dpg.set_primary_window(self.real_primary_window, True)
            dpg.render_dearpygui_frame()
            if i == "general":
                continue
            found = False
            for c in self.myComlis:
                if auditReport["title"] == c["Title"]:
                    auditReport["comlist"] = c
                    found = True
                    break
            auditReport["hascomlist"] = found
            auditReports.append(auditReport)
        siteAuditReport["auditReports"] = auditReports
        if doGeneral:
            dpg.delete_item(tempwin, children_only=True)
            i = "general"
            auditPie = self.createGenericErrors(tempwin)
            dpg.bind_item_theme(tempwin, tempTheme)
            dpg.bind_item_theme(auditPie, tempPlotTheme)
            w = dpg.get_item_width(auditPie)
            h = dpg.get_item_height(auditPie)
            # print(f"{w} {h}")
            dpg.set_viewport_width(w)
            dpg.set_viewport_height(h)
            # self.tempVroom.updateinstant((1.0 - self.auditScore[i]["missingz"])*100)
            dpg.render_dearpygui_frame()
            dpg.configure_item(self.real_primary_window, show=False)
            dpg.set_primary_window(self.real_primary_window, False)
            dpg.set_primary_window(tempwin, True)
            dpg.configure_item(tempwin, show=True)
            dpg.configure_item(tempwin, no_scrollbar=True)
            # dpg.set_item_pos(self.auditView.leftSectioncw, (-10,-10))
            dpg.render_dearpygui_frame()
            time.sleep(0.001)
            dpg.render_dearpygui_frame()
            outpath = (
                f"output/reports/sitemaps/{self.title}/{cleanFilename(i)}errors.png"
            )
            siteAuditReport["errorsimg"] = outpath
            if not os.path.exists(os.path.dirname(outpath)):
                os.makedirs(os.path.dirname(outpath))
            dpg.render_dearpygui_frame()
            dpg.output_frame_buffer(outpath)
            dpg.render_dearpygui_frame()
            dpg.configure_item(tempwin, show=False)
            dpg.configure_item(tableWin, show=True)
            # dpg.set_primary_window(tableWin, True)
            dpg.render_dearpygui_frame()
            time.sleep(0.2)
            dpg.render_dearpygui_frame()
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

            outpath = (
                f"output/reports/sitemaps/{self.title}/{cleanFilename(i)}table.png"
            )
            siteAuditReport["tableimg"] = outpath
            if not os.path.exists(os.path.dirname(outpath)):
                os.makedirs(os.path.dirname(outpath))
            dpg.render_dearpygui_frame()
            dpg.output_frame_buffer(outpath)
            dpg.render_dearpygui_frame()
            dpg.configure_item(tableWin, show=False)
            dpg.set_primary_window(tableWin, False)
            dpg.configure_item(tempwin, show=False)
        siteAuditReport["clientName"] = client
        self.bseoData.siteAuditReportAdd(siteAuditReport, client)
        dpg.set_viewport_width(width)
        dpg.set_viewport_height(height)
        dpg.configure_item(self.real_primary_window, show=True)
        dpg.set_primary_window(self.real_primary_window, True)
        dpg.delete_item(tempwin)
        dpg.delete_item(tableWin)

    def createAuditReport(self, *args, **kwargs):
        theMap = dpg.get_value(self.auditselectorCombo)
        if not theMap or theMap not in self.auditScore:
            return
        tempwin = dpg.add_window()
        oldp = dpg.get_item_parent(self.auditView.leftSectioncw)
        labels = self.auditScore[theMap]["labels"]
        values = self.auditScore[theMap]["series"]
        sitemapPie = self.createGenericPie(values, labels, parent=tempwin)
        self.tempVroom.updateinstant((1.0 - self.auditScore[theMap]["missingz"]) * 100)
        dpg.render_dearpygui_frame()
        dpg.configure_item(self.real_primary_window, show=False)
        dpg.set_primary_window(self.real_primary_window, False)
        dpg.set_primary_window(tempwin, True)
        # print("Primary set")
        # dpg.set_item_pos(self.auditView.leftSectioncw, (-10,-10))
        dpg.render_dearpygui_frame()
        # print("Frame Rendered 1")
        time.sleep(0.3)
        dpg.render_dearpygui_frame()
        # print("Frame Rendered 2")
        dpg.output_frame_buffer("testoutput.png")
        # print("Output")
        # dpg.reset_pos(self.auditView.leftSectioncw)
        # dpg.move_item(self.auditView.leftSectioncw, parent=oldp)
        dpg.configure_item(self.real_primary_window, show=True)
        # print("Showing win")
        dpg.delete_item(tempwin)
        # print("Deleted tempwin")
        dpg.set_primary_window(self.real_primary_window, True)
        # print("Primary set")
        dpg.render_dearpygui_frame()

    def createPieandErrors(self, pieV, pieL, p):
        with dpg.subplots(
            rows=1,
            columns=2,
            width=800,
            height=400,
            label="Site Audit Scores",
            pos=(0, 0),
            parent=p,
        ) as subp:
            self.createGenericPie(pieV, pieL, subp)
            self.createGenericErrors(subp)
        return subp

    def createGenericPie(self, values, labels, parent):
        with dpg.plot(
            label="Page Score",
            height=400,
            width=400,
            anti_aliased=True,
            equal_aspects=True,
            parent=parent,
            indent=0,
            no_child=True,
            no_mouse_pos=True,
        ) as auditPie:
            self.tempVroom = PlotVroom(
                (300, 270), parent=auditPie, radius1=35, radius2=55, text="Score"
            )
            leg = dpg.add_plot_legend()
            xax = dpg.add_plot_axis(
                dpg.mvXAxis, no_gridlines=True, no_tick_marks=True, no_tick_labels=True
            )
            dpg.set_axis_limits(xax, -125, 450)
            with dpg.plot_axis(
                dpg.mvYAxis, no_gridlines=True, no_tick_labels=True, no_tick_marks=True
            ) as yax:
                sitemapPie = dpg.add_pie_series(
                    200.5,
                    400.5,
                    200.5,
                    values=values,
                    labels=labels,
                    format="",
                    angle=0,
                )
            dpg.set_axis_limits(yax, 125, 650)

        return sitemapPie, auditPie

    def createGenericErrors(self, parent):
        donthurtline = dpg.get_value(self.donthurtlineseries)
        donthurtshade = dpg.get_value(self.donthurtshadeseries)
        minorline = dpg.get_value(self.minorlineseries)
        minorshade = dpg.get_value(self.minorshadeseries)
        moderateline = dpg.get_value(self.moderatelineseries)
        moderateshade = dpg.get_value(self.moderateshadeseries)
        criticalline = dpg.get_value(self.criticallineseries)
        criticalshade = dpg.get_value(self.criticalshadeseries)
        with dpg.plot(
            label="Error Chart",
            height=400,
            width=400,
            anti_aliased=True,
            equal_aspects=True,
            parent=parent,
        ) as auditErr:
            pxax = dpg.add_plot_axis(dpg.mvXAxis)
            with dpg.plot_axis(dpg.mvYAxis) as yxax:
                theList = [5, 4, 3, 4, 5]
                donthurtlineseries = dpg.add_line_series(
                    donthurtline[0], donthurtline[1], label="donthurtlineseries"
                )
                minorlineseries = dpg.add_line_series(
                    minorline[0], minorline[1], label="minorlineseries"
                )
                moderatelineseries = dpg.add_line_series(
                    moderateline[0], moderateline[1], label="moderatelineseries"
                )
                criticallineseries = dpg.add_line_series(
                    criticalline[0], criticalline[1], label="criticallineseries"
                )
                donthurtshadeseries = dpg.add_shade_series(
                    donthurtshade[0],
                    donthurtshade[1],
                    y2=donthurtshade[2],
                    label="donthurtshadeseries",
                )
                minorshadeseries = dpg.add_shade_series(
                    minorshade[0],
                    minorshade[1],
                    y2=minorshade[2],
                    label="minorshadeseries",
                )
                moderateshadeseries = dpg.add_shade_series(
                    moderateshade[0],
                    moderateshade[1],
                    y2=moderateshade[2],
                    label="moderateshadeseries",
                )
                criticalshadeseries = dpg.add_shade_series(
                    criticalshade[0],
                    criticalshade[1],
                    y2=criticalshade[2],
                    label="criticalshadeseries",
                )
                self.bindColor(
                    minorshadeseries,
                    itemtype=dpg.mvPlotCol_Fill,
                    color=(32, 50, 165, 64),
                    category=-1,
                )
                self.bindColor(
                    moderatelineseries,
                    itemtype=dpg.mvPlotCol_Line,
                    color=(150, 250, 20, 255),
                    category=-1,
                )
                self.bindColor(
                    minorlineseries,
                    itemtype=dpg.mvPlotCol_Line,
                    color=(32, 50, 165, 255),
                    category=-1,
                )
                self.bindColor(
                    donthurtshadeseries,
                    itemtype=dpg.mvPlotCol_Fill,
                    color=(125, 125, 125, 64),
                    category=-1,
                )
                self.bindColor(
                    donthurtlineseries,
                    itemtype=dpg.mvPlotCol_Line,
                    color=(125, 125, 125, 255),
                    category=-1,
                )
                self.bindColor(
                    moderateshadeseries,
                    itemtype=dpg.mvPlotCol_Fill,
                    color=(150, 250, 20, 64),
                    category=-1,
                )
                self.bindColor(
                    criticallineseries,
                    itemtype=dpg.mvPlotCol_Line,
                    color=(255, 0, 0, 255),
                    category=-1,
                )
                self.bindColor(
                    criticalshadeseries,
                    itemtype=dpg.mvPlotCol_Fill,
                    color=(255, 0, 0, 64),
                    category=-1,
                )

            dpg.set_axis_limits_auto(yxax)
            dpg.set_axis_limits_auto(pxax)
            dpg.set_axis_limits(yxax, 0, 40)
            dpg.set_axis_limits(pxax, 0, len(criticalline[0]))
        return auditErr

    def saveImg(self, s, thedat):
        dpg.save_image(
            "testoutput.png",
            dpg.get_item_width(self.auditView.leftSectioncw),
            dpg.get_item_height(self.auditSubPlot),
            thedat,
        )
        with dpg.texture_registry():
            lol = dpg.add_static_texture(
                dpg.get_item_width(self.auditView.leftSectioncw),
                dpg.get_item_height(self.auditSubPlot),
                thedat,
            )
        with dpg.viewport_drawlist():
            dpg.draw_image(
                lol,
                [0, 0],
                [
                    dpg.get_item_width(self.auditView.leftSectioncw),
                    dpg.get_item_height(self.auditSubPlot),
                ],
            )


def getProx(p: str = ""):
    global wproxy
    wproxy = p
