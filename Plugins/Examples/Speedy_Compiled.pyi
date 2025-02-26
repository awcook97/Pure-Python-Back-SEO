"""This is a .pyi file for the compiled plugin Speedy_Compiled.cp311-win_amd64.pyd.
	Basically it's the source code for the original .py file, before it was translated
	into Cython (.pyx) code (mainly using ChatGPT) and then compiled into a .pyd file.
	This file serves no purpose other than to make code look pretty in your IDE since
	.pyd files are not human-readable.
"""

from Plugins import Plugin
import dearpygui.dearpygui as dpg
import math

class SpeedyCompiled(Plugin):
    """
    Compiled plotting plugin
    """

    def __init__(self) -> None: ...
    def _create_menu(self, parent): ...
    def _create_tab(self, parent): ...
    def updatePlot(self): ...
    def isPrime(self, n): ...
    def _create_window(self): ...
