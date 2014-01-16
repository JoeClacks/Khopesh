# -*- coding: utf-8 -*-
import Image 
import sys
import math

import db
import cell
import config

import khopeshpy.exceptions

class World:
    worldId = config.getint('worldmap', 'worldId')
    heightmap = config.get('worldmap', 'heightmap')
    sealevel = config.getint('worldmap', 'sealevel')
    wrapX = config.getboolean('worldmap', 'wrapX')
    wrapY = config.getboolean('worldmap', 'wrapY')

class Setup(World):
    conn = None
    
    valid = False
    
    def __init__(self, conn):
        self.conn = conn
        
        self.data = {}
        self.data['worldSeaLevel'] = self.sealevel
        
        self.cells = {}
        
    def pullData(self):
        c = db.worldData.columns
        statment = db.select([db.worldData], (c.worldId == self.worldId))
        result = self.conn.execute(statment)
        row = result.fetchone()
        result.close()
        
        if row == None:
            msg = "No record found for world with id: (%d)" % (self.worldId)
            raise Exception(msg)
        
        self.data.update(dict(row))
        self.valid = True
        
    def pullCells(self):
        self.cells = {}
        
        for y in xrange(self.data['worldSizeY']):
            print y,
            sys.stdout.flush()
                
            for x in xrange(self.data['worldSizeX']):
                self.cells[(x,y)] = cell.Setup(conn = self.conn, position = (x,y))
                self.cells[(x,y)].pullData()
    
    def genHeightMap(self):    
        im = Image.open(self.heightmap)

        self.lengthX, self.lengthY = im.size
        
        self.data['worldSizeX'] = self.lengthX
        self.data['worldSizeY'] = self.lengthY
        
        for y in xrange(self.lengthY):
            print y,
            sys.stdout.flush()
            
            for x in xrange(self.lengthX):
                height = im.getpixel((x,y))
                cellObj = cell.Setup(position= (x, y), conn = self.conn)
                cellObj.genHeightMap(height)
                self.cells[(x,y)] = cellObj
                
    def genSurface(self):
        for y in xrange(self.lengthY):
            #print y,
            #sys.stdout.flush()
            
            for x in xrange(self.lengthX):
                self.cells[(x,y)].genSurface()
                
    def genSurfaceTemps(self):
        for y in xrange(self.data['worldSizeY']):
            lat = math.fabs(self.data['worldSizeY']/2.0 - y)/(self.data['worldSizeY']/2.0)
            
            print y,
            sys.stdout.flush()
            
            for x in xrange(self.data['worldSizeX']):
                self.cells[(x,y)].genSurfaceTemp(lat)
                
    def genSolarRadiation(self):
        for y in xrange(self.data['worldSizeY']):
            lat = math.fabs(self.data['worldSizeY']/2.0 - y)/(self.data['worldSizeY']/2.0)
            
            print y,
            sys.stdout.flush()
            
            for x in xrange(self.data['worldSizeX']):
                self.cells[(x,y)].genSolarRadiation(lat)
                
    def genBiomes(self):
        for y in xrange(self.data['worldSizeY']):
            print y,
            sys.stdout.flush()
            
            for x in xrange(self.data['worldSizeX']):
                self.cells[(x,y)].genBiomes()
                
    def genImages(self):
        for y in xrange(self.data['worldSizeY']):
            print y,
            sys.stdout.flush()
                
            for x in xrange(self.data['worldSizeX']):
                self.cells[(x,y)].genImages()
                
    def addAnimals(self):
        for y in xrange(self.data['worldSizeY']):
            print y,
            sys.stdout.flush()
                
            for x in xrange(self.data['worldSizeX']):
                self.cells[(x,y)].addAnimals()
                
    def saveAll(self):
        c = db.worldData.columns
        ins = db.worldData.insert().values(worldId = self.worldId, worldSeaLevel = self.sealevel, worldSizeX = self.lengthX, worldSizeY = self.lengthY, worldWrapX = self.wrapX, worldWrapY = self.wrapY)
        self.conn.execute(ins)
        
        for y in xrange(self.data['worldSizeY']):
            print y,
            sys.stdout.flush()
            
            for x in xrange(self.data['worldSizeX']):
                self.cells[(x,y)].saveAll()
                
    def setDefaults(self):
        #ins = db.userData.insert().values(userId = 1, username = 'joe', password = 'pass', name = 'Etarip', userX = 0, userY = 27, userZ = 100)
        #self.conn.execute(ins)
        
        #ins = db.familyData.insert().values(familyId = 1, userId = 1, name = 'Blackthrorn', state = True)
        #self.conn.execute(ins)
        
        #ins = db.avatarData.insert().values(avatarId = 1, familyId = 1, userId = 1, name = 'max', state = avatars.States.ADULT, avatarX = 36, avatarY = 25, avatarZ = 129)
        #self.conn.execute(ins)
        
        ins = db.cityData.insert().values(cityId = 1, cityName = "Primary City", cityStarter = True)
        self.conn.execute(ins)
        
        c = db.levelData.columns
        up = db.levelData.update().where((c.cellIdX == 36) & (c.cellIdY == 25) & (c.levelIdZ == 129)).values(cityId = 1, dirtyImage = True)
        self.conn.execute(up)
        
    def genZoom(self):
        print "producing first zoom layer...",
        zoom = 2
        nCells = 2 ** (zoom - 1)
        for y in xrange(0, self.data['worldSizeY'], 2):
            print y,
            sys.stdout.flush()
            
            for x in xrange(0, self.data['worldSizeX'], 2):
                try:
                    #self.cells[(x,y)].firstZoomLevel(self.cells[(x+1,y)],
                        #self.cells[(x,y+1)],self.cells[(x+1,y+1)])
                    cell.zoomMap(zoom, x, y,\
                        self.cells[(x,y)].data['cellImage'],\
                        self.cells[(x+1,y)].data['cellImage'],\
                        self.cells[(x,y+1)].data['cellImage'],\
                        self.cells[(x+1,y+1)].data['cellImage'])
                except:
                    pass
        print "finished"
        
        zoom = 3
        nCells = 2 ** (zoom - 1)
        while nCells < self.data['worldSizeX'] and nCells < self.data['worldSizeY']:
            print "Stage:", zoom, "Number of base images per new image:", nCells
            
            for y in xrange(0, self.data['worldSizeY'], nCells):
                print y,
                sys.stdout.flush()
                
                for x in xrange(0, self.data['worldSizeX'], nCells):
                    cell.prepareZoomMap(zoom, x, y)
                        
            print "Finished stage", zoom
            zoom = zoom + 1
            nCells = 2 ** (zoom - 1)
    
class Update(World):
    conn = None
    
    valid = False
    
    def __init__(self, conn):
        self.conn = conn
        
        self.data = {}
        self.data['worldSeaLevel'] = self.sealevel
        
        self.cells = {}
        
    def pullData(self):
        c = db.worldData.columns
        statment = db.select([db.worldData], (c.worldId == self.worldId))
        result = self.conn.execute(statment)
        row = result.fetchone()
        result.close()
        
        if row == None:
            msg = "No record found for world with id: (%d)" % (self.worldId)
            raise Exception(msg)
        
        self.data.update(dict(row))
        self.valid = True
        
class Model(World):
    def __init__(self, conn):
        self.conn = conn
        self.data = {}
        
    def pullData(self):
        c = db.worldData.columns
        statment = db.select([db.worldData], (c.worldId == self.worldId))
        
        result = self.conn.execute(statment)
        row = result.fetchone()
        result.close()
        
        if row == None:
            msg = "world.Model.pullData: Did not find worldData record for id: %d, exiting." % (self.worldId)
            raise khopeshpy.exceptions.JSONException(msg)
        
        self.data.update(dict(row))