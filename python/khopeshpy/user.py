#!/usr/bin/python2.6
import khopeshpy.db as db
import khopeshpy.exceptions as exceptions

class User(object):
    userId = 0
    valid = False

    data = {}

    def pullData(self):
        if self.userId <= 0:
            msg = "pullData needs a userId greater than 0, id was: %d" % (self.userId)
            raise Exception(msg)
        
        c = db.userData.columns
        statment = db.select([db.userData], c.userId == self.userId)
        
        conn = db.connect()
        result = conn.execute(statment)
        row = result.fetchone()
        result.close()
        conn.close()

        if row == None:
            msg = "pullData did not find userData record for id: %d" % (self.userId)
            raise Exception(msg)
        
        self.data.update(dict(row))
        self.valid = True
            
class Model(User):
    def __init__(self, userId, conn):
        self.userId = int(userId)
        self.conn = conn
        
        self.data = {}
        
    def pullData(self):
        c = db.userData.columns
        statment = db.select([db.userData], c.userId == self.userId)
        
        result = self.conn.execute(statment)
        row = result.fetchone()
        result.close()

        if row == None:
            msg = "user.Model.pullData: Did not find userData record for id: %d, exiting." % (self.userId)
            raise exceptions.JSONException(msg)
        
        self.data.update(dict(row))
    
class Control(User):
    loggedIn = False
    
    def login(self, username = None, password = None):
        if username == None or password == None:
            msg = "user.Control.login needs both a username and a password"
            print msg
            return (-1, msg)
            
        c = db.userData.columns
        statment = db.select([db.userData], (c.username == username) & (c.password == password))
        
        conn = db.connect()
        result = conn.execute(statment)
        row = result.fetchone()
        result.close()
        conn.close()

        if row == None:
            self.loggedIn = False
            msg = "User failed to login with username: %s password: %s" % (username, password)
            print msg
            return (-1, msg)
        else:
            self.loggedIn = True
            self.userId = row['userId']
            self.pullData()
            return (self.userId, 'Ok')
            
        #may want to return to this later but right now it's better to use pullData
        #self.data.update(dict(row))
        #self.valid = True
        #self.userId = self.data['userId']
        
        
    def register(self, username = None, password = None):
        if username == None or password == None:
            msg = "User.Control.register needs both a username and a password"
            print msg
            return (-1,msg)
        
        #first we have to check if a user with that name already exists
        c = db.userData.columns
        statment = db.select([db.userData], (c.username == username))
        
        conn = db.connect()
        result = conn.execute(statment)
        row = result.fetchone()
        result.close()
        conn.close()
        
        if row != None:
            self.valid = False
            self.loggedIn = False
            msg = "Player with username: %s already exists" % (username)
            print msg
            return (-1, msg)
        else:
            conn = db.connect()
            ins = db.userData.insert().values(username = username, password = password)
            result = conn.execute(ins)            
            conn.close()
            
            #cheap way for now
            return self.login(username, password)