import json
import sys
from mod_python import Session
from mod_python import util
from mod_python import apache

#our files
import db

#TODO Sanitize inputs
def getWorldData(data):
  cursor = db.cursor()

  cursor.execute("select worldName, worldSizeX, worldSizeY, worldSizeZ, \
		    worldWrapX, worldWrapY, worldSeaLevel \
		  from worldData where worldId = %s", (data['worldId'],))

  row = cursor.fetchone()
    
  if row == None:
    print "Did not find worldData record, exiting."
    sys.exit(1)
    

  self.lengthX = row["worldSizeX"]
  self.lengthY = row["worldSizeY"]
    
    self.wrapX = True if row["worldWrapX"] == 1 else False
    self.wrapY = True if row["worldWrapY"] == 1 else False
    
    cursor.close()

def index(req):
  session = Session.Session(req)

  #try:
    #session['hits'] += 1
  #except:
    #session['hits'] = 1

  req.content_type = 'text/plain'

  data = util.FieldStorage(req)
  if 'callback' not in data:
    msg = "Not called with jsonp callback"
    apache.log_error(msg)
    req.write(msg)
  elif 'function' not in data:
    msg = "Not called with a function"
    apache.log_error(msg)
    req.write(msg)
  elif data['function'] == 'getLocation':
    req.write(data['callback'] +'({"userX":0, "userY":0, "userZ":0})');
  elif data['function'] == 'getWorldData':
    getWorldData(data)
  else:
    msg = "Not a recognized function: " + data['function']
    apache.log_error(msg)
    req.write(msg)
    

  
  ##req.write("Hits: %d\n" % session['hits'])
  #req.write(data['callback'] +'({"data":"fjkdlskkk"})');

  #apache.log_error("Callback: " + str(data))


  

  session.save()

  return None