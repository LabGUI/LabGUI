# -*- coding: utf-8 -*-
"""
@author: zackorenberg

Fixed value, useful for PID script

Use address "FIXED"
"""

import LabDrivers.Tool as Tool

param = {'Value': '#'}

INTERFACE = Tool.INTF_NONE


class Instrument(Tool.MeasInstr):
	def __init__(self, resource_name=None, debug=False, **kwargs):
		super(Instrument, self).__init__(resource_name, name='FIXED_VALUE',
		                                 debug=debug, interface=INTERFACE,
		                                 **kwargs)
		self.value = 0
		self.value_off = 0
		self.status = False
# ------------------------------------------------------------------------------

	def initialize(self):
		"""reset the time to the current time"""
		self.status = False

	def toggle(self):
		self.status = not self.status

	def on(self):
		self.status = True

	def off(self):
		self.status = False

	def set_value(self, value):
		self.value = value

	def get_value(self):
		return self.value


	def measure(self, channel='Value'):
		# we dont care about the channel, always return iterator
		if self.status:
			return self.value
		else:
			return self.value_off


if __name__ == "__main__":
	index = Instrument()
	print(index.measure())
	(index.on())
	print(index.measure())
	(index.increment())
	print(index.measure())
