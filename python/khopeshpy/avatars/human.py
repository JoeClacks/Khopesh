# -*- coding: utf-8 -*-
'''
Created on April 7, 2011

@author: Joseph Clark
'''

from khopeshpy.avatars import base
from khopeshpy.avatars import top

from khopeshpy.avatars.actions import dead
from khopeshpy.avatars.actions import idle
from khopeshpy.avatars.actions import move
from khopeshpy.avatars.actions import sleep


class Human(object):
	'''
	Human class
	'''	
	#how fast the animal can transition from child->adult->repro->adult
	stateChangeTime = 100.0 #ticks
	
	#the database tag for this species
	species = top.Species.HUMAN
	
	#preySpecies = [top.Species.BISON]
	#scavengeEfficiency = 0.50

class Event(Human, dead.Event, idle.Event, sleep.Event, move.Event, base.Event):
	'''
	Human event class
	'''
	
class Control(Human, base.Control):
	'''
	Human event class
	'''
			
top.eventAvatarRegister(Event.species, Event)
top.controlAvatarRegister(Control.species, Control)