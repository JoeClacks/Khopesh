# -*- coding: utf-8 -*-
import Image
import cherrypy
import threading
import json
#import db
#import config


a = 4;

b = 1;

c = 4.23;

d = 0.21;

r = min(a,b,c,d)


print r

#desertImage = Image.open('img-src/desert.png')
#hillsImage = Image.open('img-src/hills.png')
#oceanImage = Image.open('img-src/ocean.png')
##im = Image.open('test.png')

#xSize, ySize = desertImage.size

#newImage = Image.new('RGB', (xSize*2, ySize*2))

#newImage.paste(desertImage, (0,0))
#newImage.paste(hillsImage,(xSize,0))
#newImage.paste(oceanImage,(0, ySize))
#newImage.paste((0,0,0), (xSize,ySize,xSize*2, ySize*2))

#newImage.thumbnail((xSize,ySize))
#newImage.save('test.png')


#class TestClass:
	#b = 13
	
	#def __init__(self, data):
		#self.c = 25
		#self.b = 42
		##self.__dict__  = data
		##self.__dict__.update(data)
		#TestClass.__dict__.update(data)
		
		#pass



#test2 = TestClass({'a' : 52})

##print test.a
#print test2.b
#print repr(test2.__dict__)
#print repr(TestClass.__dict__)

#desertImage = Image.open('img-src/desert.png')
#cityImage = Image.open('img-src/city1.png')


#desertImage.paste(cityImage, (0,0), cityImage.convert('RGBA').split()[3])

#desertImage.save('test.png')




#class UserData:
	#userId = 0
	#userName = 'blarg'

	#userX = 0
	#userY = 0
	#userZ = 0

	#def __init__(self, tmp):
		#self.userName = tmp
		
	#def json(self):
		#ret = {'userId': self.userId,
			#'userName': self.userName,
			#'userX': self.userX,
			#'userY': self.userY,
			#'userZ': self.userZ}
		#return ret
    
	#def loggedin(self):
		#return True
    
#class Main:
	#def init(self):
		#cherrypy.session['fieldname'] = {}
		
	#def set_session(self):
		##cherrypy.session['fieldname'] = {'one': 2, 'two': 3}
		#tmp = UserData('tooder')
		#cherrypy.session['fieldname'] = tmp
		#print repr(tmp.json())
		#print repr(cherrypy.session['fieldname'].json())
		
		#print 'ok'
		#return 'ok'
	#set_session.exposed = True
	
	#def set_session2(self):
		##cherrypy.session['fieldname'].userId += 1
		#userDatas[1].userId += 1
		
	#set_session2.exposed = True
	
	#def get_session(self):
		##if cherrypy.session.get('fieldname') == None:
			##self.init()
			
		##print repr(cherrypy.session['fieldname'].json())
		##print repr(userDatas[1].userId)
		##print "Count:", threading.activeCount()
		#val = cherrypy.session.get('fieldname')
		#print repr(val)
		#return repr(val)
	#get_session.exposed = True
	
	#def login(self):
		#cherrypy.session['player'] = UserData()
	#login.exposed = True
		
	#def isLoggedIn(self):
		#player = cherrypy.session.get('player')
		#print repr(player)
		#if player == None:
			#print 'Not logged in'
		#else:
			#print repr(player.loggedin())
	#isLoggedIn.exposed = True
	
	

#cherrypy.quickstart(Main(),  config="cherryConfig.ini")





#class UserData:
	#def __init__(self, userName = None, password = None, userId = None):
		#self.userName = userName
		#self.password = password
		#self.userId = userId
	
	#def pullFromDb(self):
		#c = db.userData.columns
		###statment = db.select([c.userName, c.userX, c.userY, c.userZ], c.userId == self.userId)
		#statment = db.select([db.userData], c.userId == self.userId)
		
		#conn = db.connect()
		#result = conn.execute(statment)
		#row = result.fetchone()
		#result.close()
		#conn.close()


		#if row == None:
			#self.valid = False
			#msg = "Did not find userData record for id:",self.userId,", exiting."
			#print msg
			##raise cherrypy.HTTPError(400, msg)
		
		#self.__data__.update(dict(row))
		#self.valid = True
		
	##def loggedin(self):
		##return data['valid']



#user = UserData(userName = 'joe')

#conn = db.connect()
#ins = db.familyData.insert().values(famliyName = 'familyOne', familyAlive = True)
#result = conn.execute(ins)
#ins = db.familyData.insert().values(famliyName = 'familyTwo', familyAlive = False)
#result = conn.execute(ins)
#conn.close()

#c = db.avatarData.columns
#statment = db.select([db.avatarData], c.familyId == 1)

#conn = db.connect()
#result = conn.execute(statment)
#rows = result.fetchall()
#result.close()
#conn.close()

#for k in rows:
	#print repr(k)
	
#print "Result:", repr(dict(row[0]))
#if len(row) == 0:
	#print "True"
#else:
	#print "False"

#print repr(user)
#print repr(user.__dict__)
#print repr(user.userId)
#print repr(user.__class__)
##print repr(user.getUserid())