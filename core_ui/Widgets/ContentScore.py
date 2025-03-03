from core_ui import Core_UI
import dearpygui.dearpygui as dpg
from Utils._textstat import textstat
from BackSEODataHandler import getBackSEODataHandler


class CoreContentScore:
    RECKW = 0
    RECHEADER = 1
    RECLENGTH = 2
    RECREADABILITY = 3
    TARGET = 4
    STATIC = 5

    def __init__(
        self,
        recKWs: list,
        recHead: int,
        recLength: int,
        recReadability: int,
        target=None,
    ):
        """Create the Content Score by giving it the recommended values. Then choose between a static score,
        and a dynamic score. Static score goes in reports, dynamic score is user content editor.
        target is the input text OR text widget that we're comparing"""
        self.recKWs = recKWs
        self.recHead = recHead
        self.recLength = recLength
        self.recReadability = recReadability
        self.target = target
        self.dynamic = False
        self.stats = dict()
        # print("Making stupid shit -> Theme")
        with dpg.theme() as self.subStyleTheme:
            with dpg.theme_component(dpg.mvAll) as self.subStyleThemeComponent:
                dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 5, 0)

        self.dh = getBackSEODataHandler()
        self.reg = self.dh.register
        self.subKWScoreValue = dpg.add_float_value(parent=self.reg, default_value=0.0)
        self.subHeadScoreValue = dpg.add_float_value(parent=self.reg, default_value=0.0)
        self.subLengthScoreValue = dpg.add_float_value(
            parent=self.reg, default_value=0.0
        )
        self.subReadScoreValue = dpg.add_float_value(parent=self.reg, default_value=0.0)
        self.score = dpg.add_float_value(parent=self.reg, default_value=0.0)
        self.dynamic = True
        self.colTheme = dict()

        self.totKW = 0.0
        self.getColors()
        # print("Making stupid shit -> Window drawing")
        self.draw(dpg.add_window(show=False))

    def _delete(self):
        if self.dynamic:
            dpg.delete_item(self.subKWScoreValue)
            dpg.delete_item(self.subHeadScoreValue)
            dpg.delete_item(self.subLengthScoreValue)
            dpg.delete_item(self.subReadScoreValue)
            dpg.delete_item(self.score)
            dpg.delete_item(self.allScores)
            dpg.delete_item(self.progressbar)
            dpg.delete_item(self.subScores)
            dpg.delete_item(self.subKWScore)
            dpg.delete_item(self.subHeadScore)
            dpg.delete_item(self.subLengthScore)
            dpg.delete_item(self.subReadScore)
            dpg.delete_item(self.maintooltip)
            dpg.delete_item(self.maintooltiptext)
            dpg.delete_item(self.subtooltip)
            dpg.delete_item(self.subtooltiptext)
        for i in self.colTheme.values():
            dpg.delete_item(i)

    def draw(self, parent):
        self.allScores = dpg.add_group(
            horizontal=True, horizontal_spacing=2, parent=parent
        )
        self.progressbar = dpg.add_progress_bar(
            label="Content Score",
            overlay="0/100",
            width=150,
            height=25,
            source=self.score,
            parent=self.allScores,
        )
        self.subScores = dpg.add_group(parent=self.allScores, height=6)
        self.subKWScore = dpg.add_progress_bar(
            width=15, height=5, parent=self.subScores, source=self.subKWScoreValue
        )
        self.subHeadScore = dpg.add_progress_bar(
            width=15, height=5, parent=self.subScores, source=self.subHeadScoreValue
        )
        self.subLengthScore = dpg.add_progress_bar(
            width=15, height=5, parent=self.subScores, source=self.subLengthScoreValue
        )
        self.subReadScore = dpg.add_progress_bar(
            width=15, height=5, parent=self.subScores, source=self.subReadScoreValue
        )
        self.maintooltip = dpg.add_tooltip(parent=self.progressbar)
        self.maintooltiptext = dpg.add_text("", parent=self.maintooltip)
        self.subtooltip = dpg.add_tooltip(parent=self.subScores)
        self.subtooltiptext = dpg.add_text("", parent=self.subtooltip)
        dpg.bind_item_theme(self.subScores, self.subStyleTheme)

    def getColorMapValue(self, itemV):
        myVa = dpg.sample_colormap(self.colormap, itemV)
        myV = list()
        for v in myVa:
            myV.append(v * 255)
        return myV

    def updateTheme(self, item, val):
        # dpg.lock_mutex()
        col = self.getColorMapValue(val)
        dpg.configure_item(item, overlay=f"{int(val * 100)} / 100")
        with dpg.theme() as itemtheme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(
                    dpg.mvThemeCol_PlotHistogram, col, category=dpg.mvThemeCat_Core
                )
        dpg.bind_item_theme(item, itemtheme)
        # dpg.unlock_mutex()

    def updateSources(self, s: int, newSource):
        """s is always a static. newSource is the new source
        RECKW = 0	->		List 	->	Keyword list\n
        RECHEADER = 1->		int		->	Num Headers\n
        RECLENGTH = 2->		int		->	Length\n
        RECREADABILITY = 3->int		->	Readability\n
        TARGET = 4	->		int		->	ID of dynamic target\n
        STATIC = 5	->		tuple	->	(int(headers), int(length), int(readability), ID(text))
        """
        if s == self.RECKW:
            self.recKWs = newSource
        if s == self.RECHEADER:
            self.recHead = newSource
        if s == self.RECLENGTH:
            self.recLength = newSource
        if s == self.RECREADABILITY:
            self.recReadability = newSource
        if s == self.TARGET:
            self.target = newSource
            return self.gettarStats()
        if s == self.STATIC:
            self.tarHead, self.tarLength, self.tarReadability, self.target = newSource
            return self.getStaticKWStats()

    def addSource(self, headerCount, length, readability, target, parent):
        """Creates a new static source for the displayed content score.
        This won't be updated, it will only show the bar charts.
        """
        try:
            headerCount = int(headerCount)
            length = int(length)
            readability = float(readability)
        except:
            return
        # print("Making stupid shit -> Lower article")
        lowerArt = str(target).lower()  # type: str
        totkw = 0
        artCount = 0
        # print("Making stupid shit -> recKWs")
        if self.recKWs is not None:
            # print("Making stupid shit -> recKWs Loop")
            for kw, count in self.recKWs:
                if count == 0:
                    continue
                totkw += count
                artCount += lowerArt.count(kw.lower())
        # print("Making stupid shit -> shitty equations")
        if totkw == 0:
            totkw = 1
        kwC = artCount / totkw
        if kwC > 1:
            kwC = 1
        if self.recHead == 0:
            self.recHead = 1
        hrC = headerCount / self.recHead
        if hrC > 1:
            hrC = 1
        if self.recLength == 0:
            self.recLength = 1
        lnC = length / self.recLength
        if lnC > 1:
            lnC = 1
        # print("Making stupid shit -> Readability")
        if readability > self.recReadability:
            dnC = 1 - (readability - self.recReadability) * 0.1
            if dnC < 0:
                dnC = 0.0
        elif readability < 1.0:
            dnC = 0.0
        else:
            dnC = 1.0
        score = (kwC + hrC + lnC + dnC) / 4
        # print("Okay, got the score")
        allScores = dpg.add_group(horizontal=True, horizontal_spacing=2, parent=parent)
        progressbar = dpg.add_progress_bar(
            label="Content Score",
            overlay="0/100",
            width=150,
            height=25,
            default_value=score,
            parent=allScores,
        )
        subScores = dpg.add_group(parent=allScores, height=6)
        subKWScore = dpg.add_progress_bar(
            width=15, height=5, parent=subScores, default_value=kwC
        )
        subHeadScore = dpg.add_progress_bar(
            width=15, height=5, parent=subScores, default_value=hrC
        )
        subLengthScore = dpg.add_progress_bar(
            width=15, height=5, parent=subScores, default_value=lnC
        )
        subReadScore = dpg.add_progress_bar(
            width=15, height=5, parent=subScores, default_value=dnC
        )
        maintooltip = dpg.add_tooltip(parent=progressbar)
        maintooltiptext = dpg.add_text("", parent=maintooltip)
        subtooltip = dpg.add_tooltip(parent=subScores)
        subtooltiptext = dpg.add_text("", parent=subtooltip)
        # print("Making stupid shit -> Shitty Tooltips")
        scorestats = ""
        scorestats += f"Score: {score * 100} / 100"
        dpg.configure_item(
            maintooltiptext, default_value=f"Statistics:\n{scorestats}", wrap=-1
        )
        sscostats = ""
        sscostats += f"Keywords: {artCount} / {totkw}\n"
        sscostats += f"Headers: {headerCount} / {str(int(self.recHead))}\n"
        sscostats += f"Length: {length} / {str(int(self.recLength))}\n"
        sscostats += (
            f"Readability: {round(readability, 2)} / {round(self.recReadability, 2)}"
        )
        # print("Making stupid shit -> Configuring subtooltiptext and subsccores")
        dpg.configure_item(
            subtooltiptext, default_value=f"Substats:\n{sscostats}", wrap=-1
        )
        dpg.bind_item_theme(subScores, self.subStyleTheme)
        # print("Making stupid shit -> shitty themes")
        self.updateTheme(progressbar, score)
        # print("Making stupid shit -> progressbar/score")
        self.updateTheme(subKWScore, kwC)
        # print("Making stupid shit -> subKWScore")
        self.updateTheme(subHeadScore, hrC)
        self.updateTheme(subLengthScore, lnC)
        self.updateTheme(subReadScore, dnC)
        return score

    def gettarStats(self):
        myArt = dpg.get_value(self.target)  # type: str
        myArtLower = myArt.lower()
        mySplit = myArtLower.split("\n")
        if len(myArt.split(" ")) > 125:
            txtSt = textstat(myArt, merge=True)
            self.stats = txtSt
            self.tarLength = self.stats["words"]
            if self.stats["words"] > 100:
                self.tarReadability = txtSt["Coleman-Liau"]
        else:
            self.tarReadability = 21.1
            self.tarLength = len(myArt.split(" "))
        self.tarHead = 0
        for sp in mySplit:
            if sp.startswith(("h2:", "h3:", "h4:", "h5:", "h6:")):
                self.tarHead += 1
        return self.getKWStats()

    def getStaticKWStats(self):
        if not len(self.recKWs):
            self.tarKW = 0
            self.update()
            return dict()
        myT = self.target  # type: str
        myT = myT.lower()
        rDict = dict()
        self.tarKW = 0
        self.totKW = 0
        for kw, count in self.recKWs:
            lkw = kw.lower()
            self.totKW += count
            artCount = myT.count(lkw)
            self.tarKW += artCount
            rDict[kw] = artCount
        return self.update(True)

    def getKWStats(self):
        if not len(self.recKWs):
            self.tarKW = 0
            # print (f"{self.recKWs} kws")
            self.update()
            return dict()
        myT = dpg.get_value(self.target)  # type: str
        myT = myT.lower()
        rDict = dict()
        self.tarKW = 0
        self.totKW = 0
        for kw, count in self.recKWs:
            lkw = kw.lower()
            self.totKW += count
            artCount = myT.count(lkw)
            self.tarKW += artCount
            rDict[kw] = artCount
        self.update()
        return rDict

    def update(self, so: bool = False):
        if self.totKW == 0:
            self.totKW = 1
        kwC = self.tarKW / self.totKW
        if kwC > 1:
            kwC = 1
        if self.recHead == 0:
            self.recHead = 1
        hrC = self.tarHead / self.recHead
        if hrC > 1:
            hrC = 1
        if self.recLength == 0:
            self.recLength = 1
        lnC = self.tarLength / self.recLength
        if lnC > 1:
            lnC = 1
        if self.tarReadability > self.recReadability:
            dnC = 1 - (self.tarReadability - self.recReadability) * 0.1
            if dnC < 0:
                dnC = 0.0
        elif self.tarReadability < 1.0:
            dnC = 0.0
        else:
            dnC = 1.0
        score = (kwC + hrC + lnC + dnC) / 4
        dpg.set_value(self.subKWScoreValue, kwC)
        dpg.set_value(self.subHeadScoreValue, hrC)
        dpg.set_value(self.subLengthScoreValue, lnC)
        dpg.set_value(self.subReadScoreValue, dnC)
        dpg.set_value(self.score, score)

        scorestats = ""
        if len(self.stats):
            for key, val in self.stats.items():
                scorestats += f"{key}: {val}\n"
        scorestats += f"Score: {score * 100} / 100"
        dpg.configure_item(
            self.maintooltiptext, default_value=f"Statistics:\n{scorestats}", wrap=-1
        )
        sscostats = ""
        sscostats += f"Keywords: {self.tarKW} / {self.totKW}\n"
        sscostats += f"Headers: {self.tarHead} / {str(int(self.recHead))}\n"
        sscostats += f"Length: {self.tarLength} / {str(int(self.recLength))}\n"
        sscostats += f"Readability: {round(self.tarReadability, 2)} / {round(self.recReadability, 2)}"

        dpg.configure_item(
            self.subtooltiptext, default_value=f"Substats:\n{sscostats}", wrap=-1
        )
        self.doUpdateTheme()
        if so:
            return (kwC, hrC, lnC, dnC, score)

    def doUpdateTheme(self):
        self.updateTheme(self.progressbar, dpg.get_value(self.score))
        self.updateTheme(self.subKWScore, dpg.get_value(self.subKWScore))
        self.updateTheme(self.subHeadScore, dpg.get_value(self.subHeadScore))
        self.updateTheme(self.subLengthScore, dpg.get_value(self.subLengthScore))
        self.updateTheme(self.subReadScore, dpg.get_value(self.subReadScore))

    def getColors(self):
        self.colormapRegistry = dpg.add_colormap_registry()
        self.colormap = dpg.add_colormap(
            [
                [255, 0, 0, 255],
                [248, 255, 50, 255],
                [50, 50, 200, 255],
                [0, 255, 0, 255],
            ],
            False,
            parent=self.colormapRegistry,
            label="Content Score",
        )
        # with dpg.theme() as self.yellow_theme:
        # 	with dpg.theme_component(dpg.mvAll):
        # 		dpg.add_theme_color(dpg.mvThemeCol_Button, (248, 255, 0), category=dpg.mvThemeCat_Core)
        # 		dpg.add_theme_color(dpg.mvThemeCol_Text, (0,0,0,255), category=dpg.mvThemeCat_Core)
        # with dpg.theme() as self.pb_yellow_theme:
        # 	with dpg.theme_component(dpg.mvAll):
        # 		dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, (248, 255, 0, 255), category=dpg.mvThemeCat_Core)
        # 		dpg.add_theme_color(dpg.mvThemeCol_Text, (0,0,0,255), category=dpg.mvThemeCat_Core)
        # with dpg.theme() as self.green_theme:
        # 	with dpg.theme_component(dpg.mvAll):
        # 		dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 255, 0), category=dpg.mvThemeCat_Core)
        # 		dpg.add_theme_color(dpg.mvThemeCol_Text, (0,0,0,255), category=dpg.mvThemeCat_Core)
        # with dpg.theme() as self.pb_green_theme:
        # 	with dpg.theme_component(dpg.mvAll):
        # 		dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, (0, 255, 0, 255), category=dpg.mvThemeCat_Core)
        # 		dpg.add_theme_color(dpg.mvThemeCol_Text, (0,0,0,255), category=dpg.mvThemeCat_Core)
        # with dpg.theme() as self.blue_theme:
        # 	with dpg.theme_component(dpg.mvAll):
        # 		dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 0, 255), category=dpg.mvThemeCat_Core)
        # with dpg.theme() as self.pb_blue_theme:
        # 	with dpg.theme_component(dpg.mvAll):
        # 		dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, (0, 0, 255, 255), category=dpg.mvThemeCat_Core)
        # with dpg.theme() as self.red_theme:
        # 	with dpg.theme_component(dpg.mvAll):
        # 		dpg.add_theme_color(dpg.mvThemeCol_Button, (255, 0, 0), category=dpg.mvThemeCat_Core)
        # with dpg.theme() as self.pb_red_theme:
        # 	with dpg.theme_component(dpg.mvAll):
        # 		dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, (255, 0, 0, 255), category=dpg.mvThemeCat_Core)

    def load_data(self):
        pass

    def _create_menu(self, parent):
        pass

    def _create_tab(self, parent):
        pass

    def _create_window(self):
        pass
