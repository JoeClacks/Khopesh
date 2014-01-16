# -*- coding: utf-8 -*-
import Image

im = Image.open('earth-21601x10801x65535.png')
#im = Image.open('test.png')

def shrink(divisior):
	global im
	
	xSize, ySize = im.size
	print im.size
	im = im.resize((xSize/divisior, ySize/divisior))
	im.save('earth-%dx%dx65535.png' % (xSize/divisior, ySize/divisior))


shrink(5)
shrink(5)
shrink(2)
shrink(2)