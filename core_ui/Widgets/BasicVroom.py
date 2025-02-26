from typing import List, Tuple
import dearpygui.dearpygui as dpg
import threading
import math
import time


class BasicVroom:
    def __init__(
        self,
        width,
        height,
        parent=None,
        start=0,
        pos=(0, 0),
        hasDrawList=False,
        isPlot=False,
    ):
        self.width = width
        self.height = height
        self.isPlot = isPlot
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
        if hasDrawList:
            self.withDrawlist(width, height, pos=pos, parent=parent)
        else:
            self.withoutDrawlist(width, height, pos=pos, parent=parent)
            dpg.set_item_pos(self.theDrawlist, pos)
            dpg.configure_item(self.theDrawlist, show=True)

    def withoutDrawlist(self, width, height, parent, pos=(0, 0)):
        with dpg.drawlist(
            width, height, pos=pos, parent=parent, show=False
        ) as self.theDrawlist:
            self.withDrawlist(width, height, pos=(0, 0), parent=self.theDrawlist)

    def withDrawlist(self, width, height, parent, pos=(0, 0)):
        # wpos = pos[0]
        # hpos = pos[1]
        # if wpos < 0: wpos = -1 * pos[0]
        # if hpos < 0: hpos = -1 * pos[1]
        # rectmax = (width+wpos, height+hpos)
        # somerectangle = dpg.draw_rectangle(pos, rectmax, color=[0,0,0,0], thickness=0, parent=parent)
        # parent=dpg.add_draw_node()
        # dpg.apply_transform(parent, dpg.create_translation_matrix([0,0]))

        self.xoffset = pos[0]
        self.yoffset = pos[1]
        # if self.isPlot:
        # 	self.yoffset = -1 * self.yoffset
        # 	pos = (self.xoffset, self.yoffset)

        radius = height * 0.5
        if self.isPlot:
            center = ((width / 2) + pos[0], (height / 2) - pos[1])
            centerbottom = ((width / 2) + pos[0], height - pos[1])
            innercenter = ((width / 2) + pos[0], (height + (radius / 2)) + pos[1])
            undertext = (innercenter[0], innercenter[1] - radius / 3)
            track0 = ((width / 2 - radius) + self.xoffset, height - self.yoffset)
        else:
            center = ((width / 2) + pos[0], (height / 2) + pos[1])
            centerbottom = ((width / 2) + pos[0], height + pos[1])
            innercenter = ((width / 2) + pos[0], (height - (radius / 2)) + pos[1])
            undertext = (innercenter[0], innercenter[1] + radius / 3)
            track0 = ((width / 2 - radius) + self.xoffset, height + self.yoffset)

        self.innercenter = innercenter
        self.center = center
        self.radius = radius
        self.increment = self.radius / 100 * 2
        self.size = width / 7
        self.textVal = str(self.start)
        if self.isPlot:
            self.innercenterText = (innercenter[0], innercenter[1] + self.size / 2)
        else:
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
            parent=parent,
        )
        self.linez = dpg.draw_line(
            undertext, track0, color=colors.pop(), thickness=2, parent=parent
        )
        self.inner = dpg.draw_circle(
            center=innercenter,
            radius=radius * 0.5,
            color=colors.pop(),
            thickness=2,
            fill=colors.pop(),
            parent=parent,
        )
        self.numText = dpg.draw_text(
            self.innercenterText,
            self.start,
            color=[0, 0, 0, 255],
            size=self.size,
            parent=parent,
        )
        self.track = dpg.draw_circle(
            center=track0,
            radius=radius * 0.01,
            color=colors.pop(),
            thickness=2,
            fill=colors.pop(),
            parent=parent,
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
        # print(self.size)
        if self.isPlot:
            self.innercenterText = (
                self.innercenter[0] - (self.size[0] / 3),
                self.innercenter[1] + (self.size[1] / 3),
            )
        else:
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
        if self.isPlot:
            innercenterText = (
                self.innercenter[0] - (self.size[0] / 2.25),
                self.innercenter[1] + (self.size[1] / 2.25),
            )
        else:
            innercenterText = (
                self.innercenter[0] - (self.size[0] / 2.25),
                self.innercenter[1] - (self.size[1] / 2.25),
            )
        dpg.configure_item(self.track, center=newCoords)
        dpg.configure_item(self.linez, p2=newCoords)
        dpg.configure_item(self.numText, text=str(self.start), pos=innercenterText)

    def findCoordsOfSemiCircle(self, num, radius):
        # if self.isPlot: radius *= 0.25
        x = self.increment * num
        y = math.sqrt((radius * radius) - (x - radius) * (x - radius))
        if self.isPlot:
            y = -1 * y
        x = (self.width / 2 - radius) + x + self.xoffset
        y = self.height - y
        # print(f"{x}, {y}")
        return (x, y)  # +self.yoffset)


class PlotVroom:
    def __init__(
        self,
        pos,
        radius1=15,
        radius2=30,
        value=0,
        parent=None,
        colormapInner: list = [
            [255, 0, 0, 255],
            [255, 0, 200, 255],
            [125, 25, 195, 255],
            [75, 75, 175, 255],
            [15, 100, 255, 255],
            [0, 255, 255, 255],
            [0, 255, 0, 255],
        ],
        colormapOuter: list = [
            [255, 55, 55, 150],
            [255, 255, 125, 150],
            [125, 125, 255, 150],
            [75, 175, 255, 150],
            [15, 255, 100, 150],
            [100, 255, 175, 150],
            [0, 255, 100, 150],
        ],
        text: str = "",
    ):
        """Basically basic Vroom but better"""
        self.parent = dpg.last_container() or parent
        self.pos = pos
        self.textSize = radius1
        self.radius1 = radius1
        self.radius2 = radius2
        self.value = value
        self.vrooming = False
        self.keepgoing = True
        self.myT = threading.Thread()
        self.labeltext = text
        self.test = False
        if self.test:
            colormapInner = [[255, 255, 0, 75], [255, 0, 200, 75], [125, 255, 125, 75]]
            colormapOuter = [[255, 255, 0, 75], [255, 0, 200, 75], [125, 255, 125, 75]]
            dpg.set_frame_callback(10, self.doloading)
        # self.parent = parent
        self.colormapRegistry = dpg.add_colormap_registry()
        self.colormapInner = dpg.add_colormap(
            colormapInner, False, parent=self.colormapRegistry
        )
        self.colormapOuter = dpg.add_colormap(
            colormapOuter, False, parent=self.colormapRegistry
        )
        self.outer = dpg.draw_circle(
            center=pos,
            radius=radius2,
            color=colormapInner[0],
            thickness=2,
            fill=colormapOuter[1],
            parent=self.parent,
        )
        self.outermask = dpg.draw_circle(
            center=pos,
            radius=radius2,
            color=(0, 0, 0, 55),
            thickness=2,
            fill=(0, 0, 0, 100),
            parent=self.parent,
        )
        with dpg.draw_node(parent=self.parent) as self.theNode:
            dpg.apply_transform(dpg.last_item(), dpg.create_translation_matrix(pos))
            self.centerdot = dpg.draw_circle(
                (0, 0), 0.1, color=[0, 0, 0, 255], thickness=2, fill=[0, 0, 0, 255]
            )

            self.matrii = dict()
            with dpg.draw_node(user_data=0) as self.funNode:
                for i in range(0, 360):
                    with dpg.draw_node(user_data=i * 5) as tt:
                        dpg.apply_transform(
                            tt,
                            dpg.create_rotation_matrix(math.pi * i / 100.0, [0, 0, -1])
                            * dpg.create_translation_matrix([0, 0 - radius2]),
                        )
                        if i % 10 == 0:
                            color = [255, 255, 255, 255]
                            length = 2
                        elif i % 5 == 0:
                            color = [255, 138, 0, 255]
                            length = 1
                        else:
                            color = [0, 0, 0, 255]
                            length = 0.5
                        dpg.draw_line((0, 0), (0, 0 + length), color=color, thickness=2)
            with dpg.draw_node(user_data=30.0) as self.theNode2:
                dpg.apply_transform(
                    dpg.last_item(),
                    dpg.create_rotation_matrix(math.pi * 30.0 / 80.0, [0, 0, -1]),
                )
                self.line1 = dpg.draw_line(
                    (0, 0), (0, 0 - radius2), color=[255, 255, 255, 255], thickness=5
                )
                self.line2 = dpg.draw_line(
                    (0, 0), (0, 0 - radius2 + 5), color=[0, 0, 0, 255], thickness=2
                )

        self.hidingTriangle = dpg.draw_triangle(
            pos,
            (pos[0] + radius2 * 1.3, pos[1] - radius2 * 1.3),
            (pos[0] - radius2 * 1.3, pos[1] - radius2 * 1.3),
            color=[0, 0, 0, 255],
            fill=[0, 0, 0, 255],
            thickness=2,
            parent=self.parent,
        )
        self.inner = dpg.draw_circle(
            center=pos,
            radius=radius1,
            color=colormapOuter[0],
            thickness=2,
            fill=colormapInner[1],
            parent=self.parent,
        )
        tsize = len(str(value)) * 7
        self.displayText = dpg.draw_text(
            (pos[0] - tsize, pos[1] + 16),
            str(value),
            color=[0, 0, 0, 255],
            size=radius1,
            parent=self.parent,
        )
        tsize = len(str(self.labeltext)) * 7
        self.showtext = dpg.draw_text(
            (pos[0] - (tsize), pos[1] - radius2 * 1.3 + radius1),
            str(self.labeltext),
            color=[255, 255, 255, 255],
            size=radius1,
            parent=self.parent,
        )

    def update(self, value):
        if self.vrooming:
            self.keepgoing = False
            # self.myT.join()
            self.keepgoing = True
        self.vrooming = True
        self.myT = threading.Thread(target=self.update1, args=(int(value),))
        self.myT.start()

    def update1(self, value):
        if self.value < value:
            adder = 1
        elif self.value > value:
            adder = -1
        else:
            return
        while self.value != value and self.keepgoing:
            if self.value < value:
                adder = 1
            elif self.value > value:
                adder = -1
            self.value += adder
            dpg.configure_item(self.displayText, text=str(self.value))
            self.animate(adder)
            time.sleep(0.03)
        self.vrooming = False

    def updateinstant(self, value):
        if self.vrooming:
            self.keepgoing = False
            # self.myT.join()
            self.keepgoing = True
        self.vrooming = True
        self.updateinstant1(int(value))

    def updateinstant1(self, value):
        if self.value < value:
            adder = 1
        elif self.value > value:
            adder = -1
        else:
            return
        while self.value != value and self.keepgoing:
            if self.value < value:
                adder = 1
            elif self.value > value:
                adder = -1
            self.value += adder
            dpg.configure_item(self.displayText, text=str(self.value))
            self.animate(adder)
            # time.sleep(0.003)
        self.vrooming = False

    def doloading(self):
        myT = threading.Thread(target=self.loading)
        self.loadzing = True
        myT.start()

    def getColorMapValue(
        self, itemV, colorMap, divisor=1, cmOffset=0.000, invert=False
    ) -> list:
        if itemV + cmOffset > 1 or itemV + cmOffset < 0:
            cmOffset * -1
        if dpg.is_dearpygui_running():
            myVa: List[int] | Tuple[int, ...] = dpg.sample_colormap(
                colorMap, itemV + cmOffset
            )
        myV = list()
        for v in myVa:
            if invert:
                v = 1 - v
            myV.append(v * 255 / divisor)
        return myV

    def loading(self):
        while dpg.is_dearpygui_running() and self.loadzing:
            lv = dpg.get_item_user_data(self.funNode) + 1
            dpg.apply_transform(
                self.funNode,
                dpg.create_rotation_matrix(math.pi * lv / 100.0, [0, 0, -1]),
            ) * dpg.create_translation_matrix([25, 0])
            dpg.set_item_user_data(self.funNode, lv)
            time.sleep(0.03)

    def animate(self, adder):
        lineV = dpg.get_item_user_data(self.theNode2) + adder
        dpg.apply_transform(
            self.theNode2,
            dpg.create_rotation_matrix(math.pi * lineV / 80.0, [0, 0, -1]),
        )
        dpg.set_item_user_data(self.theNode2, lineV)
        # for matt in self.matrii:
        # 	lineV = dpg.get_item_user_data(matt) + adder
        # 	dpg.apply_transform(matt, dpg.create_translation_matrix([15,0])*dpg.create_rotation_matrix(math.pi*lineV/70.0 , [0, 0, -1]))
        # 	dpg.set_item_user_data(matt, lineV)
        dpg.configure_item(
            self.inner,
            fill=self.getColorMapValue(self.value / 100, self.colormapInner),
            color=self.getColorMapValue(
                self.value / 100, self.colormapOuter, invert=True
            ),
        )
        dpg.configure_item(
            self.outer,
            fill=self.getColorMapValue(self.value / 100, self.colormapOuter),
            color=self.getColorMapValue(
                self.value / 100, self.colormapInner, invert=True
            ),
        )
        tc = self.getColorMapValue(self.value / 100, self.colormapInner, invert=True)
        ntc = [tc[0], tc[1], tc[2], 255]
        x, y = self.pos
        tsi = dpg.get_text_size(str(self.value))
        dpg.configure_item(self.displayText, color=ntc, pos=(x - tsi[0], y + tsi[1]))
        dpg.configure_item(
            self.line1,
            color=self.getColorMapValue(
                self.value / 100, self.colormapOuter, invert=True
            ),
        )
