#import os
#
#from db import worldData
#
#
#worldSizeX = 10
#worldSizeY = 20
#worldWrapX = False
#worldWrapY = True
#
#worldLevels = 20
#worldSeaLevel = 10
#
#world = None
#
##class userData:
#  #userName  = "user1"	#string
#  #password  = "pass" 	#string
#  
#  ##current location of the player
#  #cell = currentCell()	#reference? should probably be a static address (int)
#  #level = currentLeve() #should be an int between +-levelMax
#  
#  #citizenship = [] #list of all governments where citizenship is held
#    ##should only be visible to users and governments?
#    
#  #cashAccounts = []
#  #items = []
#    
#  
#class levelData:
#  cellId = 0
#  levelId = 0
#  
#  dirt = 0.0
#  water = 0.0
#  air = 0.0
#  stone = 0.0
#  #terrain = {}
#
#
#  grass = 1.0
#  forest = 0.0
#  farm = 0.0
#  developed = 0.0
#  #biome = {}
#  
#  transLevel = 0
#  devLevel = 0
#  
#  currentPlayers = []
#  
#  wildlife = []
#  buildings = []
#  defenses = []
#   
#  #should keep low numbers for special cases
#  #	we'll make 0 for unowned
#  owner = 0 #playerId or governmentId
#  
#  def __init__(self, source, cellId, levelId):
#    self.cellId = cellId
#    self.levelId = levelId
#    
#    if source == "static":
#      if self.levelId < worldSeaLevel:
#	#we may want a function to let us set one of these and have the others
#	#	auto adjust
#	dirt = 0.0
#	water = 0.0
#	air = 0.0
#	stone = 0.0
#      elif self.levelId == worldSeaLevel:
#	dirt = 0.5
#	water = 0.0
#	air = 0.5
#	stone = 0.0
#      elif self.levelId == worldSeaLevel:
#	dirt = 0.0
#	water = 0.0
#	air = 1.0
#	stone = 0.0
#	
#      grass = 1.0
#      forest = 0.0
#      farm = 0.0
#      developed = 0.0
#      
#      transLevel = 0
#      devLevel = 0
#      
#      currentPlayers = []
#
#      wildlife = []
#      buildings = []
#      defenses = []
#      
#      owner = 0     
#  
#class cellData:
#  cellId = 0
#  levels = []
#    
#  def __init__(self, source, cellId):
#    self.cellId = cellId
#    
#    self.levels = []
#    if source == "static":
#      for i in range(worldLevels):
#	self.levels.append(levelData("static", cellId, i))
#    
#  
#class worldData:
#  lengthX = 0
#  lengthY = 0
#  
#  wrapX = True
#  wrapY = True  
#  
#  cells = []
#  
#  def __init__(self, source):
#    if source == "static":
#      self.lengthX = worldSizeX
#      self.lengthY = worldSizeY
#      self.wrapX = worldWrapX
#      self.wrapY = worldWrapY
#      
#      self.cells = []
#      for i in range(self.lengthX * self.lengthY):
#	self.cells.append(cellData("static", i))
#	
#  #vert and horizCells are the number of cells to show away from the center
#  def getMap(self, cell, level, vertCells, horizCells):
#    x = cell % lengthX
#    y = cell / lengthX
#    
#    ret = []
#    for i in range(vertCells * 2 + 1):
#      row = []
#      for j in range(horizCells * 2 + 1):
#	
#    
#    
#	
#  
#def initServer(mode):
#  if mode == "static":
#    world = worldData("static")
#  
#def worldMap():
#  return world.getMap(cell, level)
#  
#def start():
#  initServer("static")
#  #initServer(dbHandle,worldid)
#  
#  #start service
#  #serviceLoop:
#    #if request ==  "world map":
#      #send(worldMap())
#  
#  
#  
#if __name__=='__main__':
#  start()
