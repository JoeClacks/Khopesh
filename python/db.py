# -*- coding: utf-8 -*-


import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, MetaData, Boolean, Index, Float, DateTime, Text


#unused imports for now
#from sqlalchemy.sql import not_, String

worldData = None
cellData = None
levelData = None
userData = None

familyData = None
avatarData = None
avatarCmdQueue = None
avatarEventQueue = None

convData = None
convMsg = None

cityData = None
#metadata = None
#conn = None

eventQueue = None
animalCmdQueue = None
animalEventQueue = None


animalData = None

def connect():  
    return engine.connect()

#rebuilds the database
def createMetadata():
    global worldData
    global cellData
    global levelData
    global userData
    
    global familyData
    global avatarData
    global avatarCmdQueue
    global avatarEventQueue
    
    global convData
    global convMsg
    
    global cityData
  
  
    
    global animalData
    global animalCmdQueue
    global animalEventQueue
      
    global metadata
    
    metadata = MetaData()
    
    worldData = Table('worldData', metadata,
      Column('worldId', Integer, primary_key=True),
      #Column('worldName', String),
      Column('worldSizeX', Integer),
      Column('worldSizeY', Integer),
      Column('worldWrapX', Boolean),
      Column('worldWrapY', Boolean),
      Column('worldSeaLevel', Integer),
      mysql_engine='InnoDB',
    )
    
    cellData = Table('cellData', metadata,
      Column('cellId', Integer, primary_key=True),
      Column('worldId', Integer),
      Column('cellIdX', Integer),
      Column('cellIdY', Integer),
      Column('cellGroundlevel', Integer),
      Column('cellTemp', Float), #celsius
      Column('cellSolar', Float), #percentage
      Column('cellImage', Text),
      Column('lastUpdated', Integer),
      mysql_engine='InnoDB',
    ) 
    
    Index('cellIndex', cellData.c.cellIdX, cellData.c.cellIdY)
    Index('cellUpdate', cellData.c.lastUpdated)
    
    levelData = Table('levelData', metadata,
      Column('levelId', Integer, primary_key=True),
      Column('worldId', Integer),
      Column('cellIdX', Integer),
      Column('cellIdY', Integer),
      Column('levelIdZ', Integer),    
      Column('water', Float),
      Column('air', Float),
      Column('rock', Float),
      
      Column('savanna', Float),
      Column('grassland', Float),
      Column('forestCanopy', Float),
      Column('taigaCanopy', Float),
      Column('tundra', Float),
      Column('forestUnderstory', Float),
      Column('taigaUnderstory', Float),
      #this stores the source image to serve instead of a custom one
      Column('baseImage', Text),
      Column('dirtyImage', Boolean),#if the tileimage needs updating
      
      #city information
      Column('cityId', Integer),
      
      #when were the variable stats (biomes) last updated
      Column('lastUpdated', Integer),
      
      mysql_engine='InnoDB',
    )
    
    Index('levelIndex', levelData.c.cellIdX, levelData.c.cellIdY, levelData.c.levelIdZ)
    Index('mapUpdate', levelData.c.dirtyImage)
    
    userData = Table('userData', metadata,
      Column('userId', Integer, primary_key=True),
      Column('username', Text),
      Column('password', Text),
      
      Column('name', Text),
      
      Column('userX', Integer), #should be the last place the player looked at?
      Column('userY', Integer), #  Oldest avatar maybe?
      Column('userZ', Integer),
      
      Column('state', Integer),
      mysql_engine='InnoDB',
    )
    
    familyData = Table('familyData', metadata,
      Column('familyId', Integer, primary_key=True),
      Column('userId', Integer),
      Column('name', Text),
      Column('state', Integer),
      mysql_engine='InnoDB',
    )
    
    avatarData = Table('avatarData', metadata,
      Column('avatarId', Integer, primary_key=True),
      Column('familyId', Integer),
      Column('userId', Integer),  #Redundent through familyId....
      
      Column('name', Text),
      
      Column('state', Integer),
      Column('stateChanged', Integer),
      
      Column('avatarX', Integer),
      Column('avatarY', Integer),
      Column('avatarZ', Integer),
      
      Column('birthDate', Integer), #when the avatar was born
      
      Column('stamina', Float),
      Column('health', Float),
      Column('stored', Float),
      Column('unprocessed', Float),
      
      Column('growth', Float),
        
      Column('forage', Float),
      Column('running', Float),
      Column('scavenge', Float),
      
      Column('attack', Float),
      
      Column('eventId', Integer),#The current event being processed
      #cheap way to find avatars that aren't doing anything
      
      Column('attackerId', Integer),#used as a lock
      mysql_engine='InnoDB',
    )
    Index('avatarPosition', avatarData.c.avatarX, avatarData.c.avatarY, avatarData.c.avatarZ)
    Index('avatarIdle', avatarData.c.eventId)
    
    
    #two things on cityStartlevelId,
    # it could combined with cityStarter
    # and we need to make sure that it is current
    cityData = Table('cityData', metadata,
      Column('cityId', Integer, primary_key=True),
      Column('cityName', Text),
      Column('cityStarter', Boolean),
      Column('cityStartX', Integer),
      Column('cityStartY', Integer),
      Column('cityStartZ', Integer),
      mysql_engine='InnoDB',
    )
    
    #npcGroupData = Table('npcGroupData', metadata,
        #Column('npcGroupId', Integer, primary_key=True),
    #)
    
    #npcData = Table('npcData', metadata,
        #Column('npcId', Integer, primary_key=True),
        #Column('npcGroupId', Integer),
        #Column('npcGene', String),
    #)
    
    #We'll apparently need an ingame friendlist
    friendData = Table('friendData', metadata,
      Column('userIdA', Integer),
      Column('userIdB', Integer),
      Column('Aaccepted', Boolean),
      Column('Baccepted', Boolean),
      mysql_engine='InnoDB',
    )
    
    
    #These tables are for the ingame chat functionality
    #might split out later to allow multi user conversations?
    convData = Table('convData', metadata,
      Column('convId', Integer, primary_key=True),
      Column('userAId', Integer),
      Column('userBId', Integer),
      Column('convActive', Boolean),
      mysql_engine='InnoDB',
    )
    
    convMsg = Table('convMsg', metadata,
      Column('msgId', Integer, primary_key=True),
      Column('convId', Integer),
      Column('userId', Integer),
      Column('text', Text),
      Column('timestamp', Integer),
      mysql_engine='InnoDB',
    )
    
    
    #thinking we'll limit this to one week of history
    avatarCmdQueue = Table('avatarCmdQueue', metadata,
      Column('avatarCmdId', Integer, primary_key=True),#auto
      Column('avatarId', Integer),#ret to the avatar this belongs to
      Column('eventId', Integer),#ref to eventQueue
      Column('sequence', Integer),#queue position, can this overflow?
      Column('active', Boolean),#has this been put into the eventQueue (current)
      Column('done', Boolean), #has the task been completed
      Column('failed', Boolean),
      Column('timeExpected', Float),#how much time we want/expect the task to take in ticks
      Column('timeStarted', DateTime),#what time was the task started (for history)
      Column('timeEnded', DateTime),#what time was it completed (for history)
      Column('command', Text),
      Column('default', Boolean), #if the command as selected by default
      Column('data', Text),#command specifics
      mysql_engine='InnoDB',
    )
    
    ##select * from avatar command queue where avatarId = 1 and done = false sort by sequence (limit 1 to get next)
    
    
    ##(eventId, eventType, eventEnd)
    ##(45, 'avatarCmdQueue', 2:00PM)
    
    avatarEventQueue = Table('avatarEventQueue', metadata,
      Column('eventId', Integer, primary_key=True),
      Column('eventType', Text),
      #//Column('eventEnd', DateTime),
      Column('eventEnd', Integer),
      mysql_engine='InnoDB',
    )
    
    #join the eventQueue and avatarCmdQueue tables to get the full picture
    #this won't give us a full history
    #we want to keep both tables from blowing up
    # a time limit on data, clean up to the previous week every day
    #n players*24 average events per day*7 days? n....but just in the avatarCmdQueue,
    #  event queue can be cleaned up immedeatly
    #will have to do date searches on the eventQueue
    #trying to schedule things instead of having just a queue seems like too much work
    
    
    animalData = Table('animalData', metadata,
      Column('animalId', Integer, primary_key = True),
      Column('animalSpecies', Integer),#bison, wolf
      
      Column('animalX', Integer),
      Column('animalY', Integer),
      Column('animalZ', Integer),
      
      Column('state', Integer),
      Column('stateChanged', Integer),
      
      Column('birthDate', Integer), #when the animal was born
      
      Column('stamina', Float),
      Column('health', Float),
      Column('stored', Float),
      Column('unprocessed', Float),
      
      Column('growth', Float),
      
      Column('forage', Float),
      Column('running', Float),
      Column('scavenge', Float),
      
      Column('attack', Float),
      #Column('defense', Float),
      #Column('counter', Float),
      
      Column('eventId', Integer),#The current event being processed
      #cheap way to find avatars that aren't doing anything
      
      Column('attackerId', Integer),#used as a lock
      mysql_engine='InnoDB',
    )
    Index('animalPosition', animalData.c.animalX, animalData.c.animalY, animalData.c.animalZ)
    Index('animalIdle', animalData.c.eventId)
      
    animalCmdQueue = Table('animalCmdQueue', metadata,
      Column('animalCmdId', Integer, primary_key=True),#auto
      Column('animalId', Integer),#ret to the avatar this belongs to
      Column('eventId', Integer),#ref to eventQueue
      Column('sequence', Integer),
      Column('active', Boolean),#has this been put into the eventQueue (current)
      Column('done', Boolean), #has the task been completed (is this a task that is still on the queue)
      Column('successful', Boolean), #was the task successful (interrupted?)
      Column('timeExpected', Float),#how much time we want/expect the task to take in ticks
      Column('timeStarted', Integer),#what time was the task started (for history)
      Column('timeEnded', Integer),#what time was it completed (for history)
      Column('command', Text), #command name
      Column('data', Text),#command specific information
      mysql_engine='InnoDB',
    )
    Index('animalCmdQueue2', animalCmdQueue.c.animalId, animalCmdQueue.c.sequence)
    Index('animalCmdQueue3', animalCmdQueue.c.eventId)
    
    animalEventQueue = Table('animalEventQueue', metadata,
      Column('eventId', Integer, primary_key=True),
      Column('eventEnd', Integer),
      mysql_engine='InnoDB',
    )
    Index('animalEventQueue1', animalEventQueue.c.eventEnd)
    
      
    metadata.create_all(engine)


def setDefaultData():
    conn = engine.connect() 
    
    ins = worldData.insert().values(worldId = 1, worldName = 'World 1', \
                worldWrapX = True, worldWrapY = False, worldSeaLevel = 0)
    
    result = conn.execute(ins)  
    
    conn.close()
  
  
#def execute(arg):
    #conn.execute(arg)
  
#def begin():
    #return conn.begin()
  
#def close():
    #conn.close()

#def testSelect():
##cursor.execute("select worldSizeX, worldSizeY, worldWrapX, worldWrapY \
        ##from worldData where worldId = %s", (worldId,))
    #d = [worldData.c.worldSizeX, worldData.c.worldSizeY, worldData.c.worldWrapX, worldData.c.worldWrapY, worldData.c.worldSeaLevel]
    ##print d
    
    ##print worldData.c['worldName']
    ##print worldData.c.worldName
    #c = (worldData.c.worldId == worldId)
  
    #s = sqlalchemy.select(d,c)
    #for row in conn.execute(s):
    #print row
    
def select(columns, clause):
    return sqlalchemy.select(columns, clause)

engine = create_engine('mysql://khopesh:khopesh@localhost/khopesh', echo=False)
#engine = create_engine('sqlite:///database.db', echo=False)
createMetadata()
#engine = create_engine('sqlite:///:memory:', echo=False)


#connect()
#createMetadata()
#setDefaultData()
#testSelect()
#print worldData.c.worldSizeX

#execute(worldData.update().where(worldData.c.worldId == 1).values(worldSeaLevel = 1))

#testSelect()
