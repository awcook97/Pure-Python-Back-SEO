from core_ui import Core_UI
from core_ui.Widgets import Add_Info
from SEO.Resources._LocalSyncTracker import runLocations
import dearpygui.dearpygui as dpg
from Utils._Scraperz import CustomThread
import Utils
from SEO.Resources.dearpygui_map import MapWidget
import time
import os


# http://sdze:wFqK@5.78.106.79:51791
class Local(Core_UI):
    def __init__(self) -> None:
        self.locked = False
        self.bseoData.addtovpresize(self._resize_vp)
        self.allBusinesses = list()
        self.zoom = 10
        with dpg.value_registry() as self.reg:
            self.keyword = dpg.add_string_value()
            self.location = dpg.add_string_value()
            self.proxyreg = dpg.add_string_value()

    def __binit__(self):
        pass

    def save_data(self):
        pass

    def load_data(self):
        pass

    def _create_menu(self, parent, *args, **kwargs):
        # with dpg.menu(label="Inspect Results", parent=parent, before=plug) as self.theMenu:
        return 0

    def _resize_vp(self):
        dpg.set_item_width(self.theWindow, dpg.get_viewport_width() * 3 / 4)
        dpg.set_item_width(self.infoCW, dpg.get_viewport_width() / 4)
        dpg.set_item_width(
            self.myMap.dpgval, dpg.get_item_width(self.theWindow) * 7 / 8
        )
        dpg.set_item_height(
            self.myMap.dpgval, dpg.get_item_height(self.theWindow) * 7 / 8
        )

    def _create_tab(self, parent, plug):
        with dpg.tab(label="Local SEO Map", parent=parent, before=plug) as self.theTab:
            with dpg.group(horizontal=True, horizontal_spacing=-1, xoffset=0.0):
                with dpg.child_window(
                    height=dpg.get_viewport_height() * 3 / 4,
                    menubar=False,
                    width=dpg.get_viewport_width() * 3 / 4,
                ) as self.theWindow:
                    self.myMap = MapWidget(
                        width=dpg.get_item_width(self.theWindow) * 7 / 8,
                        height=dpg.get_item_height(self.theWindow) * 7 / 8,
                        center=(41.360125, -71.62285),
                        zoom_level=10,
                        parent=self.theWindow,
                    )
                with dpg.child_window(
                    width=dpg.get_viewport_width() / 4,
                    height=dpg.get_viewport_height() * 3 / 4,
                    indent=0,
                ) as self.rightCW:
                    with dpg.filter_set(tag="Business_Filter"):
                        self.businessBox = dpg.add_listbox(
                            self.allBusinesses,
                            label="Businesses",
                            callback=self.load_prev,
                            width=-1,
                            num_items=10,
                        )
                    self.searcherz = dpg.add_input_text(
                        label="Filter", callback=self.searcher
                    )
                    with dpg.child_window() as self.infoCW:
                        dpg.add_tree_node(label="Info", parent=self.infoCW)
            with dpg.group(horizontal=True):
                self.localKeyword = dpg.add_input_text(
                    hint="Keyword",
                    source=self.keyword,
                    callback=self.updateMap,
                    on_enter=True,
                    width=200,
                )
                self.proxy = dpg.add_input_text(
                    hint="http://your_user:your_password@your_proxy_url:your_proxy_port",
                    source=self.proxyreg,
                    callback=self.updateMap,
                    on_enter=True,
                    width=200,
                )
            with dpg.group(horizontal=True):
                self.localLocation = dpg.add_input_text(
                    hint="Location",
                    source=self.location,
                    callback=self.updateMap,
                    on_enter=True,
                    width=200,
                )
                self.nodeDistance = dpg.add_combo(
                    [1, 2, 5, 15, 25, 50],
                    label="Distance Between Nodes (Miles)",
                    default_value=25,
                    width=200,
                )
            with dpg.group(horizontal=True):
                dpg.add_button(label="Search", callback=self.updateMap)
                dpg.add_button(label="Load Last", callback=self.load_prev)
                dpg.add_button(
                    label="Create Report",
                    user_data={"map": self.myMap.dpgval},
                    callback=self.outputFrame,
                )

        return self.theTab

    def searcher(self, sender, *args, **kwargs):
        search_list = self.allBusinesses
        modified_list = []
        if dpg.get_value(sender) == "*" or dpg.get_value(sender) == "":
            modified_list.extend(iter(search_list))
        if dpg.get_value(sender).lower():
            modified_list.extend(
                item
                for item in search_list
                if dpg.get_value(sender).lower() in item.lower()
            )

        dpg.configure_item(self.businessBox, items=modified_list)

    def updateMap(self) -> None:
        if self.locked == True:
            return
        kw: str = dpg.get_value(self.keyword)
        loc: str = dpg.get_value(self.location)
        prox: str = dpg.get_value(self.proxyreg)
        distance = int(dpg.get_value(self.nodeDistance))
        match distance:
            case 1:
                self.zoom = 14
            case 2:
                self.zoom = 13
            case 5:
                self.zoom = 12
            case 15:
                self.zoom = 11
            case 25:
                self.zoom = 10
            case 50:
                self.zoom = 9
        # if kw == "" or loc == "":
        # 	return
        # self.jobq.put_nowait((runLocalRankTracker, (kw, loc, 25, prox)))
        myT = CustomThread(
            target=self.runUpdates,
            args=(
                kw,
                loc,
                distance,
                prox,
            ),
        )
        myT.start()

    def runUpdates(self, kw, loc, distance, proxy):
        self.locked = True
        try:
            self.mapdata: dict = runLocations(kw, distance, loc, proxy)
        except:
            self.locked = False
            self.mapdata = {"error": "Error Occured"}
            return
        if "error" in self.mapdata:
            with dpg.window(
                label="Error",
                width=500,
                height=500,
                tag="LOCAL_Error",
                modal=True,
                pos=(dpg.get_viewport_width() / 2, dpg.get_viewport_height() / 2),
            ):
                dpg.add_text(self.mapdata["error"])
                dpg.add_button(
                    label="Ok", callback=lambda: dpg.delete_item("LOCAL_Error")
                )
            self.locked = False
            return
        self.updateOnMapData(self.mapdata)
        self.myMap.doCheckpoints(self.mapdata)
        self.locked = False

    def _create_window(self, *args, **kwargs):
        return 0

    def updateUData(self):
        self.searcher(self.searcherz)

    def load_prev(self, *args, **kwargs):
        if self.bseoData.loaddata("Local", "data") == None:
            return
        self.update("fileupdate", self.bseoData.loaddata("Local", "data"))
        self.myMap.doCheckpoints(
            self.bseoData.loaddata("Local", "data"), dpg.get_value(self.businessBox)
        )
        self.updateOnMapData(self.bseoData.loaddata("Local", "data"))

    def update(self, piece, data):
        if piece == "update":
            # dpg.delete_item(self.myMap.dpgval)
            self.locked = False
            self.mapdata = data
            self.loc = self.bseoData.loaddata("Local", "location")
            self.lati = self.loc[0]
            self.longi = self.loc[1]
            self.updateOnMapData(data)
            # self.myMap = MapWidget(width=500, height=500, center=(self.lati,self.longi), zoom_level=14, parent=self.theWindow)
            self.myMap.doCheckpoints(self.mapdata, dpg.get_value(self.businessBox))

        if piece == "fileupdate":
            # self.mapdata = data
            self.loc = self.bseoData.loaddata("Local", "location")
            if self.loc == None:
                return
            self.lati = self.loc[0]
            self.longi = self.loc[1]
            dpg.delete_item(self.myMap.dpgval)
            del self.myMap
            self.myMap = MapWidget(
                width=dpg.get_viewport_width() * 5 / 8,
                height=500,
                center=(self.lati, self.longi),
                zoom_level=self.zoom,
                parent=self.theWindow,
            )

    def outputFrame(self, zoom: int = 0, client="General", *args, **kwargs):
        # self.real_primary_window = dpg.get_active_window()
        data = self.bseoData.loaddata("Local", "data")
        loc = self.bseoData.loaddata("Local", "location")
        self.temporarystuffs = data
        lati = loc[0]
        longi = loc[1]
        showZoom = ""
        if zoom != 0:
            showZoom = f" - Node Distance: {zoom}"
        theBusiness = dpg.get_value(self.businessBox)
        with dpg.window(
            width=dpg.get_viewport_width(),
            height=dpg.get_viewport_height(),
            no_background=True,
            no_scrollbar=True,
        ) as tempWin:
            tempMap = MapWidget(
                width=dpg.get_viewport_width() - 50,
                height=dpg.get_viewport_height() - 50,
                center=(lati, longi),
                zoom_level=self.zoom,
                parent=tempWin,
            )
            tempMap.doCheckpoints(data, theBusiness)
            dtxt: str = f"Keyword: {data['keyword']} - Location: {data['location']} - Business: {theBusiness} {showZoom}"
            dpg.draw_rectangle(
                (0, 0),
                (tempMap.width, 25),
                color=(0, 0, 0, 155),
                thickness=0,
                rounding=0,
                parent=tempMap.dpgval,
                fill=(0, 0, 0, 255),
            )
            dpg.draw_text(
                (25, 0),
                dtxt,
                color=(255, 255, 255, 255),
                parent=tempMap.dpgval,
                size=25,
            )
            dpg.draw_rectangle(
                (0, tempMap.height - 25),
                (tempMap.width, tempMap.height),
                fill=(255, 255, 255, 100),
                color=(255, 255, 255, 100),
                parent=tempMap.dpgval,
            )
            dpg.draw_text(
                (25, tempMap.height - 25),
                "*Map for Display Purposes Only, not to scale",
                color=(0, 0, 0, 255),
                parent=tempMap.dpgval,
                size=25,
            )
        dpg.configure_item(self.real_primary_window, show=False)
        dpg.set_primary_window(self.real_primary_window, False)
        dpg.set_primary_window(tempWin, True)
        dpg.render_dearpygui_frame()
        time.sleep(1)
        dpg.render_dearpygui_frame()

        outpath = f"output/localclients/{Utils.cleanFilename(theBusiness)}/{Utils.cleanFilename(data['keyword'])}"
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        imgName = f"{outpath}/{time.strftime('%b_%d_%y', time.gmtime())}.png"
        dpg.output_frame_buffer(imgName)
        dpg.render_dearpygui_frame()
        dpg.configure_item(self.real_primary_window, show=True)
        dpg.set_primary_window(self.real_primary_window, True)
        dpg.render_dearpygui_frame()
        dpg.delete_item(tempMap.dpgval)
        dpg.delete_item(tempWin)
        dpg.render_dearpygui_frame()
        directions: list[str] = ["NW", "N", "NE", "W", "C", "E", "SW", "S", "SE"]
        dlist = list()
        auddict = dict()
        auddict["clientName"] = theBusiness
        auddict["theLocation"] = data["location"]
        auddict["keyword"] = data["keyword"]
        auddict["mapImage"] = imgName
        auddict["clientImage"] = ""
        myAgency = self.bseoData.getAgency()
        doClients = False
        if client in myAgency.clients:
            doClients = True
        for direction in directions:
            businessAdded = False
            if direction in data:
                myTempDict = dict()
                myTempDict["direction"] = direction
                myTempDict["rank1"] = ""
                myTempDict["rank2"] = ""
                myTempDict["rank3"] = ""
                theAll = list()
                if type(data[direction]) is dict:
                    if (
                        theBusiness in data[direction]
                        and "screenshot" in data[direction][theBusiness]
                    ):
                        auddict["clientImage"] = data[direction][theBusiness][
                            "screenshot"
                        ]
                        if doClients == True:
                            myAgency.clients[client].addRankings(
                                keyword=data["keyword"],
                                location=f"{data['location']}-{direction}",
                                date=time.strftime("%m %d %Y", time.localtime()),
                                rank=data[direction][theBusiness]["rank"],
                            )
                    myTempDict[f"rank1"] = "blank.png"
                    myTempDict[f"rank2"] = "blank.png"
                    myTempDict[f"rank3"] = "blank.png"
                    for k, v in data[direction].items():
                        if type(v) is dict:
                            if "rank" in v:
                                if v["rank"] < 4:
                                    if (
                                        "&" in str(v["screenshot"])
                                        or ">" in str(v["screenshot"])
                                        or "<" in str(v["screenshot"])
                                        or '"' in str(v["screenshot"])
                                        or "'" in str(v["screenshot"])
                                    ):
                                        continue
                                    myTempDict[f"rank{v['rank']}"] = v["screenshot"]
                                if "screenshot" in v:
                                    theAll.append(v["screenshot"])
                                    if k == theBusiness:
                                        # dlist.append(myTempDict)
                                        businessAdded = True
                                    if v["rank"] >= 3 and businessAdded == True:
                                        break
                if businessAdded == True:
                    myTempDict["all"] = theAll
                dlist.append(myTempDict)
                # dlist.append(myTempDict)
        auddict["tdirections"] = dlist
        auddict["zoom"] = zoom

        self.bseoData.localReportAdd(auddict, client)

    def updateOnMapData(self, data):
        self.allBusinesses = list()
        if "error" in data:
            return
        dpg.delete_item(self.infoCW, children_only=True)
        dtxt = f"Keyword: {data['keyword']} - Location: {data['location']}"
        dpg.draw_rectangle(
            (0, 0),
            (self.myMap.width, 25),
            color=(0, 0, 0, 155),
            thickness=0,
            rounding=0,
            parent=self.myMap.dpgval,
            fill=(0, 0, 0, 255),
        )
        dpg.draw_text(
            (55, 0), dtxt, color=(255, 255, 255, 255), parent=self.myMap.dpgval, size=25
        )
        dpg.draw_rectangle(
            (0, self.myMap.height - 25),
            (self.myMap.width, self.myMap.height),
            fill=(255, 255, 255, 100),
            color=(255, 255, 255, 100),
            parent=self.myMap.dpgval,
        )
        dpg.draw_text(
            (25, self.myMap.height - 25),
            "*Map for Display Purposes Only, not to scale",
            color=(0, 0, 0, 255),
            parent=self.myMap.dpgval,
            size=25,
        )
        for key, val in data.items():
            if key == "keyword":
                continue
            if key == "location":
                continue
            with dpg.tree_node(label=key, parent=self.infoCW):
                for k, v in val.items():
                    if k == "all":
                        self.allBusinesses.extend(v)
                    elif k == "error":
                        continue
                    else:
                        with dpg.tree_node(label=k):
                            for i, j in v.items():
                                dpg.add_text(f"{i}: {j}")
        self.bCount = dict()
        for i in self.allBusinesses:
            if i in self.bCount:
                self.bCount[i] += 1
            else:
                self.bCount[i] = 1
        dpg.configure_item(self.businessBox, items=list(self.bCount.keys()))


def output(s, a, ud):
    # dpg.split_frame()
    themap = ud["map"]

    # oldP = dpg.get_item_parent(themap)
    tempWindow = dpg.add_window(
        menubar=False,
        width=dpg.get_item_width(themap) + 10,
        height=dpg.get_item_height(themap) + 10,
        no_resize=True,
        no_move=True,
        no_collapse=True,
        no_close=True,
        no_title_bar=True,
    )
    dpg.move_item(themap, parent=tempWindow)
    # dpg.output_frame_buffer("output.png")
    wpos = dpg.get_item_pos(tempWindow)
    mpos = dpg.get_item_pos(themap)
    msize = dpg.get_item_rect_size(themap)
    # dpg.move_item(themap, parent=oldP)
    # dpg.delete_item(tempWindow)
    # print(wpos)
