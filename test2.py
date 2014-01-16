# -*- coding: utf-8 -*-
import math

def getMaximum():
  return lambda obj: 25.0

def getPercent(value, maximum):
  return lambda obj: getattr(obj, value)/getattr(obj, maximum)  

def getStat(name):
  return lambda obj: math.floor(math.sqrt(getattr(obj, name)/10.0)) + 1.0

def getValue(name):
  return lambda obj: obj.data[name]
  
def setValue(name):
  def setValueInner(obj, value):
    obj.data[name] = value
    
  return setValueInner
  
    
class TestClass(object):
  data = {'growth': 15.0}
  
  growth = property(getValue('growth'), setValue('growth'))
    
  growthStat = property(getStat('growth'))
  
  growthMax = property(getMaximum())
  
  growthPct = property(getPercent('growth', 'growthMax'))
  
  
anObject = TestClass()

print anObject.growth
print anObject.growthStat
print anObject.growthMax
print anObject.growthPct

anObject.growth = 25.0

print anObject.growth
print anObject.growthStat
print anObject.growthMax
print anObject.growthPct