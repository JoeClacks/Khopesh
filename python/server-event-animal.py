#!/usr/bin/python2.6
import json
import time
import cProfile

from khopeshpy import db
from khopeshpy import animals





class Main:
	conn = None
	
	def __init__(self):
		self.conn = db.connect()
		
	def processEvent(self, row):
		animals.processEvent(self.conn, row)
		
	def idle(self, row):
		animals.processIdle(self.conn, row)

	def broken(self, row):
		self.idle(row)

	def pollEventQueueMany(self):
		trans = self.conn.begin()
		try:
			c1 = db.animalEventQueue.columns
			c2 = db.animalCmdQueue.columns
			#find a event that has ended in the eventQueue
			statement = db.select([c1.eventId, c2.animalCmdId, c2.animalId, c2.timeExpected, c2.timeStarted, c2.command, c2.data],\
				(c1.eventEnd < time.time()) & (c1.eventId == c2.eventId)).limit(100)

			result = self.conn.execute(statement)
			rows = result.fetchall()
			result.close()

			good = False
			for row in rows:
				row = dict(row)
				
				c = db.animalEventQueue.columns
				#remove the event from the queue
				up = db.animalEventQueue.delete().where(c.eventId == (row['eventId']))
				result = self.conn.execute(up)
			
				#makes sure we were able to delete the row
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
		
	def pollEventQueue(self):
		trans = self.conn.begin()
		try:
			c1 = db.animalEventQueue.columns
			c2 = db.animalCmdQueue.columns
			#find a event that has ended in the eventQueue
			statement = db.select([c1.eventId, c2.animalCmdId, c2.animalId, c2.timeExpected, c2.timeStarted, c2.command, c2.data],\
				(c1.eventEnd < time.time()) & (c1.eventId == c2.eventId)).limit(1)
			#print statement
			result = self.conn.execute(statement)
			row = result.fetchone()
			result.close()
			
			if row == None:
				trans.rollback()
				return False
			else:
				row = dict(row)
				
				c = db.animalEventQueue.columns
				#remove the event from the queue
				up = db.animalEventQueue.delete().where(c.eventId == (row['eventId']))
				result = self.conn.execute(up)
			
				#only if we've managed to grab an event
				self.processEvent(row)
					
				trans.commit()
				return True
		except Exception as e:
			print e
			print "rolling back"
			trans.rollback()
			raise
			#return False		
		
	def pollIdle(self):
		c = db.animalData.columns
		statement = db.select([db.animalData], c.eventId == None).limit(1)
		result = self.conn.execute(statement)
		row = result.fetchone()
		result.close()
		
		if row == None:
			return False
		else:
			row = dict(row)
			self.idle(row)
			
			return True
				
	def pollBroken(self):
		c = db.animalData.columns
		d = db.animalEventQueue.columns
		statement = db.select([db.animalData], db.not_(c.eventId.in_(db.select([d.eventId],None)))).limit(1)
		result = self.conn.execute(statement)
		row = result.fetchone()
		result.close()
		
		if row == None:
			return False
			
		else:
			row = dict(row)
			self.broken(row)
			
			return True
		
	def spin(self):
		if self.pollEventQueueMany() != False:
		#if self.pollEventQueue() != False:
			return "got event"
			
		if self.pollIdle() != False:
			return "found idle"
			
		if self.pollBroken() != False:
			return "found a broken"
		
		print 'sleeping...'
		time.sleep(10)
		return "slept"


def helper(main):
	while(True):
	#for x in range(100):
		print main.spin()
		print time.time()
		#main.spin()

if __name__=='__main__':
	main = Main()
	
	helper(main)
	#cProfile.run('helper(main)', 'run1' + str(time.time()))
	
	
