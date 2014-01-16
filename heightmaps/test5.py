# -*- coding: utf-8 -*-
import Image
import math

im = Image.open('ETOPO1_Bed_g4.png')
#im = Image.open('test.png')

xSize, ySize = im.size

print im.size

im2 = Image.new('I', im.size)

for x in xrange(xSize):
    for y in xrange(ySize):
        pix = float(im.getpixel((x,y)))/float(19169.0)
        
        pix = int(math.floor(pix*4096.0))
        
        im2.putpixel((x,y),pix)
    
    print x,
    
im2.save('ETOPO1_Bed_g7.png')
