import abc
from typing import Union
from multiprocessing import Queue
from queue import Empty
import dearpygui.dearpygui as dpg
from BackSEODataHandler import *


class Core_UI(metaclass=abc.ABCMeta):
    """
    Core_UI - Core Features of Back SEO

    We use this interface to build the Core_UI
            Build with these methods:
                    *save_data(self): Data to be saved on exit
                    *load_data(self): Data to be loaded on startup
                    _binit_(self):initialize variables - create folders, other init stuff, no UI, parent not passed}
                    _create_menu(self, parent): create menu, defaults to 0
                    _create_tab(self, parent): create tab, defaults to 0
                    _create_window(self): create window, defaults to 0

    * Required or throw error.
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, "load_ui")
            and callable(subclass.load_ui)
            and hasattr(subclass, "register_data")
            and callable(subclass.register_data)
            and hasattr(subclass, "save_data")
            and callable(subclass.save_data)
            and hasattr(subclass, "load_data")
            and callable(subclass.load_data)
        )

    def __init_subclass__(cls) -> None:
        cls._bseoData(cls, getBackSEODataHandler())

    def create_menu(self, parent, before):
        """Create the menu that your plugin will use."""
        self._menu = Core_Menu(self._create_menu(parent, before))
        return self._menu._id

    def create_tab(self, parent, befor):
        """Create a tab in the main tab group"""
        self._tab = Core_Tab(self._create_tab(parent, befor))
        return self._tab._id

    def create_window(self):
        """Create a window"""
        self._window = Core_Window(self._create_window())
        return self._window._id

    def add_queues(self, job: list):
        self.jobq = job
        self.resultsq = Queue()

    def addRealPrimaryWindow(self, realprimarywindow: int | str):
        self.real_primary_window = realprimarywindow

    def checkQueue(self):
        self.updateUData()
        try:
            job = self.resultsq.get_nowait()
        except Empty:
            return
        callback, args = job
        callback(*args)

    def _create_menu(self, parent):
        return 0

    def _create_tab(self, parent):
        return 0

    def _create_window(self):
        return 0

    @abc.abstractmethod
    def save_data(self):
        """Save the data that's stored in the data handler"""
        raise NotImplementedError

    @abc.abstractmethod
    def load_data(self):
        """Load data from the BackSEODataHandler"""
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, piece, data):
        raise NotImplementedError

    @abc.abstractmethod
    def updateUData(self):
        raise NotImplementedError

    def _bseoData(self, d: BackSEODataHandler):
        self.bseoData = d


class Core_Menu:
    def __init__(self, uid, **kwargs):
        self._id: int | str = uid
        self.show()

    def show(self):
        if self._id == 0:
            return
        dpg.configure_item(self._id, show=True)

    def hide(self):
        if self._id == 0:
            return
        dpg.configure_item(self._id, show=False)


class Core_Tab:
    def __init__(self, uid, **kwargs):
        self._id: int | str = uid
        self.show()

    def show(self):
        if self._id == 0:
            return
        dpg.configure_item(self._id, show=True)

    def hide(self):
        if self._id == 0:
            return
        dpg.configure_item(self._id, show=False)


class Core_Window:
    def __init__(self, uid, **kwargs):
        self._id: int | str = uid
        self.hide()

    def show(self):
        if self._id == 0:
            return
        dpg.configure_item(self._id, show=True)

    def hide(self):
        if self._id == 0:
            return
        dpg.configure_item(self._id, show=False)
