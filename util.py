def genLevelData(landlevel, sealevel, z):		
	#we may want a function to let us set one of these and have the others
	#	auto adjust

	out = {}
	out['dirt'] = 0.0
	out['water'] = 0.0
	out['air'] = 0.0
	out['rock'] = 0.0

	out['grass'] = 0.0
	out['forest'] = 0.0
	out['farm'] = 0.0
	out['city'] = 0.0
	
	print "z:", z, "land:", landlevel, "sea:", sealevel

	z = int(z)
	landlevel = int(landlevel)
	sealevel = int(sealevel)

	if z < landlevel:
		print 'rock'
		out['rock'] = 1.0
	elif z > landlevel and z < sealevel:
		print 'water'
		out['water'] = 1.0
	elif z > landlevel and z > sealevel:
		print 'air'
		out['air'] = 1.0
	elif z == landlevel and z < sealevel:
		out['rock'] = 0.5
		out['water'] = 0.5
	elif z > landlevel and z == sealevel:
		out['water'] = 0.5
		out['air'] = 0.5
	elif z == landlevel and z > sealevel:
		out['rock'] = 0.5
		out['air'] = 0.5
	elif z == landlevel and z == sealevel:
		out['rock'] = 0.33
		out['water'] = 0.33
		out['air'] = 0.33
	else:
		#something went wrong, we'll leave all the settings at 0 and it will render as void
		pass

	out['baseImage'] = genSrcTileName(out)
	
	return out

def genSrcTileName(level):
		if level['rock'] > 0.9:
			#underground
			return "img-src/rock.png"
		elif level['water'] > 0.1:
			#more the ten percent water
			return "img-src/ocean.png"
		elif level['air'] > 0.99:
			#up in the sky
			return "img-src/sky.png"
		else:
			#somethings wrong
			return "img-src/void.png"