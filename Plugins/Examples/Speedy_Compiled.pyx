"""
    This file shows off the speed of compiled plugins
    We take out the GIL, which slows down the main thread, 
    and run the computation in parallel, turning the ~5 minute
    function to run in about 10 seconds. Oftentimes, the GIL
    is not a problem, but when it is, it can be a huge problem.
    This is a good example of how to get around it.
    Mainly, if your function does a lot of math, or if you're 
    doing minor NLP, then compiling might help. If you're doing 
    a lot of IO (like scraping websites) then you should use 
    multiprocessing, asyncio and/or threading (Back SEO was built
    using a combination of all 3).

    
"""
import cython
from cython.parallel import prange
import dearpygui.dearpygui as dpg
import math
import dearpygui.dearpygui as dpg
from libc.math cimport sqrt
from libc.stdlib cimport malloc, free

cdef class Plugin:
    cdef public bint active
    cdef public object _menu, _tab, _window
    cdef str plugin_name, author, info

    def __subclass_init__(self):
        self.active = False

    def __init__(self):
        self.plugin_name = "Plugin"
        self.author = "author"
        self.info = "What does the plugin do?"

    def __str__(self):
        return self.plugin_name

    def create_menu(self, parent):
        self._menu = Plugin_Menu(self._create_menu(parent))

    def create_tab(self, parent):
        self._tab = Plugin_Tab(self._create_tab(parent))

    def create_window(self):
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


cdef class Plugin_Menu:
    cdef int _id

    def __init__(self, int uid, **kwargs):
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


cdef class Plugin_Tab:
    cdef int _id

    def __init__(self, int uid, **kwargs):
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


cdef class Plugin_Window:
    cdef int _id

    def __init__(self, int uid, **kwargs):
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


cdef bint isPrime(int n) nogil:
    cdef int i, limit
    limit = <int>sqrt(n)
    if n <= 1:
        return False
    for i in range(2, limit + 1):
        if n % i == 0:
            return False
    return True

cdef class SpeedyCompiled(Plugin):
    """
    Uncompiled plotting plugin
    """
    cdef public complexPlot, xax, yax, basicSeries, advancedSeries
    
    def __init__(self):
        self.plugin_name = "This is a compiled plugin"
        self.author = "Andrew Cook"
        self.info = "Shows off the speed of compiled plugins"

    def _create_menu(self, parent):
        with dpg.menu(label="Compiled Menu", parent=parent) as backMenu:
            dpg.add_menu_item(label="Compiled Menu Item")
        return backMenu

    def _create_tab(self, parent):
        with dpg.tab(label="Compiled Tab", parent=parent) as backTab:
            with dpg.child_window(height=30):
                dpg.add_text("Let's look at a complex graph:")
            with dpg.plot() as self.complexPlot:
                self.xax = dpg.add_plot_axis(dpg.mvXAxis, label="x-axis")
                self.yax = dpg.add_plot_axis(dpg.mvYAxis, label="y-axis")
                self.basicSeries = dpg.add_line_series([1,2,3,4,5,6,7,8,9,10], [1,2,3,4,5,6,7,8,9,10], label="Basic Series", parent=self.yax)
            dpg.add_button(label="Give me a more complex plot", callback=self.updatePlot)
        return backTab
        
    @cython.boundscheck(False)
    def updatePlot(self):
        cdef int i, j, lastPrime
        cdef int *x_arr = <int *>malloc(10000000 * sizeof(int))
        cdef int *y_arr = <int *>malloc(10000000 * sizeof(int))
        cdef int[:] x = <int[:10000000]>x_arr
        cdef int[:] y = <int[:10000000]>y_arr
        cdef int chunk_size = 10000000 // 16

        for i in range(10000000):
            x[i] = i

        # Release the GIL for the computation
       ##with nogil:
        for i in prange(16, nogil=True):  # 16 threads
            lastPrime = 0
            for j in range(i*chunk_size, (i+1)*chunk_size):
                if isPrime(j):
                    y[j] = j
                    lastPrime = j
                else:
                    y[j] = lastPrime

        # Convert C arrays back to Python lists
        x_list = list(x)
        y_list = list(y)

        # Free allocated memory
        free(x_arr)
        free(y_arr)

        self.advancedSeries = dpg.add_line_series(x_list, y_list, label="Advanced Series", parent=self.yax)

    cdef bint isPrime(self, int n):
        cdef int i
        if n <= 1:
            return False
        for i in range(2, int(math.sqrt(n)) + 1):
            if n % i == 0:
                return False
        return True

    def _create_window(self):
        with dpg.window(label="Window Title") as backWin:
            with dpg.child_window():
                dpg.add_text("Window Content")
        return backWin
