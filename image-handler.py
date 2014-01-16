import cherrypy
from cherrypy.lib.static import serve_file

import os.path
import json
import sys

#our files
import db

worldData = {}
userData = None

worldId = 1

current_dir = os.path.dirname(os.path.abspath(__file__))
voidImagePath = os.path.join(current_dir, 'img-src', 'void.png')


class Main:
	def index(self):
		out = ""
	
		out += "Hello world!<br>"
		
		out += sys.version + "<br>"
		
		out += json.dumps(['foo', {'var': ('baz', None, 1.0, 2)}])
		
		return out
	index.exposed = True

	def worldmap(self, x = None, y = None, z = None):
		if x == None or y == None or z == None:
			return serve_file(voidImagePath, 'image/png')

		c = db.levelData.columns
		row = db.selectOne([c.userId, c.userName, c.userX, c.userY, c.userZ], c.userId == userId)		
		
	worldmap.exposed = True

if __name__=='__main__':
	cherrypy.config.update({'environment': 'production',
													'log.screen': False,})

	cherrypy.quickstart(Main())