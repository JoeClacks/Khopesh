import ConfigParser

cfg = ConfigParser.RawConfigParser()
cfg.read('khopesh.cfg')

tick = cfg.getfloat('gameworld', 'secondsPerTick')
worldTick = cfg.getfloat('gameworld', 'worldTick')
worldSeaLevel = cfg.getint('worldmap', 'sealevel')
maxHeight = cfg.getint('worldmap', 'maxHeight')

def get(section, option):
    return cfg.get(section, option)

def getint(section, option):
    return cfg.getint(section, option)

def getfloat(section, option):
    return cfg.getfloat(section, option)

def getboolean(section, option):
    return cfg.getboolean(section, option)