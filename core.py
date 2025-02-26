# core.py
import importlib
import regex
import os
import dearpygui.dearpygui as dpg
from Plugins import Plugin
import Utils._ChooseFonts as ChooseFonts
from Utils._EditTheme import EditTheme
from BackSEODataHandler import getBackSEODataHandler
from typing import Dict, List
from core_ui import Core_UI
from PluginController import PluginController


class BackSEOApp(Core_UI):
    def __init__(self):
        self._plugins = PluginController()
        # print(self._plugins)

    def repoProgBars(self):
        dpg.set_item_pos(self.progress1, [dpg.get_viewport_width() - 135, 0])
        dpg.set_item_pos(self.progress2, [dpg.get_viewport_width() - 135, 7])
        dpg.set_item_pos(self.progress3, [dpg.get_viewport_width() - 135, 14])
        dpg.set_item_pos(self.animations, [dpg.get_viewport_width() / 2 - 62, 0])

    def run(self):
        with dpg.window(label="Back SEO", menubar=True) as self.backSEOCoreWin:
            self.mainMenu = dpg.add_menu_bar()
            with dpg.menu(label="Tools", parent=self.mainMenu) as self.toolsMenu:
                dpg.add_menu_item(
                    label="Show About", callback=lambda: dpg.show_tool(dpg.mvTool_About)
                )
                dpg.add_menu_item(
                    label="Show Metrics",
                    callback=lambda: dpg.show_tool(dpg.mvTool_Metrics),
                )
                dpg.add_menu_item(
                    label="Show Documentation",
                    callback=lambda: dpg.show_tool(dpg.mvTool_Doc),
                )
                dpg.add_menu_item(
                    label="Show Debug", callback=lambda: dpg.show_tool(dpg.mvTool_Debug)
                )
                dpg.add_menu_item(
                    label="Show Style Editor",
                    callback=lambda: dpg.show_tool(dpg.mvTool_Style),
                )
                dpg.add_menu_item(
                    label="Show Font Manager",
                    callback=lambda: dpg.show_tool(dpg.mvTool_Font),
                )
                dpg.add_menu_item(
                    label="Show Item Registry",
                    callback=lambda: dpg.show_tool(dpg.mvTool_ItemRegistry),
                )
            self.EditTheme = EditTheme(self.mainMenu)
            self.ChooseFonts = ChooseFonts.ChooseFonts(self.mainMenu)
            self._plugins.add_plugin_menu(self.mainMenu)
            dh = getBackSEODataHandler()
            with dpg.theme() as self.subStyleTheme:
                with dpg.theme_component(dpg.mvAll) as self.subStyleThemeComponent:
                    dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 0, 0)
                    dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 0, 0)
            with dpg.group(
                horizontal=True,
                horizontal_spacing=0,
                pos=(dpg.get_viewport_width() - 135, 0),
            ) as self.progbars:
                self.animations = dpg.add_drawlist(
                    width=700, height=25, parent=self.mainMenu
                )
                with dpg.group() as self.actualProgBars:
                    self.progress1 = dpg.add_progress_bar(
                        width=125, height=3, parent=self.mainMenu, source=dh.loader1
                    )
                    self.progress2 = dpg.add_progress_bar(
                        width=125, height=3, parent=self.mainMenu, source=dh.loader2
                    )
                    self.progress3 = dpg.add_progress_bar(
                        width=125, height=7, parent=self.mainMenu, source=dh.loader3
                    )
                    with dpg.tooltip(parent=self.progress3):
                        dpg.add_text("FPS: ", source=dh.strLoader1)
            dpg.bind_item_theme(self.progbars, self.subStyleTheme)
            dpg.bind_item_theme(self.actualProgBars, self.subStyleTheme)
            dh.addtovpresize(self.repoProgBars)
            self.mainTabBar = dpg.add_tab_bar()
            self.options = dpg.add_tab(label="Options", parent=self.mainTabBar)
            self.optionsTab()
            self._plugins.initTab(self.mainTabBar)
        dpg.set_primary_window(self.backSEOCoreWin, True)

    def update(self, *args, **kwargs):
        pass

    def updateUData(self):
        # print("Updating UData")
        for plugin in self._plugins.activePlugins:
            # print(plugin)
            self._plugins._plugins[plugin].updateUData()

    def optionsTab(self):
        """
        vsync:			bool
        animations:		bool
        cpucores:		int
        helperthreads:	int
        fps:			int
        width:			int
        height:			int
        """
        dh = getBackSEODataHandler()
        self.bsettings = dh.getSettings()
        dpg.add_checkbox(
            label="Vsync",
            parent=self.options,
            default_value=self.bsettings.vsync,
            callback=lambda s, a, u: self.bsettings.changeVsync(a),
        )
        dpg.add_checkbox(
            label="Animations",
            parent=self.options,
            default_value=self.bsettings.animations,
            callback=lambda s, a, u: self.bsettings.changeAnimations(a),
        )
        dpg.add_input_int(
            label="FPS",
            parent=self.options,
            default_value=self.bsettings.fps,
            callback=lambda s, a, u: self.bsettings.changeFps(a),
            min_value=0,
            max_value=300,
            step=0,
        )
        dpg.add_text("Requires Restart", parent=self.options)
        dpg.add_input_int(
            label="CPU Cores",
            parent=self.options,
            default_value=self.bsettings.cpucores,
            callback=lambda s, a, u: self.bsettings.changeCpuCores(a),
            min_value=1,
            max_value=self.bsettings.maxcpucores,
            step=1,
            max_clamped=True,
            min_clamped=True,
        )
        dpg.add_input_int(
            label="Helper Threads",
            parent=self.options,
            default_value=self.bsettings.helperthreads,
            callback=lambda s, a, u: self.bsettings.changeHelperThreads(a),
            min_value=1,
            min_clamped=True,
            step=0,
        )
        dpg.add_input_int(
            label="Width",
            parent=self.options,
            default_value=self.bsettings.width,
            callback=lambda s, a, u: self.bsettings.changeWidth(a),
            min_value=100,
            max_value=10000,
            max_clamped=True,
            min_clamped=True,
            step=0,
        )
        dpg.add_input_int(
            label="Height",
            parent=self.options,
            default_value=self.bsettings.height,
            callback=lambda s, a, u: self.bsettings.changeHeight(a),
            min_value=100,
            max_value=10000,
            max_clamped=True,
            min_clamped=True,
            step=0,
        )

    def load_data(self):
        pass

    def save_data(self):
        pass

    def _create_menu(self, *args, **kwargs):
        return 0

    def _create_tab(self, *args, **kwargs):
        return 0

    def _create_window(self, *args, **kwargs):
        return 0


if __name__ == "__main__":
    dpg.create_context()

    dpg.create_viewport(title="Back SEO App", width=1280, height=800)
    dpg.setup_dearpygui()
    myApp = BackSEOApp()
    myApp.run()
