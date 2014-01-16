#!/usr/bin/python2.6
import json
import datetime
import time

from khopeshpy import db
import khopeshpy.user
import khopeshpy.family
from khopeshpy import avatars

worldId = 1

class Main:
	conn = None
	
	def __init__(self):
		self.conn = db.connect()
		
	def processEvent(self, row):
		avatars.processEvent(self.conn, row)
		
	def idle(self, row):
		avatars.processIdle(self.conn, row)
		
	def brokenAvatar(self, row):
		self.idle(row)
		
	def pollEventQueue(self):
		trans = self.conn.begin()
		try:
			c1 = db.avatarEventQueue.columns
			c2 = db.avatarCmdQueue.columns
			#find a event that has ended in the eventQueue
			statement = db.select([c1.eventId, c2.avatarCmdId, c2.avatarId, c2.timeExpected, c2.timeStarted, c2.command, c2.data],\
				(c1.eventEnd < time.time()) & (c1.eventId == c2.eventId)).limit(1)
			
			result = self.conn.execute(statement)
			rows = result.fetchall()
			result.close()
			
			good = False
			for row in rows:
				
				c = db.avatarEventQueue.columns
				#remove the event from the queue
				up = db.avatarEventQueue.delete().where(c.eventId == (row['eventId']))
				result = self.conn.execute(up)
				
				#make sure we were able to delete the row
				if result.rowcount == 1:
					#only if we've managed to grab an event
					self.processEvent(row)
					good = True
					
			trans.commit()
			return good
		except Exception as e:
			print e
			print "rolling back"
			trans.rollback()
			raise
			#return false
		
	def pollIdleAvatars(self):
		c = db.avatarData.columns
		statement = db.select([db.avatarData], c.eventId == None).limit(1)
		result = self.conn.execute(statement)
		row = result.fetchone()
		result.close()
		
		if row == None:
			return False
			
		else:
			row = dict(row)
			self.idle(row)
			
			return True
				
	def pollBrokenAvatars(self):
		c = db.avatarData.columns
		d = db.avatarEventQueue.columns
		statement = db.select([db.avatarData], c.eventId != db.select([d.eventId],d.eventId == d.eventId)).limit(1)
		result = self.conn.execute(statement)
		row = result.fetchone()
		result.close()
		
		if row == None:
			return False
			
		else:
			row = dict(row)
			self.brokenAvatar(row)
			
			return True
		
	def spin(self):
		if self.pollEventQueue() != False:
			return "got event"
			
		if self.pollIdleAvatars() != False:
			return "found idle avatar"
			
		if self.pollBrokenAvatars() != False:
			return "found a broken avatar"
			
		time.sleep(1)	
		return "slept"

if __name__=='__main__':
	main = Main()
	
	while 1:
		print main.spin()
		raw_input('>')
	
