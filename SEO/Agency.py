import re
from Plugins import Plugin
from core_ui import Core_UI
import dearpygui.dearpygui as dpg
from BackSEOSettings import user_local_dir
from SEO.Resources import ReportCreator
from SEO.Resources.ReportCreator import SEOAgency
from SEO.Resources.ReportCreator import SEOClient
import pickle
import os
import Utils
import xdialog

from typing import Dict, List


class Agency(Core_UI):
    """
    Plugin: Agency
    This is the agency screen. It is a part of the SEO folder of the application.
    It is a plugin currently for testing, will be removed later.

    The purpose of this module is to allow the user to manage their agency's settings.
    This includes:
            - Agency Name
            - Agency Logo
            - Agency Address
            - Agency Phone Number
            - Agency Email
            - Agency Website
            - Agency Social Media
            - Agency Employees
            - Agency Clients
                    - Client Name
                    - Client Address
                    - Client Phone Number
                    - Client Logo
                    - Client Website
                    - Client Social Media
                    - Client Target Keywords
                    - Client Target Locations
    On top of holding the information for agency and client, this module will also:
            - Generate reports for clients
    """

    def __init__(self) -> None:
        plugin_name = "Plugin"
        author = "author"
        info = "What does the plugin do?"
        # self.bseoData.bseoObjects["coreUI"]["Audit"].createAllAuditReport()
        self.agency: SEOAgency
        self.openAgencyWin: bool = True
        if os.path.exists(user_local_dir() / "seo.agency"):
            with open(user_local_dir() / "seo.agency", "rb") as f:
                self.agency = pickle.load(f)
                self.openAgencyWin = False
        else:
            self.agency = SEOAgency()
        self.agencyTextures: int | str = dpg.add_texture_registry(
            label="Agency Textures"
        )
        self.agencyLogo: int | str = Utils.load_dpg_img(
            self.agency.company_logo, self.agencyTextures
        )
        self.clientLogos: Dict[str, int | str | None] = dict()
        if len(self.agency.clients) > 0:
            for client in self.agency.clients.values():
                if client.client_logo != "" and client.client_logo is not None:
                    # print(client.client_logo)
                    self.clientLogos[client.client_name] = Utils.load_dpg_img(
                        client.client_logo, self.agencyTextures
                    )
                else:
                    self.clientLogos[client.client_name] = None
        self.clientList: List[str] = list(self.agency.clients.keys())
        self.oldList: List[str] = list()
        self.runningCommands: Dict[str, str] = dict()
        self.preq: Dict[str, list] = dict()
        self.covers = dict()
        self.setSelector: str = ""
        self.tempLogo = None
        self.bseoData.setAgency(self.agency)
        self.firstFrameRendered: bool = False

    def __binit__(self) -> None:
        pass

    def save_data(self) -> None:
        pass

    def load_data(self) -> None:
        pass

    def updateUData(self) -> None:
        # print("Here")
        if self.oldList != self.clientList:
            # print("Updating Client List")
            dpg.configure_item(self.clientSelector, items=self.clientList)
            if len(self.setSelector):
                dpg.configure_item(self.clientSelector, default_value=self.setSelector)
                self.selectClient()
            self.setSelector = ""
            self.oldList = self.clientList
        if not self.firstFrameRendered:
            dpg.configure_item(
                self.coverTitleText,
                pos=(200 - dpg.get_text_size("Report Cover")[0] / 2, 0),
            )
            self.firstFrameRendered = True

    def update(self, piece, data) -> None:
        pass

    def _create_menu(self, parent, before) -> int | str:
        backMenu: int | str
        with dpg.menu(label="Agency", parent=parent, before=before) as backMenu:
            dpg.add_menu_item(label="Your Agency", callback=self.editAgency)
            dpg.add_menu_item(
                label="Start Generating Reports", callback=self.start_reports
            )
            dpg.add_menu_item(
                label="Stop Generating Reports", callback=self.stop_reports
            )
        return backMenu

    def start_reports(self, *args, **kwargs) -> None:
        if len(self.preq) == 0:
            return
        self.jobq.clear()
        for val in self.preq.values():
            for command in val:
                self.jobq.append(command)
        self.jobq.append("START RUNNING")

    def stop_reports(self, *args, **kwargs) -> None:
        self.jobq.append("STOP")

    def _create_tab(self, parent, befor) -> int | str:
        backTab: int | str
        with dpg.tab(label="Agency", parent=parent, before=befor) as backTab:
            with dpg.child_window(height=75):
                dpg.add_text("Add or Select a Client")
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Add Client", callback=self.addClient)
                    self.clientSelector: int | str = dpg.add_combo(
                        [], label="Select Client", width=200, callback=self.selectClient
                    )
                    dpg.add_button(label="Edit Client", callback=self.editClient)

            with dpg.group(horizontal=True):
                with dpg.child_window(width=200, height=200) as self.primaryAgencycw:
                    dpg.add_text(self.agency.company_name)
                    dpg.add_image(self.agencyLogo, width=100, height=100)
                    dpg.add_text("Your Agency")
                with dpg.child_window(width=600, height=200):
                    dpg.add_text(self.agency.company_address)
                    dpg.add_text(self.agency.company_phone)
                    dpg.add_text(self.agency.company_email)
                    dpg.add_text(self.agency.company_website)
                with dpg.child_window(
                    width=200, height=200
                ) as self.clientDisplayLogocw:
                    self.clientDisplay: int | str = dpg.add_text(
                        "Select A Client", wrap=0
                    )
                    self.clientDisplayLogo: int | str = dpg.add_image(
                        self.agencyLogo, width=100, height=100
                    )
                    dpg.add_text("Selected Client")

            with dpg.child_window(width=-1, height=-1):
                with dpg.group(horizontal=True):
                    with dpg.child_window(width=200, height=-1):
                        dpg.add_text("Target Keywords")
                        self.clientKeywordDisplay: int | str = dpg.add_listbox(
                            label="", items=[], num_items=5
                        )
                        dpg.add_text("Target Locations")
                        self.clientLocationDisplay: int | str = dpg.add_listbox(
                            label="", items=[], num_items=5
                        )
                    with dpg.child_window(width=400, height=-1):
                        self.checkTargetKeywords: int | str = dpg.add_checkbox(
                            label="Target Keywords (Search, No location included)"
                        )
                        self.checkTargetLocations: int | str = dpg.add_checkbox(
                            label="Target Keywords (Search, Location Included)"
                        )
                        self.checkTargetMaps1: int | str = dpg.add_checkbox(
                            label="Target Keywords (Maps, 1mi)"
                        )
                        self.checkTargetMaps2: int | str = dpg.add_checkbox(
                            label="Target Keywords (Maps, 2mi)"
                        )
                        self.checkTargetMaps5: int | str = dpg.add_checkbox(
                            label="Target Keywords (Maps, 5mi)"
                        )
                        self.checkTargetMaps15: int | str = dpg.add_checkbox(
                            label="Target Keywords (Maps, 15mi)"
                        )
                        self.checkTargetMaps25: int | str = dpg.add_checkbox(
                            label="Target Keywords (Maps, 25mi)"
                        )
                        self.checkTargetMaps50: int | str = dpg.add_checkbox(
                            label="Target Keywords (Maps, 50mi)"
                        )
                        self.checkWebsiteAudit: int | str = dpg.add_checkbox(
                            label="Website Audit"
                        )
                        self.proxyBox: int | str = dpg.add_input_text(
                            label="Proxy", default_value=""
                        )
                        dpg.add_button(
                            label="Add to Report Automation",
                            callback=self.generateReport,
                        )
                        dpg.add_button(
                            label="Start Generating Reports",
                            callback=self.start_reports,
                        )

                    with dpg.child_window(width=400, height=-1):
                        self.coverTitleText: int | str = dpg.add_text("Report Cover")
                        dpg.add_text("Title")
                        self.reportTitle: int | str = dpg.add_input_text(
                            default_value="SEO Report"
                        )
                        dpg.add_text("Subtitle")
                        self.reportSubtitle: int | str = dpg.add_input_text(
                            default_value="SEO Report Subtitle"
                        )
                        dpg.add_text("Footer (Left)")
                        self.reportFooterLeft: int | str = dpg.add_input_text(
                            default_value="Report for CLIENT"
                        )
                        dpg.add_text("Footer (Center)")
                        self.reportFooterCenter: int | str = dpg.add_input_text(
                            default_value="Your Key to Success"
                        )
                        dpg.add_text("Footer (Right)")
                        self.reportFooterRight: int | str = dpg.add_input_text(
                            default_value="View Report -->"
                        )
                        dpg.add_button(
                            label="Upload Report Cover", callback=self.uploadReportCover
                        )
                        # self.animations = dpg.add_button(label="Animations", callback=lambda: self.jobq.append("RUN ANIMATIONS"))
                        self.reportCovercw: int | str = dpg.add_child_window(
                            width=375, height=-1
                        )
                        self.reportCover = ""
                    with dpg.group():
                        self.commandListBox = dpg.add_listbox(
                            list(self.runningCommands.keys()), num_items=10, width=-1
                        )
                        dpg.add_button(
                            label="Remove Report", callback=self.removeReportAutomation
                        )

        return backTab

    def _create_window(self) -> int:
        self.add_windows()
        return 0

    def add_windows(self) -> None:
        w: float
        h: float
        center: tuple[float, float]
        w, h = (dpg.get_viewport_width() / 2, dpg.get_viewport_height() * 5 / 6)
        center = (dpg.get_viewport_width() / 2, dpg.get_viewport_height() / 2)
        self.add_agency_win(w, h, center)
        self.add_client_win(w, h, center)
        self.createLoadFileDialog(w, h, center)
        self.createSaveFileDialog(w, h, center)

    def add_client_win(self, w, h, center) -> None:
        """
        - Client Name (str)
        - Client Address (str)
        - Client Phone Number (str)
        - Client Logo (str)
        - Client Website (str)
        - Client Social Media (dict)
        - Client Target Keywords (list)
        - Client Target Locations (list)
        """
        with dpg.window(
            label="Add Client",
            width=w,
            height=h,
            no_collapse=True,
            show=False,
            pos=(center[0] - w / 2, center[1] - h / 2),
        ) as self.clientWin:
            dpg.add_button(
                label="Close",
                callback=lambda: dpg.configure_item(self.clientWin, show=False),
            )
            with dpg.group(horizontal=True):
                self.clientName = dpg.add_input_text(
                    label="", default_value="Client Name"
                )
                dpg.add_text("Client Name")
            with dpg.group(horizontal=True):
                self.clientAddress = dpg.add_input_text(
                    label="", default_value="Client Address"
                )
                dpg.add_text("Client Address")
            with dpg.group(horizontal=True):
                self.clientPhone = dpg.add_input_text(
                    label="", default_value="Client Phone Number"
                )
                dpg.add_text("Client Phone Number")
            with dpg.group(horizontal=True):
                self.clientEmail = dpg.add_input_text(
                    label="", default_value="Client Email"
                )
                dpg.add_text("Client Email")
            with dpg.group(horizontal=True):
                self.clientWebsite = dpg.add_input_text(
                    label="", default_value="Client Website"
                )
                dpg.add_text("Client Website")
            with dpg.group(horizontal=True):
                self.clientWebsitesitemap = dpg.add_input_text(
                    label="", default_value="https://clientsite.com/sitemap.xml"
                )
                dpg.add_text("Client Sitemap")
            with dpg.tree_node(label="Client Social Media"):
                with dpg.group(horizontal=True):
                    self.clientFacebook = dpg.add_input_text(
                        label="", default_value="Facebook"
                    )
                    dpg.add_text("Facebook")
                with dpg.group(horizontal=True):
                    self.clientTwitter = dpg.add_input_text(
                        label="", default_value="Twitter"
                    )
                    dpg.add_text("Twitter")
                with dpg.group(horizontal=True):
                    self.clientInstagram = dpg.add_input_text(
                        label="", default_value="Instagram"
                    )
                    dpg.add_text("Instagram")
            with dpg.tree_node(label="Client Target Keywords"):
                with dpg.group(horizontal=True):
                    self.clientKeywords = dpg.add_input_text(
                        label="", default_value="Client Target Keywords"
                    )
                    with dpg.group():
                        b = dpg.add_button(
                            label="Add", user_data={}, callback=self.add_keywords
                        )
                        tempRemoveButton = dpg.add_button(
                            label="Remove", user_data={}, callback=self.remove_keywords
                        )
                self.clientKeywordListbox = dpg.add_listbox(
                    label="", items=[], num_items=5
                )
                dpg.set_item_user_data(
                    b,
                    {
                        "input": self.clientKeywords,
                        "listbox": self.clientKeywordListbox,
                    },
                )
                dpg.set_item_user_data(
                    tempRemoveButton,
                    {
                        "input": self.clientKeywords,
                        "listbox": self.clientKeywordListbox,
                    },
                )
            with dpg.tree_node(label="Client Target Locations"):
                with dpg.group(horizontal=True):
                    self.clientLocation = dpg.add_input_text(
                        label="", default_value="Client Locations"
                    )
                    with dpg.group():
                        b = dpg.add_button(
                            label="Add", user_data={}, callback=self.add_keywords
                        )
                        tempRemveButton = dpg.add_button(
                            label="Remove", user_data={}, callback=self.remove_keywords
                        )

                self.clientLocationBox = dpg.add_listbox(
                    label="", items=[], num_items=5
                )
                dpg.set_item_user_data(
                    b, {"input": self.clientLocation, "listbox": self.clientLocationBox}
                )
                dpg.set_item_user_data(
                    tempRemveButton,
                    {"input": self.clientLocation, "listbox": self.clientLocationBox},
                )
            self.clientLogo: str = ""
            dpg.add_button(label="Upload Client Logo", callback=self.uploadClientLogo)

            dpg.add_button(label="Save Client", callback=self.saveClient)
            self.clientLogocw = dpg.add_child_window(
                width=w - 30, height=h - 30, no_scrollbar=True
            )

    def loadclientFile(self, sender, fileData, cancelButton, *args, **kwargs) -> None:
        if not cancelButton:
            self.loadFile(sender, fileData, "client")

    def add_agency_win(self, w, h, center) -> None:
        with dpg.window(
            label="Agency",
            width=w,
            height=h,
            no_collapse=True,
            show=self.openAgencyWin,
            pos=(center[0] - w / 2, center[1] - h / 2),
        ) as self.agencyWin:
            dpg.add_button(
                label="Close",
                callback=lambda: dpg.configure_item(self.agencyWin, show=False),
            )
            with dpg.group(horizontal=True):
                dpg.add_text("Agency Name")
                self.agencyName: int | str = dpg.add_input_text(
                    label="", default_value=self.agency.company_name
                )
            with dpg.group(horizontal=True):
                dpg.add_text("Agency Address")
                self.agencyAddress = dpg.add_input_text(
                    label="", default_value=self.agency.company_address
                )
            with dpg.group(horizontal=True):
                dpg.add_text("Agency Phone Number")
                self.agencyPhone: int | str = dpg.add_input_text(
                    label="", default_value=self.agency.company_phone
                )
            with dpg.group(horizontal=True):
                dpg.add_text("Agency Email")
                self.agencyEmail: int | str = dpg.add_input_text(
                    label="", default_value=self.agency.company_email
                )
            with dpg.group(horizontal=True):
                dpg.add_text("Agency Website")
                self.agencyWebsite: int | str = dpg.add_input_text(
                    label="", default_value=self.agency.company_website
                )
            with dpg.group(horizontal=True):
                dpg.add_text("Agency Logo")

                dpg.add_button(
                    label="Upload Agency Logo", callback=self.uploadAgencyLogo
                )
                self.agencyLogoPathText: int | str = dpg.add_input_text(
                    default_value=self.agency.company_logo, readonly=True
                )
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Change Output Directory",
                    callback=self.setSavePath,
                    # callback=self.saveFile,
                )

                self.outputPath: int | str = dpg.add_input_text(
                    default_value=self.agency.output_directory, readonly=True
                )
            dpg.add_button(label="Save Agency", callback=self.saveAgency)
            self.agencyLogocw: int | str = dpg.add_child_window(
                width=130, height=130, no_scrollbar=True
            )
            dpg.add_image(
                self.agencyLogo, parent=self.agencyLogocw, width=100, height=100
            )

    def loadAgencyFile(self, sender, fileData, cancelButton, *args, **kwargs) -> None:
        if not cancelButton:
            self.loadFile(sender, fileData, "agency")

    def removeReportAutomation(self, *args, **kwargs) -> None:
        selected = dpg.get_value(self.commandListBox)
        if selected in self.runningCommands:
            del self.runningCommands[selected]
            del self.preq[selected]
            dpg.configure_item(
                self.commandListBox, items=list(self.runningCommands.keys())
            )

    def generateReport(self) -> None:
        client: str
        reportTitle: str
        reportSubtitle: str
        reportFooterLeft: str
        reportFooterCenter: str
        reportFooterRight: str
        reportCover: str
        proxy: str
        clientString: str
        client = dpg.get_value(self.clientDisplay)
        if client not in self.clientList:
            return
        reportTitle = dpg.get_value(self.reportTitle)
        reportSubtitle = dpg.get_value(self.reportSubtitle)
        reportFooterLeft = dpg.get_value(self.reportFooterLeft)
        reportFooterCenter = dpg.get_value(self.reportFooterCenter)
        reportFooterRight = dpg.get_value(self.reportFooterRight)
        reportCover = self.reportCover
        self.agency.clients[client].reportTitle = reportTitle
        self.agency.clients[client].reportSubtitle = reportSubtitle
        self.agency.clients[client].reportFooterLeft = reportFooterLeft
        self.agency.clients[client].reportFooterCenter = reportFooterCenter
        self.agency.clients[client].reportFooterRight = reportFooterRight
        self.agency.clients[client].reportCover = reportCover
        self.agency.save()
        self.masterReportCover = ReportCreator.SEOReport(
            agency=self.agency,
            title=reportTitle,
            subtitle=reportSubtitle,
            coverImage=reportCover,
            footerLeft=reportFooterLeft,
            footerCenter=reportFooterCenter,
            footerRight=reportFooterRight,
        )
        self.masterReportCover.coverPage()
        self.masterReportCover.coverHeaderFooter()
        proxy = dpg.get_value(self.proxyBox)
        self.covers[client] = self.masterReportCover
        self.masterReportCover.save(client)
        clientString = client
        self.preq[client] = list()
        if dpg.get_value(self.checkTargetKeywords):
            self.preq[client].append(f"swapTab|InspectResults")
            clientString += " Sk"
            for kw in dpg.get_item_configuration(self.clientKeywordDisplay)["items"]:
                self.preq[client].append(
                    f"inputSearchInspectResults|{kw}|{proxy}|25|{client}|{self.agency.clients[client].client_website}"
                )
        if dpg.get_value(self.checkTargetLocations):
            self.preq[client].append(f"swapTab|InspectResults")
            clientString += " Sl"
            for kw in dpg.get_item_configuration(self.clientKeywordDisplay)["items"]:
                for location in dpg.get_item_configuration(self.clientLocationDisplay)[
                    "items"
                ]:
                    self.preq[client].append(
                        f"inputSearchInspectResults|{kw} in {location}|{proxy}|25|{client}|{self.agency.clients[client].client_website}"
                    )
        if dpg.get_value(self.checkTargetMaps1):
            self.preq[client].append(f"swapTab|Local")
            clientString += " L5"
            for kw in dpg.get_item_configuration(self.clientKeywordDisplay)["items"]:
                for location in dpg.get_item_configuration(self.clientLocationDisplay)[
                    "items"
                ]:
                    self.preq[client].append(
                        f"inputSearchLocal|{kw}|{proxy}|{location}|1|{client}"
                    )
        if dpg.get_value(self.checkTargetMaps2):
            self.preq[client].append(f"swapTab|Local")
            clientString += " L5"
            for kw in dpg.get_item_configuration(self.clientKeywordDisplay)["items"]:
                for location in dpg.get_item_configuration(self.clientLocationDisplay)[
                    "items"
                ]:
                    self.preq[client].append(
                        f"inputSearchLocal|{kw}|{proxy}|{location}|2|{client}"
                    )
        if dpg.get_value(self.checkTargetMaps5):
            self.preq[client].append(f"swapTab|Local")
            clientString += " L5"
            for kw in dpg.get_item_configuration(self.clientKeywordDisplay)["items"]:
                for location in dpg.get_item_configuration(self.clientLocationDisplay)[
                    "items"
                ]:
                    self.preq[client].append(
                        f"inputSearchLocal|{kw}|{proxy}|{location}|5|{client}"
                    )
        if dpg.get_value(self.checkTargetMaps15):
            self.preq[client].append(f"swapTab|Local")
            clientString += " L15"
            for kw in dpg.get_item_configuration(self.clientKeywordDisplay)["items"]:
                for location in dpg.get_item_configuration(self.clientLocationDisplay)[
                    "items"
                ]:
                    self.preq[client].append(
                        f"inputSearchLocal|{kw}|{proxy}|{location}|15|{client}"
                    )
        if dpg.get_value(self.checkTargetMaps25):
            self.preq[client].append(f"swapTab|Local")
            clientString += " L25"
            for kw in dpg.get_item_configuration(self.clientKeywordDisplay)["items"]:
                for location in dpg.get_item_configuration(self.clientLocationDisplay)[
                    "items"
                ]:
                    self.preq[client].append(
                        f"inputSearchLocal|{kw}|{proxy}|{location}|25|{client}"
                    )
        if dpg.get_value(self.checkTargetMaps50):
            self.preq[client].append(f"swapTab|Local")
            clientString += " L50"
            for kw in dpg.get_item_configuration(self.clientKeywordDisplay)["items"]:
                for location in dpg.get_item_configuration(self.clientLocationDisplay)[
                    "items"
                ]:
                    self.preq[client].append(
                        f"inputSearchLocal|{kw}|{proxy}|{location}|50|{client}"
                    )
        if dpg.get_value(self.checkWebsiteAudit):
            self.preq[client].append(f"swapTab|Audit")
            clientString += " A"
            self.preq[client].append(
                f"inputSearchAudit|{self.agency.clients[client].client_website_sitemap}|{proxy}|{client}"
            )
        self.preq[client].append(f"FINALIZE|{client}")
        # self.jobq.append("START RUNNING")
        self.runningCommands[client] = clientString
        dpg.configure_item(self.commandListBox, items=list(self.runningCommands.keys()))

    def finalizeReport(self, client) -> None:
        siteAuds = list()
        localAuds = list()
        searchAuds = list()
        # print("FINALIZING")
        if client in self.bseoData.siteAuditReports:
            siteAuds: List[str] = self.bseoData.siteAuditReports[client]
        if client in self.bseoData.localReports:
            localAuds: List[str] = self.bseoData.localReports[client]
        if client in self.bseoData.searchReports:
            searchAuds: List[str] = self.bseoData.searchReports[client]
        ReportCreator.createMasterReport(
            self.agency,
            self.covers[client],
            localAuds,
            searchAuds,
            siteAuds,
            client,
        )

    def createLoadFileDialog(self, w, h, center, *args, **kwargs) -> None:
        homedir: str = os.path.expanduser("~")
        self.loadFileDialog = dpg.add_file_dialog(
            callback=self.loadFile,
            cancel_callback=self.cancelCallback,
            width=w,
            height=h,
            default_path=homedir,
            show=False,
            directory_selector=False,
            file_count=1,
        )
        dpg.add_file_extension(
            "Image (*.png *.jpg *.jpeg *.bmp *.psd *.gif *.hdr *.pic *.ppm *.pgm){.png,.jpg,.jpeg,.bmp,.psd,.gif,.hdr,.ppm,.pgm}",
            color=(0, 255, 0, 255),
            parent=self.loadFileDialog,
        )
        dpg.add_file_extension(".jpeg, .jpg", parent=self.loadFileDialog)
        dpg.add_file_extension(".png", parent=self.loadFileDialog)
        dpg.add_file_extension(".bmp", parent=self.loadFileDialog)
        dpg.add_file_extension(".psd", parent=self.loadFileDialog)
        dpg.add_file_extension(".gif", parent=self.loadFileDialog)
        dpg.add_file_extension(".hdr", parent=self.loadFileDialog)
        dpg.add_file_extension(".pic", parent=self.loadFileDialog)
        dpg.add_file_extension(".ppm", parent=self.loadFileDialog)
        dpg.add_file_extension(".pgm", parent=self.loadFileDialog)

    def createSaveFileDialog(self, w, h, center, *args, **kwargs) -> None:
        homedir: str = os.path.expanduser("~")
        self.saveFileDialog: int | str = dpg.add_file_dialog(
            callback=self.setSavePath,
            cancel_callback=self.cancelCallback,
            width=w,
            height=h,
            default_path=homedir,
            show=False,
            directory_selector=True,
        )

    def cancelCallback(self, *args, **kwargs) -> None:
        return

    def loadFile(self, sender, app_data, user_data, *args, **kwargs) -> None:
        # sender: int | str
        # app_data: dict (file_path_name, file_name, current_path, current_filter, min_size, max_size, selections)
        # user_data: literal["agency", "client"]
        # print(f"sender: {sender}, app_data: {app_data}, user_data: {user_data}")
        if app_data["file_name"] == ".":
            return
        if user_data == "client":
            self.clientLogo = app_data["file_path_name"]
            self.tempLogo = Utils.load_dpg_img(
                app_data["file_path_name"], self.agencyTextures
            )
            dpg.delete_item(self.clientLogocw, children_only=True)
            dpg.add_image(
                self.tempLogo, parent=self.clientLogocw, width=100, height=100
            )
        elif user_data == "agency":
            self.agencyLogoPath = app_data["file_path_name"]
            dpg.set_value(self.agencyLogoPathText, app_data["file_path_name"])
            self.tempLogo = Utils.load_dpg_img(
                app_data["file_path_name"], self.agencyTextures
            )
            dpg.delete_item(self.agencyLogocw, children_only=True)
            dpg.add_image(
                self.tempLogo, parent=self.agencyLogocw, width=100, height=100
            )
        elif user_data == "report":
            self.reportCover = app_data["file_path_name"]
            self.tempCover = Utils.load_dpg_img(
                app_data["file_path_name"], self.agencyTextures
            )
            dpg.delete_item(self.reportCovercw, children_only=True)
            dpg.add_image(
                self.tempCover, parent=self.reportCovercw, width=200, height=200
            )

    def setSavePath(self, sender, app_data, user_data, *args, **kwargs) -> None:
        # print(f"sender: {sender}, app_data: {app_data}, user_data: {user_data}")
        outputPath: str = xdialog.directory("Select Output Directory")
        if outputPath != "" and outputPath is not None and outputPath != ".":
            dpg.set_value(self.outputPath, outputPath)

    def editAgency(self, *args, **kwargs) -> None:
        dpg.configure_item(self.agencyWin, show=True)

    def saveAgency(self, *args, **kwargs) -> None:
        name: str = dpg.get_value(self.agencyName)
        address: str = dpg.get_value(self.agencyAddress)
        phone: str = dpg.get_value(self.agencyPhone)
        email: str = dpg.get_value(self.agencyEmail)
        website: str = dpg.get_value(self.agencyWebsite)
        outputPath: str = dpg.get_value(self.outputPath)
        self.agency.company_name = name
        self.agency.company_address = address
        self.agency.company_phone = phone
        self.agency.company_email = email
        self.agency.company_website = website
        self.agency.company_logo = dpg.get_value(self.agencyLogoPathText)
        self.agency.output_directory = outputPath
        self.agency.save()
        self.bseoData.backSEOSettings.changeAgencyOutput(outputPath)
        if self.tempLogo is not None and self.tempLogo != "":
            dpg.delete_item(self.primaryAgencycw, children_only=True)
            dpg.add_image(
                self.tempLogo, parent=self.primaryAgencycw, width=100, height=100
            )
        dpg.add_text(self.agency.company_name, parent=self.primaryAgencycw)
        dpg.configure_item(self.agencyWin, show=False)

    def addClient(self, *args, **kwargs) -> None:
        dpg.set_value(self.clientName, "")
        dpg.set_value(self.clientAddress, "")
        dpg.set_value(self.clientPhone, "")
        dpg.set_value(self.clientWebsite, "")
        dpg.set_value(self.clientWebsitesitemap, "")
        dpg.set_value(self.clientFacebook, "")
        dpg.set_value(self.clientTwitter, "")
        dpg.set_value(self.clientInstagram, "")
        dpg.set_value(self.clientKeywords, "")
        dpg.set_value(self.clientLocation, "")
        self.clientLogo = ""
        dpg.configure_item(self.clientKeywordListbox, items=[])
        dpg.configure_item(self.clientLocationBox, items=[])
        dpg.configure_item(self.clientWin, show=True)

    def editClient(self, *args, **kwargs) -> None:
        selected: str = dpg.get_value(self.clientSelector)
        client: SEOClient = self.agency.clients[selected]
        dpg.set_value(self.clientName, client.client_name)
        dpg.set_value(self.clientAddress, client.client_address)
        dpg.set_value(self.clientPhone, client.client_phone)
        dpg.set_value(self.clientWebsite, client.client_website)
        dpg.set_value(self.clientWebsitesitemap, client.client_website_sitemap)
        dpg.set_value(self.clientFacebook, client.client_social_media["Facebook"])
        dpg.set_value(self.clientTwitter, client.client_social_media["Twitter/X"])
        dpg.set_value(self.clientInstagram, client.client_social_media["Insta"])
        dpg.set_value(self.clientKeywords, "")
        dpg.set_value(self.clientLocation, "")
        self.clientLogo = client.client_logo
        dpg.configure_item(
            self.clientKeywordListbox, items=client.client_target_keywords
        )
        dpg.configure_item(self.clientLocationBox, items=client.client_target_locations)
        if self.clientLogo is not None and self.clientLogo != "":
            dpg.delete_item(self.clientLogocw, children_only=True)
            dpg.add_image(
                self.clientLogos[client.client_name],
                parent=self.clientLogocw,
                width=100,
                height=100,
            )
        dpg.configure_item(self.clientWin, show=True)

    def saveClient(self, *args, **kwargs) -> None:
        kws: list = dpg.get_item_configuration(self.clientKeywordListbox)["items"]
        locs: list = dpg.get_item_configuration(self.clientLocationBox)["items"]
        socials: dict[str, str] = {
            "Facebook": dpg.get_value(self.clientFacebook),
            "Twitter/X": dpg.get_value(self.clientTwitter),
            "Insta": dpg.get_value(self.clientInstagram),
        }
        client = SEOClient(
            dpg.get_value(self.clientName),
            dpg.get_value(self.clientAddress),
            dpg.get_value(self.clientPhone),
            self.clientLogo,
            dpg.get_value(self.clientEmail),
            dpg.get_value(self.clientWebsite),
            dpg.get_value(self.clientWebsitesitemap),
            socials,
            kws,
            locs,
        )
        self.agency.addClient(client)
        self.agency.save()
        self.clientList = list(self.agency.clients.keys())
        if self.tempLogo is not None:
            self.clientLogos[client.client_name] = self.tempLogo
        self.setSelector = client.client_name
        dpg.configure_item(self.clientWin, show=False)

    def uploadAgencyLogo(self, *args, **kwargs) -> None:
        agencyLogo: str = xdialog.open_file(
            title="Select Agency Logo",
            filetypes=[
                (
                    "Image Files",
                    "*.jpeg *.jpg *.png *.bmp *.psd *.gif *.hdr *.pic *.ppm *.pgm",
                ),
                (".jpeg", "*.jpeg *.jpg"),
                (".jpg", "*.jpg"),
                (".png", "*.png"),
                (".bmp", "*.bmp"),
                (".psd", "*.psd"),
                (".gif", "*.gif"),
                (".hdr", "*.hdr"),
                (".pic", "*.pic"),
                (".ppm", "*.ppm"),
                (".pgm", "*.pgm"),
            ],
        )
        if agencyLogo == "" or agencyLogo is None or agencyLogo == ".":
            return
        self.agencyLogoPath: str = agencyLogo
        dpg.set_value(self.agencyLogoPathText, agencyLogo)
        self.tempLogo: int | str = Utils.load_dpg_img(agencyLogo, self.agencyTextures)
        dpg.delete_item(self.agencyLogocw, children_only=True)
        dpg.add_image(self.tempLogo, parent=self.agencyLogocw, width=100, height=100)
        # dpg.configure_item(self.loadFileDialog, show=True)
        # dpg.set_item_user_data(self.loadFileDialog, "agency")

    def uploadClientLogo(self, *args, **kwargs) -> None:
        clientLogo: str = xdialog.open_file(
            title="Select Client Logo",
            filetypes=[
                (
                    "Image Files",
                    "*.jpeg *.jpg *.png *.bmp *.psd *.gif *.hdr *.pic *.ppm *.pgm",
                ),
                (".jpeg", "*.jpeg *.jpg"),
                (".jpg", "*.jpg"),
                (".png", "*.png"),
                (".bmp", "*.bmp"),
                (".psd", "*.psd"),
                (".gif", "*.gif"),
                (".hdr", "*.hdr"),
                (".pic", "*.pic"),
                (".ppm", "*.ppm"),
                (".pgm", "*.pgm"),
            ],
        )
        if clientLogo == "" or clientLogo is None or clientLogo == ".":
            return

        self.clientLogo = clientLogo
        self.tempLogo = Utils.load_dpg_img(clientLogo, self.agencyTextures)
        dpg.delete_item(self.clientLogocw, children_only=True)
        dpg.add_image(self.tempLogo, parent=self.clientLogocw, width=100, height=100)
        # dpg.configure_item(self.loadFileDialog, show=True)
        # dpg.set_item_user_data(self.loadFileDialog, "client")

    def uploadReportCover(self, *args, **kwargs) -> None:
        reportCover: str = xdialog.open_file(
            title="Select Report Cover",
            filetypes=[
                (
                    "Image Files",
                    "*.jpeg *.jpg *.png *.bmp *.psd *.gif *.hdr *.pic *.ppm *.pgm",
                ),
                (".jpeg", "*.jpeg *.jpg"),
                (".jpg", "*.jpg"),
                (".png", "*.png"),
                (".bmp", "*.bmp"),
                (".psd", "*.psd"),
                (".gif", "*.gif"),
                (".hdr", "*.hdr"),
                (".pic", "*.pic"),
                (".ppm", "*.ppm"),
                (".pgm", "*.pgm"),
            ],
        )
        self.changeReportCover(reportCover)

    def changeReportCover(self, reportCover: str) -> None:
        if reportCover == "" or reportCover is None or reportCover == ".":
            return
        self.reportCover: str = reportCover
        self.tempCover: int | str = Utils.load_dpg_img(reportCover, self.agencyTextures)
        dpg.delete_item(self.reportCovercw, children_only=True)
        dpg.add_image(self.tempCover, parent=self.reportCovercw, width=200, height=200)
        # dpg.configure_item(self.loadFileDialog, show=True)
        # dpg.set_item_user_data(self.loadFileDialog, "report")

    def add_keywords(self, s, a, u, *args, **kwargs) -> None:
        newKW: str = dpg.get_value(u["input"])
        kws: list = dpg.get_item_configuration(u["listbox"])["items"]
        kws.append(newKW)
        dpg.configure_item(u["listbox"], items=kws)
        dpg.set_value(u["input"], "")

    def remove_keywords(self, s, a, u, *args, **kwargs) -> None:
        kws: list = dpg.get_item_configuration(u["listbox"])["items"]
        kws.remove(dpg.get_value(u["listbox"]))
        dpg.configure_item(u["listbox"], items=kws)

    def selectClient(self, *args, **kwargs) -> None:
        clientName: str = dpg.get_value(self.clientSelector)
        client: SEOClient = self.agency.clients[clientName]
        dpg.set_value(self.clientDisplay, client.client_name)
        dpg.configure_item(
            self.clientLocationDisplay, items=client.client_target_locations
        )
        dpg.configure_item(
            self.clientKeywordDisplay, items=client.client_target_keywords
        )
        if client.client_logo is not None and client.client_logo != "":
            dpg.delete_item(self.clientDisplayLogo)
            self.clientDisplayLogo = dpg.add_image(
                self.clientLogos[client.client_name],
                parent=self.clientDisplayLogocw,
                width=100,
                height=100,
            )
        try:
            dpg.set_value(self.reportTitle, client.reportTitle)
            dpg.set_value(self.reportSubtitle, client.reportSubtitle)
            dpg.set_value(self.reportFooterLeft, client.reportFooterLeft)
            dpg.set_value(self.reportFooterCenter, client.reportFooterCenter)
            dpg.set_value(self.reportFooterRight, client.reportFooterRight)
            self.changeReportCover(client.reportCover)
        except:
            dpg.set_value(self.reportFooterLeft, f"Report for {client.client_name}")
