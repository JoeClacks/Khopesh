#!/usr/bin/python2.6

import cherrypy
import json
import sys
import shutil
import os

#our files
import db
import util

worldData = {}
userData = None

class UserData:
  userId = 0
  userName = ''
 
  userX = 0
  userY = 0
  userZ = 0

  def __init__(self, row):
    self.userId = row['userId']
    self.userName = row['userName']
    
    self.userX = row['userX']
    self.userY = row['userY']
    self.userZ = row['userZ']
    
  def json(self):
    ret = {'userId': self.userId,
	    'userName': self.userName,
	    'userX': self.userX,
	    'userY': self.userY,
	    'userZ': self.userZ}
    print ret
    return ret



class WorldData:
  worldId = 0
  worldName = 0
  
  worldSizeX = 0
  worldSizeY = 0
  worldSizeZ = 0
  worldWrapX = 0
  worldWrapY = 0
  worldSeaLevel = 0
  
  
  def __init__(self, row):
    self.worldId = row['worldId']
    
    self.worldSizeX = row['worldSizeX']
    self.worldSizeY = row['worldSizeY']
    
    self.worldWrapX = row["worldWrapX"]
    self.worldWrapY = row["worldWrapY"]
    
    self.worldSeaLevel = row['worldSeaLevel']
    
  def json(self):
    return {'worldId': self.worldId,
	    'worldSizeX': self.worldSizeX,
	    'worldSizeY': self.worldSizeY,
	    'worldWrapX': self.worldWrapX,
	    'worldWrapY': self.worldWrapY,
	    'worldSeaLevel': self.worldSeaLevel}
	    
class worldModel:
	worldId = 0
	
	worldName = (None, False)
	worldSizeX = (None, False)
	worldSizeY = (None, False)
	worldSizeZ = (None, False)
	worldWrapX = (None, False)
	worldWrapY = (None, False)
	worldSeaLevel = (None, False)
	
	def __init__(self, worldId):
		self.worldId = worldId
		
	

class Main:
  #TODO Sanitize inputs
	def getWorldData(self, worldId = None, callback = None):
		global worldData

		if worldId == None:
			print "getWorldData must be passed worldId"
			return "getWorldData must be passed worldId"
			
		elif worldId not in worldData:

			c = db.worldData.columns
			statment = db.select([c.worldId, c.worldSizeX, c.worldSizeY, c.worldWrapX, c.worldWrapY, c.worldSeaLevel], c.worldId == worldId)
			
			conn = db.connect()
			result = conn.execute(statment)
			row = result.fetchone()
			result.close()
			conn.close()

			if row == None:
				print "Did not find worldData record, exiting."
				return "Did not find worldData record, exiting."

			worldData[worldId] = WorldData(row)
		
		if callback == None:
			return json.dumps(worldData[worldId].json())
		else:
			return callback + '(' + json.dumps(worldData[worldId].json()) + ')'

		db.close()

	getWorldData.exposed = True

	def getUserData(self, userId = None, callback = None):
		global userData

		if userId == None:
			print "getUserData must be passed userId"	
			return "getUserData must be passed userId"
			
		elif userData == None:
			c = db.userData.columns
			statment = db.select([c.userId, c.userName, c.userX, c.userY, c.userZ], c.userId == userId)
			
			conn = db.connect()
			result = conn.execute(statment)
			row = result.fetchone()
			result.close()
			conn.close()

			if row == None:
				print "Did not find userData record, exiting."
				return "Did not find userData record, exiting."

			userData = UserData(row)
		
		print userData.json()
		if callback == None:
			return json.dumps(userData.json())
		else:
			return callback + '(' + json.dumps(userData.json()) + ')'
		
		db.close()
	getUserData.exposed = True 
  
  
  #called when the client can't find an image it wants
	def generateWorldmap(self, worldId = None, x = None, y = None, z = None, callback = None):
		#can't do anything if they don't send the full address
		if worldId == None or x == None or y == None or z == None:
			return "Need full parameters"
			
		#first check that there really isn't an image
		imageName = "img-world-%d/zoom0-%dx-%dy-%dz.png" % (int(worldId), int(x), int(y), int(z))
		if os.path.isfile(imageName):
			#file already exists, either it was created by another handler or somebody's mucking around
			#just return the image name
			if callback == None:
				return json.dumps(imageName)
			else:
				return callback + '(' + json.dumps(imageName) + ')'
				
		#see if their is a level entry for it
		c = db.levelData.columns
		statment = db.select([c.baseImage], 
			(c.cellIdX == x) & (c.cellIdY == y) & (c.levelIdZ == z) & (c.worldId == worldId))
			
		conn = db.connect()
		
		result = conn.execute(statment)
		level = result.fetchone()
		result.close()
		
		if level == None:
			c = db.cellData.columns
			statment = db.select([c.cellGroundlevel], 
				(c.cellIdX == x) & (c.cellIdY == y) & (c.worldId == worldId))
			result = conn.execute(statment)
			row = result.fetchone()
			result.close()
			groundLevel = row['cellGroundlevel']
			
			c = db.worldData.columns
			statment = db.select([c.worldSeaLevel], (c.worldId == worldId))
			result = conn.execute(statment)
			row = result.fetchone()
			result.close()
			seaLevel = row['worldSeaLevel']
			
			level = util.genLevelData(groundLevel, seaLevel, z)
				
			level['worldId'] = worldId
			level['cellIdX'] = x
			level['cellIdY'] = y
			level['levelIdZ'] = z
			ins = db.levelData.insert()
			conn.execute(ins, level)
		
		conn.close()
		
		oldFileName = level['baseImage']

		#the browsers cache will just reload the old(non-existant) image so we'll send it the address of the source image
		#	for the tile
		print oldFileName
		if callback == None:
			return json.dumps(oldFileName)
		else:
			return callback + '(' + json.dumps(oldFileName) + ')'
	generateWorldmap.exposed = True

	def logonUser(self, username = None, callback = None):
		if username == None:
			msg = "logonUser must be passed username"	
			print msg
			return msg
			
		c = db.userData.columns
		statment = db.select([c.userId], c.userName == username)
			
		conn = db.connect()
		result = conn.execute(statment)
		row = result.fetchone()
		result.close()
		conn.close()

		if row == None:
			msg = "Did not find username '"+username+"' in database"
			print msg
			userId = -1
		else:
			userId = row[c.userId]
		
		print "Sending userid:", userId
		if callback == None:
			return json.dumps(userId)
		else:
			return callback + '(' + json.dumps(userId) + ')'
		
		db.close()		
	logonUser.exposed = True
	
	def createUser(self, username = None, callback = None):
		if username == None:
			msg = "createUser must be passed username"	
			print msg
			return msg
		
		#no guarntee that we've made the userName field unique so we'll make sure there
		#	isn't an entry before we create a new one
		c = db.userData.columns
		statment = db.select([c.userId], c.userName == username)
			
		conn = db.connect()
		result = conn.execute(statment)
		row = result.fetchone()
		result.close()
		

		if row == None:
			msg = "Did not find username '"+username+"' in database, creating..."
			c = db.userData.columns
			
			ins = db.userData.insert().values(userName = username)
			result = conn.execute(ins)
			userId = result.last_inserted_ids()[0]
			result.close()
		else:
			msg = "Found username '"+username+"' in database, not re-creating..."
			print msg
			return msg
		
		conn.close()
		
		print "Sending new userid:", userId
		if callback == None:
			return json.dumps(userId)
		else:
			return callback + '(' + json.dumps(userId) + ')'
		
		db.close()		
	createUser.exposed = True

	def index(self):
		out = ""
		
		if cherrypy.session.get('fieldname') != None:
			#out += "'" + str(cherrypy.session.get('fieldname')) + "'<br>\n"
			out += "'" + str(cherrypy.session['fieldname']) + "'<br>"
			#cherrypy.session['fieldname'] = cherrypy.session.get('fieldname') + 1
			cherrypy.session['fieldname'] += 1
		else:
			out += "Session var not found, setting<br>"
			
			cherrypy.session['fieldname'] = 1
		out += "Hello world!<br>"
		
		out += sys.version + "<br>"
		
		out += json.dumps(['foo', {'var': ('baz', None, 1.0, 2)}])
		
		return out
	index.exposed = True

	#def getUpdate(self, objType = None, objId = None, callback = None):
		#conn = db.connect()
		#if objType == 'WorldMode':
			#if cherrypy.session.has_key['WorldMode']:
				#cherrypy.session['WorldMode'][objId]
			
		
		
		#conn.close()
	#getUpdate.exposed = True


#we could put startup code here?

#cherrypy.config.update({'log.screen': False,})

cherrypy.quickstart(Main(),  config="cherryConfig.ini")