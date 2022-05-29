from PyQt5 import QtWidgets
from functools import *

import os

# single file only
class OpenFileDialog:
	def __init__(self):
		self.last_open_dir = ''

	def open_file(self, filters):
		dialog = QtWidgets.QFileDialog()
		dialog.setModal(True)
		filepath, _ = dialog.getOpenFileName(
			None,
			'Open file dialog',
			self.last_open_dir,
			filters
		)
		self.last_open_dir, _ = os.path.split(filepath)
		return filepath

class SaveFileDialog:
	def __init__(self):
		self.last_save_dir = ''

	def save_file(self, filters):
		dialog = QtWidgets.QFileDialog()
		dialog.setModal(True)
		filepath, _ = dialog.getSaveFileName(
			None,
			'Save file dialog',
			self.last_save_dir,
			filters
		)
		if filepath == '':
			return filepath

		self.last_save_dir, _ = os.path.split(filepath)
		return filepath



class FileDialog:
	def __init__(self):
		self.open_ops = OpenFileDialog()
		self.save_ops = SaveFileDialog()

	@staticmethod
	def get_filter(filters:list):
		return reduce(lambda x, y: str(x) + ';;' + str(y), filters)

	def open_file(self, filters:list):
		_filter = self.get_filter(filters)
		return self.open_ops.open_file(_filter)

	def save_file(self, filters:list):
		_filter = self.get_filter(filters)
		return self.save_ops.save_file(_filter)
