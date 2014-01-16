var Khopesh = Khopesh ? Khopesh : {};

Khopesh.PlayerUser = {
	userId = 0,
	ready = false,
	loggedIn = false,
	
	data = {},
	
	update = function()
	{
		var me = this;
		
		Controller.proxy('updatePlayer', 
		{},
		function(json) {
			for(var k in json)
			{
				me[k] = json[k];
			}
			me.ready = true;
		});
	},
	
	construct = function(userId)
	{
		function F() {};
		F.prototype = this;
		
		//constructor code goes here
		F.userId = userId;
		F.data = {};
		
		return new F;
	},	
};
