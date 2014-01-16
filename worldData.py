# -*- coding: utf-8 -*-
import Image 
import sys

import db
import cellData


#we'll load these values from config files later
worldId = 1
#heightmap = 'heightmaps/earth-216x108x255.png'
heightmap = 'heightmaps/earth-432x216x255.png'
sealevel = 128
wrapX = True
wrapY = False

class WorldData:
	worldId = 0
	lengthX = 0
	lengthY = 0

	wrapX = True
	wrapY = True  

	sealevel = 0

	cells = {}

	def __init__(self, worldId):
		self.worldId = worldId
		self.cells = {}
		
	def loadFromDb(self, conn):
		c = db.worldData.columns

		statement = db.select([c.worldSizeX, c.worldSizeY, c.worldWrapX, c.worldWrapY, c.worldSeaLevel], c.worldId == worldId)
		
		result = conn.execute(statement)
		row = result.fetchone()
		result.close()
		
		if row == None:
			print "Did not find worldData record, exiting."
			raise

		self.lengthX = row["worldSizeX"]
		self.lengthY = row["worldSizeY"]
		
		self.wrapX = row["worldWrapX"]
		self.wrapY = row["worldWrapY"]
		
		self.sealevel = row["worldSeaLevel"]
		
		print "World object loaded from database."

	def regenHeightMap(self, conn):
		#load from globals
		self.wrapX = wrapX
		self.wrapY = wrapY
		self.sealevel = sealevel
    
		im = Image.open(heightmap)

		self.lengthX, self.lengthY = im.size
		
		c = db.worldData.columns
		ins = db.worldData.insert().values(worldId = self.worldId, worldSeaLevel = self.sealevel, worldSizeX = self.lengthX, worldSizeY = self.lengthY, worldWrapX = self.wrapX, worldWrapY = self.wrapY)
		conn.execute(ins)
		
		self.cells = {}
		for x in xrange(self.lengthX):
			print x,
			sys.stdout.flush()
			
			for y in xrange(self.lengthY):
				#we're building this assuming use of grayscale images (which have a range of 0 to 255)
				# don't know if adjustment will be needed if we try to feed it a 16 bit image
				
				height = im.getpixel((x,y))
        
				cell = cellData.CellData(worldId, x, y)
				cell.regenHeightMap(conn, height, sealevel)
				self.cells[(x,y)] = cell

	def zoomLevels(self, conn):
		#first stage, zoom1 is calculated for each cell, but condenses the levels
		print "Stage 1"
		for x in xrange(self.lengthX):
			print x,
			sys.stdout.flush()
			
			for y in xrange(self.lengthY):
				if (x,y) not in self.cells:
					cell = cellData.CellData(worldId, x, y)
					cell.loadFromDb(conn)
					self.cells[(x,y)] = cell
					
				#compress all the levels to one image, this will server as zoom level 1
				self.cells[(x,y)].compressLevels(conn)
				
		print "Finished stage 1"
		
		#after the first stage:
		zoom = 2
		nCells = 2 ** (zoom -1)
		while nCells < self.lengthX and nCells < self.lengthY:
			print "Stage:", zoom, "Number of base images per new image:", nCells
			for x in xrange(self.lengthX/nCells+1):
				print x,
				sys.stdout.flush()
				
				for y in xrange(self.lengthY/nCells+1):
					try:
						self.cells[(x*nCells,y*nCells)].zoomLevel(zoom)
					except:
						pass
			
			print "Finished stage", zoom
			zoom = zoom + 1
			nCells = 2 ** (zoom -1)
			
	def genSurface(self, conn):
		for x in xrange(self.lengthX):
			print x,
			sys.stdout.flush()
			
			for y in xrange(self.lengthY):
				if (x,y) not in self.cells:
					cell = cellData.CellData(worldId, x, y)
					cell.loadFromDb(conn)
					self.cells[(x,y)] = cell
					
				self.cells[(x,y)].genSurface(conn, self.sealevel, self.lengthY)
