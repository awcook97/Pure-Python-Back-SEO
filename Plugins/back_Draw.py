# Draw.pPlugins.back_Base
from Plugins import Plugin
import dearpygui.dearpygui as dpg
import math
import time
import threading
import importlib
from typing import List
from core_ui.Widgets.BasicVroom import PlotVroom


def createCircleFromPositions(
    numberOfPoints: int, radius: float, center: list = [0, 0]
) -> List[List[float]]:
    positions = []
    angle = 0
    angle_increment = 2 * math.pi / numberOfPoints
    for i in range(numberOfPoints):
        x = center[0] + radius * math.cos(angle)
        y = center[1] + radius * math.sin(angle)
        positions.append([x, y])
        angle += angle_increment
    return positions


class SchemaGraph:
    def __init__(self, schema: dict, parent: int | str):
        self.schema = schema
        self.parent = parent
        self.takenPos = list()
        self.lineCol = [125, 125, 125, 150]
        self.textCol = [255, 255, 255, 255]
        self.createSchema(self.schema)

    def createSchema(self, scheme: list | dict, pos=(500, 500)):
        numNodes = len(scheme)
        positions = createCircleFromPositions(numNodes * 3, numNodes * 50, pos)
        if type(scheme) is list:
            for sche in scheme:
                myPos = positions.pop()
                while myPos in self.takenPos:
                    myPos = positions.pop()
                if type(sche) is dict:
                    dpg.draw_line(
                        pos,
                        myPos,
                        color=self.lineCol,
                        thickness=2.0,
                        parent=self.parent,
                    )
                    self.createSchema(sche, myPos)
                elif type(sche) is list:
                    dpg.draw_line(
                        pos,
                        myPos,
                        color=self.lineCol,
                        thickness=2.0,
                        parent=self.parent,
                    )
                    self.createSchema(sche, myPos)
                else:
                    dpg.draw_line(
                        pos,
                        myPos,
                        color=self.lineCol,
                        thickness=2.0,
                        parent=self.parent,
                    )
                    dpg.draw_text(
                        myPos,
                        str(sche),
                        color=self.textCol,
                        size=20,
                        parent=self.parent,
                    )
                    self.takenPos.append(myPos)
        if type(scheme) is dict:
            for key, val in scheme.items():
                myPos = positions.pop()
                while myPos in self.takenPos:
                    myPos = positions.pop()
                dpg.draw_line(
                    pos, myPos, color=self.lineCol, thickness=2.0, parent=self.parent
                )
                dpg.draw_text(
                    myPos, key, parent=self.parent, color=[255, 255, 255, 255], size=20
                )
                self.takenPos.append(myPos)
                if type(val) is dict:
                    dpg.draw_line(
                        pos,
                        myPos,
                        color=self.lineCol,
                        thickness=2.0,
                        parent=self.parent,
                    )
                    self.createSchema(val, myPos)
                elif type(val) is list:
                    dpg.draw_line(
                        pos,
                        myPos,
                        color=self.lineCol,
                        thickness=2.0,
                        parent=self.parent,
                    )
                    self.createSchema(val, myPos)
                else:
                    while myPos in self.takenPos:
                        myPos = positions.pop()
                    dpg.draw_line(
                        pos,
                        myPos,
                        color=self.lineCol,
                        thickness=2.0,
                        parent=self.parent,
                    )
                    dpg.draw_text(
                        myPos, str(val), color=self.textCol, size=20, parent=self.parent
                    )
                    self.takenPos.append(myPos)
        else:
            myPos = positions.pop()
            while myPos in self.takenPos:
                myPos = positions.pop()
            dpg.draw_line(
                pos, myPos, color=self.lineCol, thickness=2.0, parent=self.parent
            )
            dpg.draw_text(
                myPos, str(scheme), color=self.textCol, size=20, parent=self.parent
            )
            self.takenPos.append(myPos)


class Draw(Plugin):
    plugin_name = "Draw_Plugin"
    author = "author"
    info = "What does the plugin do?"
    menu = False
    tab = False
    window = True
    active = False
    injectable = False
    misc = False

    def __init__(self):
        """Initialize your stuff. If you need to declare variables, declare them here. Don't call UI stuff yet. That's for the items you labeled as True above. All plugins start out deactivated at first."""
        self.active = False
        self.schema = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "name": "Questions about the Structured Data Viewer",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": "📜 What formats are supported?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "<p>At the moment the tool can read JSON-LD and Microdata. If there is enough demand I plan to add other formats like RDFaLite, microformat and meta tag base markup like Open Graph.,</p>",
                    },
                },
                {
                    "@type": "Question",
                    "name": "📝 What vocabularies are supported",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "<p>The tool will show data from all vocabularies but it currently only supports validating schema.org. There are plans to add other vocabularies if there is demand.</p>",
                    },
                },
                {
                    "@type": "Question",
                    "name": "🔎 Is Google supported",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "<p>At this time there is no special validation to check if the structured data passes Googles own guidelines. The Rich results tester (RRT) is the best toll for that at this time. I do have plans to add further validations for system like Google Search, Google Merchant Centre, Facebook, Twitter, Pinterest etc.</p>",
                    },
                },
            ],
        }
        return

    def _create_menu(self, parent):
        with dpg.menu(label="Draw", parent=parent) as menu:
            dpg.add_menu_item(label="Reload")
        return menu

    def _create_tab(self, parent):
        with dpg.tab(label="Schema Draw", parent=parent) as tab:
            self.schemadrawl = dpg.add_plot(
                label="Schema Draw",
                height=1000,
                width=1000,
                no_child=True,
                no_title=True,
            )
            self.schemadraw = SchemaGraph(self.schema, self.schemadrawl)
        return tab

    def _create_window(self):
        with dpg.window(
            label="Draw", width=1000, height=1000, no_resize=False
        ) as drawWindow:
            with dpg.menu_bar():
                with dpg.menu(label="Add"):
                    dpg.add_menu_item(
                        label="Square",
                        user_data="rectangle",
                        callback=lambda: self.addItem("rectangle"),
                    )
                    dpg.add_menu_item(
                        label="Triangle",
                        user_data="triangle",
                        callback=lambda: self.addItem("triangle"),
                    )
            width = 150
            height = 150
            self.slidezz = SliderWithWindow()
            dpg.add_button(label="Go to 100", callback=lambda: self.slidezz.update(100))
            dpg.add_button(label="Go to 0", callback=lambda: self.slidezz.update(0))
            with dpg.group(horizontal=True):
                with dpg.group(horizontal=True):

                    def sliderTo100(slider):
                        v = dpg.get_value(slider)
                        while v < 100:
                            v += 1
                            dpg.set_value(slider, v)
                            time.sleep(0.05)

                    self.mySlider = dpg.add_slider_int(
                        label="Test Slider",
                        max_value=100,
                        callback=lambda: threading.Thread(
                            target=sliderTo100, args=(self.mySlider,)
                        ).start(),
                    )
            with dpg.group(horizontal=True):
                with dpg.plot(
                    label="Pie Chart",
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
                        value=0,
                    )
                    # with dpg.draw_layer() as d:
                    # 	self.myVroom2 = BasicVroom(150, 150, parent=d, start=0, pos=(0,0), hasDrawList=True, isPlot = True)
                    leg = dpg.add_plot_legend()

                    xax = dpg.add_plot_axis(
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
                        self.sitemapPie = dpg.add_pie_series(
                            200.5,
                            400.5,
                            200.5,
                            [0.45, 0.45],
                            ["1", "2"],
                            format="",
                            angle=0,
                        )
                        # self.myVroom = BasicVroom(150, 150, parent=dpg.last_item(),start=0, pos=(200,200), hasDrawList=False)
                    dpg.set_axis_limits(yax, 200, 650)
                    dpg.set_axis_limits_auto(xax)
                    dpg.set_axis_limits_auto(yax)
            dpg.add_button(
                label="Go to 100", callback=lambda: self.newVroom.update(100)
            )
            dpg.add_button(label="Go to 0", callback=lambda: self.newVroom.update(0))
            with dpg.group(horizontal=True):
                self.myVroom = BasicVroom(width, height)
                with dpg.group():
                    dpg.add_button(
                        label="Go to 100",
                        callback=lambda: self.myVroom.changeTrack(100),
                    )
                    dpg.add_button(
                        label="Go to 0", callback=lambda: self.myVroom.changeTrack(0)
                    )
                self.myVroom2 = BasicVroom(200, 200, 75)
                with dpg.group():
                    dpg.add_button(
                        label="Go to 100",
                        callback=lambda: self.myVroom2.changeTrack(100),
                    )
                    dpg.add_button(
                        label="Go to 0", callback=lambda: self.myVroom2.changeTrack(0)
                    )
                self.myVroom3 = BasicVroom(400, 500, 30)
                with dpg.group():
                    dpg.add_button(
                        label="Go to 100",
                        callback=lambda: self.myVroom3.changeTrack(100),
                    )
                    dpg.add_button(
                        label="Go to 0", callback=lambda: self.myVroom3.changeTrack(0)
                    )
            with dpg.plot(
                equal_aspects=True, width=500, height=500, no_child=True, no_title=True
            ) as self.plotp:
                self.myPlotVroom = PlotVroom((0.5, 0.5), parent=self.plotp)
                xax = dpg.add_plot_axis(
                    dpg.mvXAxis,
                    label="X-Axis",
                    no_gridlines=True,
                    no_tick_marks=True,
                    no_tick_labels=True,
                )
                yax = dpg.add_plot_axis(
                    dpg.mvYAxis,
                    label="Y-Axis",
                    no_gridlines=True,
                    no_tick_marks=True,
                    no_tick_labels=True,
                )
                dpg.set_axis_limits(xax, -60, 60)
                dpg.set_axis_limits(yax, -45, 45)
                dpg.set_axis_limits_auto(yax)
                dpg.set_axis_limits_auto(xax)
            dpg.configure_item(self.plotp, equal_aspects=True)
            dpg.add_button(
                label="Go to 100", callback=lambda: self.myPlotVroom.update(100)
            )
            dpg.add_button(label="Go to 0", callback=lambda: self.myPlotVroom.update(0))
        return drawWindow

    def _activate(self):
        self.myVroom.doColors()
        self.myVroom2.doColors()
        self.myVroom3.doColors()

    def addItem(self, shape, *args, **kwargs):
        pass


class SliderWithWindow:
    def __init__(self, default_value=0, minimum=0, maximum=100):
        self.value = default_value
        self.minimum = minimum
        self.maximum = maximum
        self.textpos = (self.value + 7, 10)
        with dpg.drawlist(150, 50) as self.sliderDrawlist:
            self.trackRect = dpg.draw_rectangle(
                (0, 30),
                (self.value, 50),
                color=[255, 0, 0, 255],
                thickness=0.0,
                fill=[0, 255, 0, 255],
            )
            self.behindText = dpg.draw_circle(
                (self.textpos[0] + 10, self.textpos[1] + 10),
                radius=15,
                color=[255, 255, 255, 255],
                thickness=1.0,
                fill=[255, 255, 255, 255],
            )
            self.trackText = dpg.draw_text(
                self.textpos, str(self.value), color=[0, 0, 255, 255], size=25
            )

    def update(self, value):
        if self.value < value:
            adder = 1
        else:
            adder = -1
        myT = threading.Thread(target=self.doThread, args=(value, adder))
        myT.start()

    def doThread(self, value, adder):
        while self.value != value:
            self.value += adder

            self.textpos = (
                self.value + (dpg.get_text_size(str(self.value))[0] / 2),
                10,
            )
            dpg.configure_item(self.trackRect, pmax=(self.value, 50))
            dpg.configure_item(self.trackText, pos=self.textpos, text=str(self.value))
            dpg.configure_item(
                self.behindText,
                center=(self.textpos[0] + 10, self.textpos[1] + 10),
                radius=dpg.get_text_size(str(self.value))[0],
            )
            # dpg.draw_rectangle((0,30), (self.value, 50), color=[255,0,0,255], thickness=0.0, fill=[0,255,0,255])
            # dpg.draw_text(self.textpos, str(self.value), color=[0,0,255,255], size=10)
            time.sleep(0.03)


class BasicVroom:
    def __init__(self, width, height, start=0):
        self.width = width
        self.height = height
        self.start = start
        self.innPt = (start + (1 / 6)) / 100
        self.outPt = (start + (2 / 6)) / 100
        self.trackPt = 0.00
        self.colormapRegistry = dpg.add_colormap_registry()
        self.colormap = dpg.add_colormap(
            [
                [255, 0, 0, 175],
                [255, 145, 0, 175],
                [227, 255, 0, 175],
                [255, 255, 255, 175],
                [0, 0, 255, 175],
                [0, 255, 255, 175],
                [0, 255, 0, 175],
            ],
            False,
            parent=self.colormapRegistry,
            label="Content Score",
        )
        with dpg.drawlist(width, height):
            with dpg.draw_layer():
                center = (width / 2, height / 2)
                radius = height * 0.25
                centerbottom = (width / 2, height)
                innercenter = (width / 2, height - (radius / 2))
                undertext = (innercenter[0], innercenter[1] + radius / 3)
                self.innercenter = innercenter
                track0 = (width / 2 - radius, height)
                self.center = center
                self.radius = radius
                self.increment = self.radius / 100 * 2
                self.size = width / 7
                self.textVal = str(self.start)
                self.innercenterText = (
                    innercenter[0] - self.size / 2,
                    innercenter[1] - self.size / 2,
                )
                colors = [
                    [125, 125, 125, 155],
                    [0, 0, 0, 255],
                    [100, 250, 250, 150],
                    [205, 125, 30, 255],
                    [0, 0, 0, 255],
                    [200, 100, 0, 150],
                    [255, 0, 0, 255],
                ]
                self.outer = dpg.draw_circle(
                    center=centerbottom,
                    radius=radius,
                    color=colors.pop(),
                    thickness=2,
                    fill=colors.pop(),
                )
                self.inner = dpg.draw_circle(
                    center=innercenter,
                    radius=radius * 0.5,
                    color=colors.pop(),
                    thickness=2,
                    fill=colors.pop(),
                )
                self.track = dpg.draw_circle(
                    center=track0,
                    radius=2.5,
                    color=colors.pop(),
                    thickness=2,
                    fill=colors.pop(),
                )
                self.linez = dpg.draw_line(
                    undertext, track0, color=colors.pop(), thickness=2
                )
                self.numText = dpg.draw_text(
                    self.innercenterText,
                    self.start,
                    color=[0, 0, 0, 255],
                    size=self.size,
                )

    def changeTrack(self, num):
        if num < 0 or num > 100:
            return
        myT = threading.Thread(target=self.doThread, args=(num,))
        myT.start()

    def doThread(self, num):
        if num > self.start:
            adder = 1
        else:
            adder = -1
        while self.start != num:
            self.start += adder
            self.doColors(adder / 100)

            time.sleep(0.03)

    def getColorMapValue(self, itemV, divisor=1, cmOffset=0.000):
        if itemV + cmOffset > 1 or itemV + cmOffset < 0:
            cmOffset * -1
        myVa = dpg.sample_colormap(self.colormap, itemV + cmOffset)
        myV = list()
        for v in myVa:
            myV.append(v * 255 / divisor)
        return myV

    def doColors(self, adder=0):
        self.innPt += adder
        self.outPt += adder
        self.trackPt += adder
        if self.innPt > 1:
            self.innPt = 1
        if self.outPt > 1:
            self.outPt = 1
        if self.trackPt > 1:
            self.trackPt = 1
        innerColor = self.getColorMapValue(self.innPt)
        outerColor = self.getColorMapValue(self.innPt, 2)
        trackColor = self.getColorMapValue(self.innPt, 3)
        linezColor = self.getColorMapValue(self.innPt, 1, 0.2)
        self.size = dpg.get_text_size(str(self.start))
        # p#rint(self.size)
        self.innercenterText = (
            self.innercenter[0] - (self.size[0] / 3),
            self.innercenter[1] - (self.size[1] / 3),
        )
        dpg.configure_item(self.inner, fill=innerColor)
        dpg.configure_item(self.outer, fill=outerColor)
        dpg.configure_item(self.track, fill=trackColor)
        dpg.configure_item(self.linez, color=linezColor)
        dpg.configure_item(self.numText, pos=self.innercenterText)
        newCoords = self.findCoordsOfSemiCircle(self.start, self.radius)
        self.size = dpg.get_text_size(str(self.start))
        innercenterText = (
            self.innercenter[0] - (self.size[0] / 2.25),
            self.innercenter[1] - (self.size[1] / 2.25),
        )
        dpg.configure_item(self.track, center=newCoords)
        dpg.configure_item(self.linez, p2=newCoords)
        dpg.configure_item(self.numText, text=str(self.start), pos=innercenterText)

    def findCoordsOfSemiCircle(self, num, radius):
        x = self.increment * num
        y = math.sqrt((radius * radius) - (x - radius) * (x - radius))
        # print(f"X: {x}, Y: {y}")
        return ((self.width / 2 - radius) + x, self.height - y)
