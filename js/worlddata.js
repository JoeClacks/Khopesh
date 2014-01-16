function WorldData(worldId)
{
  this.worldId = worldId
  this.worldName = "";

  this.worldSizeX = 0;
  this.worldSizeY = 0;
  
  this.worldWrapX = false;
  this.worldWrapY = false;

  this.ready = false;
  
  //for callbacks
  var me = this;

  this.pullData = function (callback)
  {
    $.getJSON("http://localhost:8080/getWorldData?callback=?",
      { "worldId" : me.worldId },
      function(json)
      {
				me.worldName = json["worldName"]

				me.worldSizeX = json["worldSizeX"];
				me.worldSizeY = json["worldSizeY"];
				
				me.worldWrapX = json["worldWrapX"];
				me.worldWrapY = json["worldWrapY"];
				
				me.ready = true;
				divConsoleLog("Got response for worldData:");
				divConsoleLog(me);
				
				if (callback != undefined)
				{
					callback();
				}
      });
  }
  
  this.toString = function ()
  {
		return "worldId: " + this.worldId +
			" worldName: " + this.worldName +
			" worldSizeX: " + this.worldSizeX +
			" worldSizeY: " + this.worldSizeY +
			" worldWrapX: " + this.worldWrapX +
			" worldWrapY: " + this.worldWrapY +
			" ready: " + this.ready;  
  }
}
