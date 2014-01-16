//create the global object if it doesn't already exist
var Khopesh = Khopesh ? Khopesh : {};

Khopesh.ModelSpinner = {
	entry: function(objType, id, callback)
	{
		this.objType = objType;
		this.id = id;
		this.callback = callback;	
	},
	
	serverstring: 'http://localhost:8090/',
	callbackstring: '?callback=?',

	entries: new Array(),
	
	//objType; the type of the object being updated
	//id: the id of the object being updated
	//callback: the method to call with the result
	register: function(objType, id, callback)
	{
// 		Khopesh.console("Registering: " +objType+ "," +id+ "," +callback);
		this.entries.push(new this.entry(objType, id, callback));
	},
	
	//call with setInterval so that all the stored objects are updated constantly
	spin: function()
	{
		var me = this;

		for(var x in this.entries)
		{			
			$.getJSON(this.serverstring,
      {'objType': this.entries[x].objType, 'objId': this.entries[x].id},	
      function(json)
      {
				me.entries[x].callback(json);
      });
		}
	},	
};


//later on all we'll have to do is:
//this[entry] = value