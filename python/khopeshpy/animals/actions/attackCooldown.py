# -*- coding: utf-8 -*-
'''
Created on May 17, 2010

@author: Joseph Clark
'''

from khopeshpy import db

from khopeshpy.animals import base

class Event(base.Event):
    #NOTE: idealy attack cooldown wouldn't continue to lock, but it seems
    #    nessary for our current design
    def preCommandAttackCooldown(self, preyId):
        #check the lock
        c = db.animalData.columns
        statement = db.select([db.animalData], c.animalId == preyId)
        result = self.conn.execute(statement)
        row = result.fetchone()
        result.close()
        
        if row == None:
            #prey no longer exists
            return False
        elif row['attackerId'] == self.animalId:
            #we're already the attacker
            return True
        elif row['attackerId'] == None:
            #lock the prey as ours
            c = db.animalData.columns
            up = db.animalData.update().where((c.animalId == preyId)).\
                values(attackerId = self.data['animalId'])
            self.conn.execute(up)
            
            return True
        else:
            #the prey already has an attacker
            return False
    
    def postCommandAttackCooldown(self, row, dt):
        self.markCmdFinished(row['eventId'], True)
        
        preyId = row['data']
        
        #remove our lock on the prey, nessary as we may not be continuing to attack it
        c = db.animalData.columns
        up = db.animalData.update().where(c.animalId == preyId).values(attackerId = None)
        self.conn.execute(up)
        
        self.updateStats(dt)
        
        self.commandNext()
        
    def addCommandAttackCooldown(self, preyId, dt):
        self.addCmdQueue('attackCooldown', dt, preyId)
        
    def attackCooldown(self, stamina):
        '''
        How long the cooldown takes after the attacks
        '''        
        if stamina == 0.0:
            stamina = 0.000001
            
        return  (self.growthStat/(self.attackStat*stamina)) + 1.0
        
    def getActionMap(self):
        '''
        List of all actions and their command set
        '''
        commandMap = {
            'add': self.addCommandAttackCooldown, 
            'pre': self.preCommandAttackCooldown, 
            'post': self.postCommandAttackCooldown}
        
        actionMap = super(Event, self).getActionMap()
        actionMap['attackCooldown'] = commandMap
        return actionMap    