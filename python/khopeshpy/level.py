# -*- coding: utf-8 -*-
import time
import random
import Image
import ImageChops    

import db
import biome
import config

class Level(object):    
    valid = False

    data = {}

    def genBaseImage(self):
        if self.data['water'] > 0.1:
            topBiome = 'ocean'
        else:
            biomes = ['savanna', 'grassland', 'forestCanopy', 'taigaCanopy', 'tundra']
        
            topLevel = 0.01
            topBiome = 'rock'
            for b in biomes:
                if self.data[b] > topLevel:
                    topLevel = self.data[b]
                    topBiome = b
                
        imgName = 'img-src/' + topBiome + '.png'
        
        return imgName
            
    def isImageChanged(self):
        imgName = self.genBaseImage()
        
        if 'baseImage' not in self.data or self.data['baseImage'] != imgName:
            self.data['baseImage'] = imgName
            return True
        else:
            return False

class Setup(Level):
    conn = None
    
    def __init__(self, conn = None, position = None, data = None):
        if position != None and conn != None:
            self.conn = conn
            self.data = {}
            
            self.data['cellIdX'] = position[0]
            self.data['cellIdY'] = position[1]
            self.data['levelIdZ'] = position[2]
            self.levelIdZ = position[2]
            
            self.data['savanna'] = None
            self.data['grassland'] = None
            self.data['forestCanopy'] = None
            self.data['taigaCanopy'] = None
            self.data['tundra'] = None
        elif data != None and conn != None:
            self.conn = conn
            self.data = {}
            self.data.update(data)
            self.levelId = self.data['levelId']
        else:
            msg = "level.Setup objects must be initialized with a database connection and a position or data"
            raise Exception(msg)

    def genSurface(self, landlevel, sealevel):
        self.data['water'] = 0.0
        self.data['air'] = 0.0
        self.data['rock'] = 0.0
        
        if self.levelIdZ == landlevel and self.levelIdZ < sealevel:
            self.data['rock'] = 0.5
            self.data['water'] = 0.5
        elif self.levelIdZ > landlevel and self.levelIdZ == sealevel:
            self.data['water'] = 0.5
            self.data['air'] = 0.5
        elif self.levelIdZ == landlevel and self.levelIdZ > sealevel:
            self.data['rock'] = 0.5
            self.data['air'] = 0.5
        elif self.levelIdZ == landlevel and self.levelIdZ == sealevel:
            self.data['rock'] = 0.33
            self.data['water'] = 0.33
            self.data['air'] = 0.33

    def genBiomes(self, solar, temp, dt):        
        #generate all the different biomes
        biomes = ['savanna', 'grassland', 'forestCanopy', 'taigaCanopy', 'tundra']
        for x in biomes:
            self.data[x] = biome.growth(x, solar, temp, dt, 0.5)
        
        #normalize if the total is greater than one
        a = self.data['savanna'] + self.data['grassland']\
            + self.data['forestCanopy'] + self.data['taigaCanopy'] + self.data['tundra']
        if a > 1.0:
            self.data['savanna'] /= a
            self.data['grassland'] /= a
            self.data['forestCanopy'] /= a
            self.data['taigaCanopy'] /= a
            self.data['tundra'] /= a
            
    def addAnimals(self):
        from khopeshpy import animals

        #make sure that we are creating animals in a viable environmnet
        if self.data['rock'] > 0.1 and self.data['air'] > 0.1 and self.data['water'] < 0.1\
                and (self.data['savanna'] > 0.25 or self.data['grassland'] > 0.25):
            if random.randint(0, 50) == 0:
                position = (self.data['cellIdX'], self.data['cellIdY'], self.levelIdZ)
                
                
                for x in range(10):
                    a = animals.createNew(self.conn, animals.Species.BISON, position)
                    #a = animals.bison.Setup(conn = self.conn, position = position)
                
                for x in range(2):
                    a = animals.createNew(self.conn, animals.Species.WOLF, position)
                    #a = animals.wolf.Setup(conn = self.conn, position = position)
                
            
    def genImages(self):
        self.data['baseImage'] = self.genBaseImage()
        
        return self.data['baseImage']
        
            
    def saveAll(self):
        if self.data['water'] > 0.1:
            lastUpdated = None
        else:
            lastUpdated = time.time()
            
        c = db.levelData.columns
        ins = db.levelData.insert().values(\
                cellIdX = self.data['cellIdX'], cellIdY = self.data['cellIdY'],\
                levelIdZ = self.levelIdZ, water = self.data['water'],\
                air = self.data['air'], rock = self.data['rock'],\
                savanna = self.data['savanna'], grassland = self.data['grassland'],\
                forestCanopy = self.data['forestCanopy'], taigaCanopy = self.data['taigaCanopy'],\
                tundra = self.data['tundra'], baseImage = self.data['baseImage'], dirtyImage = False,\
                lastUpdated = lastUpdated)
        self.conn.execute(ins)    
        
class Event(Level):
    def __init__(self, row = None, position = None, conn = None):
        if conn == None or (position == None and row == None):
            msg = "Level objects must be initialized with a database connection and either a row or position"
            raise Exception(msg)
            
        if position != None:
            self.conn = conn
            self.cellIdX = position[0]
            self.cellIdY = position[1]
            self.levelIdZ = position[2]
            
            self.pullData()
        elif row != None:
            self.conn = conn
            self.data = row
            
            self.cellIdX = row['cellIdX']
            self.cellIdY = row['cellIdY']
            self.levelIdZ = row['levelIdZ']
            self.valid = True
            self.levelId = row['levelId']
        
    def pullData(self):
        c = db.levelData.columns
        statment = db.select([db.levelData], (c.cellIdX == self.cellIdX) & \
            (c.cellIdY == self.cellIdY) & (c.levelIdZ == self.levelIdZ))

        result = self.conn.execute(statment)
        row = result.fetchone()
        result.close()
        
        if row == None:
            #msg = "No record found for level with position: (%d,%d,%d)" % (self.cellIdX, self.cellIdY,self.levelIdZ)
            #raise Exception(msg)
            self.valid = False
        else:
            self.data.update(dict(row))
            self.valid = True
            self.levelId = self.data['levelId']
            
    @property
    def walkable(self):
        #if there is not to much water and there is room to stand...
        if self.data['water'] < 0.1 and self.data['air'] > 0.1 and self.data['rock'] > 0.1:
            return True
        else:
            return False
            
    def biomass(self, b):
        if self.valid == False:
            return 0.0
            
        return biome.maxBioMass(b) * self.data[b]
        
        
    def biomassEaten(self, bio, amountEaten):
        totalAmount = self.data[bio] * biome.maxBioMass(bio)
        totalAmount -= amountEaten
        self.data[bio] = totalAmount / biome.maxBioMass(bio)
        if self.data[bio] < 0.0:
            self.data[bio] = 0.0
            
        c = db.levelData.columns
        upData = {bio: self.data[bio]}
        up = db.levelData.update().where((c.levelId == self.levelId)).values(**upData)
        self.conn.execute(up)
        

class EventLevel(Level):
    conn = None
    levelId = 0
    
    def __init__(self, position = None, conn = None):        
        if position == None or conn == None:
            msg = "Level objects must be initialized with a position and a database connection"
            raise Exception(msg)
            
        self.conn = conn
        self.cellIdX = position[0]
        self.cellIdY = position[1]
        self.levelIdZ = position[2]
        
        self.pullData()
        
    def pullData(self):
        c = db.levelData.columns
        statment = db.select([db.levelData], (c.cellIdX == self.cellIdX) & \
            (c.cellIdY == self.cellIdY) & (c.levelIdZ == self.levelIdZ))

        result = self.conn.execute(statment)
        row = result.fetchone()
        result.close()
        
        if row == None:
            #msg = "No record found for level with position: (%d,%d,%d)" % (self.cellIdX, self.cellIdY,self.levelIdZ)
            #raise Exception(msg)
            self.valid = False
        else:
            self.data.update(dict(row))
            self.valid = True
            self.levelId = self.data['levelId']
        
    def walkable(self):
        if self.valid == False:
            return False
        #if there is not to much water and there is room to stand...
        if self.data['water'] < 0.1 and self.data['air'] > 0 and self.data['rock'] > 0:
            return True
        else:
            return False
            
    def biomass(self, b):
        if self.valid == False:
            return 0.0
            
        return biome.maxBioMass(b) * self.data[b]
        
    def biomassEaten(self, bio, amountEaten):
        totalAmount = self.data[bio] * biome.maxBioMass(bio)
        totalAmount -= amountEaten
        self.data[bio] = totalAmount / biome.maxBioMass(bio)
        if self.data[bio] < 0.0:
            self.data[bio] = 0.0
            
        c = db.levelData.columns
        upData = {bio: self.data[bio]}
        up = db.levelData.update().where((c.levelId == self.levelId)).values(**upData)
        self.conn.execute(up)
            

class Update(Level):
    conn = None

    def __init__(self, position = None, data = None, conn = None):
        if position != None and conn != None:
            self.conn = conn
            self.cellIdX = position[0]
            self.cellIdY = position[1]
            self.levelIdZ = position[2]
            
            self.data = {}
            
            self.pullData()
        elif data != None and conn != None:
            self.conn = conn
            
            self.data = {}
            self.data.update(dict(data))
            self.cellIdX = self.data['cellIdX']
            self.cellIdY = self.data['cellIdY']
            self.levelIdZ = self.data['levelIdZ']
            self.levelId = self.data['levelId']
        
        else:
            msg = "Level.Update objects must be initialized with a database connection and a position or data"
            raise Exception(msg)
        
    def pullData(self):
        c = db.levelData.columns
        #print self.cellIdX, self.cellIdY, self.levelIdZ
        statment = db.select([db.levelData], (c.cellIdX == self.cellIdX) & \
            (c.cellIdY == self.cellIdY) & (c.levelIdZ == self.levelIdZ))

        result = self.conn.execute(statment)
        row = result.fetchone()
        result.close()
        
        if row == None:
            #msg = "No record found for level with position: (%d,%d,%d)" % (self.cellIdX, self.cellIdY,self.levelIdZ)
            #raise Exception(msg)
            self.valid = False
        else:
            self.data.update(dict(row))
            self.valid = True
            self.levelId = self.data['levelId']
        
    def growLand(self, lat, temp, dt):        
        #grow all the different biomes
        biomes = ['savanna', 'grassland', 'forestCanopy', 'taigaCanopy', 'tundra']
        for x in biomes:
            self.data[x] = biome.growth(x, lat, temp, dt, self.data[x])
        
        #normalize if the total is greater than one
        a = self.data['savanna'] + self.data['grassland']\
            + self.data['forestCanopy'] + self.data['taigaCanopy'] + self.data['tundra']
        if a > 1.0:
            self.data['savanna'] /= a
            self.data['grassland'] /= a
            self.data['forestCanopy'] /= a
            self.data['taigaCanopy'] /= a
            self.data['tundra'] /= a            
        
        if self.data['savanna'] < 0.01 and self.data['grassland'] < 0.01 and \
                self.data['forestCanopy'] < 0.01 and self.data['taigaCanopy'] < 0.01 and \
                self.data['tundra'] < 0.01:
            image = 'img-src/rock.png'
        else:
            a = 'savanna' if self.data['savanna'] > self.data['grassland'] else 'grassland'
            b = 'forestCanopy' if self.data['forestCanopy'] > self.data['taigaCanopy'] else 'taigaCanopy'
            
    
    def saveBiome(self):
        imageChanged = self.isImageChanged()
        
        c = db.levelData.columns
        up = db.levelData.update().where((c.levelId == self.levelId))\
            .values(savanna = self.data['savanna'], grassland = self.data['grassland'], tundra = self.data['tundra'],\
            forestCanopy = self.data['forestCanopy'], taigaCanopy = self.data['taigaCanopy'],\
            dirtyImage = imageChanged, baseImage = self.data['baseImage'])
        self.conn.execute(up)
        
    def addIdle(self, a, b, c):
        self.data['savanna'] = 0.5
        self.data['grassland'] = 0.5
        self.data['forestCanopy'] = 0.5
        self.data['taigaCanopy'] = 0.5
        self.data['tundra'] = 0.5
        self.growLand(a, b, c)
        
    def updateMap(self):
        base = Image.open(self.genBaseImage())
        xSize, ySize = base.size
        
        if self.data['cityId'] != None:
            city = Image.open('img-src/city1.png')
        
            base.paste(city, (0,0), city.convert('RGBA').split()[3])
            
        #check if the image actually changed
        try:
            oldImage = Image.open(self.data['baseImage'])
        except:
            oldImage = Image.open("img-src/void.png")
            
        c = db.levelData.columns
        if ImageChops.difference(base, oldImage).getbbox() is None:
            #no change
            up = db.levelData.update().where((c.levelId == self.levelId)).values(dirtyImage = False)
        else:
            #changed, save image and update database
            self.data['baseImage'] = "img-world/zoom0-%dx-%dy-%dz.png" % (self.cellIdX, self.cellIdY, self.levelIdZ) 
            
            base.save(self.data['baseImage'])
            
            up = db.levelData.update().where((c.levelId == self.levelId)).values(baseImage = self.data['baseImage'], dirtyImage = False)

        self.conn.execute(up)

class UpdateLevel(Level):
    conn = None
    
    def dbConnect(self):
        if self.conn != None:
            return self.conn
        else:
            return db.connect()
            
    def dbClose(self, conn):
        if self.conn != None:
            pass #we were passed in a database connection so we don't need to close it
        else:
            conn.close()
            
    def __init__(self, position = None, conn = None):
        if position == None or conn == None:
            msg = "Cell objects must be initialized with a position and a database connection"
            raise Exception(msg)
        
        self.conn = conn
        self.cellIdX = position[0]
        self.cellIdY = position[1]
        self.levelIdZ = position[2]
        
        self.pullData()
            
    def pullData(self):
        conn = self.dbConnect()
        
        c = db.levelData.columns
        statment = db.select([db.levelData], (c.cellIdX == self.cellIdX) & \
            (c.cellIdY == self.cellIdY) & (c.levelIdZ == self.levelIdZ))
        result = conn.execute(statment)
        row = result.fetchone()
        result.close()

        if row == None:
            print "No record found for level with position: (%d,%d,%d)" % (self.cellIdX, self.cellIdY, self.levelIdZ)
            self.valid = False
        else:
            self.data.update(dict(row))
            self.valid = True
            self.levelId = self.data['levelId']
            
        self.dbClose(conn)
        

            
    def growLand(self, lat, temp):
        if self.data['lastUpdated'] == None:
            dt = config.tick
        else:
            dt = time.time() - self.data['lastUpdated']
        
        #grow all the different biomes
        biomes = ['savanna', 'grassland', 'forestCanopy', 'taigaCanopy', 'tundra']
        for x in biomes:
            self.data[x] = biome.growth(x, lat, temp, dt, self.data[x])
        
        #normalize if the total is greater than one
        a = self.data['savanna'] + self.data['grassland']\
            + self.data['forestCanopy'] + self.data['taigaCanopy'] + self.data['tundra']
        if a > 1.0:
            self.data['savanna'] /= a
            self.data['grassland'] /= a
            self.data['forestCanopy'] /= a
            self.data['taigaCanopy'] /= a
            self.data['tundra'] /= a
        
    def saveBiome(self):
        conn = self.dbConnect()
        
        c = db.levelData.columns
        up = db.levelData.update().where((c.levelId == self.levelId))\
            .values(savanna = self.data['savanna'], grassland = self.data['grassland'], tundra = self.data['tundra'],\
            forestCanopy = self.data['forestCanopy'], taigaCanopy = self.data['taigaCanopy'], lastUpdated = time.time())
        conn.execute(up)
        
        self.dbClose(conn)
        
        
    #we'll reintigrate these functions when we have reason to do so
    
    #def validate(self):
        #if 'savanna' not in self.data or self.data['savanna'] == None:
            #self.data['savanna'] = 0.0
        #if 'grassland' not in self.data or self.data['grassland'] == None:
            #self.data['grassland'] = 0.0
        #if 'forestCanopy' not in self.data or self.data['forestCanopy'] == None:
            #self.data['forestCanopy'] = 0.0
        #if 'taigaCanopy' not in self.data or self.data['taigaCanopy'] == None:
            #self.data['taigaCanopy'] = 0.0
        #if 'tundra' not in self.data or self.data['tundra'] == None:
            #self.data['tundra'] = 0.0
        #if 'forestUnderstory' not in self.data or self.data['forestUnderstory'] == None:
            #self.data['forestUnderstory'] = 0.0
        #if 'taigaUnderstory' not in self.data or self.data['taigaUnderstory'] == None:
            #self.data['taigaUnderstory'] = 0.0
    
    
    #def solarAbsorption(self, solarUsed):
        #if self.valid == False:
            ##cell is undefined so nothing is used
            #return solarUsed
        #else:
            ##the only ones that will block light are canopies
            #return (solarUsed - (self.data['taigaCanopy'] + self.data['forestCanopy']))
    
    #passed the level the level directly above it, if there isn't a canopy
    #    to support the understory it needs to die back
    #def understorySupport(self, upperLevel):
        #if self.data['forestUnderstory'] > upperLevel.data['forestCanopy'] + upperLevel.data['forestUnderstory']:
            #self.data['forestUnderstory'] = upperLevel.data['forestCanopy'] + upperLevel.data['forestUnderstory']
            
        #if self.data['taigaUnderstory'] > upperLevel.data['taigaCanopy'] + upperLevel.data['taigaUnderstory']:
            #self.data['taigaUnderstory'] = upperLevel.data['taigaCanopy'] + upperLevel.data['taigaUnderstory']
            
    ##makes sure that the understory hasn't been cut out from under the canopy
    #def canopySupport(self, lowerLevel):
        #if self.data['forestCanopy'] + self.data['forestUnderstory'] > lowerLevel.data['forestUnderstory']:
            #if self.data['forestUnderstory'] > lowerLevel.data['forestUnderstory']:
                ##both need to be cut, first cut the new growth
                #self.data['forestCanopy'] = 0.0
                #self.data['forestUnderstory'] = lowerLevel.data['forestUnderstory']
            #else:
                ##only need to cut the canopy
                #self.data['forestCanopy'] = lowerLevel.data['forestUnderstory'] - self.data['forestUnderstory']
                
        #if self.data['taigaCanopy'] + self.data['taigaUnderstory'] > lowerLevel.data['taigaUnderstory']:
            #if self.data['taigaUnderstory'] > lowerLevel.data['taigaUnderstory']:
                ##both need to be cut, first cut the new growth
                #self.data['taigaCanopy'] = 0.0
                #self.data['taigaUnderstory'] = lowerLevel.data['taigaUnderstory']
            #else:
                ##only need to cut the canopy
                #self.data['taigaCanopy'] = lowerLevel.data['taigaUnderstory'] - self.data['taigaUnderstory']
    
    #def saveBiome(self):
        #conn = self.dbConnect()
        
        #if self.valid == True:
            #c = db.levelData.columns
            #up = db.levelData.update().where((c.levelId == self.levelId))\
                #.values(savanna = self.data['savanna'], grassland = self.data['grassland'], tundra = self.data['tundra'],\
                #forestCanopy = self.data['forestCanopy'], taigaCanopy = self.data['taigaCanopy'],\
                #forestUnderstory = self.data['forestUnderstory'], taigaUnderstory = self.data['forestUnderstory'])
            #conn.execute(up)
        #elif self.data['forestCanopy'] > 0 or self.data['taigaCanopy'] > 0:
            ##we can assume that added cells will only be air cells, additionally we only want to save if there is
            ##    added canopy
            #ins = db.levelData.insert().values(cellIdX = self.cellIdX, cellIdY = self.cellIdY, levelIdZ = self.levelIdZ,\
                #water = 0.0, air = 1.0, rock = 0.0,\
                #forestCanopy = self.data['forestCanopy'], taigaCanopy = self.data['taigaCanopy'])
            #conn.execute(ins)
        
        #self.dbClose(conn)
        
        
    #def growLand(self, lat, temp):
        ##understories die back a certain percentage each tick
        ##self.data['forestUnderstory'] = biome.forestUnderstory.dieBack(self.data['forestUnderstory'])
        ##self.data['taigaUnderstory'] = biome.taigaUnderstory.dieBack(self.data['taigaUnderstory'])
        
        ##canopy converts to understory a certain percentage each tick
        ##setting to 1% for right now
        ##self.data['forestCanopy'], self.data['forestUnderstory'] = \
            ##biome.forestUnderstory.convert(self.data['forestCanopy'], self.data['forestUnderstory'])
        ##self.data['taigaCanopy'], self.data['taigaUnderstory'] = \
            ##biome.taigaUnderstory.convert(self.data['taigaCanopy'], self.data['taigaUnderstory'])
        
        ##grow all the different biomes
        ##biomes = ['savanna', 'grassland', 'forestCanopy', 'taigaCanopy', 'tundra']
        ##for x in biomes:
        #self.data['savanna'] = biome.savanna.growth(lat, temp, self.data['savanna'])
        #self.data['grassland'] = biome.grassland.growth(lat, temp, self.data['grassland'])
        #self.data['forestCanopy'] = biome.forestCanopy.growth(lat, temp, self.data['forestCanopy'])
        #self.data['taigaCanopy'] = biome.taigaCanopy.growth(lat, temp, self.data['taigaCanopy'])
        #self.data['tundra'] = biome.tundra.growth(lat, temp, self.data['tundra'])
        
        #a = self.data['savanna'] + self.data['grassland']\
            #+ self.data['forestCanopy'] + self.data['taigaCanopy'] +self.data['tundra']
            
        #if a > 1:
            #self.data['savanna'] /= a
            #self.data['grassland'] /= a
            #self.data['forestCanopy'] /= a
            #self.data['taigaCanopy'] /= a
            #self.data['tundra'] /= a
        
        ##availForGrowth = 1.0 - (self.data['taigaUnderstory'] + self.data['forestUnderstory'])
        
        ##self.data['savanna'] *= availForGrowth
        ##self.data['grassland'] *= availForGrowth
        ##self.data['forestCanopy'] *= availForGrowth
        ##self.data['taigaCanopy'] *= availForGrowth
        ##self.data['tundra'] *= availForGrowt
    #def growAir(self, lat, temp):
        ##understories die back a certain percentage each tick
        #self.data['forestUnderstory'] = biome.forestUnderstory.dieBack(self.data['forestUnderstory'])
        #self.data['taigaUnderstory'] = biome.taigaUnderstory.dieBack(self.data['taigaUnderstory'])
        
        ##canopy converts to understory a certain percentage each tick
        #self.data['forestCanopy'], self.data['forestUnderstory'] = \
            #biome.forestUnderstory.convert(self.data['forestCanopy'], self.data['forestUnderstory'])
        #self.data['taigaCanopy'], self.data['taigaUnderstory'] = \
            #biome.taigaUnderstory.convert(self.data['taigaCanopy'], self.data['taigaUnderstory'])
        
        ##zero out the other biomes
        #self.data['savanna'] = 0.0
        #self.data['grassland'] = 0.0
        #self.data['tundra'] = 0.0
        
        ##grow all the different biomes
        #self.data['forestCanopy'] = biome.savanna.growth(lat, temp, self.data['forestCanopy'])
        #self.data['taigaCanopy'] = biome.savanna.growth(lat, temp, self.data['taigaCanopy'])
        
        #a = self.data['forestCanopy'] + self.data['taigaCanopy']
            
        #self.data['forestCanopy'] /= a
        #self.data['taigaCanopy'] /= a
        
        #availForGrowth = 1.0 - (self.data['taigaUnderstory'] + self.data['forestUnderstory'])
        
        #self.data['forestCanopy'] *= availForGrowth
        #self.data['taigaCanopy'] *= availForGrowth
