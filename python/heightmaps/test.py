# -*- coding: utf-8 -*-
#this file converts the 16-bit signed format into 16-bit unsigned greyscale
#the command to get the png file from the orgional tiff is:
#convert ETOPO1_Bed_g.tif -depth 16 -type Grayscale ETOPO1_Bed_g2.png

import Image

im = Image.open('ETOPO1_Bed_g2.png')
#im = Image.open('test.png')

xSize, ySize = im.size

print im.size

im2 = Image.new('I', im.size)

for x in xrange(xSize):
  for y in xrange(ySize):
    pix = im.getpixel((x,y)) 
    
    if(pix >= 32768):
      pix = pix - 32768
    else:
      pix = pix + 32768
   
      
    im2.putpixel((x,y),pix)

  print x,
    
im2.save('ETOPO1_Bed_g3.png')

#