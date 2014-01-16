# -*- coding: utf-8 -*-
'''
Created on May 17, 2010

@author: Joseph Clark
'''

import time

from khopeshpy import db
from khopeshpy import config

from khopeshpy.avatars import human
from khopeshpy.avatars.top import States, Species, eventAvatarFactory, createNew, controlAvatarFactory

def processEvent(row, conn):
    '''
    Receves and processes events from the event server
    '''
    avatar = eventAvatarFactory(conn, avatarId = row['avatarId'])
    
    #state check, death
    avatar.stateCheck()
    
    #there is a problem, if say the server were left off all night
    # when it was restarted all avatars would have massive stamina deficits
    #    it would probably even kill everything, so we're changing this to just work
    # of off the anticiapted time, or if the action is interrupted then 
    #    the time until it was interrupted
    dta = row['timeExpected']#ticks
    dtb = (float(time.time() - row['timeStarted']))/config.tick #ticks
    dt = min(dta, dtb)
    
    avatar.mapPostCommand(row['command'])(row, dt)
    
    avatar.pushData()


def processIdle(conn, row):
    '''
    Receves and processes idle avatars
    '''
    avatar = eventAvatarFactory(conn, avatarId = row['avatarId'])

    avatar.addCommandDefault()

    avatar.pushData()
    
def getControlAvatars(conn, familyId):
    
    c = db.avatarData.columns
    statment = db.select([db.avatarData], c.familyId == familyId)
    result = conn.execute(statment)
    rows = result.fetchall()
    result.close()
    
    ret = {}
    for row in rows:
        ret[row['avatarId']] =  controlAvatarFactory(conn, row = row)
        
    return ret
        
    