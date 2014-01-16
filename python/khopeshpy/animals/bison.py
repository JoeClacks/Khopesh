# -*- coding: utf-8 -*-
'''
Created on May 17, 2010

@author: Joseph Clark
'''
import time

from khopeshpy import db
from khopeshpy.animals import base
from khopeshpy.animals import top

from khopeshpy.animals.actions import forage
from khopeshpy.animals.actions import sleep
from khopeshpy.animals.actions import move
from khopeshpy.animals.actions import idle
from khopeshpy.animals.actions import dead
from khopeshpy.animals.actions import defend
    
class Bison(object):
    '''
    Bison class
    '''    
    #how fast the animal can transition from child->adult->repro->adult
    stateChangeTime = 100.0 #ticks
    
    #the database tag for this species
    species = top.Species.BISON
    
    #digestion efficiency (%), feeding rate in (processed-kg/tick)
    #should be ordered by preference
    feedBiome = {'grassland': (0.2, 20.0), 'savanna': (0.1, 10.0)}
    #eats 100kg grassland/tick, 100kg savanna/tick,
    # but get twice as many nutrients from the grassland 
    
#class Setup(Bison, base.Setup):
    #'''
    #Bison setup class
    #'''
    #pass

class Event(Bison, defend.Event, dead.Event, idle.Event, sleep.Event, forage.Event, move.Event, base.Event):
    '''
    Bison event class
    '''
    #override base behavior
    def attacked(self, attackerId, atkStrength):
        '''
        Called by an attacker when it attacks us
        '''
        #being attacked is an interrupt
        
        #forage: cancel everything
        #attack cooldown.... add it to the list of attackers?
        #    defending container needs to handle multiple attackers?
        #        Not yet since we put in the lock, but we may want to account for it anyway
        #move: cancled
        #idle: cancled
        #sleep: cancled
        #dead: wtf
        
        #stack on the attacked command to then end, then delete all interruptable
        # commands
        
        #set the attacker
        self.data['attackerId'] = attackerId
        
        #update our health, can adjust later here for defense
        self.data['health'] -= atkStrength
        
        if self.data['health'] < 0.01:
            self.data['state'] = base.States.DEAD
            self.deathCleanup()
        else:
            #add the defend command to the end of the queue
            self.addCmdQueue('defend', 0.0, attackerId)
            
            #TODO: generate this automatically
            interruptibleCommands = ['forage', 'move', 'idle', 'sleep']
            
            
            #TODO: make sure this is producing the sql we want
            #remove all interruptible comands
            c = db.animalCmdQueue.columns
            up = db.animalCmdQueue.update()\
                .where((c.animalId == self.animalId) & (c.done == False) & c.command.in_(interruptibleCommands))\
                .values(active = False, done = True, successful = False, timeEnded = time.time()) 
            result = self.conn.execute(up)
            
            #pull up the current command, current is different because it has to be
            #    removed from the eventQueue:
            eventId = self.data['eventId']
            
            c = db.animalCmdQueue.columns
            statement = db.select([db.animalCmdQueue], c.eventId == eventId)
            result = self.conn.execute(statement)
            row = result.fetchone()
            result.close()
            
            if row == None:
                #...? something went wrong
                raise Exception('unknown state')
            
            if row['command'] in interruptibleCommands:
                c = db.animalEventQueue.columns
                up = db.animalEventQueue.delete().where(c.eventId == eventId)
                result = self.conn.execute(up)            
                
                #NOTE: need to adjust stats for unfinished command,
                # also we sould finish up anything we can on the interrupted command
                #self.updateStats(dt)
            
                #execute the next command only if we removed the current command
                self.commandNext()
            
        self.pushData()
            

top.eventAnimalRegister(Event.species, Event)
    
    