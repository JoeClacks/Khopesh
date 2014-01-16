# -*- coding: utf-8 -*-
'''
Created on May 17, 2010

@author: Joseph Clark
'''

from khopeshpy import db
from khopeshpy import util

from khopeshpy.animals import base
from khopeshpy.animals import top

from khopeshpy.animals.actions import move

class Event(move.Event, base.Event):
    #TODO: Wrap to throw errors
    preySpecies = []
    
    #TODO: Wrap to throw errors
    scavengeEfficiency = 0.0
    
    def preCommandScavenge(self, preyId):
        '''
        What to do right before a scavenge command is set
        '''
        
        #check that the prey.attackerId is free
        
        c = db.animalData.columns
        statement = db.select([db.animalData], c.animalId == preyId)
        result = self.conn.execute(statement)
        row = result.fetchone()
        result.close()
        
        
        #TODO: clean this up
        if row == None:
            #prey no longer exists
            #print "prey id: " + preyId + "no longer exists"
            #raise Exception("prey no longer exsists")
            return False
        elif row['attackerId'] == self.animalId:
            #we're already the attacker
            #print "success: we're the attacker"
            return True
        elif row['attackerId'] == None:
            #print "setting self as the atacker"
            #lock the prey as ours
            c = db.animalData.columns
            up = db.animalData.update().where((c.animalId == preyId)).\
                values(attackerId = self.data['animalId'])
            self.conn.execute(up)
        else:
            #print "prey's attacker is: " + repr(row['attackerId'])
            #the prey already has an attacker
            return False


        
        
    def postCommandScavenge(self, row, dt):
        '''
        What to do after a scavenge command has compleated
        '''
        self.markCmdFinished(row['eventId'], True)
        
        preyId = row['data']
        #prey = base.Event(animalId = preyId, conn = self.conn)
        prey = top.eventAnimalFactory(conn = self.conn, animalId = preyId)
        
        #amount to be eaten is the least of the amount it could have eaten, the 
        #    amount there was, and the amount of room left in it's stomach
        room = self.unprocessedMax - self.unprocessed #room in it's stomach
        amountAvailable =  (prey.growth + prey.stored) * self.scavengeEfficiency
        consumable = self.scavengeRate * dt
        
        #amount = room if room < amountAvailable else amountAvailable
        #amount = amount if amount < consumable else consumable
        amount = min(room, amountAvailable, consumable)
            
        self.stamina -= self.scavengeStaminaCost * dt
        self.stamina -= self.staminaDrain * dt
        
        self.unprocessed += amount
        prey.biomassEaten(amount / self.scavengeEfficiency)
        prey.attackerId = None
        prey.pushData()
        
        
        #remove our lock on the prey
        #c = db.animalData.columns
        #up = db.animalData.update().where((c.animalId == preyId)).\
            #values(attackerId = None)
        #self.conn.execute(up)
        
        #and to remove the prey from our list
        
        
        self.updateStats(dt)
        
        self.scavenge += dt
        
        self.commandNext()

    
    #reigon 
    def addCommandScavenge(self, preyId, dt):
        '''
        Add the scavenge to the command queue for this animal
        '''
        #print 'scavenge command added'
        
        return self.addCmdQueue('scavenge', dt, preyId)
        
    
    def selectScavengePrey(self, lvl):
        '''
        Select the best animal to feed on
        we want to find the animal from which we'll find the most food in the time
        alotted    this can either be limited by the amount of biomass, or by the 
        animal's speed of eating
        '''
        maxBiomass = 0.0
        maxPrey = None
        
        #get all dead animals in the passed level
        c = db.animalData.columns
        statement = db.select([db.animalData], (c.animalX == lvl.cellIdX)\
            & (c.animalY == lvl.cellIdY) & (c.animalZ == lvl.levelIdZ)\
            & (c.state == base.States.DEAD) & ((c.attackerId == None) | (c.attackerId == self.animalId)))
        result = self.conn.execute(statement)
        rows = result.fetchall()
        result.close()
        
        #print "prey: " + repr(self.preySpecies)
        
        #select the best one to scavange
        # note: we could check here if we can break early
        
        for row in rows:
            #print repr(rows)
            #prey = base.Event(row = row, conn = self.conn)
            prey = top.eventAnimalFactory(self.conn, row = row)
            
            #print "species: " + repr(prey.species)
            
            if prey.species in self.preySpecies:
                #print "prey is a prey species"
                biomass = (prey.growth + prey.stored) * self.scavengeEfficiency
                
                if biomass > maxBiomass:
                    maxBiomass = biomass
                    maxPrey = prey
            #else:
                #print "prey is not a prey species"
                    
                    
                    
        #can't eat more than there is room for
        room = self.unprocessedMax - self.unprocessed #room in it's stomach
        amount = min(room, maxBiomass)
        time = amount / self.scavengeRate
        
        if maxBiomass > room:
            maxBiomass = room
        
        if maxBiomass < 0.01:
            return False
        else:
            return (maxPrey, maxBiomass, time)
    
    def tryCommandScavenge(self, lvl, stateDiff):
        '''
        Try the scavenge command on the passed level
        '''
        #print 'wtf'
        moveCmd = self.tryCommandMove(lvl, stateDiff)
        
        if moveCmd == False:
            #print 'couln\'t move to the specified level'
            return False        
            
        tmp = self.selectScavengePrey(lvl)
        
        if tmp == False:
            #print 'could not find food'
            return False
        else:
            #print 'found food!'
            prey, biomass, time = tmp
            
            stateDiff['stamina'] -= self.scavengeStaminaCost * time
            stateDiff['stamina'] -= self.staminaDrain * time
            stateDiff['time'] += time
            
            if self.stamina + stateDiff['stamina'] <= 0.0:
                #print 'ran out of stamina'
                return False
        
            stateDiff['unprocessed'] += biomass
        
            moveCmd.append(('scavenge', (prey.animalId, time)))
            return moveCmd
        
    @property
    def scavengeStaminaCost(self):
        '''
        How much stamina savnenging for 1 tick costs
        '''
        return (self.growthStat/self.scavengeStat)/100.0
    
    @property
    def scavengeRate(self):
        '''
        Adjustment for how fast the animal can eat
        '''
        return (self.scavengeStat)/10.0
        
    scavenge = property(util.getValue('scavenge'), util.setValue('scavenge'))
    scavengeStat = property(util.getStat('scavenge'))
    
    def getActionMap(self):
        '''
        List of all actions and their command set
        '''
        commandMap = {
            'try': self.tryCommandScavenge, 
            'add': self.addCommandScavenge, 
            'pre': self.preCommandScavenge, 
            'post': self.postCommandScavenge}
        
        actionMap = super(Event, self).getActionMap()
        actionMap['scavenge'] = commandMap
        return actionMap    