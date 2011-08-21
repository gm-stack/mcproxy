import argparse

class LazySettings():
	def __init__(self, settings, name):
		self.settings = settings
		self.name = name
	def __repr__(self):
		return getattr(self.settings, self.name)

class Settings(argparse.Namespace):
	def __getattr__(self, name):
		return LazySetting(self, name)
	
	#default settings
	metachar = '#'
	loglevel = 'INFO'
	console = True
	gui = False

settings = Settings()