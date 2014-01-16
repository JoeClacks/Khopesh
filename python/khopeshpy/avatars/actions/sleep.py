# -*- coding: utf-8 -*-
'''
Created on May 17, 2010

@author: Joseph Clark
'''

from khopeshpy.avatars import base

from khopeshpy.avatars.actions import move

class Event(move.Event, base.Event):
    def preCommandSleep(self, row):
        pass
    
    def postCommandSleep(self, row, dt):
        '''
        converts unprocessed mass into processed mass -> stamina bar
        '''
        
        self.markCmdFinished(row['eventId'], True)
        
        #food converted into stamina is limited by either the conversion rate or 
        #    the amount of food in the animal's stomach
        convSP = self.sleepConvertRate * dt
        convSP = convSP if convSP < self.unprocessed else self.unprocessed
        
        self.unprocessed -= convSP
        
        if convSP > self.staminaMax - self.stamina:
            convHP = convSP - (self.staminaMax - self.stamina)
            convSP = self.staminaMax - self.stamina
        else:
            convHP = 0.0
            
        self.health += convHP
        self.stamina += convSP
        self.stamina -= self.sleepStaminaDrain * dt
        
        #log.debug("postCommandSleep: %f ticks, %f kg converted from unprocessed\
        #to stamina" % (dt, f))
        
        self.updateStats(dt)
        
        self.commandNext()
        
    def addCommandSleep(self, dt):
        '''
        add the sleep command
        '''
        
        return self.addCmdQueue('sleep', dt)
    
    def tryCommandSleep(self, lvl, stateDiff):
        '''
        try the sleep command
        '''
        
        moveCmd = self.tryCommandMove(lvl, stateDiff)
        
        if moveCmd == False:
            #couln't move to the specified level
            return False

        dt = 1.0
        
        stateDiff['time'] += dt
        
        convSP = self.sleepConvertRate * dt
        convSP = convSP if convSP < self.unprocessed else self.unprocessed
        
        stateDiff['unprocessed'] -= convSP
        
        #stamina overflows into health when sleeping
        #may want to change this into some sort of conversion
        if convSP > self.staminaMax - self.stamina:
            convHP = convSP - (self.staminaMax - self.stamina)
            convSP = self.staminaMax - self.stamina
        else:
            convHP = 0.0
            
        stateDiff['health'] += convHP
        stateDiff['stamina'] += convSP
        stateDiff['stamina'] -= self.sleepStaminaDrain * dt
        
        moveCmd.append(('sleep', (dt,)))
        return moveCmd
        
    @property
    def sleepConvertRate(self):
        '''
        attribute
        '''
        return self.growthStat/10.0
        
    @property
    def sleepStaminaDrain(self):
        '''
        attribute
        '''
        return self.staminaDrain/10.0
    
    def getActionMap(self):
        '''
        List of all actions and their command set
        '''
        commandMap = {
            'try': self.tryCommandSleep, 
            'add': self.addCommandSleep, 
            'pre': self.preCommandSleep, 
            'post': self.postCommandSleep}
        
        actionMap = super(Event, self).getActionMap()
        actionMap['sleep'] = commandMap
        return actionMap    
        
