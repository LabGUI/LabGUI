# -*- coding: utf-8 -*-
"""
@author: zackorenberg

Keep an index of what step a script runs, to more easily process large data files with multiple runs
"""

import LabDrivers.Tool as Tool

param = {'Step': '#'}

INTERFACE = Tool.INTF_NONE


class Instrument(Tool.MeasInstr):
	def __init__(self, resource_name=None, debug=False, idx_start=1, idx_off=0, **kwargs):
		super(Instrument, self).__init__(resource_name, name='ITERATOR',
		                                 debug=debug, interface=INTERFACE,
		                                 **kwargs)
		self.idx = self.idx_start = idx_start
		self.idx_off = idx_off
		self.status = False
# ------------------------------------------------------------------------------

	def initialize(self):
		"""reset the time to the current time"""
		self.idx = self.idx_start
		self.status = False

	def toggle(self):
		self.status = not self.status

	def on(self):
		self.status = True

	def off(self):
		self.status = False

	def increment(self):
		self.idx += 1

	def set_index(self, idx):
		self.idx = idx


	def measure(self, channel='Step'):
		# we dont care about the channel, always return iterator
		if self.status:
			return self.idx
		else:
			return self.idx_off


if __name__ == "__main__":
	index = Instrument()
	print(index.measure())
	(index.on())
	print(index.measure())
	(index.increment())
	print(index.measure())
