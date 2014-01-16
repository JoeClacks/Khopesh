#!/usr/bin/python2.6
import json
import time
import sqlalchemy
import cProfile
import sys

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
		
	def pollCellUpdates(self):
		trans = self.conn.begin()
		try:
			c = db.cellData.columns
			statement = db.select([db.cellData],\
				(c.lastUpdated < int(time.time() - khopeshpy.config.worldTick))).limit(100)
			result = self.conn.execute(statement)
			rows = result.fetchall()
			result.close()
			
			if len(rows) == 0:
				trans.rollback()
				return False
			
			ids = []
			for row in rows:
				ids.append(row['cellId'])
				
			c = db.cellData.columns
			up = db.cellData.update().where(c.cellId.in_(ids)).values(lastUpdated = time.time())
			self.conn.execute(up)
				
			trans.commit()
				
			for row in rows:
				r = dict(row)
				cell = khopeshpy.cell.Update(data = row, conn = self.conn)
				cell.updateLevels()
				
			return True
		except:
			trans.rollback()
			raise
		
	def pollImageUpdates(self):
		trans = self.conn.begin()
		try:
			c = db.levelData.columns
			statement = db.select([db.levelData], c.dirtyImage == True).limit(100)
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
		
	def pollCellIdle(self):
		trans = self.conn.begin()
		try:
			c = db.cellData.columns
			statement = db.select([db.cellData],\
					(c.lastUpdated == None) & (c.cellGroundlevel > khopeshpy.config.worldSeaLevel))\
				.limit(1)
			result = self.conn.execute(statement)
			row = result.fetchone()
			result.close()
		
			if row == None:
				trans.rollback()
				return False
			else:
				row = dict(row)
				c = db.cellData.columns
				up = db.cellData.update().where(c.cellId == row['cellId']).values(lastUpdated = time.time())
				self.conn.execute(up)
				trans.commit()
				
				cell = khopeshpy.cell.Update(data = row, conn = self.conn)
				cell.addIdleCell()
				
				return True
		except:
			trans.rollback()
			raise
			
	def spin(self):
		if self.pollCellUpdates() != False:
			return "got cell update"
			
		if self.pollImageUpdates() != False:
			return "got image update"
			
		print 'sleeping...'
		time.sleep(10)
		return "slept"

if __name__=='__main__':
	main = Main()
	
	if len(sys.argv) == 1:
		while 1:
			print main.spin()
			print time.time()
			
	elif len(sys.argv) == 2 and sys.argv[1] == "idle":
		main.pollCellIdle()
		
	#cProfile.run('helper(main)', 'run1')