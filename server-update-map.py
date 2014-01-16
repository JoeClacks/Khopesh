#!/usr/bin/python2.6
import json
import time
import sqlalchemy
import cProfile

import db
import khopeshpy.world
import khopeshpy.cell
import khopeshpy.config

class Main:
	conn = None
	
	world = None
	
	def __init__(self):
		self.conn = db.connect()
		
		self.world = khopeshpy.world.Update(conn = self.conn)
		self.world.pullData()
		
	def pollImageUpdates(self):
		trans = self.conn.begin()
		try:
			c = db.levelData.columns
			statement = db.select([db.levelData], c.dirtyImage == True).limit(1)
			result = self.conn.execute(statement)
			rows = result.fetchall()
			result.close()
			
			if len(rows) == 0:
				trans.rollback()
				return False
			
			for row in rows:
				#update the entire column at once
				r = dict(row)
				c = db.levelData.columns
				up = db.levelData.update().where((c.cellIdX == r['cellIdX']) & (c.cellIdY == r['cellIdY'])).\
					values(dirtyImage = False)
				self.conn.execute(up)
				
			trans.commit()
				
			for row in rows:
				r = dict(row)
				cell = khopeshpy.cell.Update(position = (row['cellIdX'], row['cellIdY']), conn = self.conn)
				cell.updateMap(self.world.data['worldSizeX'], self.world.data['worldSizeY'])
				
			return True
		except:
			trans.rollback()
			raise
			
	def spin(self):
		if self.pollImageUpdates() != False:
			return "got event"
			
		print 'sleeping...'
		time.sleep(10)
		return "slept"


def helper(main):
	while 1:
		print main.spin()
		print time.time()

if __name__=='__main__':
	main = Main()
	
	helper(main)
	#cProfile.run('helper(main)', 'run1')