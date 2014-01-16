# -*- coding: utf-8 -*-
'''
Created on May 17, 2010

@author: Joseph Clark
'''

from khopeshpy.avatars import base


class Event(base.Event):
	def preCommandDead(self, row):
		pass
		
	
	def postCommandDead(self, row, dt):
		'''
		Growth, stored bar mass available to predators to consume
		Slowly rots or is eaten, when all bars are empty remove all records
		'''
		
		self.markCmdFinished(row['eventId'], True)
		
		#NOTE: since max values are based on the current growth always 
		#	decrease growth last
		self.stored -= self.storedMax*self.decayRate*dt
		if self.stored < 0.0:
			self.stored = 0.0
		self.growth -= self.growthMax*self.decayRate*dt
		if self.growth < 0.0:
			self.growth = 0.0
		
		#log.debug("postCommandDead: %f ticks, %f growth mass left, %f stored mass\
		# left" % (dt, self.data['growth'],self.data['stored']))
		
		if self.growthPct < 0.01 and self.storedPct < 0.01:
			self.decomposedCleanup()
		else:
			self.commandNext()
		
	def addCommandDead(self, dt):
		'''
		add the dead command
		'''
		
		return self.addCmdQueue('dead', dt)
		
	def getActionMap(self):
		'''
		List of all actions and their command set
		'''
		commandMap = {
			'add': self.addCommandDead, 
			'pre': self.preCommandDead, 
			'post': self.postCommandDead}
		
		actionMap = super(Event, self).getActionMap()
		actionMap['dead'] = commandMap
		return actionMap	