import os
import importlib
import dearpygui.dearpygui as dpg
from typing import Dict, List
from Plugins import Plugin


class PluginController:
    def __init__(self):
        self._plugins: Dict[str, Plugin] = dict()
        self._modules = dict()
        self._builtModules = dict()
        self._menu_items = dict()
        for plugin in os.listdir("Plugins"):
            if plugin.startswith("back_") and plugin.endswith(".py"):
                callName = plugin.split("back_")[1].split(".py")[0]
                pName = plugin.split(".py")[0]
                impName = f"Plugins.{pName}"
                theImp = importlib.import_module(impName, "Plugins")
                self._modules[callName] = theImp
                # print(f"self._plugins[{callName}] = {theImp}.{callName}()")
                exec(f"self._plugins[callName] = theImp.{callName}()")
            if plugin.endswith(".pyd"):
                pName = plugin.split(".")[0]
                callName = pName.replace("_", "")
                impName = f"Plugins.{pName}"
                theImp = importlib.import_module(impName)
                exec(f"self._plugins[callName] = theImp.{callName}()")
        self.activePlugins = list()
        self.initWindows()
        with dpg.handler_registry() as self.pluginGlobalHandler:
            dpg.add_key_down_handler(dpg.mvKey_ScrollLock, callback=self.reloadAll)

    def reloadAll(self):
        for plugin in self._plugins:
            self.reload(plugin)

    def reload(self, plugin):
        wasActive = False
        if plugin in self.activePlugins:
            self.activePlugins.remove(plugin)
            wasActive = True
        self.deactivate(plugin)
        _module = importlib.reload(self._modules[plugin])
        # print(f"self._plugins[{plugin}] = {_module}.{plugin}()")
        exec(f"self._plugins[plugin] = _module.{plugin}()")
        dpg.delete_item(self._menu_items[plugin])
        self.add_plugin_menu_items(plugin, self.pluginControllerMenu)
        self._plugins[plugin].create_menu(self.mainMenu)
        self._plugins[plugin].create_tab(self.mainTabBar)
        self._plugins[plugin].create_window()
        if wasActive:
            self.toggleActive(plugin)

    def add_plugin_menu_items(self, plugin, parent):
        self._menu_items[plugin] = dpg.add_menu_item(
            label=plugin,
            callback=lambda: self.toggleActive(plugin),
            parent=parent,
            check=False,
        )

    def add_plugin_menu(self, mBar):
        with dpg.menu(label="Plugins", parent=mBar) as self.pluginControllerMenu:
            for plugin in self._plugins:
                self.add_plugin_menu_items(plugin, self.pluginControllerMenu)
        self.initMenu(mBar)
        with dpg.menu(label="Reload Plugins", parent=mBar) as self.reloadMenu:
            for plugin in self._modules:
                dpg.add_menu_item(
                    label=plugin,
                    user_data=plugin,
                    callback=lambda s, a, u: self.reload(u),
                    parent=self.reloadMenu,
                )

    def initMenu(self, menuBar):
        self.mainMenu = menuBar
        for p in self._plugins.values():
            p.create_menu(menuBar)

    def initTab(self, tabBar):
        self.mainTabBar = tabBar
        for p in self._plugins.values():
            p.create_tab(tabBar)

    def initWindows(self):
        for p in self._plugins.values():
            p.create_window()

    def activate(self, plugin):
        self._plugins[plugin].activate()
        dpg.configure_item(self._menu_items[plugin], check=True)

    def deactivate(self, plugin):
        self._plugins[plugin].deactivate()
        dpg.configure_item(self._menu_items[plugin], check=False)

    def toggleActive(self, plugin):
        try:
            self.activePlugins.remove(plugin)
            self.deactivate(plugin)
        except:
            self.activePlugins.append(plugin)
            self.activate(plugin)
