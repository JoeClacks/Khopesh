# -*- coding: utf-8 -*-
'''
Base module for all animals
'''

import time
import math
#import pprint

from khopeshpy import config
from khopeshpy import db
from khopeshpy import level
#from khopeshpy import log
from khopeshpy import util
from khopeshpy.animals.top import States, createNew

class Animal(object):
    '''
    Base animal class
    '''
    
    #hold the data we pull from and push to the database
    data = {}
    
    #that rate at which an animal's remains decay
    decayRate = 0.05 #% of max per tick
    
    #Set by child classes
    species = None
    
    #Set by child classes
    stateChangeTime = None
    
    #holds the database connection
    conn = None
    
    def __init__(self, conn = None):
        '''
        sets up the animal
        '''
        
        if conn == None:
            msg = "Animal objects must be initialized with a database connection"
            raise Exception(msg)
        
        self.conn = conn
        
        self.data = {}
        
#class Setup(Animal):
    #'''
    #Base animal setup class
    #'''
    
    #def __init__(self, conn = None, position = None):
        #'''
        #sets up the animal
        #'''
        
        #super(Setup, self).__init__(conn)
        
        #if position == None:
            #msg = "Animal setup objects must be initialized with a position"
            #raise Exception(msg)
        
        #self.createNew(position)
        
class Event(Animal):
    '''
    Base animal event class
    '''
    
    actionMap = None
        
    def __init__(self, conn, row):
        '''
        sets up the animal
        '''
        #parent sets the database connection
        super(Event, self).__init__(conn)

        self.animalId = row['animalId']
        self.data.update(dict(row))
        
        self.actionMap = self.getActionMap()
            
        #else:
            #msg = "Animal event objects must be initialized with a db row"

            #raise Exception(msg)
        
    #def pullData(self):
        #'''
        #pulls the data for the animal from the database
        #'''
        
        #c = db.animalData.columns
        #statment = db.select([db.animalData], c.animalId == self.animalId)
        
        #result = self.conn.execute(statment)
        #row = result.fetchone()
        #result.close()
        
        #if row == None:
            #msg = "No record found for an animal with animalId: %d" % (self.animalId)
            #raise Exception(msg)
        
        #self.data.update(dict(row))
        
    def pushData(self):
        '''
        pushes the self.data variable to the database
        '''
        
        c = db.animalData.columns
        up = db.animalData.update().where(c.animalId == self.animalId).\
            values(**(self.data))
        self.conn.execute(up)
            
    def updateStats(self, dt):
        '''
        Handles conversion between bars
        '''
        
        convRate = self.conversionRate * dt
        
        if self.staminaPct < 0.25:
            #stamina is most important, can't do anything without it
            #    so we'll convert from stored or even health if we need to
            if self.storedPct > 0.01:
                #convert from stored
                total = self.stored if self.stored < convRate else convRate
                self.stamina += total
                self.stored -= total
            else:
                #convert from health
                total = self.health if self.health < convRate else convRate
                self.stamina += total
                self.health -= total
        elif self.healthPct < 0.25:
            #if health has fallen low convert from stored
            total = self.stored if self.stored < convRate else convRate
            self.health += total
            self.stored -= total
        elif self.healthPct > 0.75 and self.staminaPct > 0.75:
            #everything is hunky dory
            if self.growthPct < 0.99:
                #fill growth first, equally from health and stamina
                if self.growthMax - self.growth < convRate:
                    total = self.growthMax - self.growth
                else:
                    total = convRate
                
                self.health -= total/2
                self.stamina -= total/2
                self.growth += total
            else:
                #try to fill up stored
                if self.storedMax - self.stored < convRate:
                    total = self.storedMax - self.stored
                else:
                    total = convRate
                    
                self.health -= total/2
                self.stamina -= total/2
                self.stored += total
            
            
    def markCmdFinished(self, eventId, successful):
        '''
        updated the command queue for a completed actions
        '''
        c = db.animalCmdQueue.columns
        up = db.animalCmdQueue.update().where(c.eventId == eventId)\
            .values(active = False, done = True, 
                successful = successful, timeEnded = time.time())
        self.conn.execute(up)

    
    def commandSet(self, animalCmdId, timeExpected):
        '''
        set the current command for the animal
        '''
        
        ins = db.animalEventQueue.insert()\
            .values(eventEnd = time.time() + timeExpected*config.tick)
        result = self.conn.execute(ins)
        
        eventId = result.last_inserted_ids()[0]
            
        #and the animal object
        self.data['eventId'] = eventId
        
        
        #update the command queue
        c = db.animalCmdQueue.columns
        up = db.animalCmdQueue.update()\
            .where(c.animalCmdId == animalCmdId)\
            .values(eventId = eventId, sequence = None, \
                active = True, timeStarted = time.time())
        self.conn.execute(up)
        
        
    def commandNext(self):
        '''
        find the next command and set it as the current one
        '''
        
        #get the next command
        c = db.animalCmdQueue.columns
        statement = db.select([db.animalCmdQueue], (c.animalId == self.animalId) 
            & (c.done == False)).order_by(c.sequence.asc()).limit(1)
        result = self.conn.execute(statement)
        row = result.fetchone()
        result.close()
        
        if row == None:
            #add a default one if there is none
            self.addCommandDefault()
        else:
            #quick point: preCommands can fail (an animal is already being attacked)
            #    how are we going to handle this?
            #two possibilities for failure, move on to the next command or invalidate
            #    all the commands
            
            
            ##expecting problems with the data field, we're using the same format for
            ## direct calls as for calls from the database
            #scratch that, removed the direct call and replaced it with a call to this
            # function
            if(self.mapPreCommand(row['command'])(row['data']) != False):
                #print 'precommand failed: ' + row['command']
                #only set the command if the precommand succeeded 
                self.commandSet(row['animalCmdId'], row['timeExpected'])
            else:
                #otherwise mark the command as failed and move onto the next one
                self.markCmdFinished(row['eventId'], False)
                self.commandNext()
                
    def commandNextDefault(self):
        '''
        find the next command and set it as the current one
        (this version is only used by addCommandDefault
        '''
        
        #get the next command
        c = db.animalCmdQueue.columns
        statement = db.select([db.animalCmdQueue], (c.animalId == self.animalId) 
            & (c.done == False)).order_by(c.sequence.asc()).limit(1)
        result = self.conn.execute(statement)
        row = result.fetchone()
        result.close()
        
        if row == None:
            raise Exception("addCommandDefault() did not add any commands")
        else:
            if(self.mapPreCommand(row['command'])(row['data']) != False):
                #print 'precommand failed: ' + row['command']
                #only set the command if the precommand succeeded 
                self.commandSet(row['animalCmdId'], row['timeExpected'])
            else:
                print "Command: " + row['command'] + " Data: " + row['data']
                raise Exception("addCommandDefault() added a command that could not be executed")
            
            
        
    def getNextSequenceNumber(self):
        '''
        find the sequence number to add this command to the end of the command queue
        '''
        
        c = db.animalCmdQueue.columns
        statement = db.select([db.animalCmdQueue], (c.animalId == self.animalId))\
            .order_by(c.sequence.desc()).limit(1)
        result = self.conn.execute(statement)
        row = result.fetchone()
        result.close()
        
        if row == None:
            return 1
        if row['sequence'] == None:
            return 1
        else:
            return (row['sequence'] + 1)
            
    def addCmdQueue(self, command, timeExpected, data = None):
        '''
        add the passed command to the command queue
        returns the id of the entered command and the time expected
        '''
        
        ins = db.animalCmdQueue.insert().values(animalId = self.animalId,
            sequence = self.getNextSequenceNumber(), active = False, done = False, 
            command = command, timeExpected = timeExpected, data = data)
        result = self.conn.execute(ins)
        
        return (result.last_inserted_ids()[0], timeExpected)
        
    
    def getActionMap(self):
        return {}
        
    def mapAddCommand(self, command):
        if command in self.actionMap:
            return self.actionMap[command]['add']
        else:
            msg = "Unknown add command: " + command
            raise Exception(msg)
            
    def mapPreCommand(self, command):
        if command in self.actionMap:
            return self.actionMap[command]['pre']
        else:
            msg = "Unknown pre command: " + command
            raise Exception(msg)
        
    def mapPostCommand(self, command):
        if command in self.actionMap:
            return self.actionMap[command]['post']
        else:
            msg = "Unknown post command: " + command
            raise Exception(msg)
        
    def addCommandDefault(self):
        '''
        search for the best command for the animal and add it to the command queue
        '''
        
        #death check is done here
        if self.data['state'] == States.DEAD:
            cmdId, dt = self.actionMap['dead']['add'](dt = 1.0)
            #being dead has no preCommand
            self.commandSet(cmdId, dt)
            return
            
        #get the levels we have access to
        c = db.levelData.columns
        statement = db.select([db.levelData],
                c.cellIdX.between(self.position[0]-1, self.position[0]+1) &
                c.cellIdY.between(self.position[1]-1, self.position[1]+1) &
                c.levelIdZ.between(self.position[2]-1, self.position[2]+1))
        #statement = db.select([db.levelData],
                #(c.cellIdX == self.position[0]) &
                #(c.cellIdY == self.position[1]) &
                #(c.levelIdZ == self.position[2]))
        result = self.conn.execute(statement)
        rows = result.fetchall()
        result.close()

        levels = []
        for row in rows:
            levels.append(level.Event(row = row, conn = self.conn))

        #list of sequences of valid actions, parameters, and their need calculation
        #form of [(needCalc, [(command1, param1), (command2, param2)]]
        validActionList = []
        
        for lvl in levels:
            #only need to check if we can move to the level
            if lvl.walkable:
                #for action in self.getActionList():
                for action in self.actionMap:
                    if 'try' in self.actionMap[action]:
                        stateDiff = {'health': 0.0, 'stamina': 0.0, \
                            'unprocessed': 0.0, 'time': 0.0}
                        
                        cmdQueue = self.actionMap[action]['try'](lvl, stateDiff)
                        
                        #if the command is false then it failed for some reason, usually
                        #    either ran out of health or stamina
                        if cmdQueue != False and len(cmdQueue) > 0:
                            validActionList.append((self.needCalc(stateDiff), cmdQueue))
            
        
        #NOTE: what happens if the validActionList is empty? pass out or suicide?
        # right now the only possiblity of this happening is if a level becomes
        #    unwalkable, and (there is either not a walkable level nearby or the\
        # animal doesn't have enough stamina to walk there)
        #if there was no action then kill the animal
        if len(validActionList) == 0:
            self.data['state'] = States.DEAD
            self.deathCleanup()
            
        #sort and run the top action queue
        validActionList.sort(reverse = True)
        
        
        #break out the best action to preform
        #    (don't actually need the needRating)
        #print repr(validActionList)
        #pprint.pprint(validActionList)
        needRating, bestActionSequence = validActionList[0]
        
        #iterate over the cmdQueue of the top (best) action, adding each command 
        # in turn
        #NOTE: could we do this better with closures?
        for action in bestActionSequence:
            
            #the first arguement should be the function to add the command to the
            #    queue, the second should be the arguments to pass to the add command
            # function
            #cmdId, dt = action[0](*action[1])
            cmdId, dt = self.mapAddCommand(action[0])(*action[1])
            
            #if first:
                ##if it's the first we want to set the command
                ##do the preCommand stuff
                #self.mapPreCommand(action[0])(*action[1])
                
                ## and set the command
                #self.commandSet(cmdId, dt)
                #first = False
            #NOTE: ran into problems while adding the pre command option
            #    Just calling command next after the commands are added 
            # means we don't duplicate code and don't have to have
            # two interfaces to pre-commands
            #But gives us one more command against the database
            #    we may want to move it back out again later.
            #
            #Finally, this introduces the possibility of an infinite loop because
            #    commandNext calls this function if it can't find any queued commands
        self.commandNextDefault()
        
    def needCalc(self, stateDiff):
        '''
        calculate the need value for a state change
        '''
        
        #health
        #healthGain = (self.health + stateDiff['health'])
        healthGain = stateDiff['health']
        #healthGain = healthGain if healthGain < self.healthMax else self.healthMax
        
        #tired
        #staminaGain = (self.stamina + stateDiff['stamina'])
        staminaGain = stateDiff['stamina']
        #staminaGain = staminaGain if staminaGain 
        #    < self.staminaMax else self.staminaMax
        
        #hunger
        #unprocessedGain = (self.unprocessed + stateDiff['unprocessed'])
        unprocessedGain = stateDiff['unprocessed']
        #unprocessedGain = unprocessedGain if unprocessedGain 
        #    < self.unprocessedMax else self.unprocessedMax
        
        #NOTE: what if there is an 'instant' action that is positive, we run into a 
        #    divide by zero, for now make sure time is some minimum value
        if stateDiff['time'] < 0.1:
            stateDiff['time'] = 0.1
        
        return (healthGain + staminaGain + unprocessedGain)/stateDiff['time']

    def stateCheck(self):
        '''
        check if the animal needs to change it's state
        '''
        
        if self.state == States.DEAD:
            #the dead stay dead, for now
            return
        elif self.healthPct < 0.01:
            self.state = States.DEAD
            self.deathCleanup()
            
        timeSinceChanged = float(time.time() - self.stateChanged)/config.tick
        
        if self.state == States.CHILD:
            if timeSinceChanged > self.stateChangeTime:
                if self.growthPct > 0.9:
                    self.state = States.ADULT
                    self.stateChanged = time.time()
                
        elif self.state == States.ADULT:
            if timeSinceChanged > self.stateChangeTime \
                    and self.growthPct > 0.9 and self.healthPct > 0.9:
                self.state = States.REPRO
                self.stateChanged = time.time()
                
        elif self.state == States.REPRO:
            if timeSinceChanged > self.stateChangeTime:
                createNew(self.conn, self.species, self.position)
                self.state = States.ADULT
                self.stateChanged = time.time()
                
        #otherwise do nothing
        
    
    def deathCleanup(self):
        '''
        remove all references in the command queue
        '''
        
        c = db.animalCmdQueue.columns
        delete = db.animalCmdQueue.delete().where(c.animalId == self.animalId)
        self.conn.execute(delete)
        
    def decomposedCleanup(self):
        '''
        remove all references to an animal
        '''
        
        c = db.animalCmdQueue.columns
        delete = db.animalCmdQueue.delete().where(c.animalId == self.animalId)
        self.conn.execute(delete)
        
        c = db.animalData.columns
        delete = db.animalData.delete().where(c.animalId == self.animalId)
        self.conn.execute(delete)
        
    def biomassEaten(self, amount):
        '''
        used after the animal has died (we may want to check for that) to track
        how much of the animal was eaten
        '''
        if amount < self.stored:
            self.stored -= amount
        else:
            amount -= self.stored
            self.stored = 0.0
            self.growth -= amount
            
            if self.growth < 0:
                self.growth = 0.0
                
        c = db.animalData.columns
        up = db.animalData.update().where((c.animalId == self.animalId)).\
            values(growth = self.growth, stored = self.stored)
        self.conn.execute(up)
        
    def attacked(self, attackerId, atkStrength):
        msg = "Attacked behavior not defined"
        raise Exception(msg)
        
        
    #properties
    state = property(util.getValue('state'), util.setValue('state'))
    stateChanged = property(util.getValue('stateChanged'), util.setValue('stateChanged'))
    
    
    @property
    def position(self):
        '''
        attribute
        '''
        return (self.data['animalX'], self.data['animalY'], self.data['animalZ'])
    
    @property
    def staminaDrain(self):
        '''
        attribute
        '''
        return self.growthStat/500.0
        
    @property
    def conversionRate(self):
        '''
        attribute
        '''
        return self.growthStat/5.0
    
    @property
    def growthMax(self):
        '''
        the maximum value for growth, right now based on age
        '''
        age = (time.time() - self.data['birthDate'])/config.tick
        final = math.sqrt(math.sqrt(age)) + 5.0
        return final
            
    growth = property(util.getValue('growth'), util.setValue('growth'))
    growthStat = property(util.getStat('growth'))
    growthPct = property(util.getPercent('growth', 'growthMax'))
    
    
    
    @property
    def staminaMax(self):
        '''
        the maximum value for stamina
        '''
        return self.growthStat
    
    stamina = property(util.getValue('stamina'), util.setBarValue('stamina', 'staminaMax'))
    staminaPct = property(util.getPercent('stamina', 'staminaMax'))
    
    @property
    def healthMax(self):
        '''
        the maximum value for health
        '''
        return self.growthStat
        
    health = property(util.getValue('health'), util.setBarValue('health', 'healthMax'))
    healthPct = property(util.getPercent('health', 'healthMax'))
    
    
    @property
    def storedMax(self):
        '''
        the maximum value for stored
        '''
        return self.growthStat
        
    stored = property(util.getValue('stored'), util.setBarValue('stored', 'storedMax'))
    storedPct = property(util.getPercent('stored', 'storedMax'))
    
    @property
    def unprocessedMax(self):
        '''
        attribute
        '''
        return self.growthStat
        
    unprocessed = property(util.getValue('unprocessed'), util.setBarValue('unprocessed', 'unprocessedMax'))
    unprocessedPct = property(util.getPercent('unprocessed', 'unprocessedMax'))
    
        
    def attackStrength(self, health):
        '''
        How strong an attack is
        '''
        return self.growthStat * self.attackStat * health
    
    
    @property
    def attackStaminaCost(self):
        '''
        How much stamina attacking costs
        '''
        return (self.growthStat/self.attackStat)/100.0
    
    attack = property(util.getValue('attack'), util.setValue('attack'))
    attackStat = property(util.getStat('attack'))
    