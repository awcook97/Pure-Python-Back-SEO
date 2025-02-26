import pickle
import os
import multiprocessing
import dearpygui.dearpygui as dpg
import threading

"""Utility functions"""

import platform
from pathlib import Path


def user_settings_dir() -> Path:
    r"""Return path to application cache directory

    For different platforms, cache directories are:
        Windows:    C:\Users\<username>\AppData\Local\dearpygui_map\Cache
        Mac OS X:   ~/Library/Caches/dearpygui_map
        Unix:       ~/.cache/dearpygui_map
    """
    app_name = "Back SEO Marketing Software"
    if platform.system() == "Windows":
        return Path.home() / "AppData" / "Local" / app_name / "Settings"
    if platform.system() == "Darwin":
        return Path.home() / "Library" / "Caches" / app_name
    return Path.home() / ".cache" / app_name


def user_local_dir() -> Path:
    app_name = "Back SEO Marketing Software"
    if platform.system() == "Windows":
        return Path.home() / "AppData" / "Local" / app_name / "Local"
    if platform.system() == "Darwin":
        return Path.home() / "Library" / "Local" / app_name
    return Path.home() / ".cache" / app_name


"""Only Need One Settings Instance"""


class SingletonMeta(type):
    _instances = {}
    _lock = multiprocessing.Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


"""Settings Class"""


class BackSEOSettings(metaclass=SingletonMeta):
    def __init__(self):
        if not os.path.exists("output/custom"):
            os.makedirs("output/custom")
        if not os.path.exists("output/htmls"):
            os.makedirs("output/htmls")
        if not os.path.exists("output/images"):
            os.makedirs("output/images")
        if not os.path.exists("output/localclients"):
            os.makedirs("output/localclients")
        if not os.path.exists("output/reports"):
            os.makedirs("output/reports")
        if not os.path.exists("output/screenshots"):
            os.makedirs("output/screenshots")
        if not os.path.exists("output/search_results_audit"):
            os.makedirs("output/search_results_audit")
        if not os.path.exists("output/sitemap_audits"):
            os.makedirs("output/sitemap_audits")
        if not os.path.exists("Plugins"):
            os.makedirs("Plugins")
        self.vsync: bool = True
        self.animations: bool = True
        self.cpucores: int = multiprocessing.cpu_count() / 2
        self.maxcpucores: int = multiprocessing.cpu_count()
        self.helperthreads: int = 4
        self.fps: int = 120
        self.width: int = 1280
        self.height: int = 800
        self.agencyOutput: str = "output"
        self.settingsOutpath: Path = user_settings_dir()
        if not os.path.exists(self.settingsOutpath):
            os.makedirs(self.settingsOutpath)
        self.settingsFile: Path = self.settingsOutpath / "settings.bseo"
        if os.path.exists(self.settingsFile):
            with open(self.settingsFile, "rb") as f:
                tempSettings = pickle.load(f)
            self.__dict__.update(tempSettings.__dict__)
            del tempSettings
        self.save()
        # self.fullscreen:	bool	=	False

    def setVp(self, viewport):
        self.vp = viewport

    def changeVsync(self, value: bool):
        self.vsync = value
        dpg.configure_viewport(self.vp, vsync=value)
        self.save()

    def changeAnimations(self, value: bool):
        self.animations = value
        dpg.configure_app(wait_for_input=not value)
        self.save()

    # def changeFullscreen(self, value:bool):
    # 	self.fullscreen = value
    # 	self.save()

    def changeCpuCores(self, value: int):
        self.cpucores = value
        self.save()

    def changeHelperThreads(self, value: int):
        self.helperthreads = value
        self.save()

    def changeFps(self, value: int):
        self.fps = value
        self.save()

    def changeWidth(self, value: int):
        self.width = value
        self.save()

    def changeHeight(self, value: int):
        self.height = value
        self.save()

    def changeAgencyOutput(self, value: str):
        self.agencyOutput = value
        self.save()

    def save(self):
        with open(self.settingsFile, "wb") as f:
            pickle.dump(self, f)

    def load(self):
        if os.path.exists(self.settingsFile):
            with open(self.settingsFile, "rb") as f:
                return pickle.load(f)
        return self
