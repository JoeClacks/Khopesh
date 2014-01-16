//This class is built with the idea that eventually we will be able to
// send out all the requests at once can only need to wait for one response.
//But for simplicity we'll just use it as a container to call each of the
//	methods individually for right now

//note: this creates more of a namespace or a singleton than an acual class
//	and does not need to be and should not be instantiated
//Then entires array will be instantiated when the closure is loaded

//create the global object if it doesn't already exist
var Khopesh = Khopesh ? Khopesh : {};
Khopesh.ModelSpinner = {
	entry: function(objType, id, callback)
	{
		this.objType = objType;
		this.id = id;
		this.callback = callback;	
	},
	
	serverstring: 'http://localhost:8080/getUpdate?callback=?',

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
	
	spinOnce: function(objType, id, callback)
	{
		$.getJSON(this.serverstring,
		{'objType': objType, 'objId': id},	
		function(json)
		{
			callback(json);
		});
	}
};


//later on all we'll have to do is:
//this[entry] = value