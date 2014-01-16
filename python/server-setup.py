#!/usr/bin/python2.6
# -*- coding: utf-8 -*-
import random
import sys
import sqlalchemy
import time

import khopeshpy.world
from khopeshpy import db

def setup(world, conn):
	trans = conn.begin()
	
	try:
		print 'genHeightMap...',
		world.genHeightMap()
		print 'finished'
		
		print 'genSurface...',
		world.genSurface()
		print 'finished'
		
		print 'genSurfaceTemps...',
		world.genSurfaceTemps()
		print 'finished'
		
		print 'genSolarRadiation...',
		world.genSolarRadiation()
		print 'finished'
		
		print 'genBiomes...',
		world.genBiomes()
		print 'finished'
		
		print 'genImages...',
		world.genImages()
		print 'finished'
		
		print 'addAnimals...',
		world.addAnimals()
		print 'finished'
		
		print 'saveAll...',
		world.saveAll()
		print 'finished'
		
		print 'setDefaults...',
		world.setDefaults()
		print 'finished'
		
		trans.commit()
	except:
		trans.rollback()
		print 'Could not commit changes to database'
		raise
		

if __name__=='__main__':
	conn = db.connect()
	
	random.seed()
	
	world = khopeshpy.world.Setup(conn)
	
	if len(sys.argv) == 1:
		setup(world, conn)
		world.genZoom()
	elif len(sys.argv) == 2 and sys.argv[1] == "db":
		setup(world, conn)
	elif len(sys.argv) == 2 and sys.argv[1] == "zoom":
		world.pullData()
		world.pullCells()
		world.genZoom()
		
	conn.close()