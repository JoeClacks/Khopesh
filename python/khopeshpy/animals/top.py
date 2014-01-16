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
    Possible states for an animal
    '''
    
    DEAD = 0
    CHILD = 1
    ADULT = 2
    REPRO = 3
    
class Species(object):
    '''
    Possible species for an animal
    '''
    
    BISON = 0
    WOLF = 1
    
        
eventAnimalList = {}    
def eventAnimalRegister(name, species):
    eventAnimalList[name] = species

def eventAnimalFactory(conn, animalId = None, row = None):
    '''
    Return the correct event animal object if it exists in the 
        registered event animal list
    ''' 
    if animalId != None:
        c = db.animalData.columns
        statment = db.select([db.animalData], c.animalId == animalId)
        
        result = conn.execute(statment)
        row = result.fetchone()
        result.close()
        
        if row == None:
            msg = "No record found for an animal with animalId: %d" % (animalId)
            raise Exception(msg)
        #fall though now that row is populated
        
    if row['animalSpecies'] in eventAnimalList:
        return eventAnimalList[row['animalSpecies']](conn, row)
    else:
        msg = "Unknown species: " + repr(row['animalSpecies'])
        raise Exception(msg)
    
    
    
def createNew(conn, species, location):
    '''
    Creates a new animal at the passed location of the passed species and returns 
        the new animal's animalId
    '''
    ins = db.animalData.insert()\
        .values(
            animalSpecies = species,
            
            animalX = location[0], 
            animalY = location[1], 
            animalZ = location[2],
            
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
