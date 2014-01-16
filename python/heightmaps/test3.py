# -*- coding: utf-8 -*-
import Image
import math

im = Image.open('ETOPO1_Bed_g4.png')
#im = Image.open('test.png')

xSize, ySize = im.size

print im.size

im2 = Image.new('RGB', im.size)

for x in xrange(xSize):
  for y in xrange(ySize):
    pix = float(im.getpixel((x,y)))/float(19169.0)

    if pix < 0.3333:
      r = 1.0 - (pix*1.0/0.3333)
    elif pix > 0.6666:
      r = (pix - 0.6666)*(1.0/0.3333)
    else:
      r = 0.0
      
    if pix < 0.3333:
      b = pix*1.0/0.3333
    elif pix > 0.3333 and pix < 0.6666:
      b = (0.6666 - pix)*(1.0/0.3333)
    else:
      b = 0.0
      
      
    if pix > 0.6666:
      g = (1.0 - pix)*(1.0/0.3333)
    elif pix > 0.3333 and pix < 0.6666:
      g = ((pix - 0.3333)*1.0/0.3333)
    else:
      g = 0.0
            
    r = int(math.floor(r*255.0))
    g = int(math.floor(g*255.0))
    b = int(math.floor(b*255.0))
    
    im2.putpixel((x,y),(r,g,b))

  print x,
    
im2.save('ETOPO1_Bed_g5.png')
