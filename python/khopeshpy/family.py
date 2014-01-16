#!/usr/bin/python2.6
import khopeshpy.db as db
import khopeshpy.avatars as avatar
import khopeshpy.city as city

class States(object):
    '''
    Possible states for a family
    '''
    DEAD = 0
    ALIVE = 1

class Family(object):
    #NOTE: userId is not guaranteed to be 1-to-1 
    userId = -1
    familyId = -1
    valid = False

    data = {}
    
    def __init__(self, userId = -1, familyId = -1):
        if familyId == -1 and userId == -1:
            msg = "Family objects must be initialized with either a userId or a familyId"
            raise Exception(msg)
        
        self.familyId = familyId
        self.userId = userId
        
        self.pullData()
        
        return
    
    def pullData(self):
        #NOTE: selecting old family id's may be a problem
        if self.familyId > 0:
            c = db.familyData.columns
            statment = db.select([db.familyData], c.familyId == self.familyId)
            
            conn = db.connect()
            result = conn.execute(statment)
            row = result.fetchone()
            result.close()
            conn.close()
            
            if row == None:
                msg = "No record found for a family with familyId: %d" % (self.familyId)
                raise Exception(msg)
            
            self.data.update(dict(row))
            self.valid = True
            self.userId = self.data['userId']
        elif self.userId > 0:
            c = db.familyData.columns
            statment = db.select([db.familyData], (c.userId == self.userId) & (c.state == States.ALIVE))
            
            conn = db.connect()
            result = conn.execute(statment)
            row = result.fetchone()
            result.close()
            conn.close()
            
            if row == None:
                msg = "No record found for a living family for userId: %d" % (self.userId)
                raise Exception(msg)
            
            self.data.update(dict(row))
            self.valid = True
            self.familyId = self.data['familyId']
        else:
            msg = "Family objects must be initialized with a valid a userId or a valid familyId"
            raise Exception(msg)        
    
class Model(Family):
    pass
    
#only used for the current player's family, use the model interface for other player's families
class Control(Family):
    #With the control the current family is always assumed
    def __init__(self, userId = -1):
        if userId == -1:
            msg = "Family control objects must be initialized with a userId"
            raise Exception(msg)
        
        self.userId = userId
        
        self.pullData()
        
        return
    
#used to create a new family
#returns (familyId, "Ok") on success (-1, msg) on failure
# thinking that we'll create the family-avatar relationship as an invariant
# where if a family has no member's it is considered dead
# assumes that userId is valid
def createNew(conn, userId, familyName, avatarName):    
    #first we have to check if a family with that name already exists
    c = db.familyData.columns
    statment = db.select([db.familyData], (c.name == familyName))
    
    result = conn.execute(statment)
    row = result.fetchone()
    result.close()
    
    if row != None:
        msg = "Family with name: %s already exists" % (familyName)
        print msg
        return (-1, msg)
    else:
        #Avatar names aren't unique so we don't have to check that.
        #This is a new family so we don't have to worry about the
        # second check if an avatar with that name already exits        
        
        ins = db.familyData.insert()\
            .values(
                userId = userId, 
                name = familyName, 
                state = States.ALIVE
            )
            
        result = conn.execute(ins)
        
        familyId = result.last_inserted_ids()[0]
        
        #now that we a family id create the avatar
        #how to pick the location?
        # thinking we'll set certain cities to be starter cities (their's 
        # currently a flag to do that....)
        #woo! cities are defined over a number of cells, just select a random one? 
        avatar.createNew(conn, userId,  familyId, avatarName, city.getStartingLocation(conn))
        return (familyId, "Ok")
    
    
        
        
        

        

        
        
        
        
        