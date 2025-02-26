from BackSEOSettings import BackSEOSettings
import regex
import os
import aiohttp
import dearpygui.dearpygui as dpg
import inspect
import time
import concurrent.futures
import multiprocessing
from multiprocessing import Queue, pool
import threading
from typing import Any, Dict, List, Union


from BackSEODataHandler import *
from core import BackSEOApp
from core_ui import InspectResults as _InspectResults, Audit as _Audit
from core_ui import Core_UI
from SEO import Local as _Local
from SEO.Agency import Agency as _Agency
from FlaskApp import FlaskApp as _FlaskApp
# import cython


class BackSEOApplicationManager:
    _app: BackSEOApp
    InspectResults: _InspectResults.CoreInspectResults
    Audit: _Audit.CoreAudit
    Local: _Local.Local
    Agency: _Agency
    FlaskApp: _FlaskApp

    def __init__(self) -> None:
        self._app = BackSEOApp()
        # self.Editor = Editor.CoreEditor()
        self.InspectResults = _InspectResults.CoreInspectResults()
        self.Audit = _Audit.CoreAudit()
        self.Local = _Local.Local()
        self.Agency = _Agency()
        self.FlaskApp = _FlaskApp(self.Agency)
        self.FlaskApp.run(debug=False)

        self.modules: Dict[str, Core_UI] = dict()
        self.tabs: Dict[str, int | str] = dict()
        self.menus: Dict[str, int | str] = dict()
        self.windows: Dict[str, int | str] = dict()
        self.commandQ: List[str] = list()
        self.commandQDone: List[str] = list()
        self.commandQC: List[str] = list()

        self.curCommand: str = ""

        self.doRunCommands: bool = False
        self.commandComplete: bool = False
        self.commandRunning: bool = False

        self.backDataHandler: BackSEODataHandler = getBackSEODataHandler()
        self.modules["Core"] = self._app
        self.modules["Agency"] = self.Agency
        # self.modules["Editor"]			= self.Editor
        self.modules["InspectResults"] = self.InspectResults
        self.modules["Audit"] = self.Audit
        self.modules["Local"] = self.Local
        self.addQueues()
        self._app.run()
        self.setTabs()
        self.setMenus()
        self.setWindows()
        self.mainTab: int | str = self._app.mainTabBar

    def addQueues(self) -> None:
        for name, module in self.modules.items():
            module.add_queues(self.commandQ)

    def setTabs(self) -> None:
        for name, module in self.modules.items():
            self.tabs[name] = module.create_tab(self._app.mainTabBar, self._app.options)
            module.addRealPrimaryWindow(self._app.backSEOCoreWin)

    def setMenus(self) -> None:
        for name, module in self.modules.items():
            self.menus[name] = module.create_menu(
                self._app.mainMenu, before=self._app.toolsMenu
            )

    def setWindows(self) -> None:
        for name, module in self.modules.items():
            self.windows[name] = module.create_window()

    def updateUDatas(self) -> None:
        for name, module in self.modules.items():
            module.updateUData()

    def update(self, piece: str, data: Any) -> None:
        for name, module in self.modules.items():
            module.update(piece, data)

    def running_animation(self) -> None:
        # r: cython.double
        # g: cython.double
        # b: cython.double
        # a: cython.double
        # directi: cython.int
        # y: cython.int
        # transparency: cython.int
        # i: cython.int
        if not self.doRunCommands:
            return
        transparency = 0
        myText: int | str = dpg.draw_text(
            text="Automating...",
            pos=(0, 0),
            color=[255, 255, 255, transparency],
            parent=self._app.animations,
            size=20,
        )
        direction = 3
        myballs = list()

        r, g, b, a = (0, 0, 0, 255)
        y = 0
        directi = 1
        for i in range(20):
            if i % 3 == 0:
                r += 3
                g += 27
                b += 5
            elif i % 3 == 1:
                r += 56
                g += 22
                b += 1
            elif i % 3 == 2:
                r += 19
                b += 2
                g += 3
            if r > 255:
                r = i / 2
            if g > 255:
                g = i / 3
            if b > 255:
                b = i / 4
            y += directi
            if y > 26:
                directi = -1
            elif y < 0:
                directi = 1
            myballs.append(
                dpg.draw_circle(
                    center=(i * 5 + 170, y),
                    radius=2,
                    user_data=(i * 5 + 170, y, i % 3, 1, (r, g, b, a)),
                    color=[r, g, b, a],
                    fill=[r, g, b, a],
                    parent=self._app.animations,
                )
            )

        while dpg.is_dearpygui_running() and self.doRunCommands:
            transparency += direction
            if transparency > 254:
                direction = -3
            elif transparency < 1:
                direction = 3
            if transparency > 200:
                theText = "Automating..."
            elif transparency > 140:
                theText = "Automating.."
            elif transparency > 100:
                theText = "Automating."
            else:
                theText = "Automating"
            dpg.configure_item(
                myText, text=theText, color=[255, 255, 255, transparency]
            )
            for ball in myballs:
                self.doUpDown(ball)
            time.sleep(0.03)
        # dpg.render_dearpygui_frame()
        dpg.delete_item(self._app.animations, children_only=True)

    def doUpDown(self, item: int | str) -> None:
        # x: cython.int
        # y: cython.int
        # i: cython.int
        # verti: cython.int
        # c: tuple
        # r: cython.double
        # g: cython.double
        # b: cython.double
        # a: cython.double
        x, y, i, verti, c = dpg.get_item_user_data(item)
        x += 10
        if x > 700:
            x = 170
        if y > 26:
            verti = -1
        elif y < 0:
            verti = 1
        y += verti
        r, g, b, a = c
        if i % 3 == 0:
            r += 3
            g += 27
            b += 5
        elif i % 3 == 1:
            r += 56
            g += 22
            b += 1
        elif i % 3 == 2:
            r += 19
            b += 2
            g += 3
        if r > 255:
            r = i / 2
        if g > 255:
            g = i / 3
        if b > 255:
            b = i / 4
        dpg.configure_item(
            item,
            center=(x, y),
            color=[r, g, b, a],
            fill=[r, g, b, a],
            user_data=(x, y, i, verti, (r, g, b, a)),
        )

    def runCommands(self, *args, **kwargs) -> None:
        """
        This function runs the commands in the command queue.
        The command queue is a list of tuples that automate the core UI
        It only runs one command per frame cycle and won't run the next until it
        is confirmed complete. This is to prevent the UI from freezing.
        There are helper functions that make the process a lot easier. They are:
                - swapTab
                - inputSearch (
                        InspectResults: searchkeyword, searchProxy, numResult	-> startSearch	-> createSearchReport
                        Audit: auditInput, searchProxy							-> startAudit	-> createAllAuditReport
                        Local: localKeyword, proxy, localLocation, nodeDistance	-> updateMap	-> outputFrame
                )
                - generateFullReport
        """
        if "START RUNNING" in self.commandQ:
            self.doRunCommands = True
            myT = threading.Thread(target=self.running_animation)
            myT.start()
            self.commandQ.remove("START RUNNING")
            # print("START RUNNING")
        if "STOP" in self.commandQ:
            self.doRunCommands = False
            self.commandQ.remove("STOP")
            # print("STOP")
            return
        if "JUST ANIMATIONS" in self.commandQ:
            return
        if "RUN ANIMATIONS" in self.commandQ:
            self.commandQ.remove("RUN ANIMATIONS")
            self.commandQ.append("JUST ANIMATIONS")
            self.doRunCommands = True
            myT = threading.Thread(target=self.running_animation)
            myT.start()
            # print("RUN ANIMATIONS")
            return
        if self.doRunCommands:
            if self.commandRunning:
                if self.InspectResults.searching:
                    return
                elif self.Audit.auditing:
                    return
                elif self.Local.locked:
                    return
                else:
                    self.commandComplete = True
                    self.doCommand(self.curCommand)
                    self.commandRunning = False
                    self.curCommand = ""
                    self.commandQDone.append(self.curCommand)
                    return
            if len(self.commandQ) > 0:
                if len(self.commandQC) == 0:
                    self.commandQC = self.commandQ.copy()
                    self.commandQC.reverse()
                self.curCommand = self.commandQC.pop()
                if len(self.commandQC) == 0:
                    self.doRunCommands = False

                self.doCommand(self.curCommand)

    def doCommand(self, command: str, *args, **kwargs) -> None:
        # print("Entered Do Command")
        commandparts: list[str] = command.split("|")
        if commandparts[0] == "swapTab":
            # print("Swapping Tab")
            self.swapTab(commandparts[1])
        elif commandparts[0] == "inputSearchInspectResults":
            self.inputSearchInspectResults(
                commandparts[1],
                commandparts[2],
                int(commandparts[3]),
                commandparts[4],
                commandparts[5],
            )
        elif commandparts[0] == "inputSearchAudit":
            self.inputSearchAudit(commandparts[1], commandparts[2], commandparts[3])
        elif commandparts[0] == "inputSearchLocal":
            self.inputSearchLocal(
                commandparts[1],
                commandparts[2],
                commandparts[3],
                commandparts[4],
                commandparts[5],
            )
        elif commandparts[0] == "FINALIZE":
            self.Agency.finalizeReport(commandparts[1])

    def swapTab(self, tabName: str, *args, **kwargs) -> None:
        """
        This function swaps the tab to the tabName passed in.
        Example:
                swapTab("Audit")
        """
        if tabName in self.tabs:
            dpg.set_value(self._app.mainTabBar, self.tabs[tabName])

    def inputSearchInspectResults(
        self,
        searchkeyword: str,
        searchProxy: str,
        numResult: int,
        client: str = "",
        clientSite: str = "",
    ) -> None:
        """
        This function inputs the searchkeyword, searchProxy, and numResult into the InspectResults tab.
        Example:
                inputSearchInspectResults("keyword", "proxy", 100)
        """
        if not self.commandRunning:
            # print(f"searchkeyword: {searchkeyword}, searchProxy: {searchProxy}, numResult: {numResult}")
            dpg.set_value(self.InspectResults.searchkeyword, searchkeyword)
            dpg.set_value(self.InspectResults.searchProxy, searchProxy)
            dpg.set_value(self.InspectResults.numResult, numResult)
            self.InspectResults.startSearch()
            self.commandRunning = True
        else:
            # print(f"Creating Search Report for {searchkeyword}")
            self.InspectResults.createSearchReport(searchkeyword, client, clientSite)
            if not self.commandRunning and not self.doRunCommands:
                self.Agency.finalizeReport()

        # Audit: auditInput, searchProxy							-> startAudit	-> createAllAuditReport
        # Local: localKeyword, proxy, localLocation, nodeDistance	-> updateMap	-> outputFrame

    def inputSearchAudit(
        self, auditInput: str, searchProxy: str, client: str = ""
    ) -> None:
        """
        This function inputs the auditInput and searchProxy into the Audit tab.
        Example:
                inputSearchAudit("keyword", "proxy")
        """
        if not self.commandRunning:
            # print(f"auditInput: {auditInput}, searchProxy: {searchProxy}")
            dpg.set_value(self.Audit.auditinput, auditInput)
            dpg.set_value(self.Audit.searchProxy, searchProxy)
            self.Audit.startAudit()
            self.commandRunning = True
        else:
            # print(f"Creating Audit Report for {auditInput} {client}")
            self.Audit.createAllAuditReport(auditInput, client)
            if not self.commandRunning and not self.doRunCommands:
                self.Agency.finalizeReport()

    def inputSearchLocal(
        self,
        localKeyword: str,
        proxy: str,
        localLocation: str,
        nodeDistance: str,
        client: str = "",
    ) -> None:
        """
        This function inputs the localKeyword, proxy, localLocation, and nodeDistance into the Local tab.
        Example:
                inputSearchLocal("keyword", "proxy", "location", "distance")
        """
        if not self.commandRunning:
            # print(f"localKeyword: {localKeyword}, proxy: {proxy}, localLocation: {localLocation}, nodeDistance: {nodeDistance}")
            dpg.set_value(self.Local.localKeyword, localKeyword)
            dpg.set_value(self.Local.proxy, proxy)
            dpg.set_value(self.Local.localLocation, localLocation)
            dpg.set_value(self.Local.nodeDistance, nodeDistance)
            self.Local.updateMap()
            self.commandRunning = True
        else:
            # print(f"Creating Local Report for {localKeyword} {client}")
            businesses = self.Local.allBusinesses
            clientFound = False
            if client != "":
                if client in businesses:
                    dpg.set_value(self.Local.businessBox, client)
                    clientFound = True
                else:
                    for business in businesses:
                        if client in business:
                            dpg.set_value(self.Local.businessBox, business)
                            clientFound = True
                            break
            if not clientFound:
                return
            self.Local.outputFrame(zoom=nodeDistance, client=client)
            if not self.commandRunning and not self.doRunCommands:
                self.Agency.finalizeReport()
