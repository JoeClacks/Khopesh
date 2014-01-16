function UserData(userId)
{
  this.userId = userId;
  this.userName = "";

  this.userX = 0;
  this.userY = 0;
  this.userZ = 0;

  this.ready = false;
  
  //used for callbacks
  var me = this;
  
  this.updateEvent = new Array();
  
  this.pullData = function (callback)
  {
    $.getJSON("http://localhost:8080/getUserData?callback=?",
      {"userId" : me.userId },
      function(json)
      {
	
				me.userName = json["userName"];
				me.userX = json["userX"];
				me.userY = json["userY"];
				me.userZ = json["userZ"];
				me.ready = true;
				divConsoleLog("Got response for userData:");
				divConsoleLog(me);

				if (callback != undefined)
				{
					callback();
				}
      });
  }
  
	this.toString = function ()
	{
		return "userId: " + this.userId + 
			" userName: " + this.userName + 
			" userX: " + this.userX + 
			" userY: " + this.userY + 
			" userZ: " + this.userZ +
			" ready: " + this.ready;
	}

	this.update = function(update)
	{
		for(var x in update)
		{
			this[x] = update[x];
		}
		
		for(var x in updateEvent)
		{
			updateEvent[x]();
		}
	}
	
	this.onUpdate = function(callback)
	{
		this.updateEvent.push(callback);	
	}
		//

}