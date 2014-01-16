# -*- coding: utf-8 -*-
import Image
import ImageChops

import db

class LevelData:
	worldId = 0
	cellIdX = 0
	cellIdY = 0
	levelIdZ = 0

	#base layer types
	water = 0.0
	air = 0.0
	rock = 0.0

	#overlay/biome types
	artic = 0.0
	swamp = 0.0
	hills = 0.0
	mountains = 0.0
	jungle = 0.0
	plains = 0.0
	grassland = 0.0
	forest = 0.0
	
	cityId = -1
	
	baseImage = ""

	def __init__(self, worldId = None, cellIdX = None, cellIdY = None, levelIdZ = None, rowData = None):
		if rowData is None:
			self.worldId = worldId
			self.cellIdX = cellIdX
			self.cellIdY = cellIdY
			self.levelIdZ = levelIdZ
		else:
			self.__dict__ = rowData
			
	def genBaseImage(self):
		image = 'img-src/void.png'
		#return the right image
		
		#if self.artic >=0.9:
			#image = 'img-src/ice.png'
		#elif self.swamp >= 0.9:
			#image = 'img-src/swamp.png'
		#elif self.hills >= 0.9:
			#image = 'img-src/hills.png'
		#elif self.mountains >= 0.9:
			#image = 'img-src/mountains.png'
		#elif self.jungle >= 0.9:
			#image = 'img-src/jungle.png'
		#elif self.plains >= 0.9:
			#image = 'img-src/plains.png'
		#elif self.grassland >= 0.9:
			#image = 'img-src/grassland.png'
		#elif self.forest >= 0.9:
			#image = 'img-src/forest.png'
		if self.water >= 0.1:
			image = 'img-src/ocean.png'
		elif self.rock >= 0.1:
			image = 'img-src/rock.png'
		else:
			image = 'img-src/sky.png'
		

			
		return image
			
		
	def genSurface(self, conn, landlevel, sealevel, worldMaxY):
		self.water = 0.0
		self.air = 0.0
		self.rock = 0.0
		
		if self.levelIdZ == landlevel and self.levelIdZ < sealevel:
			self.rock = 0.5
			self.water = 0.5
		elif self.levelIdZ > landlevel and self.levelIdZ == sealevel:
			self.water = 0.5
			self.air = 0.5
		elif self.levelIdZ == landlevel and self.levelIdZ > sealevel:
			self.rock = 0.5
			self.air = 0.5
		elif self.levelIdZ == landlevel and self.levelIdZ == sealevel:
			self.rock = 0.33
			self.water = 0.33
			self.air = 0.33
		else:
			#something went wrong
			pass
			
		
		#get lat in percent (0% being the pole, 100% being the equator)
		y = self.cellIdY
		if y > worldMaxY / 2:
			y = worldMaxY - y
		lat = y/(worldMaxY / 2.0)
		
		#get height in percent (0% being sealevel, 100% being the hightest peak)
		#	using 255 for now we'll have to modifiy the genHeightMap function to store the
		#	highest land value in the database
		height = (self.levelIdZ - sealevel)/(255.0 - sealevel)
		
		#biomes
		#self.artic = 0.0
		#self.swamp = 0.0
		#self.hills = 0.0
		#self.mountains = 0.0
		#self.jungle = 0.0
		#self.plains = 0.0
		#self.grassland = 0.0
		#self.forest = 0.0
		
		#set the right biome and image
		#if self.air > 0.99:
			#pass
		#elif self.rock > 0.99:
			#pass
		#elif lat < 0.2:
			#self.artic = 1.0
		#elif self.water > 0.4:
			#pass
		#elif self.levelIdZ == sealevel:
			#self.swamp = 1.0
		#elif height > 0.33:
			#self.hills = 1.0
		#elif height > 0.66:
			#self.mountains = 1.0
		#elif lat > 0.8:
			#self.jungle = 1.0
		#elif lat > 0.6:
			#self.plains = 1.0
		#elif lat > 0.4:
			#self.grassland = 1.0
		#else:
			#self.forest = 1.0
	
		self.baseImage = self.genBaseImage()
		
		c = db.levelData.columns
		#ins = db.levelData.insert().values(worldId = self.worldId, cellIdX = self.cellIdX, cellIdY = self.cellIdY, levelIdZ = self.levelIdZ,
																				#water = self.water, air = self.air, rock = self.rock,
																				#artic = self.artic, swamp = self.swamp, hills = self.hills, mountains = self.mountains, jungle = self.jungle,
																				#plains = self.plains, grassland = self.grassland, forest = self.forest,
																				#baseImage = self.baseImage, dirtyImage = False, cityId = -1)
		ins = db.levelData.insert().values(worldId = self.worldId, cellIdX = self.cellIdX, cellIdY = self.cellIdY, levelIdZ = self.levelIdZ,
																				water = self.water, air = self.air, rock = self.rock,
																				baseImage = self.baseImage, dirtyImage = False, cityId = -1)
		conn.execute(ins)	

	def updateImage(self, conn):
		base = Image.open(self.genBaseImage())
		
		xSize, ySize = base.size
		
		if self.cityId != -1:
			city = Image.open('img-src/city1.png')
		
			base.paste(city, (0,0), city.convert('RGBA').split()[3])
			
		#check if the image actually changed
		try:
			oldImage = Image.open(self.baseImage)
		except:
			oldImage = Image.open("img-src/void.png")
			
		c = db.levelData.columns
		if ImageChops.difference(base, oldImage).getbbox() is None:
			#no change
			up = db.levelData.update().where((c.cellIdX == self.cellIdX) & (c.cellIdY == self.cellIdY) & 
				(c.levelIdZ == self.levelIdZ) & (c.worldId == self.worldId)).values(dirtyImage = False)
				
		else:
			#changed, save image and update database
			self.baseImage = "img-world-%d/zoom0-%dx-%dy-%dz.png" % (self.worldId, self.cellIdX, self.cellIdY, self.levelIdZ) 
			
			base.save(self.baseImage)
			
			up = db.levelData.update().where((c.cellIdX == self.cellIdX) & (c.cellIdY == self.cellIdY) & 
				(c.levelIdZ == self.levelIdZ) & (c.worldId == self.worldId)).values(baseImage = self.baseImage, dirtyImage = False)

		conn.execute(up)
			