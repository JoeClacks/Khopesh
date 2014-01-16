# -*- coding: utf-8 -*-
'''
Created on April 6, 2011

@author: Joseph Clark
'''
import time

from khopeshpy import db
from khopeshpy import config

class States(object):
    '''
    Possible states for an avatar
    '''
    
    DEAD = 0
    CHILD = 1
    ADULT = 2
    REPRO = 3
    
class Species(object):
    '''
    Possible species for an avatar
    '''
    
    HUMAN = 0
    
        
eventAvatarList = {}    
def eventAvatarRegister(name, species):
    eventAvatarList[name] = species

def eventAvatarFactory(conn, avatarId = None, row = None):
    '''
    Return the correct event avatar object if it exists in the 
        registered event avatar list
    ''' 
    if avatarId != None:
        c = db.avatarData.columns
        statment = db.select([db.avatarData], c.avatarId == avatarId)
        
        result = conn.execute(statment)
        row = result.fetchone()
        result.close()
        
        if row == None:
            msg = "No record found for an avatar with avatarId: %d" % (avatarId)
            raise Exception(msg)
        #fall though now that row is populated
        
    if row['avatarSpecies'] in eventAvatarList:
        return eventAvatarList[row['avatarSpecies']](conn, row)
    else:
        msg = "Unknown species: " + repr(row['avatarSpecies'])
        raise Exception(msg)
    
controlAvatarList = {}
def controlAvatarRegister(name, species):
    controlAvatarList[name] = species
    
def controlAvatarFactory(conn, avatarId = None, row = None):
    '''
    Return the correct event avatar object if it exists in the 
        registered event animal list
    ''' 
    if avatarId != None:
        c = db.avatarData.columns
        statment = db.select([db.avatarData], c.avatarId == avatarId)
        
        result = conn.execute(statment)
        row = result.fetchone()
        result.close()
        
        if row == None:
            msg = "No record found for an avatar with avatarId: %d" % (avatarId)
            raise Exception(msg)
        #fall though now that row is populated
        
    if row['avatarSpecies'] in controlAvatarList:
        return controlAvatarList[row['avatarSpecies']](conn, row)
    else:
        msg = "Unknown species: " + repr(row['avatarSpecies'])
        raise Exception(msg)
    
    
    
#differences from the animal implementation:
# currently we only have the human species, to that doesn't need to be passed in
# require the name of the avatar, avatar names aren't unique, so the avatar creation can't fail on that
# still need location, assuming that a safe spawn will be passed in from below 
#  (any choices would be based on the family anyway wouldn't they?)
# Needs familyId so has to be created after the family exists
# Shouldn't really be able to fail
def createNew(conn, userId, familyId, avatarName, location):
    '''
    Creates a new avatar at the passed location of the passed species and returns 
        the new avatar's avatarId
    '''
    ins = db.avatarData.insert()\
        .values(   
            #avatarId should be auto generated
            #
            familyId = familyId,
            userId = userId,
            
            name = avatarName,
            
            avatarX = location[0], 
            avatarY = location[1], 
            avatarZ = location[2],
            
            state = States.CHILD,
            stateChanged = time.time(),            
            
            birthDate = (time.time() - config.tick),
            
            stamina = 0.5,
            health = 0.5,
            stored = 0.5,
            unprocessed = 0.5,
            
            growth = 1.0,
            forage = 1.0,
            running = 1.0,
            attack = 1.0,
            scavenge = 1.0,
        )
    result = conn.execute(ins)

    return result.last_inserted_ids()[0]
