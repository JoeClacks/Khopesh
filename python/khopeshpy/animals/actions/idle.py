# -*- coding: utf-8 -*-
'''
Created on May 17, 2010

@author: Joseph Clark
'''

from khopeshpy.animals import base

from khopeshpy.animals.actions import move

class Event(move.Event, base.Event):
	def preCommandIdle(self, row):
		pass
	
	def postCommandIdle(self, row, dt):
		'''
		just let the animal do nothing for a bit, still drains stamina
		'''
		
		self.markCmdFinished(row['eventId'], True)
		
		self.data['stamina'] -= self.staminaDrain * dt
		
		#log.debug("postCommandIdle: %f ticks" % (dt))
		
		self.updateStats(dt)
		
		self.commandNext()
	
	def addCommandIdle(self, dt):
		'''
		add the idle command
		'''
		
		return self.addCmdQueue('idle', dt)
		
	def tryCommandIdle(self, lvl, stateDiff):
		'''
		try the idle command
		'''
		
		moveCmd = self.tryCommandMove(lvl, stateDiff)
		
		if moveCmd == False:
			#couln't move to the specified level
			return False

		dt = 1.0
		
		stateDiff['stamina'] -= self.staminaDrain * dt
		stateDiff['time'] += dt
		
		if self.stamina + stateDiff['stamina'] <= 0.0:
			#ran out of stamina
			return False
		
		moveCmd.append(('idle', (dt,)))
		return moveCmd
		
	def getActionMap(self):
		'''
		List of all actions and their command set
		'''
		commandMap = {
			'try': self.tryCommandIdle, 
			'add': self.addCommandIdle, 
			'pre': self.preCommandIdle, 
			'post': self.postCommandIdle}
		
		actionMap = super(Event, self).getActionMap()
		actionMap['idle'] = commandMap
		return actionMap	