# -*- coding: utf-8 -*-
'''
Created on May 17, 2010

@author: Joseph Clark
'''

from khopeshpy.animals import base

from khopeshpy.animals.actions import attackCooldown

class Event(attackCooldown.Event, base.Event):
	def preCommandDefend(self, row):
		#don't actually do anything for defend right now
		pass
	
	def postCommandDefend(self, row, dt):
		#don't actually do anything for defend right now
		self.markCmdFinished(row['eventId'], True)
		
		self.updateStats(dt)
		
		self.commandNext()
		
	def addCommandDefend(self, dt, attackerId):
		self.addCmdQueue('defend', 1.0, attackerId)
		
	def getActionMap(self):
		'''
		List of all actions and their command set
		'''
		commandMap = {
			'add': self.addCommandDefend, 
			'pre': self.preCommandDefend, 
			'post': self.postCommandDefend}
		
		actionMap = super(Event, self).getActionMap()
		actionMap['defend'] = commandMap
		return actionMap	