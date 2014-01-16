import math

instances = {}

def growth(biomeType, lat, temp, dt, initial):
    return instances[biomeType].growth(lat, temp, dt, initial)
    
def maxBioMass(biomeType):
    return instances[biomeType].maxBioMass
    
class Biome:
    #looks like we'll have to guess for these
    maxBioMass = None    
        
class BiomeGrown(Biome):
    tempIdeal = None
    tempRange = None #one sided
    
    def growth(self, solar, temp, dt, P):
        #make sure we have something to work with
        if P < 0.01 or P == None:
            P = 0.01
            
        #temp adjustment
        a = math.fabs(self.tempIdeal - temp)/self.tempRange
        b = 1 - a**2
        
        #solar rad adjustment, stuff closer to the equator has more available energy
        #    and can grow faster
        r = b * solar
        
        #adjust our dt to the length of a tick
        #t = (float(dt)/config.tick)
        
        #logistic function to simulate growth
        # accuracy will be dependent on how often it is updated
        newP = P + dt*r*P*(1.0 - P)
        
        if newP < 0:
            newP = 0
            
        return newP
    
    
    

    
class BiomeSavanna(BiomeGrown):
    tempIdeal = 25.0
    tempRange = 10
    
    maxBioMass = 25000.0

instances['savanna'] = BiomeSavanna()

class BiomeGrassland(BiomeGrown):
    tempIdeal = 15.0
    tempRange = 10
    
    maxBioMass = 35000.0
    
instances['grassland'] = BiomeGrassland()
    
class BiomeForestCanopy(BiomeGrown):
    tempIdeal = 5.0
    tempRange = 10
    
    maxBioMass = 100000.0
    
instances['forestCanopy'] = BiomeForestCanopy()
    
class BiomeTaigaCanopy(BiomeGrown):
    tempIdeal = -5.0
    tempRange = 10
    
    maxBioMass = 100000.0
    
instances['taigaCanopy'] = BiomeTaigaCanopy()
    
class BiomeTundra(BiomeGrown):
    tempIdeal = -15.0
    tempRange = 10
    
    maxBioMass = 10000.0

instances['tundra'] = BiomeTundra()


#for now we'll use desert and ice to represent lack of a biome based on tempature


#not using right now
#class BiomeConverted(Biome):
    #dieBackRate = None
    #convertRate = None
    
    #def dieBack(self, initial):
        #return initial*self.dieBackRate
        
    #def convert(self, canopy, understory):
        #canopyConvert = canopy * self.convertRate
        #canopy -= canopyConvert
        #understory += canopyConvert
        
        #return (canopy, understory)
        
#class BiomeTaigaUnderstory(BiomeConverted):
    #dieBackRate = 0.01
    #convertRate = 0.01
    
    #maxBioMass = 200.0
    
#instances['taigaUnderstory'] = BiomeTaigaUnderstory()

#class BiomeForestUnderstory(BiomeConverted):
    #dieBackRate = 0.01
    #convertRate = 0.01
    
    #maxBioMass = 200.0
    
#instances['forestUnderstory'] = BiomeForestUnderstory()
    