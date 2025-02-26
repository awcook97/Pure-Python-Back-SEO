import dearpygui.dearpygui as dpg


class Plugin:
    # plugin_name = "Plugin"
    # author = "author"
    # info = "What does the plugin do?"
    def __subclass_init__(self):
        """Set the plugin to inactive by default"""
        self.active = False

    def __init__(self) -> None:
        self.plugin_name = "Plugin"
        self.author = "author"
        self.info = "What does the plugin do?"

    def __str__(self):
        return self.plugin_name

    def create_menu(self, parent):
        """Create the menu that your plugin will use."""
        self._menu = Plugin_Menu(self._create_menu(parent))

    def create_tab(self, parent):
        """Create a tab in the main tab group"""
        self._tab = Plugin_Tab(self._create_tab(parent))

    def create_window(self):
        """Create a window"""
        self._window = Plugin_Window(self._create_window())

    def activate(self):
        self._menu.show()
        self._tab.show()
        self._window.show()
        self._activate()

    def deactivate(self):
        self._menu.hide()
        self._tab.hide()
        self._window.hide()
        self._deactivate()

    def _activate(self):
        return

    def _deactivate(self):
        return

    def _create_menu(self, parent):
        return 0

    def _create_tab(self, parent):
        return 0

    def _create_window(self):
        return 0

    def updateUData(self):
        return


class Plugin_Menu:
    def __init__(self, uid, **kwargs):
        self._id = uid
        self.hide()

    def show(self):
        if self._id == 0:
            return
        dpg.configure_item(self._id, show=True)

    def hide(self):
        if self._id == 0:
            return
        dpg.configure_item(self._id, show=False)


class Plugin_Tab:
    def __init__(self, uid, **kwargs):
        self._id = uid
        self.hide()

    def show(self):
        if self._id == 0:
            return
        dpg.configure_item(self._id, show=True)

    def hide(self):
        if self._id == 0:
            return
        dpg.configure_item(self._id, show=False)


class Plugin_Window:
    def __init__(self, uid, **kwargs):
        self._id = uid
        self.hide()

    def show(self):
        if self._id == 0:
            return
        dpg.configure_item(self._id, show=True)

    def hide(self):
        if self._id == 0:
            return
        dpg.configure_item(self._id, show=False)


if __name__ == "__main__":
    dpg.create_context()
    import back_Draw

    drawP = back_Draw.Draw()
    my_window = Plugin_Window(drawP.create_window())
    my_window.show()
    with dpg.viewport_menu_bar() as pMenuTest:
        my_menu = Plugin_Menu(drawP.create_menu(pMenuTest))
        my_menu.show()
    # with dpg.tab_bar(parent=my_window) as pTabTest:
    # 	my_tab_one = Plugin_Tab("Tab 1")
    # 	my_tab_one.add_child(dpg.add_text("my_tab_one"))
    # 	my_tab_one.show(pTabTest)
    # 	my_tab_two = Plugin_Tab("Tab 2")
    # 	my_tab_two.add_child(dpg.add_text("my_tab_two"))
    # 	my_tab_two.show(pTabTest)
    dpg.create_viewport(title="Plugin Test")
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
