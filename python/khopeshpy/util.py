'''
utility functions
'''

import math

def getPercent(value, maximum):
    return lambda obj: getattr(obj, value)/getattr(obj, maximum)  

def getStat(name):
    '''
    converts a value into a stat, right now we're justing sqrt, floor and +1 make
    sure that it is always an integer (not that important) and 1 or greater 
    (very important if we have to divide anywhere)
    '''
    return lambda obj: math.floor(math.sqrt(getattr(obj, name)/10.0)) + 1.0

def getValue(name):
    return lambda obj: obj.data[name]

def setValue(name):
    def setValueInner(obj, value):
        obj.data[name] = value

    return setValueInner
    
def setBarValue(name, maximum):
    '''
    closure for setBarValueInner
    '''
    
    def setBarValueInner(obj, value):
        '''
        does bounds checking before setting the value
        '''
        
        if value > maximum:
            value = maximum
        elif value < 0.0:
            value = 0.0
            
        obj.data[name] = value

    return setBarValueInner
