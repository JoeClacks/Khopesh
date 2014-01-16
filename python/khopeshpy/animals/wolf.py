# -*- coding: utf-8 -*-
'''
Created on May 17, 2010

@author: Joseph Clark
'''
from khopeshpy.animals import base
from khopeshpy.animals import top

from khopeshpy.animals.actions import scavenge
from khopeshpy.animals.actions import hunt
from khopeshpy.animals.actions import sleep
from khopeshpy.animals.actions import move
from khopeshpy.animals.actions import idle
from khopeshpy.animals.actions import dead

class Wolf(object):
	'''
	Wolf class
	'''	
	#how fast the animal can transition from child->adult->repro->adult
	stateChangeTime = 100.0 #ticks
	
	#the database tag for this species
	species = top.Species.WOLF
	
	preySpecies = [top.Species.BISON]
	
	scavengeEfficiency = 0.50
	
#class Setup(Wolf, base.Setup):
	#'''
	#Wolf setup class
	#'''
	#pass

class Event(Wolf, dead.Event, idle.Event, sleep.Event, hunt.Event, scavenge.Event,
	move.Event, base.Event):
	'''
	Wolf event class
	'''
			
top.eventAnimalRegister(Event.species, Event)
	
