#!/usr/bin/python2.6
import json
import time
import sqlalchemy
import cProfile

import db
import khopeshpy.cell
import khopeshpy.config

class Main:
	conn = None
	
	def __init__(self):
		self.conn = db.connect()
		
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
			
			for row in rows:
				r = dict(row)
				c = db.cellData.columns
				up = db.cellData.update().where(c.cellId == r['cellId']).values(lastUpdated = time.time())
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
			return "got event"
			
		#if self.pollCellIdle() != False:
		#	return "found idle"
			
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
	
	
