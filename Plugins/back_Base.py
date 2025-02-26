from Plugins import Plugin
import dearpygui.dearpygui as dpg


class Base(Plugin):
    """
    Base Plugin is the plugin that you copy in order to create a Plugin. It does nothing, just for copy/paste.
    > All plugins start with back_<ClassName>.py. Ex: back_Base.py contains the Base class, back_Draw.py contains the Draw class.
    > When you create a plugin, you can make a new window, make a menu, or put it in the main tab bar, up to you.
    > Back SEO will read the filename, so if you want to be included in the program, the file must start with "back_"
    > For extra speed, you can try to compile the plugin into a .pyd file. To do that, you can find that information
            in the Examples folder (Speedy_Compiled.pyx)

    :param Plugin: Subclass of Plugin
    :type Plugin: Back SEO Plugin
    """

    def __init__(self) -> None:
        plugin_name = "Plugin"
        author = "author"
        info = "What does the plugin do?"

    def _create_menu(self, parent):
        with dpg.menu(label="Menu Name", parent=parent) as backMenu:
            dpg.add_menu_item(label="Menu Item")
        return backMenu

    def _create_tab(self, parent):
        with dpg.tab(label="Tab Name", parent=parent) as backTab:
            with dpg.child_window(height=120):
                dpg.add_text("Tab Content")
        return backTab

    def _create_window(self):
        with dpg.window(label="Window Title") as backWin:
            with dpg.child_window():
                dpg.add_text("Window Content")
        return backWin
