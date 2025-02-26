from core_ui import Core_UI
import dearpygui.dearpygui as dpg

class CoreAudit(Core_UI):
    def __init__(self) -> None:
        pass
    def __binit__(self):
        pass
    def save_data(self):
        pass
    def load_data(self):
        pass
    def _create_menu(self, parent, plug):
        # with dpg.menu(label="Inspect Results", parent=parent, before=plug) as self.theMenu:
        return 0
    def _create_tab(self, parent, plug):
        # with dpg.tab(label="Inspect Results", parent=parent, before=plug) as self.theTab:
        return 0
    def _create_window(self):
        return 0
    def updateUData(self):
        pass
    def update(self, piece, data):
        pass
