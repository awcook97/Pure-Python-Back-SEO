class Plugin(object):

	plugin_name = "Plugin"
	author = "author"
	info = "What does the plugin do?"
	menu = False
	tab = False
	window = False
	active = False
	injectable = False
	misc = False

	def __init__(self):
		"""Initialize your stuff. If you need to declare variables, declare them here. Don't call UI stuff yet. That's for the items you labeled as True above. All plugins start out deactivated at first."""
		self.active = False
		return

	def get_configuration(self):
		"""
		get_configuration simple struct like format

		1. menu
		2. tab
		3. window
		4. injectable
		5. misc

		:return: list
		:rtype: list
		"""
		return [
			self.menu,
			self.tab,
			self.window,
			self.injectable,
			self.misc,
		]


	def begin(self):
		self.active = False


	def __str__(self):
		return self.plugin_name

	def create_misc(self):
		"""If you need to create miscellaneous items, do it here. This is called after everything else has been created"""
		return self._create_misc()

	def create_menu(self):
		"""Create the menu that your plugin will use."""
		return self._create_menu()

	def create_tab(self):
		"""Create a tab in the main tab group"""
		return self._create_tab()

	def create_window(self, tag):
		"""Create a window"""
		return self._create_window(tag)

	def inject(self):
		"""If you need to inject something into something else, do it here. This is called before any other code is active, including the main module."""
		return self._inject()
	
	def _create_misc(self):
		pass
	
	def _create_menu(self):
		pass
	
	def _create_tab(self):
		pass
	
	def _create_window(self):
		pass
	
	def _inject(self):
		pass

myP = Plugin
def getPlugin():
	return myP