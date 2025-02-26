from Plugins import Plugin
import dearpygui.dearpygui as dpg
import math


class Speedy_Uncompiled(Plugin):
    """
    Uncompiled plotting plugin
    """

    def __init__(self) -> None:
        plugin_name = "This is an uncompiled plugin"
        author = "Andrew Cook"
        info = "Demonstrates how uncompiled plugins work."

    def _create_menu(self, parent):
        with dpg.menu(label="UnCompiled Menu", parent=parent) as backMenu:
            dpg.add_menu_item(label="Compiled Menu Item")
        return backMenu

    def _create_tab(self, parent):
        with dpg.tab(label="UnCompiled Tab", parent=parent) as backTab:
            with dpg.child_window(height=30):
                dpg.add_text("Let's look at a complex graph:")
            with dpg.plot() as self.complexPlot:
                self.xax = dpg.add_plot_axis(dpg.mvXAxis, label="x-axis")
                self.yax = dpg.add_plot_axis(dpg.mvYAxis, label="y-axis")
                self.basicSeries = dpg.add_line_series(
                    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                    label="Basic Series",
                    parent=self.yax,
                )
            dpg.add_button(
                label="Give me a more complex plot", callback=self.updatePlot
            )
        return backTab

    def updatePlot(self):
        x = list()
        y = list()
        lastPrime = 0
        for i in range(10000000):
            x.append(i)
            if self.isPrime(i):
                y.append(i)
                lastPrime = i
            else:
                y.append(lastPrime)
        self.advancedSeries = dpg.add_line_series(
            x, y, label="Advanced Series", parent=self.yax
        )

    def isPrime(self, n):
        if n <= 1:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True

    def _create_window(self):
        with dpg.window(label="Window Title") as backWin:
            with dpg.child_window():
                dpg.add_text("Window Content")
        return backWin
