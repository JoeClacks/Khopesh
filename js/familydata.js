function FamilyData()
{
	this.familyId = 0;
	this.familyName = "";
	this.familyState = 0;
	
	this.ready = false;
	
	//used for callbacks
  var me = this;
  
  this.pullData = function (userid, callback)
  {
    $.getJSON("http://localhost:8080/getFamilyData?callback=?",
      {"userId" : userId },
      function(json)
      {
				if(json != -1)
				{
					me.familyId = json["familyId"];
					me.familyName = json["familyName"];
					me.familyState = json["familyState"];
					me.ready = true;
					divConsoleLog("Got response for familyData:");
					divConsoleLog(me);

					if (callback != undefined)
					{
						callback();
					}
				}
      });
  }
  
	this.toString = function ()
	{
		return "familyId: " + this.familyId + 
			" familyName: " + this.familyName + 
			" familyState: " + this.familyState;
	}
}