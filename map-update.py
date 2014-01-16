#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
import random
import sys
import time
import sqlalchemy
import sqlalchemy.exc


import db
import levelData
import cellData
import worldData

#we'll load these values from config files later
worldId = 1


#currently we'll only be running this without threads so we can store the database
#	connectin in a global variable
conn = None
	
def update():	
	i = 1
	while(i==1):
		i +=1
		trans = conn.begin()
		
		try:
			#query database for a dirty level
			c = db.levelData.columns
			statement = db.select([c.worldId, c.cellIdX, c.cellIdY, c.levelIdZ],(c.dirtyImage == True)).limit(1)
			
			result = conn.execute(statement)
			row = result.fetchone()
			result.close()
		
			if row == None:
				#we didn't find anything that needed updating
				trans.rollback()
				
				#sleep
				time.sleep(30)
				#loop
			else:
				#get all layers for that cell
				c = db.levelData.columns
				statement = db.select([c.worldId, c.cellIdX, c.cellIdY, c.levelIdZ,
					c.water, c.air, c.rock, 
					c.artic, c.swamp, c.hills, c.mountains, c.jungle, c.plains, c.grassland, c.forest,
					c.baseImage, c.dirtyImage, c.cityId],(c.worldId == row['worldId']) &
					(c.cellIdX == row['cellIdX']) & (c.cellIdY == row['cellIdY']))
				
				result = conn.execute(statement)
				rows = result.fetchall()
				result.close()
				
			
				#update the image for each of the layers that needs it
				levels = {}
				for row in rows:
					print dict(row)
					level = levelData.LevelData(rowData = dict(row))
					if row['dirtyImage'] == True:
						level.updateImage(conn)
						
					levels[row['levelIdZ']] = level
						
				##we can commit the changes to the database here
				trans.commit()
				
						
				cell = cellData.CellData(row['worldId'], row['cellIdX'], row['cellIdY'], levels)
				##check if the surface image has changed
				changed = cell.compressLevels(conn)
				
				print 'changed:', changed
				
				worldObj = worldData.WorldData(worldId)
				worldObj.loadFromDb(conn)
				
				#if so then update all the zoom images until we reach a level that isn't affected
				zoom = 2
				nCells = 2 ** (zoom -1)
				while nCells < worldObj.lengthX and nCells < worldObj.lengthY and changed:
					print "Stage:", zoom, "Number of base images per new image:", nCells
					
					print 'x,y:', row['cellIdX'], row['cellIdY']
					x = row['cellIdX'] - (row['cellIdX'] % nCells)
					y = row['cellIdY'] - (row['cellIdY'] % nCells)
					
					print 'x,y:', x, y
					
					cell = cellData.CellData(row['worldId'], x, y)
					
					changed = cell.zoomLevel(zoom)
		
					zoom = zoom + 1
					nCells = 2 ** (zoom -1)
					
				trans.rollback()
		except sqlalchemy.exc.SQLAlchemyError, exc:
			trans.rollback()
			print 'Could not commit changes to database'
			print 'Error:', exc
			
	conn.close()

if __name__=='__main__':
	conn = db.connect()
	random.seed()

	if (len(sys.argv) == 2 and sys.argv[1] == "update") or len(sys.argv) == 2:
		##update the tiles to reflect changes in the database
		#worldObj = worldData(worldId)
		#cProfile.run('worldObj = worldData(worldId)')
		#worldObj.drawTiles()
		update()
	else:
		print "usage:"
		print "map-update.py update"
		
	conn.close()
    
