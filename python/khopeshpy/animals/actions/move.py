# -*- coding: utf-8 -*-
'''
Created on May 17, 2010

@author: Joseph Clark
'''
import pickle

from khopeshpy import level
from khopeshpy import log
from khopeshpy import util

from khopeshpy.animals import base



class Event(base.Event):	
	def preCommandMove(self, row):
		#TODO: put in a check for if the cell is full
		pass
	
	def move(self, position):
		'''
		checks that that move is legal, and move the animal
		'''
		
		distance = (self.data['animalX'] - position[0])**2 \
				+ (self.data['animalY'] - position[1])**2 \
				+ (self.data['animalZ'] - position[2])**2
				
		if distance > 3:
			#cannot move more than one square at a time
			log.debug("move: failed due to out of distance")
			return False
			
		lvl = level.Event(position = position, conn = self.conn)
		if not lvl.walkable:
			#level must be walkable
			log.debug("move: failed due to unwalkable target")
			return False
			
		self.data['animalX'] = position[0]
		self.data['animalY'] = position[1]
		self.data['animalZ'] = position[2]
		
		#log.debug("move: success")
		return True
			
			
	def postCommandMove(self, row, dt):
		'''
		moves an animal
		'''
		
		self.markCmdFinished(row['eventId'], True)
		
		#no need to add anything unless we have a movement check
		self.move(pickle.loads(row['data']))
		
		#a failed move still drains stamina
		self.stamina -= self.runningStaminaCost
		self.stamina -= self.staminaDrain * dt
		
		#log.debug("postCommandMove: %f ticks, %f stamina used" %\
		#(dt, self.moveFoodStamina))
		
		self.updateStats(dt)
		
		self.running += 1.0
		
		self.commandNext()
		
	def addCommandMove(self, lvl, dt):
		'''
		add the move command
		'''
		
		#NOTE: we should add a position attribute to the level class
		newPosition = (lvl.data['cellIdX'], \
			lvl.data['cellIdY'], lvl.data['levelIdZ'])
		
		return self.addCmdQueue('move', dt, pickle.dumps(newPosition))
		
	
	def tryCommandMove(self, lvl, stateDiff):
		'''
		try the move command
		'''
		
		distance = (self.data['animalX'] - lvl.data['cellIdX'])**2 +\
			(self.data['animalY'] - lvl.data['cellIdY'])**2 +\
			(self.data['animalZ'] - lvl.data['levelIdZ'])**2
				
		if distance == 0:
			#the passed level is the one we're currently in
			#do nothing
			return []
		if distance > 3 or lvl.walkable == False:
			#right now we only handle one move at a time so fail
			return False
					
		dt = self.runningTimeCost
		
		stateDiff['stamina'] -= self.runningStaminaCost
		stateDiff['stamina'] -= self.staminaDrain * dt
		stateDiff['time'] += dt
		
		if self.stamina + stateDiff['stamina'] <= 0.0:
			#ran out of stamina
			return False
			
		return [('move', (lvl, dt))]
		
	@property
	def runningTimeCost(self):
		'''
		attribute
		'''
		return (self.growthStat/(self.runningStat * self.healthPct))/2.0
		
	@property
	def runningStaminaCost(self):
		'''
		attribute
		'''
		return (self.growthStat/self.runningStat)/10.0	
		
	running = property(util.getValue('running'), util.setValue('running'))
	runningStat = property(util.getStat('running'))
	
	def getActionMap(self):
		'''
		List of all actions and their command set
		'''
		commandMap = {
			'try': self.tryCommandMove, 
			'add': self.addCommandMove, 
			'pre': self.preCommandMove, 
			'post': self.postCommandMove}
		
		actionMap = super(Event, self).getActionMap()
		actionMap['move'] = commandMap
		return actionMap