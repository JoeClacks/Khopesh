# -*- coding: utf-8 -*-
import Image
import ImageChops
import time

import db
import level
import config

class Cell:
    data = {}
    
    valid = False
    
    conn = None
    
    cellIdX = None
    cellIdY = None
    
    
    #later on we might do some alpha blending and transparency, but right now
    # our only concern is setting the cell image to the image of the heighest 
    # non-air level
    def compressLevels(self):
        c = db.levelData.columns
        statement = db.select([db.levelData], (c.cellIdX == self.cellIdX) & (c.cellIdY == self.cellIdY))
        result = self.conn.execute(statement)
        rows = result.fetchall()
        result.close()
        
        #instantiate the levels for this cell
        highest = None
        self.levels = {}
        for row in rows:
            z = row['levelIdZ']
            self.levels[z] = level.Setup(data = row, conn = self.conn)
            self.levels[z].genMap()
            
            #and find the highest non-air image
            if self.levels[z].data['air'] < 0.99 and (highest == None or highest < z):
                highest = z
                
        #set the cell image to the highest non-air image
        if highest == None:
            oldImageName = 'img-src/void.png'
        else:
            oldImageName = self.levels[highest].data['baseImage']
            
        self.data['cellImage'] = oldImageName
        c = db.cellData.columns
        up = db.cellData.update().where((c.cellIdX == self.cellIdX) & (c.cellIdY == self.cellIdY)).values(cellImage = self.data['cellImage'])
        self.conn.execute(up)
        
        #newImageName = "img-world/zoom1-%dx-%dy.png" % (self.cellIdX, self.cellIdY) 
        
        #until we start doing stuff with transparency we can just hard link and keep
        #    down space usage
        #os.link(oldImageName, newImageName)

        ##not just copying because eventually we'll be doing things like merging between layers
        #image1 = Image.open(oldImageName)

        ##if we don't find the image we want default to the void image
        #try:
            #image2 = Image.open(newImageName)
        #except:
            #image2 = Image.open("img-src/void.png")
        
        #if ImageChops.difference(image1, image2).getbbox() is None:
            ##no change, don't need to do anything
            #return False
        #else:
            ##Image has been changed, save the new one
            #image1.save(newImageName)
            #return True
            
    def firstZoomLevel(self, image2, image3, image4):
        #note: zoom will always start at 2
        
        try:
            oldImage1 = Image.open(self.data['cellImage'])
        except:
            oldImage1 = Image.open("img-src/void.png")
            
        try:
            oldImage2 = Image.open(image2.data['cellImage'])
        except:
            oldImage2 = Image.open("img-src/void.png")
            
        try:
            oldImage3 = Image.open(image3.data['cellImage'])
        except:
            oldImage3 = Image.open("img-src/void.png")
        
        try:
            oldImage4 = Image.open(image4.data['cellImage'])
        except:
            oldImage4 = Image.open("img-src/void.png")
        
        xSize, ySize = oldImage1.size

        newImage = Image.new('RGB', (xSize*2, ySize*2))
        
        newImage.paste(oldImage1, (0,0))
        newImage.paste(oldImage2, (xSize,0))
        newImage.paste(oldImage3, (0, ySize))
        newImage.paste(oldImage4, (xSize,ySize))

        newImage.thumbnail((xSize,ySize))
        
        name = "img-world/zoom2-%dx-%dy.png" % (self.cellIdX, self.cellIdY)
        
        try:
            oldImage = Image.open(name)
        except:
            oldImage = Image.open("img-src/void.png")
        
        oldImage = oldImage.convert('RGB')
        
        if ImageChops.difference(newImage, oldImage).getbbox() is None:
            #there was no change to the image, leave everything alone and return false
            return False
        else:
            #save and return true
            newImage.save("img-world/zoom2-%dx-%dy.png" % (self.cellIdX, self.cellIdY))
            
            return True
            
    def zoomLevel(self,zoom):
        #note: zoom will always start at 2
        
        oldNCells = 2 ** (zoom - 2)
        
        x = (self.cellIdX / oldNCells) * oldNCells
        y = (self.cellIdY / oldNCells) * oldNCells
        
        #open the previous zoom level image to get the image size information
        try:
            oldImage1 = Image.open("img-world/zoom%d-%dx-%dy.png" % (zoom - 1,self.cellIdX, self.cellIdY))
        except:
            oldImage1 = Image.open("img-src/void.png")
            
        try:
            oldImage2 = Image.open("img-world/zoom%d-%dx-%dy.png" % (zoom - 1,self.cellIdX + oldNCells, self.cellIdY))
        except:
            oldImage2 = Image.open("img-src/void.png")
            
        try:
            oldImage3 = Image.open("img-world/zoom%d-%dx-%dy.png" % (zoom - 1,self.cellIdX, self.cellIdY + oldNCells))
        except:
            oldImage3 = Image.open("img-src/void.png")
        
        try:
            oldImage4 = Image.open("img-world/zoom%d-%dx-%dy.png" % (zoom - 1,self.cellIdX + oldNCells, self.cellIdY + oldNCells))
        except:
            oldImage4 = Image.open("img-src/void.png")
        
        xSize, ySize = oldImage1.size

        newImage = Image.new('RGB', (xSize*2, ySize*2))
        
        newImage.paste(oldImage1, (0,0))
        newImage.paste(oldImage2,(xSize,0))
        newImage.paste(oldImage3,(0, ySize))
        newImage.paste(oldImage4, (xSize,ySize))

        newImage.thumbnail((xSize,ySize))
        
        name = "img-world/zoom%d-%dx-%dy.png" % (zoom,self.cellIdX, self.cellIdY)
        
        try:
            oldImage = Image.open(name)
        except:
            oldImage = Image.open("img-src/void.png")
        
        oldImage = oldImage.convert('RGB')
        
        #print '1:', newImage.getbands(), '2:', oldImage.getbands()
        if ImageChops.difference(newImage, oldImage).getbbox() is None:
            #there was no change to the image, leave everything alone and return false
            return False
        else:
            #save and return true
            newImage.save("img-world/zoom%d-%dx-%dy.png" % (zoom,self.cellIdX, self.cellIdY))
            
            return True

class Setup(Cell):
    conn = None
    
    levels = {} 
    
    def __init__(self, position = None, conn = None):
        if position == None or conn == None:
            msg = "cell.Setup needs a db connection and position"
            raise Exception(msg)
        
        
        self.conn = conn
        self.data = {}
        self.levels = {}
        
        self.data['cellIdX'] = position[0]
        self.data['cellIdY'] = position[1]
        self.cellIdX = position[0]
        self.cellIdY = position[1]
        
    def pullData(self):
        c = db.cellData.columns
        statment = db.select([db.cellData],\
            (c.cellIdX == self.cellIdX) & (c.cellIdY == self.cellIdY))
        result = self.conn.execute(statment)
        row = result.fetchone()
        result.close()
        
        if row == None:
            msg = "No record found for cell at location: (%d, %d)" % (self.cellIdX, self.cellIdY)
            raise Exception(msg)
        
        self.data.update(dict(row))
        self.cellId = self.data['cellId']
        self.valid = True
        
    def genHeightMap(self, groundlevel):
        self.data['cellGroundlevel'] = groundlevel
        self.groundlevel = groundlevel
        
    def genSurface(self):        
        z = config.worldSeaLevel if config.worldSeaLevel > self.data['cellGroundlevel'] else self.data['cellGroundlevel']
        
        levelObj = level.Setup(position = (self.cellIdX, self.cellIdY, z), conn = self.conn)
        
        levelObj.genSurface(self.data['cellGroundlevel'], config.worldSeaLevel)
        
        self.levels[z] = levelObj
        
    def genSurfaceTemp(self, lat):
        #we're only worried about land cells right now
        if self.data['cellGroundlevel'] < config.worldSeaLevel:
            self.data['cellTemp'] = None
        else:
            height = float((self.data['cellGroundlevel'] - config.worldSeaLevel))/(config.maxHeight - config.worldSeaLevel)

            temp = 36.0 - (60.0*lat + 85.0*height)
            
            self.data['cellTemp'] = temp
        
    def genSolarRadiation(self, lat):
        if self.data['cellGroundlevel'] < config.worldSeaLevel:
            self.data['cellSolar'] = None
        else:
            self.data['cellSolar'] = 1 - (lat)**2
        
    def genBiomes(self):
        if self.data['cellGroundlevel'] <= config.worldSeaLevel:
            return
        
        for z in self.levels:
            self.levels[z].genBiomes(self.data['cellSolar'], self.data['cellTemp'], 1.0)
            
    def genImages(self):
        for z in self.levels:
            self.data['cellImage'] = self.levels[z].genImages()
            
    def addAnimals(self):
        if self.data['cellGroundlevel'] < config.worldSeaLevel:
            return
            
            
        for z in self.levels:
            self.levels[z].addAnimals()
            
    def saveAll(self):
        if self.data['cellGroundlevel'] < config.worldSeaLevel:
            lastUpdated = None
        else:
            lastUpdated = time.time()
            
        c = db.cellData.columns
        ins = db.cellData.insert().values(cellIdX = self.cellIdX,\
                cellIdY = self.cellIdY, cellGroundlevel = self.data['cellGroundlevel'],\
                cellTemp = self.data['cellTemp'], cellSolar = self.data['cellSolar'],\
                cellImage = self.data['cellImage'], lastUpdated = lastUpdated)
        self.conn.execute(ins)
        
        for z in self.levels:
            self.levels[z].saveAll()
            

            

        
class Update(Cell):
    conn = None
    
    def __init__(self, data = None, position = None, conn = None):
        if conn != None and data != None:
            self.conn = conn
            self.data = {}
            self.data.update(dict(data))
            self.valid = True
            
            self.cellId = self.data['cellId']
            self.cellIdX = self.data['cellIdX']
            self.cellIdY = self.data['cellIdY']
        elif conn != None and position != None:
            self.conn = conn
            self.data = {}
            
            self.cellIdX = position[0]
            self.cellIdY = position[1]
        else:
            msg = "cell.Update needs a db connection and data or position"
            raise Exception(msg)
            
    def updateMap(self, worldSizeX, worldSizeY):
        #grab all the levels that belong to this cell
        c = db.levelData.columns
        statement = db.select([db.levelData], (c.cellIdX == self.cellIdX) & (c.cellIdY == self.cellIdY))
        result = self.conn.execute(statement)
        rows = result.fetchall()
        result.close()
        
        highest = None
        highestImage = None
        levels = {}
        for row in rows:
            #create an instance of each and update it's image
            levels[row['levelIdZ']] = level.Update(data = row, conn = self.conn)
            levels[row['levelIdZ']].updateMap()
            
            #check if it's the highest and save the image name if it is
            if (highest == None or row['levelIdZ'] >  highest) and row['air'] < 0.99:
                highest = row['levelIdZ']
                highestImage = levels[row['levelIdZ']].data['baseImage']
                
        if highest == None:
            highestImage = 'img-src/void.png'
            
        self.data['cellImage'] = highestImage
        c = db.cellData.columns
        up = db.cellData.update().where((c.cellIdX == self.cellIdX) & (c.cellIdY == self.cellIdY)).values(cellImage = self.data['cellImage'])
        self.conn.execute(up)
        
        
        #and update the zoom images
        x = (self.cellIdX / 2) * 2
        y = (self.cellIdY / 2) * 2
        
        c = db.cellData.columns
        statement = db.select([db.cellData],\
            ((c.cellIdX == x) | (c.cellIdX == (x + 1))) &    \
            ((c.cellIdY == y) | (c.cellIdY == (y + 1))))
        result = self.conn.execute(statement)
        rows = result.fetchall()
        result.close()
        
        images = {}
        for row in rows:
            images[(row['cellIdX'], row['cellIdY'])] = row['cellImage']
            
        keepGoing = zoomMap(2, x, y, images[(x,y)], images[(x+1,y)], images[(x,y+1)], images[(x+1,y+1)])

        zoom = 3
        nCells = 2 ** (zoom -1)
        keepGoing = True
        while nCells < worldSizeX and nCells < worldSizeY and keepGoing:
            keepGoing = prepareZoomMap(zoom, x, y)
            zoom = zoom + 1
            nCells = 2 ** (zoom -1)
        
    def updateLevels(self):
        dta = 1.0 #cells are always scheduled to be updated once per worldTick
        dtb = (float(time.time() - self.data['lastUpdated']))/config.worldTick #ticks
        dt = dta if dta < dtb else dtb
        
        levelObj = level.Update(conn = self.conn, position = (self.cellIdX, self.cellIdY, self.data['cellGroundlevel']))
        levelObj.growLand(self.data['cellSolar'], self.data['cellTemp'], dt)
        levelObj.saveBiome()
        
    def addIdleCell(self):
        dt = 1.0
        
        levelObj = level.Update(conn = self.conn, position = (self.cellIdX, self.cellIdY, self.data['cellGroundlevel']))
        levelObj.addIdle(self.data['cellSolar'], self.data['cellTemp'], dt)
        levelObj.saveBiome()
        
class UpdateCell(Cell):
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
        
        self.pullData()
        
    def pullData(self):
        conn = self.dbConnect()
        
        c = db.cellData.columns
        statment = db.select([db.cellData], (c.cellIdX == self.cellIdX) & \
            (c.cellIdY == self.cellIdY))
        result = conn.execute(statment)
        row = result.fetchone()
        result.close()
        
        if row == None:
            msg = "No record found for cell with position: (%d,%d)" % (self.cellIdX, self.cellIdY)
            raise Exception(msg)
        
        self.data.update(dict(row))
        self.valid = True
        
        self.cellId = self.data['cellId']
        #self.cellIdX = self.data['cellIdX']
        #self.cellIdY = self.data['cellIdY']
        
        self.dbClose(conn)
    
    def updateSurfaceTemps(self, lat, seaLevel):
        #we're only worried about land cells right now
        if self.data['cellGroundlevel'] < seaLevel:
            return
            
        conn = self.dbConnect()

        height = (self.data['cellGroundlevel'] - seaLevel)/(255.0 - seaLevel)
        temp = (36.0 - 38.0*lat) - 85.0*height
        
        self.data['cellTemp'] = temp
        
        c = db.cellData.columns
        up = db.cellData.update().where((c.cellId == self.cellId)).values(cellTemp = temp)
        conn.execute(up)
        
        self.dbClose(conn)
        
    def updateSolarRadiation(self, lat, seaLevel):
        #we're only worried about land cells right now
        if self.data['cellGroundlevel'] < seaLevel:
            return
            
        conn = self.dbConnect()

        solar = 1 - (lat)**2
        
        self.data['cellSolar'] = solar
        
        c = db.cellData.columns
        up = db.cellData.update().where((c.cellId == self.cellId)).values(cellSolar = solar)
        conn.execute(up)
        
        self.dbClose(conn)

    
    def updateBiosphere(self, seaLevel):
        #we're only worried about land cells right now
        if self.data['cellGroundlevel'] < seaLevel:
            return
            
        conn = self.dbConnect()
        
        #maxLevel = self.getHighestLevel()
        
        levelObj = level.UpdateLevel(conn = conn, position = (self.cellIdX, self.cellIdY, self.data['cellGroundlevel']))
        levelObj.growLand(self.data['cellSolar'], self.data['cellTemp'])
        levelObj.saveBiome()
        
        self.dbClose(conn)
        #create the levels dict
        #the plus 2 is for if there is growth into the new level
        #levels = {}
        #for z in xrange(self.data['cellGroundlevel'], maxLevel + 2):
            #levels[z] = level.UpdateLevel(conn = conn, position = (self.cellIdX, self.cellIdY, z))
        
        #for z in xrange(maxLevel, self.data['cellGroundlevel'] + 1, -1):
            #pass the level the level directly above it, if there isn't a canopy
            #    to support the understory it needs to die back
            #levels[z].understorySupport(levels[z+1])
        
        #for z in xrange(self.data['cellGroundlevel'] + 1, maxLevel + 1):
            #make sure that the understory hasn't been cut out from under the canopy
            #levels[z].canopySupport(levels[z - 1])
            
        #do the growth pass (upward)
        #for z in xrange(self.data['cellGroundlevel'], maxLevel + 2):
            #if z == self.data['cellGroundlevel']:
                #levels[z].growLand(self.data['cellSolar'], self.data['cellTemp'])
            #else:
                #leave out upper level growth for now
                #levels[z].growAir(self.data['cellSolar'], self.data['cellTemp'])
                #pass
            
        #and save
        #for z in levels:
            #levels[z].saveBiome()        
        
        
        
    #not using until we get multi-level biomes
    #def getHighestLevel(self):
        #conn = self.dbConnect()
        
        ##pull levelData
        #c = db.levelData.columns
        #statment = db.select([db.levelData], (c.cellIdX == self.cellIdX)\
            #& (c.cellIdY == self.cellIdY) & (c.levelIdZ >= self.data['cellGroundlevel']))
        #result = self.conn.execute(statment)
        #rows = result.fetchall()
        #result.close()
        
        ##we should be able to replace this with a very small sql query
        #maxLevel = None
        #for row in rows:
            #if maxLevel == None or maxLevel < row['levelIdZ']:
                #maxLevel = row['levelIdZ']
                
        #return maxLevel
                
        #self.dbClose(conn)
        
        
def prepareZoomMap(zoom, x, y):
    oldNCells = 2 ** (zoom - 2)
    
    x = (x / oldNCells) * oldNCells
    y = (y / oldNCells) * oldNCells
    
    #open the previous zoom level image to get the image size information
    image1 = "img-world/zoom%d-%dx-%dy.png" % (zoom - 1,x, y)
    image2 = "img-world/zoom%d-%dx-%dy.png" % (zoom - 1,x + oldNCells, y)
    image3 = "img-world/zoom%d-%dx-%dy.png" % (zoom - 1,x, y + oldNCells)
    image4 = "img-world/zoom%d-%dx-%dy.png" % (zoom - 1,x + oldNCells, y + oldNCells)
        
    return zoomMap(zoom, x, y, image1, image2, image3, image4)
        
def zoomMap(zoom, x, y, image1, image2, image3, image4):
    try:
        oldImage1 = Image.open(image1)
    except:
        oldImage1 = Image.open("img-src/void.png")
        
    try:
        oldImage2 = Image.open(image2)
    except:
        oldImage2 = Image.open("img-src/void.png")
        
    try:
        oldImage3 = Image.open(image3)
    except:
        oldImage3 = Image.open("img-src/void.png")
    
    try:
        oldImage4 = Image.open(image4)
    except:
        oldImage4 = Image.open("img-src/void.png")
    
    xSize, ySize = oldImage1.size

    newImage = Image.new('RGB', (xSize*2, ySize*2))
    
    newImage.paste(oldImage1, (0,0))
    newImage.paste(oldImage2, (xSize,0))
    newImage.paste(oldImage3, (0, ySize))
    newImage.paste(oldImage4, (xSize,ySize))

    newImage.thumbnail((xSize,ySize))
    
    name = "img-world/zoom%d-%dx-%dy.png" % (zoom, x, y)
    
    try:
        oldImage = Image.open(name)
    except:
        oldImage = Image.open("img-src/void.png")
    
    oldImage = oldImage.convert('RGB')
    
    if ImageChops.difference(newImage, oldImage).getbbox() is None:
        #there was no change to the image, leave everything alone and return false
        return False
    else:
        #save and return true
        newImage.save("img-world/zoom%d-%dx-%dy.png" % (zoom, x, y))
        
        return True
