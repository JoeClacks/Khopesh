# -*- coding: utf-8 -*-
'''
Created on May 17, 2010

@author: Joseph Clark
'''

from khopeshpy import level
from khopeshpy import util

from khopeshpy.animals import base

from khopeshpy.animals.actions import move

class Event(move.Event, base.Event):
	#TODO: get this to throw an error if it's accessed
	# function wrapper?
	feedBiome = {}
	
	def preCommandForage(self, data):
		pass

	def postCommandForage(self, row, dt):
		'''
		What to do after a forage command has compleated
		decreases cell's biomass at (%efficiency, %rate) per biome 
		adds to unprocessed mass
		pass biome that is being feed on through the data paramater
		'''
		self.markCmdFinished(row['eventId'], True)
		
		lvl = level.Event(position = self.position, conn = self.conn)
		biome = row['data']
		
		#amount to be eaten is the least of the amount it could have eaten, the 
		#	amount there was, and the amount of room left in it's stomach
		room = self.unprocessedMax - self.unprocessed #room in it's stomach
		amountInLevel = lvl.biomass(biome)*self.feedBiome[biome][0]
		consumable = self.feedBiome[biome][1]*self.forageRate*dt
		
		amount = room if room < amountInLevel else amountInLevel
		amount = amount if amount < consumable else consumable
			
		self.stamina -= self.forageStaminaCost * dt
		self.stamina -= self.staminaDrain * dt
		
		self.unprocessed += amount
		lvl.biomassEaten(biome, amount/self.feedBiome[biome][0])
		
		#log.debug("postCommandForage: %f ticks, %f processed kg eaten, %f stamina \
		#used" % (dt, f, dt * self.eatStamina))
		
		
		self.forage += dt

		self.updateStats(dt)
		
		self.commandNext()

	
	def selectFeedBiome(self, lvl, dt):
		'''
		Select the best biome to feed on for this animal
		we want to find the biome from which we'll find the most food in the time alotted
		this can either be limited by the amount of biomass, or by the animal's 
		speed of eating
		'''
		maxBiomass = 0.0
		maxBiome = ""
		
		room = self.unprocessedMax - self.unprocessed #room in it's stomach
		
		for food in self.feedBiome:
			#adjust for efficiency
			amountInLevel = lvl.biomass(food)*self.feedBiome[food][0] 
			
			#how much it can eat in the time passed
			consumable = self.feedBiome[food][1]*self.forageRate*dt
				
			amount = room if room < amountInLevel else amountInLevel
			amount = amount if amount < consumable else consumable
			
			if amount > maxBiomass:
				maxBiomass = amount
				maxBiome = food
				
		if maxBiomass < 0.01:
			return False
		else:
			return (maxBiome, maxBiomass)
		
		
	def addCommandForage(self, biome, dt):
		'''
		Add the forage to the command queue for this animal
		'''
		return self.addCmdQueue('forage', dt, biome)
		
	def tryCommandForage(self, lvl, stateDiff):
		'''
		Try the forage command on the passed level
		'''
		moveCmd = self.tryCommandMove(lvl, stateDiff)
		
		if moveCmd == False:
			#print 'couln\'t move to the specified level'
			return False
		
		dt = 1.0
		
		stateDiff['stamina'] -= self.forageStaminaCost * dt
		stateDiff['stamina'] -= self.staminaDrain * dt
		stateDiff['time'] += dt
		
		tmp = self.selectFeedBiome(lvl, dt)
		if tmp == False:
			#print 'could not find food'
			return False
		else:
			biome, biomass = tmp
		
		stateDiff['unprocessed'] += biomass
		
		if self.stamina + stateDiff['stamina'] <= 0.0:
			#print 'ran out of stamina'
			return False
		
		moveCmd.append(('forage', (biome, dt)))
		return moveCmd
	
	@property
	def forageStaminaCost(self):
		'''
		How much stamina foraging for 1 tick costs
		'''
		return (self.growthStat/self.forageStat)/100.0
	
	@property
	def forageRate(self):
		'''
		Adjustment for how fast the animal can eat
		'''
		return (self.forageStat)/10.0
	
	forage = property(util.getValue('forage'), util.setValue('forage'))
	forageStat = property(util.getStat('forage'))
	
	
	def getActionMap(self):
		'''
		List of all actions and their command set
		'''
		commandMap = {
			'try': self.tryCommandForage, 
			'add': self.addCommandForage, 
			'pre': self.preCommandForage, 
			'post': self.postCommandForage}
		
		actionMap = super(Event, self).getActionMap()
		actionMap['forage'] = commandMap
		return actionMap	