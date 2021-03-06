#!/usr/bin/python2.6
import cherrypy
import json

import khopeshpy

from khopeshpy import db
import khopeshpy.user
import khopeshpy.family
import khopeshpy.config
import khopeshpy.avatars


#just to get pylint to stop complaining
#if not hasattr(cherrypy, 'session'):
    #cherrypy.session = dict()
    

class Main:
    #we'll handle any logging here
    # return what we want eventually returned to the client
    def errorHandler(self, msg):
        print "Error:", msg
        return "alert(\"" + msg + "\");"
        
    def jsonpWrap(self, data, callback):
        if callback == None:
            return json.dumps(data)
        else:
            return callback + '(' + json.dumps(data) + ')'
            
    #sets up the class player variable, if there isn't a logged in player then
    def checkUser(self):
        user = cherrypy.session.get('user') #@UndefinedVariable
        
        if user == None or user.valid != True or user.loggedIn != True:
            msg = 'function needs to have a logged in user'
            raise Exception(msg)
        
        return user
        
    def checkFamily(self):
        family = cherrypy.session.get('family') #@UndefinedVariable
        
        if family == None or family.valid != True:
            msg = 'function needs to have a valid family'
            raise Exception(msg)
        
        return family
        
    def checkAvatars(self):
        avatars = cherrypy.session.get('avatars') #@UndefinedVariable
        
        #not checking for valid, it's redundant right now though 
        if avatars == None:
            msg = 'function needs to have existing avatars'
            raise Exception(msg)
        
        return avatars
        
    #catch any wayward requests and let the user know
    def default(self, *vpath, **params):
        msg = 'no match for: ' + repr(vpath) + ': (' + repr(params) + ')'
        return self.errorHandler(msg)
    default.exposed = True

    #if the player is not logged in the return -1, otherwise return the players userId
    def tryLogin(self, callback = None, _ = None):
        player = cherrypy.session.get('player') #@UndefinedVariable
        
        #NOTE: not using checkPlayer because that would mean we're using exceptions
        # almost all the time
        if player == None or player.valid != True or player.loggedIn != True:
            ret = -1
            print "Player not logged in, sending back userId:", ret
        else:
            ret = player.userId
            print "Player logged in, sending back userId:", ret
        return self.jsonpWrap(ret, callback)
    tryLogin.exposed = True
        
    def doLogin(self, username = None, password = None, callback = None, _ = None):
        user = khopeshpy.user.Control()

        userId, msg = user.login(username, password)
        if userId > 0:
            ret = (userId, msg)
            
            
            
            
            #setting up the family and avatar data here
            conn = khopeshpy.db.connect()
            family = khopeshpy.family.Control(userId = userId)
            
            avatars = khopeshpy.avatars.getControlAvatars(conn, family.familyId)
            conn.close()
        else:
            #TODO: should wipe everything else also
            user = None
            family = None
            avatars = None
            ret = (-1, msg)
        
        print 'setting the session var'
        cherrypy.session['user'] = user #@UndefinedVariable
        cherrypy.session['family'] = family #@UndefinedVariable
        cherrypy.session['avatars'] = avatars #@UndefinedVariable
        
        return self.jsonpWrap(ret, callback)
    doLogin.exposed = True        
    
    def doRegister(self, username = None, password = None, callback = None, _ = None):            
        user = khopeshpy.user.Control()
        
        userId, msg = user.register(username, password)
        if userId > 0:
            ret = (userId, msg)
        else:
            #TODO: should wipe everything else also
            user = None
            ret = (-1, msg)
            
        print 'setting the session var'
        cherrypy.session['user'] = user #@UndefinedVariable
        
        print "Sending userId:", ret
        return self.jsonpWrap(ret, callback)
    doRegister.exposed = True
    
    #don't need a userId because we can assume that players will get data about
    #    users other than themselves through the model interface
    def pullUserData(self, callback = None, _ = None):
        try:        
            user = self.checkUser()
            return self.jsonpWrap(user.data, callback)
        except Exception as inst:
            return self.errorHandler('pullUserData: '+str(inst))
    pullUserData.exposed = True
    
    def pullFamilyData(self, callback = None, _ = None):
        try:
            family = self.checkFamily()
            return self.jsonpWrap(family.data, callback)
        except Exception as inst:
            return self.errorHandler('pullFamilyData: '+str(inst))
    pullFamilyData.exposed = True
            
    #if an avatarId is passed then return only that avatar, otherwise return 
    #    all avatars for that player
    def pullAvatarData(self, avatarId = None, callback = None, _ = None):
        try:
            avatars = self.checkAvatars()
            
            if avatarId != None:
                avatarId = int(avatarId)
                
                if avatarId not in avatars:
                    ret = (-1, 'invalid avatarId: %s' % (str(avatarId)))
                else:
                    avatar = avatars[avatarId]
                    ret = (avatar, "Ok")
            else:                
                avatarList = {}
                for avatarId in avatars:
                    avatarList[avatarId] = avatars[avatarId].data
                
                ret = (avatarList, "Ok")
        except Exception as inst:
            ret = (-1, str(inst))
            
        return self.jsonpWrap(ret, callback)
    pullAvatarData.exposed = True
    
    #returns false if there is no current family, otherwise the currently valid family id
    def loadFamilyData(self, callback = None, _ = None):
        try:
            user = self.checkUser()
            
            family = khopeshpy.family.Control(userId = user.userId)
            
            #save it to the session
            cherrypy.session['family'] = family #@UndefinedVariable
            
            ret = (family.familyId, "Ok")
        except Exception as inst:
            #failure case
            ret = (-1, str(inst))

        
        print "getFamilyData is returning:", repr(ret)
        return self.jsonpWrap(ret, callback)
    loadFamilyData.exposed = True
            

    
    #the family/avatar relationship is interesting, in production we shouln't 
    #    have one without the other, but are there any edge cases?
    #
    #use case: new user
    #    create family and progenitor avatar
    #use case: normal operation
    #    family exists and has more than one avatar
    #use case: all avatars dead
    #    family line is ended. start new family and progenitor with boosts
    #
    #we'll only consider the first and second cases for now, worry about the last
    #    later
    
    
    
    #assuming new user, therefore creates the family and an avatar
    #returns false on failure, otherwise the familyId and message
    def createFamily(self, familyName = None, avatarName = None, callback = None, _ = None):
        if familyName == None or avatarName == None:
            msg = 'createFamily needs for familyName and avatarName to be passed'
            return self.errorHandler(msg)
        try:
            player = self.checkUser()
            
            conn = khopeshpy.db.connect()
            
            familyId, msg = khopeshpy.family.createNew(conn, player.userId, familyName, avatarName)
            
            if familyId == -1:
                ret = (-1, msg)
            else:
                family = khopeshpy.family.Control(conn, userId = player.userId)
                
                ret = (family.familyId, "Ok")
                
                cherrypy.session['family'] = family #@UndefinedVariable
            
            conn.close()
        except Exception as inst:
            #failure case
            ret = (-1, str(inst))
        
        return self.jsonpWrap(ret, callback)
    createFamily.exposed = True
    
    
    #returns false if there is no current avatars, a list of all avatarId's
    def loadAvatarData(self, callback = None, _ = None):
        try:
            family = self.checkFamily()
    
            conn = khopeshpy.db.connect()

            avatars = khopeshpy.avatars.getControlAvatars(conn, family.familyId)
            
            if(len(avatars) <= 0):
                ret = (-1, "No avatars found")
            else:
                #save it to the session
                cherrypy.session['avatars'] = avatars #@UndefinedVariable
            
                ret = (avatars.keys(), "Ok")
        except Exception as inst:
            #failure case
            ret = (-1, str(inst))

            conn.close()
        
        print "loadAvatarData is returning:", repr(ret)
        return self.jsonpWrap(ret, callback)
    loadAvatarData.exposed = True
    
    
    def error(self):
        raise cherrypy.HTTPError(400, "A generic error...")
    error.exposed = True
    
    def test(self, callback = None, _ = None):
      return self.jsonpWrap("working", callback)
    test.exposed = True
    
    def sendChat(self, to = None, msg = None, callback = None, _ = None):
        if to == None or msg == None:
            msg = 'sendMessage needs a reciepent and a message'
            print msg
            raise cherrypy.HTTPError(400, msg)
        
        #doesn't look like we'll need to modifiy the player, later on we can release
        # the session lock here
        player = self.checkUser()
        
        #TODO: we may want some sort of sanity check to see if the recepiant exists
        # and typechecking
        
        #first see if there is an active conversation
        conv = khopeshpy.db.convData.columns
        statment = khopeshpy.db.select([conv.convId], 
            ((conv.userAId == player.userId) & (conv.userBId == to) |
            (conv.userAId == to) & (conv.userBId == player.userId)))
        
        conn = khopeshpy.db.connect()
        result = conn.execute(statment)
        row = result.fetchone()
        result.close()
        conn.close()
        
        convId = None
        if row != None:
            convId = row['convId']
        else:
            #if not then create one
            conn = khopeshpy.db.connect()
            ins = khopeshpy.db.convData.insert().values(userAId = player.userId, userBId = to, active = True)
            result = conn.execute(ins)
            conn.close()
            
            convId = result.last_inserted_ids()[0]
        
        #and add the message to the conversation
        conn = khopeshpy.db.connect()
        ins = khopeshpy.db.convMsg.insert().values(convId = convId, userId = player.userId, text = msg)
        result = conn.execute(ins)
        conn.close()
        return self.jsonpWrap(True, callback)
    sendChat.exposed = True
    
    def pullChat(self, to = None, callback = None, _ = None):
        if to == None:
            msg = 'pullChat needs an id for the other member of the chat'
            print msg
            raise cherrypy.HTTPError(400, msg)
            
        player = self.checkUser()
            
        #first see if there is an active conversation
        conv = khopeshpy.db.convData.columns
        statment = khopeshpy.db.select([conv.convId], 
            ((conv.userAId == player.userId) & (conv.userBId == to) |
            (conv.userAId == to) & (conv.userBId == player.userId)))
        
        conn = khopeshpy.db.connect()
        result = conn.execute(statment)
        row = result.fetchone()
        result.close()
        conn.close()
        
        convId = None
        if row == None:
            #return nothing
            ret = None
        else:
            convId = row['convId']
            
            c = khopeshpy.db.convMsg.columns
            statment = khopeshpy.db.select([khopeshpy.db.convMsg], (c.convId == convId))
            
            conn = khopeshpy.db.connect()
            result = conn.execute(statment)
            rows = result.fetchall()
            result.close()
            conn.close()
        
            ret = []
            for row in rows:
                ret.append({'msg': row['text'], 'time': row['timestamp'].isoformat()})
                
            print 'Ret: ', repr(ret)
        return self.jsonpWrap(ret, callback)
    pullChat.exposed = True    

#cherrypy.config.update({'server.socket_host': '192.168.1.2'})
cherrypy.config.update({'server.socket_host': khopeshpy.config.get('server', 'host')})
#cherrypy.config.update({'server.socket_port': 8090})
cherrypy.config.update({'server.socket_port': khopeshpy.config.getint('server', 'controlPort')})
cherrypy.quickstart(Main(),  config="cherryConfig.ini")
