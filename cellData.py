# -*- coding: utf-8 -*-
import Image
import ImageChops

import db
import levelData

class CellData:
	cellIdX = 0
	cellIdY = 0
	cellGroundlevel = 0
	
	levels = None
	
	def __init__(self, worldId, cellIdX, cellIdY, levels = None):
		self.worldId = worldId
		self.cellIdX = cellIdX
		self.cellIdY = cellIdY
		self.levels = levels

		
	def loadFromDb(self, conn):
		c = db.cellData.columns
		
		statement = db.select([c.cellGroundlevel], (c.cellIdX == self.cellIdX) & (c.cellIdY == self.cellIdY) & (c.worldId == self.worldId))
		
		result = conn.execute(statement)
		row = result.fetchone()
		result.close()
		
		if row != None:
			self.cellGroundlevel = row['cellGroundlevel']
		else:
			print "Could not find cell record:", self.cellIdX, self.cellIdY

	def regenHeightMap(self, conn, groundlevel, sealevel):
		self.cellGroundlevel = groundlevel
	
		c = db.cellData.columns
		ins = db.cellData.insert().values(worldId = self.worldId, cellIdX = self.cellIdX, cellIdY = self.cellIdY, cellGroundlevel = self.cellGroundlevel)
		conn.execute(ins)
		

	def compressLevels(self, conn):
		if self.levels == None:
			#need to set the image for the hightest non-air level
			c = db.levelData.columns
			statement = db.select([c.levelIdZ, c.air, c.baseImage], (c.cellIdX == self.cellIdX) & (c.cellIdY == self.cellIdY) & (c.worldId == self.worldId))
			
			result = conn.execute(statement)
			rows = result.fetchall()
			result.close()
	
			oldImageName = None
			highest = None
			if rows != None:
				for row in rows:
					if row['air'] < 0.99 and (highest == None or highest < row['levelIdZ']):
						highest = row['levelIdZ']
						oldImageName = row['baseImage']
		
		else:
			#otherwise work off of our stored levels
			oldImageName = None
			highest = None
			for k in self.levels:
				if self.levels[k].air < 0.99 and (highest == None or highest < k):
					highest = k
					oldImageName = self.levels[k].baseImage
			
			
		if oldImageName == None:
			oldImageName = 'img-src/void.png'
			
		newImageName = "img-world-%d/zoom1-%dx-%dy.png" % (self.worldId, self.cellIdX, self.cellIdY) 
		#print 'new:', newImageName, 'old:', oldImageName

		#not just copying because eventually we'll be doing things like merging between layers
		image1 = Image.open(oldImageName)

		try:
			image2 = Image.open(newImageName)
		except:
			image2 = Image.open("img-src/void.png")
		
		if ImageChops.difference(image1, image2).getbbox() is None:
			#no change, don't need to do anything
			return False
		else:
			#Image has been changed, save the new one
			image1.save(newImageName)
			return True
		

		
	def zoomLevel(self,zoom):
		#note: zoom will always start at 2
		
		oldNCells = 2 ** (zoom - 2)
		
		#open the previous zoom level image to get the image size information
		try:
			oldImage1 = Image.open("img-world-%d/zoom%d-%dx-%dy.png" % (self.worldId, zoom - 1,self.cellIdX, self.cellIdY))
		except:
			oldImage1 = Image.open("img-src/void.png")
			
		try:
			oldImage2 = Image.open("img-world-%d/zoom%d-%dx-%dy.png" % (self.worldId, zoom - 1,self.cellIdX + oldNCells, self.cellIdY))
		except:
			oldImage2 = Image.open("img-src/void.png")
			
		try:
			oldImage3 = Image.open("img-world-%d/zoom%d-%dx-%dy.png" % (self.worldId, zoom - 1,self.cellIdX, self.cellIdY + oldNCells))
		except:
			oldImage3 = Image.open("img-src/void.png")
		
		try:
			oldImage4 = Image.open("img-world-%d/zoom%d-%dx-%dy.png" % (self.worldId, zoom - 1,self.cellIdX + oldNCells, self.cellIdY + oldNCells))
		except:
			oldImage4 = Image.open("img-src/void.png")
		
		xSize, ySize = oldImage1.size

		newImage = Image.new('RGB', (xSize*2, ySize*2))
		
		newImage.paste(oldImage1, (0,0))
		newImage.paste(oldImage2,(xSize,0))
		newImage.paste(oldImage3,(0, ySize))
		newImage.paste(oldImage4, (xSize,ySize))

		newImage.thumbnail((xSize,ySize))
		
		name = "img-world-%d/zoom%d-%dx-%dy.png" % (self.worldId, zoom,self.cellIdX, self.cellIdY)
		
		try:
			oldImage = Image.open(name)
		except:
			oldImage = Image.open("img-src/void.png")
		
		oldImage = oldImage.convert('RGB')

		#oldImage.save("zoom%d-%dx-%dy.old.png" % (zoom,self.cellIdX, self.cellIdY))
		#newImage.save("zoom%d-%dx-%dy.new.png" % (zoom,self.cellIdX, self.cellIdY))

		#print '1:', newImage.getbands(), '2:', oldImage.getbands()
		if ImageChops.difference(newImage, oldImage).getbbox() is None:
			#there was no change to the image, leave everything alone and return false
			return False
		else:
			#save and return true
			newImage.save("img-world-%d/zoom%d-%dx-%dy.png" % (self.worldId, zoom,self.cellIdX, self.cellIdY))
			
			return True
		
	def genSurface(self, conn, Sealevel, worldMaxY):
		if Sealevel > self.cellGroundlevel:
			z = Sealevel
		else:
			z = self.cellGroundlevel

		level = levelData.LevelData( self.worldId, self.cellIdX, self.cellIdY, z)
		
		level.genSurface(conn, self.cellGroundlevel, Sealevel, worldMaxY )
		
		self.levels = {}
		self.levels[z] = level