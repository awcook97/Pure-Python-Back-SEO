import dearpygui.dearpygui as dpg
import webbrowser
from Utils import articleToHTML


class CheckBrowser:
    def __init__(self, source, parent):
        self.source = source
        dpg.add_button(
            label="View In Browser", callback=self.OpenBrowser, parent=parent
        )

    def OpenBrowser(self, *args, **kwargs):
        myInp = dpg.get_value(self.source)
        theFile, theHTML = articleToHTML(myInp)
        webbrowser.open_new(theFile)
