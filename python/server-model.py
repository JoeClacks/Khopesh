#!/usr/bin/python2.6
import cherrypy
import json
import os

from khopeshpy import db
import khopeshpy.user
import khopeshpy.family
import khopeshpy.world
import khopeshpy.exceptions
import khopeshpy.config
    
class Main:
	def errorHandler(self, msg):
		print "Error:", msg
		return "alert(\"" + msg + "\");"

	def jsonpWrap(self, data, callback):
		if callback == None:
			return json.dumps(data)
		else:
			return callback + '(' + json.dumps(data) + ')'
			
	def getUpdate(self, objType = None, objId = None, callback = None):
		try:
			if objType == None or objId == None:
				msg = "model-server.getUpdate: ObjType or ObjId not passed"
				raise khopeshpy.exceptions.JSONException(msg)
			
			conn = db.connect()

			if objType == 'UserModel':
				tmp = khopeshpy.user.Model(objId, conn)
			elif objType == 'WorldModel':
				tmp = khopeshpy.world.Model(conn)
			else:
				msg = "model-server.getUpdate: Unknown object type"
				raise khopeshpy.exceptions.JSONException(msg)

			tmp.pullData()
			
			conn.close()
			
			return self.jsonpWrap(tmp.data, callback)
		except khopeshpy.exceptions.JSONException as e:
			return self.errorHandler(e.msg)
	getUpdate.exposed = True
	
	#should return a list of all player names and their id's
	#	using this to build the prototype chat
	def getPlayerList(self, callback = None):
		c = db.userData.columns
		statment = db.select([c.userId,c.username], 1)

		conn = db.connect()
		result = conn.execute(statment)
		rows = result.fetchall()
		result.close()
		conn.close()
		
		ret = {}
		for row in rows:
			ret[row.userId] = row.userName
			
		return self.jsonpWrap(ret, callback)
	getPlayerList.exposed = True
	
	def pullWorldData(self, worldId = None, callback = None):
		conn = db.connect()
		
		tmp = khopeshpy.world.Model(conn)
		tmp.pullData()
		
		conn.close()
	
		return self.jsonpWrap(tmp.data, callback)
	pullWorldData.exposed = True
			
	def error(self):
		raise cherrypy.HTTPError(400, "Some generic error...")
	error.exposed = True
	
	#called when the client can't find an image it wants
	def getImage(self, zoom = None, x = None, y = None, z = None, callback = None):
		try:
			#can't do anything if they don't send the full address
			if zoom == None or x == None or y == None or z == None:
				msg = "model-server.getImage: Need full parameters"
				raise khopeshpy.exceptions.JSONException(msg)
				
			#first check that there really isn't an image
			imageName = "img-world/zoom%d-%dx-%dy-%dz.png" % (int(zoom), int(x), int(y), int(z))
			if os.path.isfile(imageName):
				#file already exists, either it was created by another handler or somebody's mucking around
				#just return the image name
				return self.jsonpWrap(imageName, callback)
			
			conn = db.connect()
			
			#otherwise we have to pull it from the database
			if int(zoom) == 0:
				c = db.levelData.columns
				statment = db.select([c.baseImage], (c.cellIdX == int(x)) & (c.cellIdY == int(y)) & (c.levelIdZ == int(z)))
				
				result = conn.execute(statment)
				level = result.fetchone()
				result.close()
				
				if level == None:
					ret = 'img-src/void.png'
				else:
					ret = level['baseImage']
			elif int(zoom) == 1:
				c = db.cellData.columns
				statment = db.select([c.cellImage], (c.cellIdX == int(x)) & (c.cellIdY == int(y)))
				
				result = conn.execute(statment)
				cell = result.fetchone()
				result.close()
				
				if cell == None:
					ret = 'img-src/void.png'
				else:
					ret = cell['cellImage']
			else:
				#note: all zoomed images above level 1 should have been pregenerated
				ret = 'img-src/void.png'
				
			conn.close()
					
			return self.jsonpWrap(ret, callback)
		except khopeshpy.exceptions.JSONException as e:
			return self.errorHandler(e.msg)
	getImage.exposed = True

#cherrypy.config.update({'server.socket_host': '192.168.1.2'})		
cherrypy.config.update({'server.socket_host': khopeshpy.config.get('server', 'host')})
#cherrypy.config.update({'server.socket_port': 8095})
cherrypy.config.update({'server.socket_port': khopeshpy.config.getint('server', 'modelPort')})
cherrypy.quickstart(Main(),  config="cherryConfig.ini")
