# -*- coding: utf-8 -*-
'''
Created on May 17, 2010

@author: Joseph Clark
'''

from khopeshpy import db

from khopeshpy.animals import base
from khopeshpy.animals import top

from khopeshpy.animals.actions import move
from khopeshpy.animals.actions import attackCooldown
from khopeshpy.animals.actions import scavenge

class Event(scavenge.Event, attackCooldown.Event, move.Event, base.Event):
	
	
	preySpecies = []
		
	def preCommandHunt(self, preyId):
		'''
		What to do right before a hunt command is set
		'''
		
		#check that the prey.attackerId is free
		c = db.animalData.columns
		statement = db.select([db.animalData], c.animalId == preyId)
		result = self.conn.execute(statement)
		row = result.fetchone()
		result.close()
		
		if row == None or row['state'] == base.States.DEAD:
			#prey no longer exists, or is dead
			return False
		elif row['attackerId'] != None and row['attackerId'] != self.data['animalId']:
			#has has an attacker who isn't us
			return False
			
		#do the actual attack
		#from khopeshpy.animals import top
		#prey = top.event(animalId = preyId, conn = self.conn)
		#prey = base.Event(animalId = preyId, conn = self.conn)
		prey = top.eventAnimalFactory(self.conn, row = row)
		
		#first, attacker gets first strike so do that first
		self.stamina -= self.attackStaminaCost
		
		atkStr = self.attackStrength(self.health)
		prey.attacked(self.animalId, atkStr)
		
		dt = self.attackCooldown(self.stamina)
		self.addCommandAttackCooldown(dt, preyId)
		
		#two options
		if prey.health > 0.0:
			#print 'the prey lives'
			#any code to break off the attack would go here
			#do we need to be able to set this as un-interruptable?
			self.addCommandHunt(preyId, 0.0)
		else:
			#print 'the prey is dead'
			#set it to scavange the prey for a token amount of time
			self.addCommandScavenge(preyId, 1.0)
			
			
	def postCommandHunt(self, row, dt):
		'''
		What to do after a hunt command has compleated
		'''
		self.markCmdFinished(row['eventId'], True)
		
		#leaving our lock on the prey since hunt is always followed by attack cooldown,
		# which would then lock the prey
		#	may want to look into if we can streamline this
		
		self.updateStats(dt)
		
		self.commandNext()
		
	def addCommandHunt(self, preyId, dt):
		'''
		Add the hunt to the command queue for this animal
		'''
		
		#attacking is instant
		return self.addCmdQueue('hunt', 0.0, preyId)




		
	#we may want to consider moving this higer, especially as we improve it
	def simulateFight(self, predator, prey):
		#we need to figure out if the predator is expected to win and 
		# how much health+stamina the predator is expected to lose if the do so
		
		#would be nice to use the actuall attack/defend functions but we don't 
		# know if that's possible right now
		preyHealth = prey.health
		preyStamina = prey.stamina
		predatorHealth = predator.health
		predatorStamina = predator.stamina
		
		#attacks will be on a timer so we have to figure that in
		
		#prey has one delay before they can attack
		preyTimer = prey.attackCooldown(preyStamina)
		predatorTimer = 0.0
		
		#need to keep track of total time
		timer = 0.0
		
		#NOTE: we're forgetting to calculate in normal stamina drain
		
		#fight is over whenever samina or health is exhausted for the prey or the predator
		while predatorHealth > 0.0 and preyHealth > 0.0 \
			and preyStamina > 0.0 and predatorStamina > 0.0:
			#print 'preyattackCooldown: ' + repr(prey.attackCooldown(preyStamina))
			#print 'predattackCooldown: ' + repr(predator.attackCooldown(predatorStamina))
			#print 'preyHealth: ' + repr(preyHealth)
			
			if preyTimer < predatorTimer:
				#print 'prey gets to attack'
				
				predatorHealth -= prey.attackStrength(preyHealth)
				preyStamina -= prey.attackStaminaCost
				
				timer += preyTimer
				predatorTimer -= preyTimer
				preyTimer = prey.attackCooldown(preyStamina)
				
			else: #predatorTimer < preyTimer
				#print 'predator gets to attack'
				
				preyHealth -= predator.attackStrength(predatorHealth)
				predatorStamina -= predator.attackStaminaCost
				
				#and update the cooldown timers
				timer += predatorTimer
				preyTimer -= predatorTimer
				predatorTimer = predator.attackCooldown(predatorStamina)
				#print 'preyHealth: ' + repr(preyHealth)
				
		#print 'timer: ' + repr(timer)
		#and check our results
		if predatorHealth > 0.0 and predatorStamina > 0.0:
			#we survived!
			
			#looks like we convert health and stamina without loss, this will need
			# to be adjusted if we change that later
			
			staminaDiff = -(predator.stamina - predatorStamina)
			healthDiff = -(predator.health - predatorHealth)
			
			return (staminaDiff, healthDiff, timer)
		else:
			#use false to flag that it wasn't successful
			return False
		
	def selectHuntPrey(self, lvl, stateDiff):
		'''
		Select the best animal to attack
		We want to find the animal which will give the best cost/oppertunity
		We have to consider how much mass we expect to get if we kill the animal vs.
		How much mass we'll lose to damage, energy, etc?
		'''
		
		#print "stateDiff before: " + repr(stateDiff)
		
		maxBiomass = 0.0
		maxPrey = None
		
		#ugh, have to pop these up to this level
		maxGainedBiomass = None
		maxNetStamina = None
		maxNetHealth = None
		maxNetTime = None
		
		#get all live animals, in the passed level, who don't have an attacker
		# current model can't handle multiple attackers
		c = db.animalData.columns
		statement = db.select([db.animalData], (c.animalX == lvl.cellIdX) &\
				(c.animalY == lvl.cellIdY) & (c.animalZ == lvl.levelIdZ) &\
				(c.state != base.States.DEAD) & (c.attackerId == None) & (c.animalId != self.animalId))
		result = self.conn.execute(statement)
		rows = result.fetchall()
		result.close()
		
		#select the best one to hunt
		
		#create a dictionary of cost/advantage?
		for row in rows:
			#prey = base.Event(self.conn, animalId = row['animalId'])
			prey = top.eventAnimalFactory(self.conn, row = row)
			
			#only consider if it is a prey species
			if prey.species in self.preySpecies:
				#total biomass that will be available having killed the animal
				gainedBiomass = (prey.growth + prey.stored) * self.scavengeEfficiency
				
				#now the hard part
				#we want to simulate the fight and try to guess how much health we'll lose
				
				#the oppertunity cost should be absolute (ratio makes no sense)
				result = self.simulateFight(self, prey)
				
				
				if result != False: #if we didn't lose the fight
					lostStamina, lostHealth, lostTime = result
					
					netBiomass = gainedBiomass - (lostStamina + lostHealth)
					
					if netBiomass > maxBiomass:
						maxBiomass = netBiomass
						maxPrey = prey
						maxGainedBiomass = gainedBiomass
						maxNetStamina = lostStamina
						maxNetHealth = lostHealth
						maxNetTime = lostTime
					
					
		if maxPrey == None:
			#didn't find anything woth attacking
			return False
			
			
		#found something we want to attack, adjust the stateDiff
		stateDiff['stamina'] += maxNetStamina
		stateDiff['health'] += maxNetHealth
		stateDiff['time'] += maxNetTime
		
		if self.stamina + stateDiff['stamina'] <= 0.0:
			#ran out of stamina
			return False
		elif self.health + stateDiff['health'] <= 0.0:
			#ran out of health
			return False
			
			
		#now to calculate how much we gain by scavanging
	
		#only test for unprocessedMax because the hunter will be able to sit down and eat until their full

		#can't eat more than there is room for
		room = self.unprocessedMax - self.unprocessed #room in it's stomach
		amount = min(room, maxGainedBiomass)
		eatingTime = amount / self.scavengeRate
			
		#simulate eating until full
		stateDiff['unprocessed'] += amount
		stateDiff['time'] += eatingTime
		
		#print "stateDiff after: " + repr(stateDiff)
		
		totalTime = maxNetTime + eatingTime
		stateDiff['stamina'] -= self.staminaDrain * totalTime
		stateDiff['stamina'] -= self.scavengeStaminaCost * eatingTime
		return maxPrey.data['animalId'], totalTime
		
	def tryCommandHunt(self, lvl, stateDiff):
		'''
		Try the hunt command on the passed level
		'''
		moveCmd = self.tryCommandMove(lvl, stateDiff)
		
		if moveCmd == False:
			#print 'couln\'t move to the specified level'
			return False
			
		#hunt itself doesn't have any time or drain....
		
		result = self.selectHuntPrey(lvl, stateDiff)
		
		#print 'reslult: ' + repr(result)
		
		if result == False:
			return False
		else:
			#stateDiff changes are handled in selectHuntPrey
			preyId, dt = result
			
			moveCmd.append(('hunt', (preyId, dt)))
			
			return moveCmd
			
	def getActionMap(self):
		'''
		List of all actions and their command set
		'''
		commandMap = {
			'try': self.tryCommandHunt, 
			'add': self.addCommandHunt, 
			'pre': self.preCommandHunt, 
			'post': self.postCommandHunt}
		
		actionMap = super(Event, self).getActionMap()
		actionMap['hunt'] = commandMap
		return actionMap	