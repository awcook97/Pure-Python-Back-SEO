import base64
import os
import dearpygui.dearpygui as dpg
import importlib
import importlib.util
import json
import ctypes
import sys
from Plugin import Plugin
import inspect

class PluginController(object):
	def __init__(self) -> None:
		self.plugins = dict() # type: dict[str,Plugin]
		self.activePlugins = dict() # type: dict[str, bool]
		self.confs = dict() # type: dict[str, list]
		self.confs["menu"] = list() # type: list[str]
		self.confs["tab"] = list() # type: list[str]
		self.confs["window"] = list() # type: list[str]
		self.confs["inject"] = list() # type: list[str]
		self.confs["injectDone"] = list() # type: list[str]
		self.confs["misc"] = list() # type: list[str]
		self.confs["miscDone"] = list() # type: list[str]
		thdir = os.getcwd()
		if os.path.exists('plugins'):
			for name in os.listdir('plugins'):
				#print(name)
				if name.endswith('.py') and name.count("Plugin"):
					oName = name.split('.py')[0]
					xt = '.py'
				
				# elif name.endswith('.pyd'):
				# 	oName = name.split('.')[0]
				# 	xt = '.pyd'
				else: continue
				spec = importlib.util.spec_from_file_location(oName, f"{thdir}/plugins/{oName}{xt}")
				tempP = importlib.util.module_from_spec(spec)
				sys.modules[oName] = tempP
				spec.loader.exec_module(tempP)
				print(tempP)
				self.plugins[oName] = tempP.getPlugin()
				self.activePlugins[oName] = False
				self.plugins[oName].active = False
		else:
			return
		self.activatePlugins()
		self.doinject()

	def activatePlugins(self):
		if not os.path.exists("plugins.plugins"):
			with open("plugins.plugins", 'w', encoding="utf-8") as f:
				json.dump(self.activePlugins, f)
		with open("plugins.plugins", 'r') as f:
			self.activePlugins = self.activePlugins | json.load(f)
		for plugin, active in self.activePlugins.items():
			if active: 
				self.plugins[plugin].active = True
				m, t, w, i, misc = self.plugins[plugin].get_configuration()
				if m: self.confs["menu"].append(plugin)
				if t: self.confs["tab"].append(plugin)
				if w: self.confs["window"].append(plugin)
				if i: self.confs["inject"].append(plugin)
				if misc: self.confs["misc"].append(plugin)

	def domenu(self, parent="childWindowPluginMenuBar"):
		dpg.delete_item(parent, children_only=True)
		for plugin in self.confs["menu"]:
			with dpg.menu(tag=f"pre{plugin}menu", parent=parent):
				self.plugins[plugin].create_menu()

	def dotab(self, parent="pluginTagBar"):
		dpg.delete_item(parent, children_only=True)
		for plugin in self.confs["tab"]:
			with dpg.tab(tag=f"pre{plugin}tab", parent=parent):
				self.plugins[plugin].create_tab()

	def dowindow(self):
		for plugin in self.confs["window"]:
			with dpg.window(tag=f"pre{plugin}window"):
				self.plugins[plugin].create_window(f"pre{plugin}window")

	def doinject(self):
		for plugin in self.confs["inject"]:
			if plugin not in self.confs["injectDone"]: 
				self.plugins[plugin].inject()
				self.confs["injectDone"].append(plugin)

	def domisc(self):
		for plugin in self.confs["misc"]:
			if plugin not in self.confs["miscDone"]: 
				self.plugins[plugin].create_misc()
				self.confs["miscDone"].append(plugin)
	def savePlugins(self):
		with open("plugins.plugins", 'w', encoding="utf-8") as f:
			json.dump(self.activePlugins, f)
	def togglePlugin(self, plugin: str):
		m, t, w, i, misc = self.plugins[plugin].get_configuration()
		amI = self.activePlugins[plugin]
		if amI:
			self.activePlugins[plugin] = False
		else:
			self.activePlugins[plugin] = True
		#self.activePlugins[plugin] = not self.activePlugins[plugin]
		self.plugins[plugin].active = self.activePlugins[plugin]
		if self.activePlugins[plugin]:
			if m: self.confs["menu"].append(plugin)
			if t: self.confs["tab"].append(plugin)
			if w: self.confs["window"].append(plugin)
			if i: self.confs["inject"].append(plugin)
			if misc: self.confs["misc"].append(plugin)
		else:
			if m:
				self.confs["menu"].remove(plugin)
				#dpg.delete_item(f"pre{plugin}menu")
			if t:
				self.confs["tab"].remove(plugin)
				#dpg.delete_item(f"pre{plugin}tab")
			if w:
				self.confs["window"].remove(plugin)
				dpg.delete_item(f"pre{plugin}window")
			if i:
				self.confs["inject"].remove(plugin)
			if misc:
				self.confs["misc"].remove(plugin)
		self.domenu()
		self.dotab()
		self.dowindow()
		self.doinject()
		self.domisc()
		self.savePlugins()
		
	def create_Menu(self):
		dpg.add_menu(label="Plugins", tag="menuPluginsDEF")
		for plugin in list(self.plugins.keys()):
			try:
				udt=plugin
				dpg.add_menu_item(label=plugin, callback=togglePlugin2, check=self.plugins[plugin].active, parent="menuPluginsDEF", tag=f"ptvpmenu{plugin}", user_data=udt)
				print(plugin)
			except Exception as e:
				print(f'dafuq {e}')
def togglePlugin2(a, b, c, *args, **kwargs):
	print(f"a {a} b {b} c {c} ")

def main():
	global pct
	pct = PluginController()

	dpg.create_context()
	dpg.create_viewport(title='Custom Title', width=1200, height=800)

	#dpg.show_debug()
	try:
		with dpg.viewport_menu_bar():
			pct.create_Menu()
			with dpg.menu(label="Tools"):
				dpg.add_menu_item(label="Show About", 			callback=lambda:dpg.show_tool(dpg.mvTool_About))
				dpg.add_menu_item(label="Show Metrics", 		callback=lambda:dpg.show_tool(dpg.mvTool_Metrics))
				dpg.add_menu_item(label="Show Documentation", 	callback=lambda:dpg.show_tool(dpg.mvTool_Doc))
				dpg.add_menu_item(label="Show Debug", 			callback=lambda:dpg.show_tool(dpg.mvTool_Debug))
				dpg.add_menu_item(label="Show Style Editor", 	callback=lambda:dpg.show_tool(dpg.mvTool_Style))
				dpg.add_menu_item(label="Show Font Manager", 	callback=lambda:dpg.show_tool(dpg.mvTool_Font))
				dpg.add_menu_item(label="Show Item Registry", 	callback=lambda:dpg.show_tool(dpg.mvTool_ItemRegistry))
		with dpg.window(tag="main2"):
			with dpg.child_window():
				with dpg.menu_bar(tag="childWindowPluginMenuBar"):
					pct.domenu()
				dpg.add_text("This is text")
				dpg.add_input_text(tag="articleText", multiline=True, width=-1, height=-1)
				dpg.add_button(tag="This is a button", label="THIS IS A BUTTON")
				dpg.add_checkbox(label="Check Box")
				with dpg.child_window(autosize_x=True, autosize_y=True):
					with dpg.tab_bar(tag="pluginTagBar"):
						with dpg.tab(label="THIS IS A TAB"):
							with dpg.tree_node(label="THIS IS A TREE NODE"):
								randListOfStuff = ['THIS', 'IS', 'A', 'LIST']
								dpg.add_combo(randListOfStuff)
								dpg.add_listbox(randListOfStuff)
						pct.dotab()
		pct.dowindow()
		
	except Exception as e:
		print(f'dafuq {e}')
		#dpg.add_window(tag="main2")
	dpg.set_primary_window("main2", True)
	dpg.setup_dearpygui()
	pct.domisc()
	dpg.show_viewport()
	dpg.start_dearpygui()
	dpg.destroy_context()
 
if __name__ == "__main__":
	main()