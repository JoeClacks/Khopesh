# -*- coding: utf-8 -*-
import Image
#moves all the pixles towards 0
im = Image.open('ETOPO1_Bed_g3.png')
#im = Image.open('test.png')

xSize, ySize = im.size

print im.size

im2 = Image.new('I', im.size)

for x in xrange(xSize):
  for y in xrange(ySize):
    pix = im.getpixel((x,y)) 
    
    pix = pix - 21870    
    
    im2.putpixel((x,y),pix)

  print x,
    
im2.save('ETOPO1_Bed_g4.png')
