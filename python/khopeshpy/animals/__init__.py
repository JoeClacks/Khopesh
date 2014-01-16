# -*- coding: utf-8 -*-
'''
Created on May 17, 2010

@author: Joseph Clark
'''

import time

from khopeshpy import config

from khopeshpy.animals import bison
from khopeshpy.animals import wolf
from khopeshpy.animals.top import States, Species, eventAnimalFactory, createNew


def processEvent(conn, row):
    '''
    Receves and processes events from the event server
    '''
    animal = eventAnimalFactory(conn, animalId = row['animalId'])
    
    #state check, death
    animal.stateCheck()
    
    #there is a problem, if say the server were left off all night
    # when it was restarted all animals would have massive stamina deficits
    #    it would probably even kill everything, so we're changing this to just work
    # of off the anticipated time, or if the action is interrupted then 
    #    the time until it was interrupted
    dta = row['timeExpected']#ticks
    dtb = (float(time.time() - row['timeStarted']))/config.tick #ticks
    dt = min(dta, dtb)
    
    animal.mapPostCommand(row['command'])(row, dt)
    
    animal.pushData()

def processIdle(conn, row):
    '''
    Receves and processes idle animals
    '''
    animal = eventAnimalFactory(conn, animalId = row['animalId'])

    animal.addCommandDefault()

    animal.pushData()

