import khopeshpy.db as db

#needs to return (x,y,z)...
def getStartingLocation(conn):
    c = db.cityData.columns
    statment = db.select([db.cityData], c.cityStarter == True)
    
    result = conn.execute(statment)
    row = result.fetchone()
    result.close()
    
    #just get the first one now, select one randomly later
    if row != None:
        return (row['cityStartX'],row['cityStartY'],row['cityStartZ'],)
    else:
        return (-1,-1,-1)